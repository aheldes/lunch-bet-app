from typing import Optional
from pydantic import BaseModel

from dependencies.enums import Currency


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
    original_currency: Currency
    conversion_rate: Optional[float] = None
    price_in_czk: float

    @staticmethod
    async def calculate_totals(converted_prices: list["ConvertedPrice"]) -> float:
        """Calculates the total sum of all prices in CZK."""
        return sum(price.price_in_czk for price in converted_prices)
