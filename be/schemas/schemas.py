from typing import Optional
from pydantic import BaseModel, Field

from models.models import Game, GamePrice
from dependencies.enums import Currency

# pylint: disable=missing-class-docstring, too-few-public-methods


class GamePriceResponse(BaseModel):
    user_id: str
    price: float
    currency: Currency
    conversion_rate: Optional[float]
    price_in_czk: float
    created_at: str

    @classmethod
    def from_game_price_obj(cls, price: GamePrice) -> "GamePriceResponse":
        """Create an instance from a GamePrice SQLAlchemy model instance."""
        return cls(
            user_id=price.user_id,
            price=price.price,
            currency=price.currency,
            conversion_rate=price.conversion_rate,
            price_in_czk=price.price_in_czk,
            created_at=price.created_at.isoformat(),
        )


class GameResponse(BaseModel):
    id: str
    room_id: str
    loser: str
    price: float
    created_at: str
    prices: list[GamePriceResponse]

    @classmethod
    def from_game_obj(cls, game: Game) -> "GameResponse":
        """Create an instance from a Game SQLAlchemy model instance."""
        return cls(
            id=game.id,
            room_id=game.room_id,
            loser=game.loser,
            price=game.price,
            created_at=game.created_at.isoformat(),
            prices=[
                GamePriceResponse.from_game_price_obj(price) for price in game.prices
            ],
        )


class RoomBase(BaseModel):
    name: str = Field(max_length=15)


class RoomCreate(RoomBase):
    user_id: str


class RoomResponse(RoomBase):
    id: str
    created_at: str
    created_by: str


class RoomUserResponse(BaseModel):
    user_id: str
    is_admin: bool
    status: str
    created_at: str
