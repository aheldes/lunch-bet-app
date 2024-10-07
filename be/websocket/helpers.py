import asyncio
import json
import random
from typing import Optional
from fastapi import WebSocket
from pydantic import BaseModel

from dependencies import create_user, fetch_actions_from_redis, log_action_to_redis
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
            print("here?")
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
            case RoomEventTypes.EVALUATE:
                evaluator = GameEvaluator(self.room_id)
                await evaluator.evaluate()
                return
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


class Bet(BaseModel):
    """Data class for bets from redis."""

    bet: int
    user_id: str


class Price(BaseModel):
    """Data class for prices from redis."""

    price: float
    currency: str
    user_id: str


class ConvertedPrice(BaseModel):
    """Data class for converted prices."""

    user_id: str
    original_price: float
    original_currency: str
    conversion_rate: Optional[float] = None
    price_in_czk: float


class CurrencyConverter:
    """Class for converting for calculating total value in czk."""

    def __init__(self) -> None:
        self.rates = self.fetch_current_exchange_rates()

    def fetch_current_exchange_rates(self) -> dict:
        """Fetches the current exchange rates for USD and EUR to CZK."""
        return {Currency.EUR.value: 23.10, Currency.USD.value: 25.35}

    def convert_to_czk(self, price: Price) -> ConvertedPrice:
        """Converts the given price into CZK."""
        if price.currency == Currency.CZK.value:
            price_in_czk = price.price
            conversion_rate = None
        else:
            conversion_rate = self.rates[price.currency]
            price_in_czk = price.price * conversion_rate
        return ConvertedPrice(
            user_id=price.user_id,
            original_price=price.price,
            original_currency=price.currency,
            price_in_czk=price_in_czk,
            conversion_rate=conversion_rate,
        )

    def calculate_total_in_czk(
        self, prices: list[Price]
    ) -> tuple[float, list[ConvertedPrice]]:
        """Calculates the total value in CZK and returns a list of converted prices."""
        total_value_in_czk: float = 0.0
        converted_prices: list[ConvertedPrice] = []

        for price in prices:
            converted_price = self.convert_to_czk(price)
            total_value_in_czk += converted_price.price_in_czk
            converted_prices.append(converted_price)

        return total_value_in_czk, converted_prices


class GameEvaluator:
    """Class for game evaluation."""

    def __init__(self, room_id: str) -> None:
        self.room_id = room_id
        self.converter = CurrencyConverter()

    async def evaluate(self):
        """Evaluates the game state by fetching actions and
        generating a random number."""
        redis_actions, random_number = await asyncio.gather(
            self.fetch_bets_and_prices(), self.generate_random_number()
        )

        bets, prices = redis_actions
        print(f"Random number generated: {random_number}")
        print(f"Bets: {bets}")
        print(f"Prices: {prices}")

        looser = self.calculate_furthest_from_number(bets, random_number)
        print(f"Looser: {looser}")

        total_value_czk, converted_prices = self.converter.calculate_total_in_czk(
            prices
        )
        print(f"Total Value in CZK: {total_value_czk}")
        print(f"Converted Prices: {converted_prices}")

    async def fetch_bets_and_prices(self) -> tuple[list[Bet], list[Price]]:
        """Fetches bets and prices from redis actions."""
        redis_actions = await fetch_actions_from_redis(self.room_id, True)

        bets: list[Bet] = []
        prices: list[Price] = []

        for action in redis_actions:
            if action["action"] == "set_price":
                prices.append(
                    Price(
                        price=action["price"],
                        currency=action["currency"],
                        user_id=action["user_id"],
                    )
                )
            elif action["action"] == "bet":
                bets.append(Bet(bet=action["bet"], user_id=action["user_id"]))

        return bets, prices

    @staticmethod
    async def generate_random_number() -> int:
        """Generates a random number between 1 and 10,000."""
        return random.randint(1, 10000)

    @staticmethod
    def calculate_furthest_from_number(
        bets: list[Bet], random_number: int
    ) -> Optional[Bet]:
        """Calculates the user whose bet is furthest from the generated number.
        If there is a tie, picks one randomly."""
        if not bets:
            return None

        furthest_bets = sorted(
            bets, key=lambda bet: abs(bet.bet - random_number), reverse=True
        )

        max_distance = abs(furthest_bets[0].bet - random_number)

        furthest_candidates = [
            bet for bet in furthest_bets if abs(bet.bet - random_number) == max_distance
        ]

        looser = (
            random.choice(furthest_candidates)
            if len(furthest_candidates) > 1
            else furthest_candidates[0]
        )
        return looser
