import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from dependencies import create_user, log_action_to_redis
from dependencies.enums import RoomMessageTypes

from websocket import socket_manager
from websocket.helpers import RoomMessageGenerator

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
    channel = f"room:{room_id}"
    await socket_manager.create_channel(channel, websocket)

    await create_user(user_id)

    message = RoomMessageGenerator.generate_join_message(user_id)

    await socket_manager.broadcast(
        channel,
        json.dumps(
            {
                "type": RoomMessageTypes.JOIN.value,
                "user_id": user_id,
                "message": message,
            }
        ),
    )

    await log_action_to_redis(
        room_id=room_id,
        user_id=user_id,
        message=message,
        action_type=RoomMessageTypes.JOIN,
    )

    try:
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        await socket_manager.remove_user(channel, websocket)

        message = RoomMessageGenerator.generate_leave_message(user_id)

        await socket_manager.broadcast(
            channel,
            json.dumps(
                {
                    "type": RoomMessageTypes.LEAVE.value,
                    "user_id": user_id,
                    "message": message,
                }
            ),
        )

        await log_action_to_redis(
            room_id=room_id,
            user_id=user_id,
            message=message,
            action_type=RoomMessageTypes.LEAVE,
        )
