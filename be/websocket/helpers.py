import json
from fastapi import WebSocket

from dependencies import create_user, log_action_to_redis
from dependencies.enums import RoomEventTypes
from websocket import socket_manager


class RoomEventMessageGenerator:
    """Helper class for generation of event messages."""

    @staticmethod
    def generate_join_message(user_id: str) -> str:
        """Generates user join message."""
        return f"User {user_id} joined the room."

    @staticmethod
    def generate_leave_message(user_id: str) -> str:
        """Generates user leave message."""
        return f"User {user_id} left the room."

    @staticmethod
    def generate_game_start_message(user_id: str) -> str:
        """Generates game start message."""
        return f"User {user_id} started the game."

    @staticmethod
    def generate_game_end_message(user_id: str) -> str:
        """Generates game end message."""
        return f"User {user_id} ended the game."


class RoomEventHandler:
    """Handler class for handling ws events."""

    def __init__(self, websocket: WebSocket, room_id: str, user_id: str) -> None:
        self.channel = f"room:{room_id}"
        self.websocket = websocket
        self.room_id = room_id
        self.user_id = user_id

    async def handle_event(self, data: str) -> None:
        """Handle incoming event."""
        try:
            input_data = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid input format: {e}") from e

        event_type = RoomEventTypes.get_event_type_from_string(input_data["type"])
        user_id = input_data["user_id"]

        match event_type:
            case RoomEventTypes.GAME_START:
                message = RoomEventMessageGenerator.generate_game_start_message(user_id)
            case RoomEventTypes.GAME_END:
                message = RoomEventMessageGenerator.generate_game_end_message(user_id)
            case _:
                raise NotImplementedError(
                    f"Event type {event_type} is not implemented."
                )

        await socket_manager.broadcast(
            self.channel,
            json.dumps(
                {
                    "type": event_type.value,
                    "user_id": user_id,
                    "message": message,
                }
            ),
        )

        await log_action_to_redis(
            room_id=self.room_id,
            user_id=user_id,
            message=message,
            action_type=event_type,
        )

    async def handle_user_join_room(self) -> None:
        """Handle user join event."""
        await socket_manager.create_channel(self.channel, self.websocket)

        await create_user(self.user_id)

        message = RoomEventMessageGenerator.generate_join_message(self.user_id)

        await socket_manager.broadcast(
            self.channel,
            json.dumps(
                {
                    "type": RoomEventTypes.JOIN.value,
                    "user_id": self.user_id,
                    "message": message,
                }
            ),
        )

        await log_action_to_redis(
            room_id=self.room_id,
            user_id=self.user_id,
            message=message,
            action_type=RoomEventTypes.JOIN,
        )

    async def handle_user_leave_room(self) -> None:
        """Handle user leave room event."""
        await socket_manager.remove_user(self.channel, self.websocket)

        message = RoomEventMessageGenerator.generate_leave_message(self.user_id)

        await socket_manager.broadcast(
            self.channel,
            json.dumps(
                {
                    "type": RoomEventTypes.LEAVE.value,
                    "user_id": self.user_id,
                    "message": message,
                }
            ),
        )

        await log_action_to_redis(
            room_id=self.room_id,
            user_id=self.user_id,
            message=message,
            action_type=RoomEventTypes.LEAVE,
        )
