"""
Session Manager for Presentation Context
=========================================

Manages presentation sessions with slide history for context retention.
Supports both in-memory and Redis-based storage.
"""

import os
import json
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
import asyncio
from threading import Lock

from app.models.session import SessionContext, SlideContext, SessionCacheEntry

# Redis support (optional)
try:
    import redis.asyncio as redis
except ImportError:
    redis = None


logger = logging.getLogger(__name__)


class BaseSessionStore:
    """
    Abstract base class for session storage backends.
    """

    async def get(self, presentation_id: str) -> Optional[SessionContext]:
        """Get session by presentation ID."""
        raise NotImplementedError

    async def set(
        self,
        presentation_id: str,
        session: SessionContext,
        ttl: int = 3600
    ):
        """Store session with TTL."""
        raise NotImplementedError

    async def delete(self, presentation_id: str):
        """Delete session."""
        raise NotImplementedError

    async def exists(self, presentation_id: str) -> bool:
        """Check if session exists."""
        raise NotImplementedError

    async def cleanup_expired(self):
        """Clean up expired sessions."""
        pass


class InMemorySessionStore(BaseSessionStore):
    """
    In-memory session storage.

    Uses dictionary with TTL tracking. Thread-safe with locks.
    Good for development and single-instance deployments.
    """

    def __init__(self):
        self._sessions: Dict[str, SessionCacheEntry] = {}
        self._lock = Lock()

    async def get(self, presentation_id: str) -> Optional[SessionContext]:
        """Get session from memory."""
        with self._lock:
            if presentation_id not in self._sessions:
                return None

            entry = self._sessions[presentation_id]

            # Check if expired
            if entry.is_expired():
                logger.info(f"Session expired: {presentation_id}")
                del self._sessions[presentation_id]
                return None

            return entry.session_context

    async def set(
        self,
        presentation_id: str,
        session: SessionContext,
        ttl: int = 3600
    ):
        """Store session in memory with TTL."""
        with self._lock:
            entry = SessionCacheEntry(
                session_context=session,
                ttl=ttl
            )
            self._sessions[presentation_id] = entry

            logger.debug(f"Stored session: {presentation_id} (TTL: {ttl}s)")

    async def delete(self, presentation_id: str):
        """Delete session from memory."""
        with self._lock:
            if presentation_id in self._sessions:
                del self._sessions[presentation_id]
                logger.debug(f"Deleted session: {presentation_id}")

    async def exists(self, presentation_id: str) -> bool:
        """Check if session exists and is not expired."""
        session = await self.get(presentation_id)
        return session is not None

    async def cleanup_expired(self):
        """Remove expired sessions from memory."""
        with self._lock:
            expired_keys = [
                key for key, entry in self._sessions.items()
                if entry.is_expired()
            ]

            for key in expired_keys:
                del self._sessions[key]

            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired sessions")


class RedisSessionStore(BaseSessionStore):
    """
    Redis-based session storage.

    Uses Redis with automatic TTL expiration.
    Good for production and multi-instance deployments.
    """

    def __init__(self, redis_url: str, key_prefix: str = "session:"):
        if redis is None:
            raise ImportError(
                "redis not installed. "
                "Install with: pip install redis"
            )

        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self._client: Optional[redis.Redis] = None

    async def _get_client(self) -> redis.Redis:
        """Get or create Redis client."""
        if self._client is None:
            self._client = await redis.from_url(self.redis_url)
            logger.info("Connected to Redis for session storage")

        return self._client

    def _make_key(self, presentation_id: str) -> str:
        """Make Redis key from presentation ID."""
        return f"{self.key_prefix}{presentation_id}"

    async def get(self, presentation_id: str) -> Optional[SessionContext]:
        """Get session from Redis."""
        client = await self._get_client()
        key = self._make_key(presentation_id)

        data = await client.get(key)
        if data is None:
            return None

        # Deserialize JSON to SessionContext
        try:
            session_dict = json.loads(data)
            return SessionContext(**session_dict)
        except Exception as e:
            logger.error(f"Error deserializing session {presentation_id}: {e}")
            return None

    async def set(
        self,
        presentation_id: str,
        session: SessionContext,
        ttl: int = 3600
    ):
        """Store session in Redis with TTL."""
        client = await self._get_client()
        key = self._make_key(presentation_id)

        # Serialize SessionContext to JSON
        session_json = session.model_dump_json()

        await client.setex(key, ttl, session_json)
        logger.debug(f"Stored session in Redis: {presentation_id} (TTL: {ttl}s)")

    async def delete(self, presentation_id: str):
        """Delete session from Redis."""
        client = await self._get_client()
        key = self._make_key(presentation_id)

        await client.delete(key)
        logger.debug(f"Deleted session from Redis: {presentation_id}")

    async def exists(self, presentation_id: str) -> bool:
        """Check if session exists in Redis."""
        client = await self._get_client()
        key = self._make_key(presentation_id)

        return await client.exists(key) > 0

    async def cleanup_expired(self):
        """Redis handles TTL expiration automatically."""
        pass


