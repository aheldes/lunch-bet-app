from typing import Optional

from redis.asyncio import Redis

from .enums import UserType


class CacheKeyGenerator:
    """Helper class for getting cache keys."""

    @staticmethod
    def generate_room_user_cache_key(room_id: str, user_type: UserType) -> str:
        """Generate room user cache key from room id and user type."""
        return f"room:{room_id}:users:{user_type}"

    @staticmethod
    def generate_rooms_cache_key() -> str:
        """Generate rooms cache key."""
        return "rooms"


async def invalidate_cache(cache_key: str, redis: Redis) -> None:
    """Invalidates the cache for a specific key."""
    await redis.delete(cache_key)


async def set_cache(cache_key: str, json_data: str, redis: Redis) -> None:
    """Sets the cache for a specific key, accepting JSON string."""
    await redis.set(cache_key, json_data)


async def get_cache(cache_key: str, redis: Redis) -> Optional[str]:
    """Gets the cache for a specific key, returning JSON string."""
    cached_data = await redis.get(cache_key)
    if cached_data:
        return cached_data.decode("utf-8")
    return None
