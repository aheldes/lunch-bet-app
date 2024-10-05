from enum import Enum


class UserType(Enum):
    """Enum for user types of a room."""

    ADMIN = "admin"
    NON_ADMIN = "non_admin"


class AdminApprovalStatus(Enum):
    """Enum for user approval status."""

    APPROVE = "approve"
    REJECTE = "reject"
