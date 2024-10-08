from datetime import datetime, timezone
import json
import logging
from typing import Optional

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database import get_session, get_redis
from database.models import Game, Room, RoomUser, User
from exceptions.custom_exceptions import (
    RoomNameNotUniqueError,
    RoomNotFoundError,
    UserAlreadyInRoomError,
    UserNotAdminOfRoomError,
    UserNotFound,
    UserNotInARoomError,
    UserNotPending,
)
from schemas import GameResponse, RoomCreate, RoomResponse, RoomUserResponse

from .cache import CacheKeyGenerator, get_cache, invalidate_cache, set_cache
from .enums import AdminApprovalStatus, ApprovalStatus, RoomEventTypes, UserType

logger = logging.getLogger("uvicorn.error")


async def get_game_history(
    room_id: str, session: AsyncSession = Depends(get_session)
) -> list[GameResponse]:
    """Fetches game history for a room."""
    logger.info("Fetching game history for room_id: %s", room_id)

    query = (
        select(Game).options(selectinload(Game.prices)).filter(Game.room_id == room_id)
    )
    result = await session.execute(query)
    games = result.scalars().all()

    if not games:
        logger.warning("No game history found for room_id: %s", room_id)
        return []

    logger.info("Game history retrieved successfully for room_id: %s", room_id)
    return [GameResponse.from_game_obj(game) for game in games]


async def create_user(user_id: str):
    """Creates a new user."""
    logger.info("Attempting to create user with user_id: %s", user_id)

    user = User(id=user_id)
    async for session in get_session():
        try:
            session.add(user)
            await session.commit()
            logger.info("User created successfully with user_id: %s", user_id)
        except IntegrityError:
            await session.rollback()
            logger.warning(
                "User creation failed: User with user_id %s already exists", user_id
            )


async def get_user(user_id: str, session: AsyncSession) -> User:
    """Fetches a user from db and raises an error if non-existing."""
    logger.info("Fetching user from db with id: %s.", user_id)

    result = await session.execute(select(User).filter_by(id=user_id))
    user = result.scalar_one_or_none()
    if not user:
        logger.error("User with id %s not found.", user_id)
        raise UserNotFound()
    logger.info("User with id %s found.", user_id)
    return user


async def create_room_dependency(
    room_data: RoomCreate,
    redis: Redis = Depends(get_redis),
    session: AsyncSession = Depends(get_session),
):
    """Dependency to handle the creation of a room."""
    logger.info("Creating new room with name: %s", room_data.name)

    user = await get_user(room_data.user_id, session)
    new_room = Room(name=room_data.name, created_by=user.id)
    try:
        session.add(new_room)
        await session.commit()
        await session.refresh(new_room)
        room_response = RoomResponse(
            id=new_room.id,
            created_at=new_room.created_at.isoformat(),
            created_by=new_room.created_by,
            name=new_room.name,
        )

        logger.info("Room created successfully: %s", new_room)
        logger.info("Publishing room creation message.")

        await redis.publish("rooms", json.dumps(room_response.model_dump()))
        logger.info("Invalidating room cache.")

        await invalidate_cache(CacheKeyGenerator.generate_rooms_cache_key(), redis)
        return new_room
    except IntegrityError as exc:
        logger.error("Room creation failed due to IntegrityError: %s", exc)
        await session.rollback()
        raise RoomNameNotUniqueError() from exc


async def get_room(
    room_id: str,
    session: AsyncSession = Depends(get_session),
) -> Room:
    """Dependency that fetches a room from db."""
    logger.info("Fetching room with room_id: %s", room_id)

    room = await session.get(Room, room_id)
    if room is None:
        logger.error("Room not found with room_id: %s", room_id)
        raise RoomNotFoundError()
    logger.info("Room found: %s", room)

    return room


