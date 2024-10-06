import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from dependencies import create_user

from websocket import socket_manager

router = APIRouter()


@router.websocket("/ws/rooms/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """Websocket that servers list of rooms and all newly created rooms."""
    channel = "rooms"
    await socket_manager.create_channel(channel, websocket)

    await create_user(user_id)

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        await socket_manager.remove_user(channel, websocket)
