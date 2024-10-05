from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from models import Room, RoomUser
from schemas import RoomResponse, RoomUserResponse
from dependencies import create_room_dependency, join_room_dependency, get_room_users


router = APIRouter()


@router.post("/rooms/", response_model=RoomResponse)
async def create_room(
    room: Room = Depends(create_room_dependency),
):
    """Create a new room with the provided name and user ID."""
    return room


@router.post("/rooms/{room_id}/join")
async def join_room(
    _: RoomUser = Depends(join_room_dependency),
):
    """Request to join a room."""
    return JSONResponse(content=None, status_code=status.HTTP_201_CREATED)


@router.get("/rooms/{room_id}/users", response_model=list[RoomUserResponse])
async def get_users(users: list[RoomUserResponse] = Depends(get_room_users)):
    """Requests to join room"""
    return users
