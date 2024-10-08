from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from models import Room, RoomUser
from schemas import GameResponse, RoomResponse, RoomUserResponse
from dependencies.dependencies import (
    approve_user,
    create_room_dependency,
    get_game_history,
    fetch_actions_from_redis,
    get_all_rooms,
    get_room_users,
    join_room_dependency,
)


router = APIRouter()


@router.get("/rooms/{room_id}/actions")
async def get_actions(room_id: str):
    """Gets list of all actions for a room."""
    actions = await fetch_actions_from_redis(room_id)
    return actions


@router.get("/rooms/{room_id}/history")
async def get_history(game_history: list[GameResponse] = Depends(get_game_history)):
    """Gets list of all games played for a room."""
    return game_history


@router.get("/rooms")
async def get_rooms(rooms: list[RoomResponse] = Depends(get_all_rooms)):
    """Gets the list of all rooms"""
    return rooms


@router.post("/rooms")
async def create_room(
    _: Room = Depends(create_room_dependency),
):
    """Create a new room with the provided name and user ID."""
    return JSONResponse(content=None, status_code=status.HTTP_201_CREATED)


@router.post("/rooms/{room_id}/join")
async def join_room(
    _: RoomUser = Depends(join_room_dependency),
):
    """Request to join a room."""
    return JSONResponse(content=None, status_code=status.HTTP_201_CREATED)


@router.get("/rooms/{room_id}/users", response_model=list[RoomUserResponse])
async def get_users(users: list[RoomUserResponse] = Depends(get_room_users)):
    """Gets the list of all users for a room"""
    return users


@router.post("/rooms/{room_id}/users/moderate")
async def approve_users(_: RoomUser = Depends(approve_user)):
    """Approve/Reject user from joining a room"""
    return JSONResponse(content=None, status_code=status.HTTP_201_CREATED)
