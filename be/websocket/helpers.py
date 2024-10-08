import asyncio
import json
import logging
import random
from fastapi import WebSocket


from dependencies.dependencies import (
    create_user,
    fetch_actions_from_redis,
    log_action_to_redis,
    remove_actions_from_redis,
)
from dependencies.enums import Currency, RoomEventTypes
from database.models import Game
from websocket import socket_manager
from websocket.models import Bet, ConvertedPrice, Price

logger = logging.getLogger("uvicorn.error")


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

    @staticmethod
    def generate_result_message(user_id: str, amount: float) -> str:
        """Generates result message."""
        return f"User {user_id} lost and has to pay {amount} CZK."


class RoomEventHandler:
    """Handler class for handling ws events."""

    def __init__(self, websocket: WebSocket, room_id: str, user_id: str) -> None:
        self.channel = f"room:{room_id}"
        self.websocket = websocket
        self.room_id = room_id
        self.user_id = user_id

    async def handle_event(self, data: str) -> None:
        """Handle incoming event."""
        input_data = await self._parse_input_data(data)
        event_type = RoomEventTypes.get_event_type_from_string(input_data["type"])
        user_id = input_data["user_id"]
        logger.info("Handling event: %s for user: %s", event_type, user_id)

        addition: dict = {}
        message = await self._process_event(event_type, input_data, user_id, addition)

        if event_type == RoomEventTypes.EVALUATE:
            event_type = RoomEventTypes.RESULT

        await self._broadcast_message(event_type, user_id, message, addition)

    async def handle_user_join_room(self) -> None:
        """Handle user join event."""
        logger.info("User %s joining room %s", self.user_id, self.room_id)
        await socket_manager.create_channel(self.channel, self.websocket)

        await create_user(self.user_id)

        message = RoomEventMessageGenerator.generate_join_message(self.user_id)

        await self._broadcast_message(RoomEventTypes.JOIN, self.user_id, message, {})

    async def handle_user_leave_room(self) -> None:
        """Handle user leave room event."""
        logger.info("User %s leaving room %s", self.user_id, self.room_id)
        await socket_manager.remove_user(self.channel, self.websocket)

        message = RoomEventMessageGenerator.generate_leave_message(self.user_id)

        await self._broadcast_message(RoomEventTypes.LEAVE, self.user_id, message, {})

    async def _parse_input_data(self, data: str) -> dict:
        """Parse incoming event data from JSON."""
        try:
            input_data = json.loads(data)
            logger.debug("Parsed input data: %s", input_data)
            return input_data
        except json.JSONDecodeError as e:
            logger.error("Invalid input format: %s", e)
            raise ValueError(f"Invalid input format: {e}") from e

    async def _process_event(
        self, event_type, input_data: dict, user_id: str, addition: dict
    ) -> str:
        """Process the specific event based on its type."""
        match event_type:
            case RoomEventTypes.GAME_START:
                return await self._handle_game_start(user_id)
            case RoomEventTypes.GAME_END:
                return await self._handle_game_end(user_id)
            case RoomEventTypes.SET_PRICE:
                return await self._handle_set_price(input_data, user_id, addition)
            case RoomEventTypes.SET_BET:
                return await self._handle_set_bet(input_data, user_id)
            case RoomEventTypes.EVALUATE:
                return await self._handle_evaluate()
            case _:
                logger.error("Event type %s is not implemented.", event_type)
                raise NotImplementedError(
                    f"Event type {event_type} is not implemented."
                )

    async def _handle_game_start(self, user_id: str) -> str:
        """Handle game start event."""
        message = RoomEventMessageGenerator.generate_game_start_message(user_id)
        logger.info("Game started by user: %s", user_id)
        return message

    async def _handle_game_end(self, user_id: str) -> str:
        """Handle game end event."""
        message = RoomEventMessageGenerator.generate_game_end_message(user_id)
        logger.info("Game ended by user: %s", user_id)
        return message

    async def _handle_set_price(
        self, input_data: dict, user_id: str, addition: dict
    ) -> str:
        """Handle setting the price event."""
        price = input_data["price"]
        currency = Currency.get_currency_type_from_string(input_data["currency"])
        message = RoomEventMessageGenerator.generate_set_price_message(
            user_id, price, currency
        )
        addition.update({"price": price, "currency": currency.value})
        logger.info("Price set by user %s: %s %s", user_id, price, currency)
        return message

    async def _handle_set_bet(self, input_data: dict, user_id: str) -> str:
        """Handle setting the bet event."""
        message = RoomEventMessageGenerator.generate_set_bet_message(user_id)
        logger.info("Bet set by user: %s", user_id)

        # Log action again so the bet is not visible to other users.
        await log_action_to_redis(
            room_id=self.room_id,
            user_id=user_id,
            message=message,
            action_type=RoomEventTypes.BET,
            addition={"bet": input_data["bet"]},
        )
        return message

    async def _handle_evaluate(self) -> str:
        """Handle game evaluation."""
        evaluator = GameEvaluator(self.room_id)
        looser, converted_prices = await evaluator.evaluate()
        total_in_czk = await ConvertedPrice.calculate_totals(converted_prices)
        message = RoomEventMessageGenerator.generate_result_message(
            looser.user_id, total_in_czk
        )

        await Game.create_game_with_prices(
            room_id=self.room_id,
            loser_id=looser.user_id,
            converted_prices=converted_prices,
            total_in_czk=total_in_czk,
        )

        await remove_actions_from_redis(self.room_id)
        logger.info(
            "Game evaluated. Looser: %s, Total in CZK: %s", looser.user_id, total_in_czk
        )

        return message

    async def _broadcast_message(
        self, event_type, user_id: str, message: str, addition: dict
    ) -> None:
        """Broadcast message to the channel."""
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


