import json
from fastapi import WebSocket

from dependencies import create_user, log_action_to_redis
from dependencies.enums import Currency, RoomEventTypes
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

    @staticmethod
    def generate_set_price_message(user_id: str, price: str, currency: Currency) -> str:
        """Generates set price message."""
        return f"User {user_id} set price to: {price} {currency.value}."

    @staticmethod
    def generate_set_bet_message(user_id: str) -> str:
        """Generates set bet message."""
        return f"User {user_id} set bet."


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

        addition = {}

        match event_type:
            case RoomEventTypes.GAME_START:
                message = RoomEventMessageGenerator.generate_game_start_message(user_id)
            case RoomEventTypes.GAME_END:
                message = RoomEventMessageGenerator.generate_game_end_message(user_id)
            case RoomEventTypes.SET_PRICE:
                price = input_data["price"]
                currency = Currency.get_currency_type_from_string(
                    input_data["currency"]
                )
                message = RoomEventMessageGenerator.generate_set_price_message(
                    user_id, price, currency
                )
                addition = {"price": price, "currency": currency.value}
            case RoomEventTypes.SET_BET:
                message = RoomEventMessageGenerator.generate_set_bet_message(user_id)

                # Log action again so on frontend the bet is not visible to other users.
                await log_action_to_redis(
                    room_id=self.room_id,
                    user_id=user_id,
                    message=message,
                    action_type=RoomEventTypes.BET,
                    addition={"bet": input_data["bet"]},
                )

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
                    **addition,
                }
            ),
        )

        await log_action_to_redis(
            room_id=self.room_id,
            user_id=user_id,
            message=message,
            action_type=event_type,
            addition=addition,
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
