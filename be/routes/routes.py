from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import Room, RoomUser
from schemas import RoomCreate, RoomResponse, RoomJoinRequest
from dependencies import join_room_dependency


router = APIRouter()


@router.post("/rooms/", response_model=RoomResponse)
async def create_room(
    room_data: RoomCreate, session: AsyncSession = Depends(get_session)
):
    """Create a new room with the provided name and user ID."""
    new_room = Room(name=room_data.name, created_by=room_data.user_id)
    try:
        session.add(new_room)
        await session.commit()
        await session.refresh(new_room)
        return new_room
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=400, detail="Room name must be unique."
        ) from exc


@router.post("/rooms/{room_id}/join")
async def join_room(
    room_id: str,  # pylint: disable=unused-argument
    join_request: RoomJoinRequest,  # pylint: disable=unused-argument
    _: RoomUser = Depends(join_room_dependency),
):
    """Request to join a room."""
    return JSONResponse(content=None, status_code=status.HTTP_201_CREATED)
