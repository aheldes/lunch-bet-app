class RoomError(Exception):
    """Base class for room-related errors."""

    def __init__(self, detail: str):
        self.detail = detail


class RoomNotFoundError(RoomError):
    """Raised when a room is not found."""


class UserAlreadyInRoomError(RoomError):
    """Raised when a user tries to join a room they are already in."""