class SessionManager:
    """
    High-level session manager.

    Manages presentation sessions with automatic context retention.
    """

    def __init__(
        self,
        store: Optional[BaseSessionStore] = None,
        default_ttl: int = 3600,
        max_history: int = 5
    ):
        """
        Initialize session manager.

        Args:
            store: Storage backend (defaults to InMemorySessionStore)
            default_ttl: Default session TTL in seconds
            max_history: Maximum number of slides to keep in history
        """
        self.store = store or InMemorySessionStore()
        self.default_ttl = default_ttl
        self.max_history = max_history

        logger.info(
            f"SessionManager initialized with {self.store.__class__.__name__} "
            f"(TTL: {default_ttl}s, max_history: {max_history})"
        )

    async def get_or_create_session(
        self,
        presentation_id: str,
        presentation_theme: Optional[str] = None,
        target_audience: Optional[str] = None,
        overall_narrative: Optional[str] = None
    ) -> SessionContext:
        """
        Get existing session or create new one.

        Args:
            presentation_id: Unique presentation identifier
            presentation_theme: Presentation theme (for new sessions)
            target_audience: Target audience (for new sessions)
            overall_narrative: Overall narrative (for new sessions)

        Returns:
            SessionContext for the presentation
        """
        # Try to get existing session
        session = await self.store.get(presentation_id)

        if session is not None:
            logger.debug(f"Retrieved existing session: {presentation_id}")
            return session

        # Create new session
        session = SessionContext(
            presentation_id=presentation_id,
            presentation_theme=presentation_theme,
            target_audience=target_audience,
            overall_narrative=overall_narrative
        )

        await self.store.set(presentation_id, session, self.default_ttl)
        logger.info(f"Created new session: {presentation_id}")

        return session

    async def add_slide_to_session(
        self,
        presentation_id: str,
        slide_context: SlideContext
    ):
        """
        Add slide to session history.

        Args:
            presentation_id: Presentation identifier
            slide_context: Slide context to add
        """
        session = await self.get_or_create_session(presentation_id)

        # Add slide to history
        session.add_slide(slide_context)

        # Save updated session
        await self.store.set(presentation_id, session, self.default_ttl)
        logger.debug(
            f"Added slide {slide_context.slide_number} to session {presentation_id}"
        )

    async def get_session_context(
        self,
        presentation_id: str
    ) -> Optional[SessionContext]:
        """
        Get session context.

        Args:
            presentation_id: Presentation identifier

        Returns:
            SessionContext or None if not found
        """
        return await self.store.get(presentation_id)

    async def get_context_summary(
        self,
        presentation_id: str,
        max_slides: int = 3
    ) -> str:
        """
        Get formatted context summary for LLM prompts.

        Args:
            presentation_id: Presentation identifier
            max_slides: Maximum number of recent slides to include

        Returns:
            Formatted context string
        """
        session = await self.store.get(presentation_id)

        if session is None:
            return "This is the first slide in the presentation."

        return session.get_context_summary()

    async def delete_session(self, presentation_id: str):
        """
        Delete a session.

        Args:
            presentation_id: Presentation identifier
        """
        await self.store.delete(presentation_id)
        logger.info(f"Deleted session: {presentation_id}")

    async def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        await self.store.cleanup_expired()


# Factory function for creating session manager
def create_session_manager() -> SessionManager:
    """
    Create session manager from environment configuration.

    Environment variables:
    - USE_REDIS: Set to "true" to use Redis
    - REDIS_URL: Redis connection URL (if USE_REDIS=true)
    - SESSION_CACHE_TTL: Session TTL in seconds (default: 3600)
    - SESSION_MAX_HISTORY: Max slides in history (default: 5)

    Returns:
        Configured SessionManager instance
    """
    use_redis = os.getenv("USE_REDIS", "false").lower() == "true"
    ttl = int(os.getenv("SESSION_CACHE_TTL", "3600"))
    max_history = int(os.getenv("SESSION_MAX_HISTORY", "5"))

    if use_redis:
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            logger.warning("USE_REDIS=true but REDIS_URL not set, falling back to in-memory")
            store = InMemorySessionStore()
        else:
            store = RedisSessionStore(redis_url)
    else:
        store = InMemorySessionStore()

    return SessionManager(
        store=store,
        default_ttl=ttl,
        max_history=max_history
    )


# Singleton instance
_session_manager_instance: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """
    Get the singleton SessionManager instance.

    Returns:
        Shared SessionManager instance
    """
    global _session_manager_instance

    if _session_manager_instance is None:
        _session_manager_instance = create_session_manager()

    return _session_manager_instance


# Example usage
if __name__ == "__main__":
    async def test_session_manager():
        """Test session manager."""
        manager = get_session_manager()

        # Create a session
        session = await manager.get_or_create_session(
            presentation_id="pres_test_123",
            presentation_theme="professional",
            target_audience="executives"
        )

        print("Created session:", session.presentation_id)

        # Add slides
        for i in range(3):
            slide = SlideContext(
                slide_id=f"slide_{i+1:03d}",
                slide_number=i + 1,
                slide_title=f"Slide {i+1} Title",
                content_summary=f"Summary of slide {i+1} content",
                key_themes=["theme1", "theme2"],
                content_type="text"
            )
            await manager.add_slide_to_session("pres_test_123", slide)

        # Get context summary
        summary = await manager.get_context_summary("pres_test_123")
        print("\nContext Summary:")
        print(summary)

        # Cleanup
        await manager.delete_session("pres_test_123")
        print("\nSession deleted")

    asyncio.run(test_session_manager())
