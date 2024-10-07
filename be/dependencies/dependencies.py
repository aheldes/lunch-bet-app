from datetime import datetime, timezone
import json
import logging

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_session, get_redis
from models.models import ApprovalStatus, Room, RoomUser, User
from exceptions.custom_exceptions import (
    RoomNameNotUniqueError,
    RoomNotFoundError,
    UserAlreadyInRoomError,
    UserNotAdminOfRoomError,
    UserNotFound,
    UserNotInARoomError,
    UserNotPending,
)
from schemas import RoomCreate, RoomResponse, RoomUserResponse

from .cache import CacheKeyGenerator, get_cache, invalidate_cache, set_cache
from .enums import AdminApprovalStatus, RoomEventTypes, UserType

logger = logging.getLogger("uvicorn.error")


async def create_user(user_id: str):
    """Creates a new user."""
    user = User(id=user_id)
    logger.info("Creating user.")
    async for session in get_session():
        try:
            session.add(user)
            await session.commit()
            logger.info("User created.")
        except IntegrityError:
            await session.rollback()
            logger.info("User not created as already existing.")


async def get_user(user_id: str, session: AsyncSession) -> User:
    """Fetches a user from db and raises an error if non-existing."""
    result = await session.execute(select(User).filter_by(id=user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise UserNotFound()
    return user


async def create_room_dependency(
    room_data: RoomCreate,
    redis: Redis = Depends(get_redis),
    session: AsyncSession = Depends(get_session),
):
    """Dependency to handle the creation of a room."""
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
        await redis.publish("rooms", json.dumps(room_response.model_dump()))
        await invalidate_cache(CacheKeyGenerator.generate_rooms_cache_key(), redis)
        return new_room
    except IntegrityError as exc:
        await session.rollback()
        raise RoomNameNotUniqueError() from exc


async def get_room(
    room_id: str,
    session: AsyncSession = Depends(get_session),
) -> Room:
    """Dependency that fetches a room from db."""
    room = await session.get(Room, room_id)
    if room is None:
        raise RoomNotFoundError()
    return room


async def get_all_rooms(
    redis: Redis = Depends(get_redis), session: AsyncSession = Depends(get_session)
) -> list[RoomResponse]:
    """Fetch all rooms from the database."""
    cached_rooms = await get_cache(CacheKeyGenerator.generate_rooms_cache_key(), redis)
    if cached_rooms:
        logger.info("Cached rooms found")
        return [RoomResponse.model_validate(obj) for obj in json.loads(cached_rooms)]
    logger.info("No cached rooms found")
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
    return rooms_response


async def get_user_in_room(
    room_id: str,
    user_id: str,
    session: AsyncSession = Depends(get_session),
) -> RoomUser:
    """Dependency that checks if user is in a room"""
    user_query = await session.execute(
        select(RoomUser).filter_by(
            room_id=room_id, user_id=user_id, status=ApprovalStatus.APPROVED
        )
    )
    room_user = user_query.scalar_one_or_none()

    if room_user is None:
        raise UserNotInARoomError()

    return room_user


async def must_be_admin(
    room_id: str,
    admin_user_id: str,
    session: AsyncSession = Depends(get_session),
) -> bool:
    """Dependency that checks if a user is admin of a room."""
    user_query = await session.execute(
        select(RoomUser).filter_by(
            room_id=room_id, user_id=admin_user_id, status=ApprovalStatus.APPROVED
        )
    )
    room_user = user_query.scalar_one_or_none()
    if room_user is None or not room_user.is_admin:
        raise UserNotAdminOfRoomError()
    return True


async def join_room_dependency(
    room_id: str,
    user_id: str,
    _: Room = Depends(get_room),
    redis: Redis = Depends(get_redis),
    session: AsyncSession = Depends(get_session),
):
    """Dependency to handle joining a room."""
    existing_user = await session.execute(
        select(RoomUser).filter_by(room_id=room_id, user_id=user_id)
    )
    if existing_user.scalar() is not None:
        raise UserAlreadyInRoomError()

    room_user = RoomUser(
        room_id=room_id,
        user_id=user_id,
        is_admin=False,
        status=ApprovalStatus.PENDING,
    )

    session.add(room_user)

    await session.commit()

    await invalidate_cache(
        CacheKeyGenerator.generate_room_user_cache_key(room_id, UserType.ADMIN), redis
    )

    return room_user


async def get_room_users(
    room_id: str,
    _: Room = Depends(get_room),
    room_user: RoomUser = Depends(get_user_in_room),
    redis: Redis = Depends(get_redis),
    session: AsyncSession = Depends(get_session),
) -> list[RoomUserResponse]:
    """Dependency for getting users."""
    is_admin = room_user.is_admin

    user_type = UserType.ADMIN if is_admin else UserType.NON_ADMIN

    cached_users = await get_cache(
        CacheKeyGenerator.generate_room_user_cache_key(room_id, UserType.ADMIN), redis
    )
    if cached_users:
        logger.info("Cached users found")
        return [
            RoomUserResponse.model_validate(obj) for obj in json.loads(cached_users)
        ]

    logger.info("No cached users found")
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
    user_query = await session.execute(
        select(RoomUser).filter_by(room_id=room_id, user_id=user_id)
    )
    user_to_approve = user_query.scalar_one_or_none()

    if user_to_approve is None:
        raise UserNotInARoomError()

    if user_to_approve.status in (ApprovalStatus.APPROVED, ApprovalStatus.REJECTED):
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

    return user_to_approve


async def log_action_to_redis(
    room_id: str, user_id: str, action_type: RoomEventTypes, message: str
):
    """Logs action to redis for a specific room."""
    async for redis in get_redis():
        action_log = {
            "user_id": user_id,
            "action": action_type.value,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "message": message,
        }
        await redis.rpush(  # type: ignore
            f"room:{room_id}:actions", json.dumps(action_log)
        )


async def fetch_actions_from_redis(room_id: str):
    """Fetches actions from redis for a specific room."""
    async for redis in get_redis():
        actions = await redis.lrange(f"room:{room_id}:actions", 0, -1)  # type: ignore
        return [json.loads(action) for action in actions]


async def remove_actions_from_redis(room_id: str):
    """Removes actions from redis for a specific room."""
    async for redis in get_redis():
        await redis.delete(f"room:{room_id}:actions")
