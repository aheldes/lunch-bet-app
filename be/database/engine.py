from typing import AsyncGenerator

from databases import Database
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

from .base_model import Base

DATABASE_URL = "sqlite+aiosqlite:///./test.db"
database = Database(DATABASE_URL)
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an asynchronous database session.

    Yields:
        AsyncSession: The database session for interacting with the DB.
    """
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    """Initialize the database by connecting and creating all tables."""
    await database.connect()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def disconnect_db() -> None:
    """Disconnect from the database."""
    await database.disconnect()
