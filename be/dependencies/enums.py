from enum import Enum


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

    @classmethod
    def get_event_type_from_string(cls, event_type_str: str) -> "RoomEventTypes":
        """Helper method to return RoomEventTypes from string."""
        try:
            return cls[event_type_str.upper()]
        except KeyError as exc:
            raise ValueError(f"Invalid event type: {event_type_str}") from exc
