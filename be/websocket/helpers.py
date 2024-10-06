class RoomMessageGenerator:
    """Helper class for generation of event messages."""

    @staticmethod
    def generate_join_message(user_id: str) -> str:
        """Generates user join message."""
        return f"User {user_id} joined the room."

    @staticmethod
    def generate_leave_message(user_id: str) -> str:
        """Generates user leave message."""
        return f"User {user_id} left the room."
