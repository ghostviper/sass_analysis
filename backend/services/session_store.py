"""
Session Store - Redis-based session storage with SQLite fallback.

Provides a unified interface for chat session and message storage.
All real-time operations go through Redis, with async persistence to SQLite.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from config.redis_config import get_redis_config, RedisConfig
from services.redis_client import (
    RedisClient,
    redis_hgetall,
    redis_hset,
    redis_expire,
    redis_zadd,
    redis_zrange,
    redis_zrem,
    redis_sadd,
    redis_srem,
    redis_smembers,
    redis_delete,
    redis_exists,
    redis_pipeline,
)

logger = logging.getLogger(__name__)


class SessionStore:
    """
    Redis-based session storage with SQLite fallback.

    Usage:
        store = SessionStore()
        session = await store.get_session(session_id)
        await store.add_message(session_id, message)
    """

    def __init__(self):
        self.config = get_redis_config()
        self._fallback_mode = False

    async def _check_redis(self) -> bool:
        """Check if Redis is available."""
        if self._fallback_mode:
            return False
        client = await RedisClient.get_client()
        return client is not None

    async def _use_fallback(self) -> bool:
        """Determine if we should use SQLite fallback."""
        if not self.config.enabled:
            return True
        if not self.config.fallback_on_error:
            return not await self._check_redis()
        return not await self._check_redis()

    # ==================== Session Operations ====================

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session from Redis, fallback to SQLite if not found.

        Args:
            session_id: The session UUID

        Returns:
            Session data dict or None if not found
        """
        if await self._use_fallback():
            return await self._get_session_sqlite(session_id)

        key = self.config.get_session_key(session_id)
        data = await redis_hgetall(key)

        if not data:
            # Try SQLite and cache to Redis
            session = await self._get_session_sqlite(session_id)
            if session:
                await self._cache_session_to_redis(session)
            return session

        return self._deserialize_session(data)

    async def create_session(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        title: Optional[str] = None,
        enable_web_search: bool = False,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new session in Redis.

        Args:
            session_id: Optional session UUID (generated if not provided)
            user_id: Optional user identifier
            title: Optional session title
            enable_web_search: Whether web search is enabled
            context: Optional context dict with type, value, products

        Returns:
            The created session data
        """
        if session_id is None:
            session_id = str(uuid.uuid4())

        now = datetime.utcnow()
        now_iso = now.isoformat()

        session = {
            "session_id": session_id,
            "user_id": user_id or "",
            "title": title or "",
            "summary": "",
            "enable_web_search": enable_web_search,
            "context_type": context.get("type", "") if context else "",
            "context_value": context.get("value", "") if context else "",
            "context_products": json.dumps(context.get("products", [])) if context else "[]",
            "message_count": 0,
            "turn_count": 0,
            "total_cost": 0.0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "is_archived": False,
            "is_deleted": False,
            "created_at": now_iso,
            "updated_at": now_iso,
            "last_message_at": now_iso,
            "synced_at": "",
            "dirty": True,
        }

        if await self._use_fallback():
            return await self._create_session_sqlite(session)

        key = self.config.get_session_key(session_id)
        await redis_hset(key, self._serialize_session(session))
        await redis_expire(key, self.config.session_ttl)

        # Add to sessions list index
        scope = user_id or "global"
        list_key = self.config.get_sessions_list_key(scope)
        await redis_zadd(list_key, {session_id: now.timestamp()})
        await redis_expire(list_key, self.config.sessions_list_ttl)

        # Mark as dirty for sync
        await redis_sadd(self.config.dirty_set_key, session_id)

        return session

    async def ensure_session_exists(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        enable_web_search: bool = False,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Ensure a session exists, create if not found.

        Args:
            session_id: The session UUID
            user_id: Optional user identifier
            enable_web_search: Whether web search is enabled
            context: Optional context dict

        Returns:
            Existing or newly created session data
        """
        session = await self.get_session(session_id)
        if session:
            return session

        return await self.create_session(
            session_id=session_id,
            user_id=user_id,
            enable_web_search=enable_web_search,
            context=context,
        )

    async def update_session(
        self,
        session_id: str,
        **updates: Any,
    ) -> bool:
        """
        Update session fields.

        Args:
            session_id: The session UUID
            **updates: Fields to update (title, summary, is_archived, etc.)

        Returns:
            True if successful
        """
        if await self._use_fallback():
            return await self._update_session_sqlite(session_id, **updates)

        key = self.config.get_session_key(session_id)
        exists = await redis_exists(key)
        if not exists:
            return await self._update_session_sqlite(session_id, **updates)

        updates["updated_at"] = datetime.utcnow().isoformat()
        updates["dirty"] = True

        await redis_hset(key, self._serialize_session(updates))
        await redis_sadd(self.config.dirty_set_key, session_id)
        return True

    async def delete_session(self, session_id: str, hard: bool = False) -> bool:
        """
        Delete a session (soft or hard delete).

        Args:
            session_id: The session UUID
            hard: If True, permanently delete; otherwise soft delete

        Returns:
            True if successful
        """
        if hard:
            # Hard delete from both Redis and SQLite
            if await self._check_redis():
                key = self.config.get_session_key(session_id)
                messages_key = self.config.get_messages_index_key(session_id)

                # Get all message IDs
                message_ids = await redis_zrange(messages_key, 0, -1)

                # Delete all message keys
                if message_ids:
                    msg_keys = [
                        self.config.get_message_key(session_id, mid)
                        for mid in message_ids
                    ]
                    await redis_delete(*msg_keys)

                await redis_delete(key, messages_key)
                await redis_srem(self.config.dirty_set_key, session_id)

                # Remove from sessions list
                for scope in ["global"]:  # Could iterate user_id scopes too
                    list_key = self.config.get_sessions_list_key(scope)
                    await redis_zrem(list_key, session_id)

            return await self._delete_session_sqlite(session_id, hard=True)

        # Soft delete
        return await self.update_session(session_id, is_deleted=True)

    async def list_sessions(
        self,
        user_id: Optional[str] = None,
        include_archived: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List sessions, optionally filtered by user.

        Args:
            user_id: Optional user filter
            include_archived: Whether to include archived sessions
            limit: Maximum number of sessions
            offset: Offset for pagination

        Returns:
            List of session dicts
        """
        if await self._use_fallback():
            return await self._list_sessions_sqlite(
                user_id, include_archived, limit, offset
            )

        scope = user_id or "global"
        list_key = self.config.get_sessions_list_key(scope)

        # Get session IDs from sorted set (sorted by updated_at desc)
        session_ids = await redis_zrange(
            list_key, offset, offset + limit - 1, desc=True
        )

        if not session_ids:
            # Fall back to SQLite
            return await self._list_sessions_sqlite(
                user_id, include_archived, limit, offset
            )

        sessions = []
        for sid in session_ids:
            session = await self.get_session(sid)
            if session:
                if session.get("is_deleted"):
                    continue
                if not include_archived and session.get("is_archived"):
                    continue
                sessions.append(session)

        return sessions

    # ==================== Message Operations ====================

    async def add_message(
        self,
        session_id: str,
        message: Dict[str, Any],
    ) -> str:
        """
        Add a message to a session.

        Args:
            session_id: The session UUID
            message: Message dict with role, content, etc.

        Returns:
            The message ID
        """
        message_id = message.get("id") or str(uuid.uuid4())
        now = datetime.utcnow()
        now_iso = now.isoformat()

        if await self._use_fallback():
            return await self._add_message_sqlite(session_id, message)

        # Get current message count for sequence
        session = await self.get_session(session_id)
        if not session:
            session = await self.create_session(session_id=session_id)

        sequence = session.get("message_count", 0) + 1

        # Prepare message data
        msg_data = {
            "id": message_id,
            "session_id": session_id,
            "role": message.get("role", "user"),
            "content": message.get("content", ""),
            "sequence": sequence,
            "tool_calls": json.dumps(message.get("tool_calls", [])),
            "content_blocks": json.dumps(message.get("content_blocks", [])),
            "input_tokens": message.get("input_tokens", 0),
            "output_tokens": message.get("output_tokens", 0),
            "cost": message.get("cost", 0.0),
            "model": message.get("model", ""),
            "duration_ms": message.get("duration_ms", 0),
            "created_at": message.get("created_at") or now_iso,
            "synced": False,
        }

        # Save message to Redis
        msg_key = self.config.get_message_key(session_id, message_id)
        await redis_hset(msg_key, self._serialize_message(msg_data))
        await redis_expire(msg_key, self.config.message_ttl)

        # Add to messages index
        messages_key = self.config.get_messages_index_key(session_id)
        await redis_zadd(messages_key, {message_id: sequence})
        await redis_expire(messages_key, self.config.message_ttl)

        # Update session stats
        role = message.get("role", "user")
        cost = message.get("cost", 0.0)
        input_tokens = message.get("input_tokens", 0)
        output_tokens = message.get("output_tokens", 0)

        update_data = {
            "message_count": sequence,
            "updated_at": now_iso,
            "last_message_at": now_iso,
            "dirty": True,
        }

        if role == "user":
            update_data["turn_count"] = session.get("turn_count", 0) + 1

        if cost:
            update_data["total_cost"] = session.get("total_cost", 0.0) + cost
        if input_tokens:
            update_data["total_input_tokens"] = session.get("total_input_tokens", 0) + input_tokens
        if output_tokens:
            update_data["total_output_tokens"] = session.get("total_output_tokens", 0) + output_tokens

        session_key = self.config.get_session_key(session_id)
        await redis_hset(session_key, self._serialize_session(update_data))
        await redis_sadd(self.config.dirty_set_key, session_id)

        # Update sessions list score
        scope = session.get("user_id") or "global"
        list_key = self.config.get_sessions_list_key(scope)
        await redis_zadd(list_key, {session_id: now.timestamp()})

        return message_id

    async def get_messages(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get messages for a session.

        Args:
            session_id: The session UUID
            limit: Maximum number of messages
            offset: Offset for pagination

        Returns:
            List of message dicts ordered by sequence
        """
        if await self._use_fallback():
            return await self._get_messages_sqlite(session_id, limit, offset)

        messages_key = self.config.get_messages_index_key(session_id)
        message_ids = await redis_zrange(messages_key, offset, offset + limit - 1)

        if not message_ids:
            # Fall back to SQLite
            messages = await self._get_messages_sqlite(session_id, limit, offset)
            # Cache to Redis
            for msg in messages:
                await self._cache_message_to_redis(session_id, msg)
            return messages

        messages = []
        for mid in message_ids:
            msg_key = self.config.get_message_key(session_id, mid)
            data = await redis_hgetall(msg_key)
            if data:
                messages.append(self._deserialize_message(data))
            else:
                # Message not in Redis, try SQLite
                msg = await self._get_message_sqlite(session_id, mid)
                if msg:
                    await self._cache_message_to_redis(session_id, msg)
                    messages.append(msg)

        return messages

    async def get_recent_messages(
        self,
        session_id: str,
        count: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get the most recent messages for a session.

        Args:
            session_id: The session UUID
            count: Number of recent messages

        Returns:
            List of message dicts in chronological order
        """
        if await self._use_fallback():
            return await self._get_recent_messages_sqlite(session_id, count)

        messages_key = self.config.get_messages_index_key(session_id)
        # Get last N message IDs
        message_ids = await redis_zrange(messages_key, -count, -1)

        if not message_ids:
            return await self._get_recent_messages_sqlite(session_id, count)

        messages = []
        for mid in message_ids:
            msg_key = self.config.get_message_key(session_id, mid)
            data = await redis_hgetall(msg_key)
            if data:
                messages.append(self._deserialize_message(data))

        return messages

    # ==================== Sync Operations ====================

    async def mark_dirty(self, session_id: str) -> None:
        """Mark a session as needing sync to SQLite."""
        if await self._check_redis():
            await redis_sadd(self.config.dirty_set_key, session_id)
            session_key = self.config.get_session_key(session_id)
            await redis_hset(session_key, {"dirty": "1"})

    async def get_dirty_sessions(self) -> List[str]:
        """Get list of session IDs that need sync."""
        if not await self._check_redis():
            return []
        return list(await redis_smembers(self.config.dirty_set_key))

    async def mark_synced(self, session_id: str) -> None:
        """Mark a session as synced."""
        if await self._check_redis():
            await redis_srem(self.config.dirty_set_key, session_id)
            session_key = self.config.get_session_key(session_id)
            await redis_hset(session_key, {
                "dirty": "0",
                "synced_at": datetime.utcnow().isoformat()
            })

    async def sync_to_sqlite(self, session_id: str) -> bool:
        """
        Sync a session and its messages from Redis to SQLite.

        Args:
            session_id: The session UUID

        Returns:
            True if sync was successful
        """
        if not await self._check_redis():
            return True  # Nothing to sync

        try:
            # Get session from Redis
            session = await self.get_session(session_id)
            if not session:
                return True

            # Get all messages from Redis
            messages = await self.get_messages(session_id, limit=10000)

            # Write to SQLite
            await self._sync_session_to_sqlite(session, messages)

            # Mark as synced
            await self.mark_synced(session_id)
            return True

        except Exception as e:
            logger.error(f"Failed to sync session {session_id}: {e}")
            return False

    # ==================== Serialization ====================

    def _serialize_session(self, session: Dict[str, Any]) -> Dict[str, str]:
        """Convert session dict to Redis-storable format (all strings)."""
        result = {}
        for k, v in session.items():
            if v is None:
                result[k] = ""
            elif isinstance(v, bool):
                result[k] = "1" if v else "0"
            elif isinstance(v, (int, float)):
                result[k] = str(v)
            elif isinstance(v, (list, dict)):
                result[k] = json.dumps(v)
            else:
                result[k] = str(v)
        return result

    def _deserialize_session(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Convert Redis hash data back to session dict."""
        result = {}
        bool_fields = {"enable_web_search", "is_archived", "is_deleted", "dirty"}
        int_fields = {"message_count", "turn_count", "total_input_tokens", "total_output_tokens"}
        float_fields = {"total_cost"}
        json_fields = {"context_products"}

        for k, v in data.items():
            if k in bool_fields:
                result[k] = v in ("1", "true", "True")
            elif k in int_fields:
                result[k] = int(v) if v else 0
            elif k in float_fields:
                result[k] = float(v) if v else 0.0
            elif k in json_fields:
                try:
                    result[k] = json.loads(v) if v else []
                except json.JSONDecodeError:
                    result[k] = []
            else:
                result[k] = v if v else None

        return result

    def _serialize_message(self, message: Dict[str, Any]) -> Dict[str, str]:
        """Convert message dict to Redis-storable format."""
        result = {}
        for k, v in message.items():
            if v is None:
                result[k] = ""
            elif isinstance(v, bool):
                result[k] = "1" if v else "0"
            elif isinstance(v, (int, float)):
                result[k] = str(v)
            elif isinstance(v, (list, dict)):
                result[k] = json.dumps(v)
            else:
                result[k] = str(v)
        return result

    def _deserialize_message(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Convert Redis hash data back to message dict."""
        result = {}
        bool_fields = {"synced"}
        int_fields = {"sequence", "input_tokens", "output_tokens", "duration_ms"}
        float_fields = {"cost"}
        json_fields = {"tool_calls", "content_blocks"}

        for k, v in data.items():
            if k in bool_fields:
                result[k] = v in ("1", "true", "True")
            elif k in int_fields:
                result[k] = int(v) if v else 0
            elif k in float_fields:
                result[k] = float(v) if v else 0.0
            elif k in json_fields:
                try:
                    result[k] = json.loads(v) if v else []
                except json.JSONDecodeError:
                    result[k] = []
            else:
                result[k] = v if v else None

        return result

    # ==================== SQLite Fallback Methods ====================

    async def _get_session_sqlite(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session from SQLite."""
        from services.chat_history import ChatHistoryService
        return await ChatHistoryService.get_session_dict(session_id)

    async def _create_session_sqlite(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Create session in SQLite."""
        from services.chat_history import ChatHistoryService
        await ChatHistoryService.create_session(
            session_id=session["session_id"],
            user_id=session.get("user_id") or None,
            title=session.get("title") or None,
            enable_web_search=session.get("enable_web_search", False),
            context={
                "type": session.get("context_type"),
                "value": session.get("context_value"),
                "products": json.loads(session.get("context_products", "[]")),
            } if session.get("context_type") else None,
        )
        return session

    async def _update_session_sqlite(self, session_id: str, **updates) -> bool:
        """Update session in SQLite."""
        from services.chat_history import ChatHistoryService
        # Filter out Redis-only fields
        sqlite_updates = {k: v for k, v in updates.items() if k not in ("dirty", "synced_at")}
        return await ChatHistoryService.update_session(session_id, **sqlite_updates)

    async def _delete_session_sqlite(self, session_id: str, hard: bool = False) -> bool:
        """Delete session from SQLite."""
        from services.chat_history import ChatHistoryService
        return await ChatHistoryService.delete_session(session_id, hard=hard)

    async def _list_sessions_sqlite(
        self,
        user_id: Optional[str],
        include_archived: bool,
        limit: int,
        offset: int,
    ) -> List[Dict[str, Any]]:
        """List sessions from SQLite."""
        from services.chat_history import ChatHistoryService
        return await ChatHistoryService.list_sessions(
            user_id=user_id,
            include_archived=include_archived,
            limit=limit,
            offset=offset,
        )

    async def _add_message_sqlite(
        self,
        session_id: str,
        message: Dict[str, Any],
    ) -> str:
        """Add message to SQLite."""
        from services.chat_history import ChatHistoryService
        return await ChatHistoryService.add_message(
            session_id=session_id,
            role=message.get("role", "user"),
            content=message.get("content", ""),
            tool_calls=message.get("tool_calls"),
            input_tokens=message.get("input_tokens"),
            output_tokens=message.get("output_tokens"),
            cost=message.get("cost"),
            model=message.get("model"),
            duration_ms=message.get("duration_ms"),
        )

    async def _get_messages_sqlite(
        self,
        session_id: str,
        limit: int,
        offset: int,
    ) -> List[Dict[str, Any]]:
        """Get messages from SQLite."""
        from services.chat_history import ChatHistoryService
        return await ChatHistoryService.get_messages(
            session_id=session_id,
            limit=limit,
            offset=offset,
        )

    async def _get_recent_messages_sqlite(
        self,
        session_id: str,
        count: int,
    ) -> List[Dict[str, Any]]:
        """Get recent messages from SQLite."""
        from services.chat_history import ChatHistoryService
        return await ChatHistoryService.get_recent_messages(
            session_id=session_id,
            count=count,
        )

    async def _get_message_sqlite(
        self,
        session_id: str,
        message_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get a single message from SQLite."""
        # This would need to be implemented in ChatHistoryService
        # For now, return None
        return None

    async def _cache_session_to_redis(self, session: Dict[str, Any]) -> None:
        """Cache a session from SQLite to Redis."""
        if not await self._check_redis():
            return

        session_id = session.get("session_id")
        if not session_id:
            return

        key = self.config.get_session_key(session_id)
        serialized = self._serialize_session(session)
        serialized["dirty"] = "0"  # Already in SQLite
        await redis_hset(key, serialized)
        await redis_expire(key, self.config.session_ttl)

    async def _cache_message_to_redis(
        self,
        session_id: str,
        message: Dict[str, Any],
    ) -> None:
        """Cache a message from SQLite to Redis."""
        if not await self._check_redis():
            return

        message_id = message.get("id") or str(uuid.uuid4())
        msg_key = self.config.get_message_key(session_id, message_id)

        msg_data = {**message, "synced": True}
        await redis_hset(msg_key, self._serialize_message(msg_data))
        await redis_expire(msg_key, self.config.message_ttl)

        # Update messages index
        sequence = message.get("sequence", 0)
        messages_key = self.config.get_messages_index_key(session_id)
        await redis_zadd(messages_key, {message_id: sequence})

    async def _sync_session_to_sqlite(
        self,
        session: Dict[str, Any],
        messages: List[Dict[str, Any]],
    ) -> None:
        """Write session and messages from Redis to SQLite."""
        from services.chat_history import ChatHistoryService

        session_id = session.get("session_id")

        # Check if session exists in SQLite
        existing = await ChatHistoryService.get_session_dict(session_id)

        if not existing:
            # Create session
            await ChatHistoryService.create_session(
                session_id=session_id,
                user_id=session.get("user_id") or None,
                title=session.get("title") or None,
                enable_web_search=session.get("enable_web_search", False),
                context={
                    "type": session.get("context_type"),
                    "value": session.get("context_value"),
                    "products": session.get("context_products", []),
                } if session.get("context_type") else None,
            )

        # Update session stats
        await ChatHistoryService.update_session(
            session_id,
            title=session.get("title"),
            message_count=session.get("message_count", 0),
            turn_count=session.get("turn_count", 0),
            total_cost=session.get("total_cost", 0.0),
            is_archived=session.get("is_archived", False),
        )

        # Sync messages that haven't been synced yet
        existing_messages = await ChatHistoryService.get_messages(session_id, limit=10000)
        existing_sequences = {m.get("sequence") for m in existing_messages}

        for msg in messages:
            seq = msg.get("sequence", 0)
            if seq not in existing_sequences:
                await ChatHistoryService.add_message(
                    session_id=session_id,
                    role=msg.get("role", "user"),
                    content=msg.get("content", ""),
                    tool_calls=msg.get("tool_calls"),
                    input_tokens=msg.get("input_tokens"),
                    output_tokens=msg.get("output_tokens"),
                    cost=msg.get("cost"),
                    model=msg.get("model"),
                    duration_ms=msg.get("duration_ms"),
                )


# Singleton instance
_store: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    """Get the session store singleton."""
    global _store
    if _store is None:
        _store = SessionStore()
    return _store
