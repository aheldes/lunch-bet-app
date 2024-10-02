from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_session
from models.models import ApprovalStatus, Room, RoomUser
from exceptions.custom_exceptions import (
    RoomNameNotUniqueError,
    RoomNotFoundError,
    UserAlreadyInRoomError,
)
from schemas import RoomCreate, RoomJoinRequest


async def create_room_dependency(
    room_data: RoomCreate,
    session: AsyncSession = Depends(get_session),
):
    """Dependency to handle creation of a room."""
    new_room = Room(name=room_data.name, created_by=room_data.user_id)
    try:
        session.add(new_room)
        await session.commit()
        await session.refresh(new_room)
        return new_room
    except IntegrityError as exc:
        await session.rollback()
        raise RoomNameNotUniqueError("Room name must be unique.") from exc


async def join_room_dependency(
    room_id: str,
    join_request: RoomJoinRequest,
    session: AsyncSession = Depends(get_session),
):
    """Dependency to handle joining a room."""
    room = await session.get(Room, room_id)
    if room is None:
        raise RoomNotFoundError("Room not found.")

    existing_user = await session.execute(
        select(RoomUser).filter_by(room_id=room_id, user_id=join_request.user_id)
    )
    if existing_user.scalar() is not None:
        raise UserAlreadyInRoomError("User is already in the room.")

    room_user = RoomUser(
        room_id=room_id,
        user_id=join_request.user_id,
        is_admin=False,
        status=ApprovalStatus.PENDING,
    )

    session.add(room_user)

    await session.commit()
    return room_user
