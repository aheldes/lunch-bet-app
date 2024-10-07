import uuid
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, TIMESTAMP, String
from sqlalchemy.engine import Connection
from sqlalchemy.event import listen
from sqlalchemy.orm import mapped_column, Mapped, Mapper, Session, relationship


from database.base_model import Base
from database.engine import get_session
from dependencies.enums import ApprovalStatus, Currency
from websocket.models import ConvertedPrice

# pylint: disable=missing-class-docstring, too-few-public-methods


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(tz=timezone.utc)
    )

    rooms: Mapped[list["RoomUser"]] = relationship("RoomUser", back_populates="user")
    game_prices: Mapped[list["GamePrice"]] = relationship(
        "GamePrice", back_populates="user"
    )
    lost_games: Mapped[list["Game"]] = relationship("Game", back_populates="loser_user")


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(
        String(15), index=True, nullable=False, unique=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(tz=timezone.utc)
    )
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)

    users: Mapped[list["RoomUser"]] = relationship("RoomUser", back_populates="room")
    games: Mapped[list["Game"]] = relationship("Game", back_populates="room")


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
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    status: Mapped[ApprovalStatus] = mapped_column(
        nullable=False, default=ApprovalStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(tz=timezone.utc)
    )

    room: Mapped[Room] = relationship("Room", back_populates="users")
    user: Mapped[User] = relationship("User", back_populates="rooms")


class Game(Base):
    __tablename__ = "games"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    room_id: Mapped[str] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    loser: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(tz=timezone.utc)
    )

    room: Mapped[Room] = relationship("Room", back_populates="games")
    prices: Mapped[list["GamePrice"]] = relationship("GamePrice", back_populates="game")
    loser_user: Mapped[User] = relationship(
        "User", back_populates="lost_games", foreign_keys=[loser]
    )

    @classmethod
    async def create_game_with_prices(
        cls,
        room_id: str,
        loser_id: str,
        converted_prices: list[ConvertedPrice],
        total_in_czk: float,
    ) -> None:
        """Creates a game and its associated prices asynchronously."""
        async for session in get_session():
            game = cls(room_id=room_id, loser=loser_id, price=total_in_czk)

            session.add(game)
            await session.flush()

            for converted_price in converted_prices:
                game_price = GamePrice(
                    game_id=game.id,
                    user_id=converted_price.user_id,
                    price=converted_price.original_price,
                    currency=converted_price.original_currency,
                    conversion_rate=converted_price.conversion_rate,
                    price_in_czk=converted_price.price_in_czk,
                )
                session.add(game_price)

            await session.commit()


class GamePrice(Base):
    __tablename__ = "game_prices"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    game_id: Mapped[str] = mapped_column(ForeignKey("games.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)

    price: Mapped[float] = mapped_column(nullable=False)
    currency: Mapped[Currency] = mapped_column(nullable=False)
    conversion_rate: Mapped[float] = mapped_column(nullable=True)
    price_in_czk: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(tz=timezone.utc)
    )

    game: Mapped[Game] = relationship("Game", back_populates="prices")
    user: Mapped[User] = relationship("User", back_populates="game_prices")