class DataFetcher:  # pylint: disable=R0903
    """Class responsible for fetching data from Redis."""

    def __init__(self, room_id: str):
        self.room_id = room_id

    async def fetch_bets_and_prices(self) -> tuple[list[Bet], list[Price]]:
        """Fetches bets and prices from Redis actions."""
        logger.info("Fetching bets and prices from Redis for room: %s", self.room_id)
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
                logger.debug("Added price action: %s", action)
            elif action["action"] == "bet":
                bets.append(Bet(bet=action["bet"], user_id=action["user_id"]))
                logger.debug("Added bet action: %s", action)

        logger.info("Fetched bets: %s, prices: %s", bets, prices)
        return bets, prices


class CurrencyConverter:
    """Class for converting and calculating total value in CZK."""

    def __init__(self) -> None:
        self.rates = self.fetch_current_exchange_rates()
        logger.info("Initialized CurrencyConverter with exchange rates: %s", self.rates)

    def fetch_current_exchange_rates(self) -> dict:
        """Fetches the current exchange rates for USD and EUR to CZK."""
        rates = {Currency.EUR.value: 23.10, Currency.USD.value: 25.35}
        logger.info("Fetched current exchange rates: %s", rates)
        return rates

    def convert_to_czk(self, price: Price) -> ConvertedPrice:
        """Converts the given price into CZK."""
        logger.debug("Converting price: %s %s", price.price, price.currency)

        if price.currency == Currency.CZK.value:
            price_in_czk = price.price
            conversion_rate = None
            logger.debug("Price is already in CZK: %s", price_in_czk)
        else:
            conversion_rate = self.rates[price.currency]
            price_in_czk = price.price * conversion_rate
            logger.debug(
                "Converted price from %s to CZK using rate %s: %s",
                price.price,
                conversion_rate,
                price_in_czk,
            )

        converted_price = ConvertedPrice(
            user_id=price.user_id,
            original_price=price.price,
            original_currency=Currency.get_currency_type_from_string(price.currency),
            price_in_czk=price_in_czk,
            conversion_rate=conversion_rate,
        )
        logger.info("Converted price object created: %s", converted_price)
        return converted_price


class GameEvaluator:
    """Class for game evaluation."""

    def __init__(self, room_id: str) -> None:
        self.room_id = room_id
        self.converter = CurrencyConverter()
        self.data_fetcher = DataFetcher(room_id)
        logger.info("Initialized GameEvaluator for room: %s", room_id)

    async def evaluate(self):
        """Evaluates the game state by fetching actions and
        generating a random number."""
        logger.info("Starting game evaluation for room: %s", self.room_id)

        redis_actions, random_number = await asyncio.gather(
            self.data_fetcher.fetch_bets_and_prices(), self.generate_random_number()
        )

        bets, prices = redis_actions
        logger.info("Random number generated: %d", random_number)
        logger.info("Fetched bets: %s", bets)
        logger.info("Fetched prices: %s", prices)

        looser = self.calculate_furthest_from_number(bets, random_number)
        logger.info("Looser determined: %s", looser)

        converted_prices = [self.converter.convert_to_czk(price) for price in prices]
        logger.info("Converted Prices: %s", converted_prices)

        return looser, converted_prices

    @staticmethod
    async def generate_random_number() -> int:
        """Generates a random number between 1 and 10,000."""
        random_number = random.randint(1, 10000)
        logger.debug("Generated random number: %d", random_number)
        return random_number

    @staticmethod
    def calculate_furthest_from_number(bets: list[Bet], random_number: int) -> Bet:
        """Calculates the user whose bet is furthest from the generated number.
        If there is a tie, picks one randomly."""
        logger.info("Calculating furthest bet from random number: %d", random_number)
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
        logger.info("Looser calculated: %s", looser)
        return looser
