class Error(Exception):
    """Base class for errors."""

    def __init__(self, detail: str):
        self.detail = detail


class RoomNameNotUniqueError(Error):
    """Raised when room name is not unique."""


class RoomNotFoundError(Error):
    """Raised when a room is not found."""


class UserAlreadyInRoomError(Error):
    """Raised when a user tries to join a room they are already in."""
