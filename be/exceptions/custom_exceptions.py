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


class UserNotAdminOfRoomError(Error):
    """
    Raised when a user tries to do admin actions for a room which they are
    not an admin of.
    """


class UserNotInARoomError(Error):
    """Raised when user tries to access a room where they are not approved."""


class UserNotPending(Error):
    """
    Raised when admin tries to approve/reject an user that was already
    approved/rejected.
    """
