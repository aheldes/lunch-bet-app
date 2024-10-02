import enum
import uuid
from datetime import datetime, timezone

from database.base_model import Base
from sqlalchemy import ForeignKey, TIMESTAMP, String
from sqlalchemy.engine import Connection
from sqlalchemy.event import listen
from sqlalchemy.orm import mapped_column, Mapped, Mapper, Session, relationship

# pylint: disable=missing-class-docstring, too-few-public-methods


class ApprovalStatus(enum.Enum):
    APPROVED = "approved"
    PENDING = "pending"
    REJECTED = "rejected"


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(
        String(15), index=True, nullable=False, unique=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(tz=timezone.utc)
    )
    created_by: Mapped[str] = mapped_column(nullable=False)

    users: Mapped[list["RoomUser"]] = relationship("RoomUser", back_populates="room")


def create_room_user(_: Mapper, __: Connection, target: Room) -> None:
    """Helper function for automatic creation of admin user in RoomUser table."""
    session = Session.object_session(target)
    if session is not None:
        room_user = RoomUser(
            room_id=target.id,
            user_id=target.created_by,
            is_admin=True,
            status=ApprovalStatus.APPROVED,
        )
        session.add(room_user)


listen(Room, "after_insert", create_room_user)


class RoomUser(Base):
    __tablename__ = "room_users"

    room_id: Mapped[str] = mapped_column(ForeignKey("rooms.id"), primary_key=True)
    user_id: Mapped[str] = mapped_column(primary_key=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    status: Mapped[ApprovalStatus] = mapped_column(
        nullable=False, default=ApprovalStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(tz=timezone.utc)
    )

    room: Mapped[Room] = relationship("Room", back_populates="users")
