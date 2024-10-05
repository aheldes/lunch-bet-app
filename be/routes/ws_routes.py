import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect


from websocket import socket_manager
from dependencies import get_all_rooms

router = APIRouter()


@router.websocket("/ws/rooms")
async def websocket_endpoint(websocket: WebSocket):
    """Websocket that servers list of rooms and all newly created rooms."""
    channel = "rooms"
    await socket_manager.create_channel(channel, websocket)

    rooms = await get_all_rooms()
    await websocket.send_text(f"{[room.model_dump() for room in rooms]}")
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        await socket_manager.remove_user(channel, websocket)