async def get_all_rooms(
    redis: Redis = Depends(get_redis), session: AsyncSession = Depends(get_session)
) -> list[RoomResponse]:
    """Fetch all rooms from the database."""
    logger.info("Fetching all rooms from the database.")

    cached_rooms = await get_cache(CacheKeyGenerator.generate_rooms_cache_key(), redis)
    if cached_rooms:
        logger.info("Cached rooms found")
        return [RoomResponse.model_validate(obj) for obj in json.loads(cached_rooms)]

    logger.info("No cached rooms found. Querying database.")

    rooms_query = await session.execute(select(Room).order_by(Room.created_at.desc()))
    rooms_response = [
        RoomResponse(
            id=room.id,
            created_at=room.created_at.isoformat(),
            created_by=room.created_by,
            name=room.name,
        )
        for room in rooms_query.scalars()
    ]
    await set_cache(
        CacheKeyGenerator.generate_rooms_cache_key(),
        json.dumps([room.model_dump() for room in rooms_response]),
        redis,
    )

    logger.info("All rooms fetched successfully. Total rooms: %d", len(rooms_response))
    return rooms_response


async def get_user_in_room(
    room_id: str,
    user_id: str,
    session: AsyncSession = Depends(get_session),
) -> RoomUser:
    """Dependency that checks if user is in a room"""
    logger.info("Checking if user_id: %s is in room_id: %s", user_id, room_id)

    user_query = await session.execute(
        select(RoomUser).filter_by(
            room_id=room_id, user_id=user_id, status=ApprovalStatus.APPROVED
        )
    )
    room_user = user_query.scalar_one_or_none()

    if room_user is None:
        logger.error("User with user_id: %s is not in room_id: %s", user_id, room_id)
        raise UserNotInARoomError()

    logger.info("User with user_id: %s found in room_id: %s", user_id, room_id)
    return room_user


async def must_be_admin(
    room_id: str,
    admin_user_id: str,
    session: AsyncSession = Depends(get_session),
) -> bool:
    """Dependency that checks if a user is admin of a room."""
    logger.info(
        "Checking if user_id: %s is an admin of room_id: %s", admin_user_id, room_id
    )

    user_query = await session.execute(
        select(RoomUser).filter_by(
            room_id=room_id, user_id=admin_user_id, status=ApprovalStatus.APPROVED
        )
    )
    room_user = user_query.scalar_one_or_none()
    if room_user is None or not room_user.is_admin:
        logger.error(
            "User with user_id: %s is not an admin of room_id: %s",
            admin_user_id,
            room_id,
        )
        raise UserNotAdminOfRoomError()

    logger.info(
        "User with user_id: %s is confirmed as admin of room_id: %s",
        admin_user_id,
        room_id,
    )
    return True


async def join_room_dependency(
    room_id: str,
    user_id: str,
    _: Room = Depends(get_room),
    redis: Redis = Depends(get_redis),
    session: AsyncSession = Depends(get_session),
):
    """Dependency to handle joining a room."""
    logger.info(
        "User with user_id: %s is attempting to join room_id: %s", user_id, room_id
    )

    existing_user = await session.execute(
        select(RoomUser).filter_by(room_id=room_id, user_id=user_id)
    )
    if existing_user.scalar() is not None:
        logger.warning(
            "User with user_id: %s is already in room_id: %s", user_id, room_id
        )
        raise UserAlreadyInRoomError()

    room_user = RoomUser(
        room_id=room_id,
        user_id=user_id,
        is_admin=False,
        status=ApprovalStatus.PENDING,
    )

    session.add(room_user)

    await session.commit()

    logger.info(
        "User with user_id: %s joined room_id: %s successfully", user_id, room_id
    )

    await invalidate_cache(
        CacheKeyGenerator.generate_room_user_cache_key(room_id, UserType.ADMIN), redis
    )

    logger.info("Invalidated cache for room_id: %s after user join", room_id)

    return room_user


