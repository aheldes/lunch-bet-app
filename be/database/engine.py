import logging
from typing import Any, AsyncGenerator

from databases import Database
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

from settings import settings
from .base_model import Base


DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USERNAME}:"
    f"{settings.DB_PASSWORD}@localhost:5432/postgres"
)
database = Database(DATABASE_URL)
engine = create_async_engine(DATABASE_URL)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)

logger = logging.getLogger("uvicorn.error")


async def get_redis() -> AsyncGenerator[redis.Redis, Any]:
    """Yields an asyncrhonous redis session."""
    logger.info("Getting redis session.")
    pool = redis.StrictRedis(host="localhost", port=6379, db=0)
    try:
        yield pool
    finally:
        await pool.close()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an asynchronous database session.

    Yields:
        AsyncSession: The database session for interacting with the DB.
    """
    logger.info("Getting db session.")
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    """Initialize the database by connecting and creating all tables."""
    logger.info("Initializing database.")
    await database.connect()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def disconnect_db() -> None:
    """Disconnect from the database."""
    logger.info("Disconnecting from db.")
    await database.disconnect()
