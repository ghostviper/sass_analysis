"""
Redis Client - Connection pool and basic operations wrapper.

Provides a singleton Redis client with connection pooling for async operations.
"""

import asyncio
import logging
from typing import Optional, Any, List, Dict, Union

try:
    import redis.asyncio as redis
    from redis.asyncio import ConnectionPool, Redis
    from redis.exceptions import ConnectionError, TimeoutError, RedisError
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None
    ConnectionPool = None
    Redis = None
    ConnectionError = Exception
    TimeoutError = Exception
    RedisError = Exception

from config.redis_config import get_redis_config, RedisConfig

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Singleton Redis client with connection pooling.

    Usage:
        client = await RedisClient.get_client()
        await client.set("key", "value")
        value = await client.get("key")
    """

    _pool: Optional["ConnectionPool"] = None
    _client: Optional["Redis"] = None
    _lock: asyncio.Lock = asyncio.Lock()
    _initialized: bool = False

    @classmethod
    async def get_client(cls) -> Optional["Redis"]:
        """
        Get the Redis client instance.

        Returns:
            Redis client if available and configured, None otherwise.
        """
        if not REDIS_AVAILABLE:
            logger.warning("redis package not installed, Redis features disabled")
            return None

        config = get_redis_config()
        if not config.enabled:
            logger.info("Redis is disabled by configuration")
            return None

        async with cls._lock:
            if cls._client is None:
                try:
                    cls._pool = ConnectionPool.from_url(
                        config.url,
                        password=config.password,
                        decode_responses=True,
                        max_connections=config.max_connections,
                        socket_timeout=5.0,
                        socket_connect_timeout=5.0,
                    )
                    cls._client = Redis(connection_pool=cls._pool)
                    # Test connection
                    await cls._client.ping()
                    cls._initialized = True
                    logger.info("Redis connection established")
                except (ConnectionError, TimeoutError, RedisError) as e:
                    logger.error(f"Failed to connect to Redis: {e}")
                    cls._client = None
                    cls._pool = None
                    if not config.fallback_on_error:
                        raise
                except Exception as e:
                    logger.error(f"Unexpected error connecting to Redis: {e}")
                    cls._client = None
                    cls._pool = None

        return cls._client

    @classmethod
    async def close(cls) -> None:
        """Close the Redis connection pool."""
        async with cls._lock:
            if cls._client:
                try:
                    await cls._client.close()
                except Exception as e:
                    logger.error(f"Error closing Redis client: {e}")
                finally:
                    cls._client = None

            if cls._pool:
                try:
                    await cls._pool.disconnect()
                except Exception as e:
                    logger.error(f"Error disconnecting Redis pool: {e}")
                finally:
                    cls._pool = None

            cls._initialized = False
            logger.info("Redis connection closed")

    @classmethod
    def is_available(cls) -> bool:
        """Check if Redis is available and connected."""
        return cls._initialized and cls._client is not None

    @classmethod
    async def health_check(cls) -> Dict[str, Any]:
        """Perform a health check on the Redis connection."""
        result = {
            "available": REDIS_AVAILABLE,
            "enabled": get_redis_config().enabled,
            "connected": False,
            "latency_ms": None,
            "error": None,
        }

        if not REDIS_AVAILABLE:
            result["error"] = "redis package not installed"
            return result

        client = await cls.get_client()
        if client is None:
            result["error"] = "Redis client not available"
            return result

        try:
            import time
            start = time.perf_counter()
            await client.ping()
            latency = (time.perf_counter() - start) * 1000
            result["connected"] = True
            result["latency_ms"] = round(latency, 2)
        except Exception as e:
            result["error"] = str(e)

        return result


# Convenience functions for common operations


async def redis_get(key: str) -> Optional[str]:
    """Get a value from Redis."""
    client = await RedisClient.get_client()
    if client is None:
        return None
    try:
        return await client.get(key)
    except RedisError as e:
        logger.error(f"Redis GET error for key {key}: {e}")
        return None


async def redis_set(
    key: str,
    value: str,
    ex: Optional[int] = None,
    px: Optional[int] = None,
    nx: bool = False,
    xx: bool = False,
) -> bool:
    """Set a value in Redis with optional expiration."""
    client = await RedisClient.get_client()
    if client is None:
        return False
    try:
        result = await client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)
        return result is True or result == "OK"
    except RedisError as e:
        logger.error(f"Redis SET error for key {key}: {e}")
        return False


async def redis_delete(*keys: str) -> int:
    """Delete one or more keys from Redis."""
    client = await RedisClient.get_client()
    if client is None:
        return 0
    try:
        return await client.delete(*keys)
    except RedisError as e:
        logger.error(f"Redis DELETE error: {e}")
        return 0


async def redis_hgetall(key: str) -> Dict[str, str]:
    """Get all fields and values in a hash."""
    client = await RedisClient.get_client()
    if client is None:
        return {}
    try:
        return await client.hgetall(key)
    except RedisError as e:
        logger.error(f"Redis HGETALL error for key {key}: {e}")
        return {}


async def redis_hset(key: str, mapping: Dict[str, Any]) -> int:
    """Set multiple hash fields."""
    client = await RedisClient.get_client()
    if client is None:
        return 0
    try:
        # Convert all values to strings
        str_mapping = {k: str(v) if v is not None else "" for k, v in mapping.items()}
        return await client.hset(key, mapping=str_mapping)
    except RedisError as e:
        logger.error(f"Redis HSET error for key {key}: {e}")
        return 0


async def redis_expire(key: str, seconds: int) -> bool:
    """Set a key's time to live in seconds."""
    client = await RedisClient.get_client()
    if client is None:
        return False
    try:
        return await client.expire(key, seconds)
    except RedisError as e:
        logger.error(f"Redis EXPIRE error for key {key}: {e}")
        return False