async def get_room_users(
    room_id: str,
    _: Room = Depends(get_room),
    room_user: RoomUser = Depends(get_user_in_room),
    redis: Redis = Depends(get_redis),
    session: AsyncSession = Depends(get_session),
) -> list[RoomUserResponse]:
    """Dependency for getting users."""
    logger.info("Fetching users for room_id: %s", room_id)

    is_admin = room_user.is_admin

    user_type = UserType.ADMIN if is_admin else UserType.NON_ADMIN

    cached_users = await get_cache(
        CacheKeyGenerator.generate_room_user_cache_key(room_id, UserType.ADMIN), redis
    )
    if cached_users:
        logger.info("Cached users found for room_id: %s", room_id)
        return [
            RoomUserResponse.model_validate(obj) for obj in json.loads(cached_users)
        ]

    logger.info("No cached users found for room_id: %s. Querying database.", room_id)

    query = select(RoomUser).filter_by(room_id=room_id)

    if not is_admin:
        query = query.filter(RoomUser.status == ApprovalStatus.APPROVED)

    users_query = await session.execute(query)
    users = users_query.scalars().all()

    users_response = [
        RoomUserResponse(
            user_id=user.user_id,
            is_admin=user.is_admin,
            status=user.status.name,
            created_at=user.created_at.isoformat(),
        )
        for user in users
    ]

    await set_cache(
        CacheKeyGenerator.generate_room_user_cache_key(room_id, user_type),
        json.dumps([user.model_dump() for user in users_response]),
        redis,
    )
    logger.info(
        "Fetched and cached users for room_id: %s. Total users: %d",
        room_id,
        len(users_response),
    )

    return users_response


async def approve_user(
    room_id: str,
    user_id: str,
    status: AdminApprovalStatus,
    _: bool = Depends(must_be_admin),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    """Dependency for approval/rejection of an user"""
    logger.info(
        "Approving user_id: %s for room_id: %s with status: %s",
        user_id,
        room_id,
        status,
    )

    user_query = await session.execute(
        select(RoomUser).filter_by(room_id=room_id, user_id=user_id)
    )
    user_to_approve = user_query.scalar_one_or_none()

    if user_to_approve is None:
        logger.error("User not found in room: %s", room_id)
        raise UserNotInARoomError()

    if user_to_approve.status in (ApprovalStatus.APPROVED, ApprovalStatus.REJECTED):
        logger.warning(
            "User %s is already in status: %s", user_id, user_to_approve.status
        )
        raise UserNotPending()

    if status == AdminApprovalStatus.APPROVE:
        user_to_approve.status = ApprovalStatus.APPROVED
    elif status == AdminApprovalStatus.REJECTE:
        user_to_approve.status = ApprovalStatus.REJECTED

    await session.commit()

    await invalidate_cache(
        CacheKeyGenerator.generate_room_user_cache_key(room_id, UserType.NON_ADMIN),
        redis,
    )
    await invalidate_cache(
        CacheKeyGenerator.generate_room_user_cache_key(room_id, UserType.ADMIN), redis
    )

    logger.info("User %s approved/rejected successfully and cache invalidated", user_id)

    return user_to_approve


async def log_action_to_redis(
    room_id: str,
    user_id: str,
    action_type: RoomEventTypes,
    message: str,
    addition: Optional[dict] = None,
):
    """Logs action to redis for a specific room."""
    logger.info(
        "Logging action to redis for room_id: %s by user_id: %s", room_id, user_id
    )

    if addition is None:
        addition = {}

    async for redis in get_redis():
        action_log = {
            "user_id": user_id,
            "action": action_type.value,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "message": message,
            **addition,
        }
        await redis.rpush(  # type: ignore
            f"room:{room_id}:actions", json.dumps(action_log)
        )
        logger.info("Action logged successfully for room_id: %s", room_id)


async def fetch_actions_from_redis(room_id: str, fetch_all: Optional[bool] = False):
    """Fetches actions from Redis for a specific room, filtering out 'bet' actions."""
    logger.info("Fetching actions from redis for room_id: %s", room_id)

    async for redis in get_redis():
        actions = await redis.lrange(f"room:{room_id}:actions", 0, -1)  # type: ignore
        actions = [json.loads(action) for action in actions]

        if not fetch_all:
            actions = [action for action in actions if action.get("action") != "bet"]

        logger.info("Actions fetched successfully for room_id: %s", room_id)
        return actions


async def remove_actions_from_redis(room_id: str):
    """Removes actions from redis for a specific room."""
    logger.info("Removing actions from redis for room_id: %s", room_id)

    async for redis in get_redis():
        await redis.delete(f"room:{room_id}:actions")
        logger.info("Actions removed successfully for room_id: %s", room_id)
