"""
Redis configuration for chat session storage.

Redis is used as the primary storage for real-time chat operations,
with async persistence to SQLite for durability.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RedisConfig:
    """Redis connection and behavior configuration."""

    # Connection settings
    url: str = "redis://localhost:6379/0"
    password: Optional[str] = None
    max_connections: int = 20

    # TTL settings (in seconds)
    session_ttl: int = 7 * 24 * 3600  # 7 days
    message_ttl: int = 7 * 24 * 3600  # 7 days
    stream_ttl: int = 3600  # 1 hour for stream buffers
    sessions_list_ttl: int = 30 * 24 * 3600  # 30 days for session list index

    # Sync settings
    sync_interval: int = 60  # seconds between sync checks
    sync_batch_size: int = 100  # max sessions to sync per batch
    sync_on_done: bool = True  # immediately sync after stream completes

    # Key prefixes
    session_prefix: str = "chat:session:"
    message_prefix: str = "chat:message:"
    messages_index_prefix: str = "chat:messages:"
    sessions_list_prefix: str = "chat:sessions:list:"
    stream_prefix: str = "chat:stream:"
    dirty_set_key: str = "chat:dirty_sessions"

    # Feature flags
    enabled: bool = True  # If False, fall back to direct SQLite writes
    fallback_on_error: bool = True  # Fall back to SQLite if Redis fails

    @classmethod
    def from_env(cls) -> "RedisConfig":
        """Create configuration from environment variables."""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

        # Check if Redis is explicitly disabled
        enabled = os.getenv("REDIS_ENABLED", "true").lower() in ("true", "1", "yes")

        return cls(
            url=redis_url,
            password=os.getenv("REDIS_PASSWORD") or None,
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "20")),
            session_ttl=int(os.getenv("REDIS_SESSION_TTL", str(7 * 24 * 3600))),
            message_ttl=int(os.getenv("REDIS_MESSAGE_TTL", str(7 * 24 * 3600))),
            sync_interval=int(os.getenv("SYNC_INTERVAL_SECONDS", "60")),
            sync_batch_size=int(os.getenv("SYNC_BATCH_SIZE", "100")),
            sync_on_done=os.getenv("SYNC_ON_DONE", "true").lower() in ("true", "1", "yes"),
            enabled=enabled,
            fallback_on_error=os.getenv("REDIS_FALLBACK_ON_ERROR", "true").lower() in ("true", "1", "yes"),
        )

    def get_session_key(self, session_id: str) -> str:
        """Get Redis key for a session."""
        return f"{self.session_prefix}{session_id}"

    def get_message_key(self, session_id: str, message_id: str) -> str:
        """Get Redis key for a message."""
        return f"{self.message_prefix}{session_id}:{message_id}"

    def get_messages_index_key(self, session_id: str) -> str:
        """Get Redis key for messages index (sorted set)."""
        return f"{self.messages_index_prefix}{session_id}"

    def get_sessions_list_key(self, scope: str = "global") -> str:
        """Get Redis key for sessions list (sorted set)."""
        return f"{self.sessions_list_prefix}{scope}"

    def get_stream_key(self, session_id: str, request_id: str) -> str:
        """Get Redis key for stream buffer."""
        return f"{self.stream_prefix}{session_id}:{request_id}"


# Global config instance
_config: Optional[RedisConfig] = None


def get_redis_config() -> RedisConfig:
    """Get the Redis configuration singleton."""
    global _config
    if _config is None:
        _config = RedisConfig.from_env()
    return _config


def reload_redis_config() -> RedisConfig:
    """Reload Redis configuration from environment."""
    global _config
    _config = RedisConfig.from_env()
    return _config
