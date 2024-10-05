class RoomNameNotUniqueError(Exception):
    """Raised when room name is not unique."""

    def __init__(self):
        self.detail = "Room name must be unique."


class RoomNotFoundError(Exception):
    """Raised when a room is not found."""

    def __init__(self):
        self.detail = "Room not found."


class UserAlreadyInRoomError(Exception):
    """Raised when a user tries to join a room they are already in."""

    def __init__(self):
        self.detail = "User is already in the room."


class UserNotAdminOfRoomError(Exception):
    """
    Raised when a user tries to do admin actions for a room which they are
    not an admin of.
    """

    def __init__(self):
        self.detail = "Only admins can do this acction for this room."


class UserNotInARoomError(Exception):
    """Raised when user tries to access a room where they are not approved."""

    def __init__(self):
        self.detail = "User not in a room."


class UserNotPending(Exception):
    """
    Raised when admin tries to approve/reject an user that was already
    approved/rejected.
    """

    def __init__(self):
        self.detail = "User was already approved/rejected."
