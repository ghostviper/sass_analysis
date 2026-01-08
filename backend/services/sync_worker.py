"""
Sync Worker - Background task for Redis -> SQLite persistence.

Runs as a background asyncio task, periodically syncing dirty sessions
from Redis to SQLite for durability.
"""

import asyncio
import logging
from typing import Optional, Set
from datetime import datetime

from config.redis_config import get_redis_config

logger = logging.getLogger(__name__)


class SyncWorker:
    """
    Background worker for syncing Redis data to SQLite.

    Usage:
        worker = SyncWorker()
        await worker.start()
        # ... later ...
        await worker.stop()
    """

    def __init__(self, interval: Optional[int] = None):
        """
        Initialize the sync worker.

        Args:
            interval: Sync interval in seconds (default from config)
        """
        self.config = get_redis_config()
        self.interval = interval or self.config.sync_interval
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._pending_syncs: Set[str] = set()
        self._sync_lock = asyncio.Lock()

    async def start(self) -> None:
        """Start the background sync loop."""
        if self._running:
            logger.warning("SyncWorker already running")
            return

        if not self.config.enabled:
            logger.info("Redis disabled, SyncWorker not starting")
            return

        self._running = True
        self._task = asyncio.create_task(self._sync_loop())
        logger.info(f"SyncWorker started with interval={self.interval}s")

    async def stop(self) -> None:
        """Stop the sync worker and perform final sync."""
        if not self._running:
            return

        logger.info("Stopping SyncWorker...")
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        # Final sync before shutdown
        await self._sync_all_dirty()
        logger.info("SyncWorker stopped")

    async def mark_for_sync(self, session_id: str) -> None:
        """
        Mark a session for immediate sync (after stream completion).

        Args:
            session_id: The session to sync
        """
        if not self.config.enabled:
            return

        async with self._sync_lock:
            self._pending_syncs.add(session_id)

        # If sync_on_done is enabled, sync immediately
        if self.config.sync_on_done:
            asyncio.create_task(self._sync_session(session_id))

    async def _sync_loop(self) -> None:
        """Main sync loop - runs periodically."""
        while self._running:
            try:
                await asyncio.sleep(self.interval)
                if self._running:
                    await self._sync_all_dirty()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")
                await asyncio.sleep(5)  # Brief pause before retry

    async def _sync_all_dirty(self) -> None:
        """Sync all dirty sessions."""
        from services.session_store import get_session_store

        store = get_session_store()

        try:
            # Get pending syncs from local set
            async with self._sync_lock:
                local_pending = self._pending_syncs.copy()
                self._pending_syncs.clear()

            # Get dirty sessions from Redis
            redis_dirty = await store.get_dirty_sessions()

            # Combine both sets
            all_dirty = local_pending | set(redis_dirty)

            if not all_dirty:
                return

            logger.info(f"Syncing {len(all_dirty)} dirty sessions")

            # Batch sync
            batch_size = self.config.sync_batch_size
            dirty_list = list(all_dirty)

            for i in range(0, len(dirty_list), batch_size):
                batch = dirty_list[i:i + batch_size]
                await asyncio.gather(
                    *[self._sync_session(sid) for sid in batch],
                    return_exceptions=True
                )

        except Exception as e:
            logger.error(f"Error syncing dirty sessions: {e}")

    async def _sync_session(self, session_id: str) -> bool:
        """
        Sync a single session to SQLite.

        Args:
            session_id: The session to sync

        Returns:
            True if sync was successful
        """
        from services.session_store import get_session_store

        store = get_session_store()

        try:
            success = await store.sync_to_sqlite(session_id)
            if success:
                logger.debug(f"Synced session {session_id}")
            else:
                logger.warning(f"Failed to sync session {session_id}")
            return success
        except Exception as e:
            logger.error(f"Error syncing session {session_id}: {e}")
            return False

    @property
    def is_running(self) -> bool:
        """Check if the worker is running."""
        return self._running

    async def get_stats(self) -> dict:
        """Get sync worker statistics."""
        from services.session_store import get_session_store
        store = get_session_store()

        pending_count = len(self._pending_syncs)
        dirty_sessions = await store.get_dirty_sessions()

        return {
            "running": self._running,
            "interval_seconds": self.interval,
            "pending_local": pending_count,
            "pending_redis": len(dirty_sessions),
            "batch_size": self.config.sync_batch_size,
        }


# Global worker instance
_worker: Optional[SyncWorker] = None


def get_sync_worker() -> SyncWorker:
    """Get the sync worker singleton."""
    global _worker
    if _worker is None:
        _worker = SyncWorker()
    return _worker


async def start_sync_worker() -> None:
    """Start the global sync worker."""
    worker = get_sync_worker()
    await worker.start()


async def stop_sync_worker() -> None:
    """Stop the global sync worker."""
    worker = get_sync_worker()
    await worker.stop()
