import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from dependencies.dependencies import create_user

from websocket import socket_manager
from websocket.helpers import RoomEventHandler

router = APIRouter()


@router.websocket("/ws/rooms/{user_id}")
async def websocket_rooms(websocket: WebSocket, user_id: str):
    """Websocket that servers all newly created rooms."""
    channel = "rooms"
    await socket_manager.create_channel(channel, websocket)

    await create_user(user_id)

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        await socket_manager.remove_user(channel, websocket)


@router.websocket("/ws/room/{room_id}/{user_id}")
async def websocket_room(websocket: WebSocket, room_id: str, user_id: str):
    """Websocket that servers actions in a room."""
    handler = RoomEventHandler(websocket, room_id, user_id)
    await handler.handle_user_join_room()

    try:
        while True:
            data = await websocket.receive_text()
            await handler.handle_event(data)
    except WebSocketDisconnect:
        await handler.handle_user_leave_room()