async def redis_zadd(
    key: str,
    mapping: Dict[str, float],
    nx: bool = False,
    xx: bool = False,
) -> int:
    """Add members to a sorted set with scores."""
    client = await RedisClient.get_client()
    if client is None:
        return 0
    try:
        return await client.zadd(key, mapping, nx=nx, xx=xx)
    except RedisError as e:
        logger.error(f"Redis ZADD error for key {key}: {e}")
        return 0


async def redis_zrange(
    key: str,
    start: int = 0,
    end: int = -1,
    desc: bool = False,
    withscores: bool = False,
) -> Union[List[str], List[tuple]]:
    """Get a range of members from a sorted set."""
    client = await RedisClient.get_client()
    if client is None:
        return []
    try:
        if desc:
            return await client.zrevrange(key, start, end, withscores=withscores)
        return await client.zrange(key, start, end, withscores=withscores)
    except RedisError as e:
        logger.error(f"Redis ZRANGE error for key {key}: {e}")
        return []


async def redis_zrem(key: str, *members: str) -> int:
    """Remove members from a sorted set."""
    client = await RedisClient.get_client()
    if client is None:
        return 0
    try:
        return await client.zrem(key, *members)
    except RedisError as e:
        logger.error(f"Redis ZREM error for key {key}: {e}")
        return 0


async def redis_sadd(key: str, *members: str) -> int:
    """Add members to a set."""
    client = await RedisClient.get_client()
    if client is None:
        return 0
    try:
        return await client.sadd(key, *members)
    except RedisError as e:
        logger.error(f"Redis SADD error for key {key}: {e}")
        return 0


async def redis_smembers(key: str) -> set:
    """Get all members of a set."""
    client = await RedisClient.get_client()
    if client is None:
        return set()
    try:
        return await client.smembers(key)
    except RedisError as e:
        logger.error(f"Redis SMEMBERS error for key {key}: {e}")
        return set()


async def redis_srem(key: str, *members: str) -> int:
    """Remove members from a set."""
    client = await RedisClient.get_client()
    if client is None:
        return 0
    try:
        return await client.srem(key, *members)
    except RedisError as e:
        logger.error(f"Redis SREM error for key {key}: {e}")
        return 0


async def redis_exists(*keys: str) -> int:
    """Check if keys exist."""
    client = await RedisClient.get_client()
    if client is None:
        return 0
    try:
        return await client.exists(*keys)
    except RedisError as e:
        logger.error(f"Redis EXISTS error: {e}")
        return 0


async def redis_pipeline() -> Optional[Any]:
    """Get a Redis pipeline for batch operations."""
    client = await RedisClient.get_client()
    if client is None:
        return None
    return client.pipeline()
