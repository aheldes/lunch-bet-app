from enum import Enum


class ApprovalStatus(Enum):
    """User approval status."""

    APPROVED = "approved"
    PENDING = "pending"
    REJECTED = "rejected"


class UserType(Enum):
    """Enum for user types of a room."""

    ADMIN = "admin"
    NON_ADMIN = "non_admin"


class AdminApprovalStatus(Enum):
    """Enum for user approval status."""

    APPROVE = "approve"
    REJECTE = "reject"


class RoomEventTypes(Enum):
    """Enum for room event types."""

    JOIN = "join"
    LEAVE = "leave"
    GAME_START = "game_start"
    GAME_END = "game_end"
    SET_PRICE = "set_price"
    SET_BET = "set_bet"
    BET = "bet"  # this is internal
    EVALUATE = "evaluate"
    RESULT = "result"

    @classmethod
    def get_event_type_from_string(cls, event_type_str: str) -> "RoomEventTypes":
        """Helper method to return RoomEventTypes from string."""
        try:
            return cls[event_type_str.upper()]
        except KeyError as exc:
            raise ValueError(f"Invalid event type: {event_type_str}") from exc


class Currency(Enum):
    """Enum for currencies."""

    CZK = "czk"
    EUR = "eur"
    USD = "usd"

    @classmethod
    def get_currency_type_from_string(cls, currency_str: str) -> "Currency":
        """Helper method to return Currency from string."""
        try:
            return cls[currency_str.upper()]
        except KeyError as exc:
            raise ValueError(f"Invalid event type: {currency_str}") from exc
