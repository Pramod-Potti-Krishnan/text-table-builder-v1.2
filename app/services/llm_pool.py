"""
LLM Connection Pool with Concurrency Control and Rate Limiting
==============================================================

Manages concurrent LLM requests with:
- Semaphore-based concurrency control (prevents overload)
- Rate limiting (respects Vertex AI API quotas)
- Request queue with overflow protection
- Timeout handling per request
- Status monitoring for observability
"""

import asyncio
import time
import logging
from typing import Optional, Callable, Any
from dataclasses import dataclass, field
from collections import deque
from enum import Enum

logger = logging.getLogger(__name__)


class PoolStatus(str, Enum):
    """Pool operational status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"  # High utilization
    OVERLOADED = "overloaded"  # Queue full


@dataclass
class LLMPoolConfig:
    """
    Configuration for LLM Connection Pool.

    Attributes:
        max_concurrent: Maximum parallel LLM calls (default: 10)
        max_queue_size: Maximum pending requests before rejection (default: 50)
        timeout_seconds: Per-request timeout (default: 120s)
        rate_limit_rpm: Requests per minute limit (Vertex AI: ~300 RPM)
        warning_threshold: Queue depth that triggers degraded status (default: 0.7)
    """
    max_concurrent: int = 10
    max_queue_size: int = 50
    timeout_seconds: float = 120.0
    rate_limit_rpm: int = 300
    warning_threshold: float = 0.7  # 70% of max_queue_size


@dataclass
class PoolMetrics:
    """Real-time pool metrics for monitoring."""
    active_requests: int = 0
    queued_requests: int = 0
    requests_last_minute: int = 0
    total_requests: int = 0
    total_successes: int = 0
    total_failures: int = 0
    total_timeouts: int = 0
    total_rejections: int = 0
    avg_latency_ms: float = 0.0
    last_request_time: Optional[float] = None


class QueueFullError(Exception):
    """Raised when the LLM request queue is at capacity."""
    pass


class RateLimitError(Exception):
    """Raised when rate limit is exceeded and cannot wait."""
    pass


class LLMConnectionPool:
    """
    Manages concurrent LLM requests with rate limiting.

    Features:
    - Semaphore-based concurrency control
    - Request queue with overflow protection
    - Rate limiting to respect API quotas
    - Timeout handling per request
    - Real-time metrics for monitoring

    Usage:
        pool = LLMConnectionPool(LLMPoolConfig(max_concurrent=10))
        result = await pool.execute(llm_client.generate, prompt)
    """

    def __init__(self, config: Optional[LLMPoolConfig] = None):
        """
        Initialize the connection pool.

        Args:
            config: Pool configuration. Uses defaults if not provided.
        """
        self.config = config or LLMPoolConfig()
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent)
        self._request_times: deque = deque()  # For rate limiting
        self._lock = asyncio.Lock()
        self._metrics = PoolMetrics()
        self._latencies: deque = deque(maxlen=100)  # Rolling window for avg

        logger.info(
            f"LLM Pool initialized: max_concurrent={self.config.max_concurrent}, "
            f"max_queue={self.config.max_queue_size}, "
            f"rate_limit={self.config.rate_limit_rpm} RPM"
        )

    async def execute(
        self,
        llm_callable: Callable,
        prompt: str,
        timeout: Optional[float] = None
    ) -> Any:
        """
        Execute an LLM request through the pool.

        Args:
            llm_callable: Async callable that takes prompt and returns result
            prompt: The prompt to send to the LLM
            timeout: Optional per-request timeout (uses config default if not set)

        Returns:
            Result from the LLM callable

        Raises:
            QueueFullError: If queue is at capacity
            asyncio.TimeoutError: If request times out
            Exception: Any exception from the LLM callable
        """
        timeout = timeout or self.config.timeout_seconds

        # Check if we can accept this request
        await self._check_capacity()

        # Wait for rate limit if needed
        await self._wait_for_rate_limit()

        # Track request
        async with self._lock:
            self._metrics.queued_requests += 1
            self._metrics.total_requests += 1

        start_time = time.time()

        try:
            # Acquire semaphore slot (blocks if all slots busy)
            async with self._semaphore:
                async with self._lock:
                    self._metrics.queued_requests -= 1
                    self._metrics.active_requests += 1
                    self._request_times.append(time.time())

                # Log pool state
                print(
                    f"[LLM-POOL] Executing: active={self._metrics.active_requests}, "
                    f"queued={self._metrics.queued_requests}"
                )

                try:
                    # Execute with timeout
                    result = await asyncio.wait_for(
                        llm_callable(prompt),
                        timeout=timeout
                    )

                    # Record success
                    latency_ms = (time.time() - start_time) * 1000
                    async with self._lock:
                        self._metrics.total_successes += 1
                        self._metrics.last_request_time = time.time()
                        self._latencies.append(latency_ms)
                        self._metrics.avg_latency_ms = sum(self._latencies) / len(self._latencies)

                    print(f"[LLM-POOL] Success: latency={latency_ms:.0f}ms")
                    return result

                except asyncio.TimeoutError:
                    async with self._lock:
                        self._metrics.total_timeouts += 1
                    print(f"[LLM-POOL] Timeout after {timeout}s")
                    raise

                except Exception as e:
                    async with self._lock:
                        self._metrics.total_failures += 1
                    print(f"[LLM-POOL] Error: {str(e)[:100]}")
                    raise

                finally:
                    async with self._lock:
                        self._metrics.active_requests -= 1

        except QueueFullError:
            async with self._lock:
                self._metrics.queued_requests -= 1
                self._metrics.total_rejections += 1
            raise

    async def _check_capacity(self):
        """Check if pool can accept more requests."""
        async with self._lock:
            current_pending = self._metrics.queued_requests + self._metrics.active_requests

        if current_pending >= self.config.max_queue_size:
            raise QueueFullError(
                f"LLM pool at capacity ({self.config.max_queue_size} requests). "
                "Try again later."
            )

    async def _wait_for_rate_limit(self):
        """Wait if we're exceeding rate limits."""
        async with self._lock:
            now = time.time()

            # Remove requests older than 60 seconds
            while self._request_times and now - self._request_times[0] > 60:
                self._request_times.popleft()

            self._metrics.requests_last_minute = len(self._request_times)

            # If at limit, wait for oldest request to age out
            if len(self._request_times) >= self.config.rate_limit_rpm:
                wait_time = 60 - (now - self._request_times[0])
                if wait_time > 0:
                    print(f"[LLM-POOL] Rate limit: waiting {wait_time:.1f}s")
                    # Release lock while waiting
                    self._lock.release()
                    try:
                        await asyncio.sleep(wait_time)
                    finally:
                        await self._lock.acquire()

    @property
    def status(self) -> PoolStatus:
        """Get current pool status."""
        utilization = (self._metrics.queued_requests + self._metrics.active_requests) / self.config.max_queue_size

        if utilization >= 1.0:
            return PoolStatus.OVERLOADED
        elif utilization >= self.config.warning_threshold:
            return PoolStatus.DEGRADED
        return PoolStatus.HEALTHY

    @property
    def metrics(self) -> dict:
        """Get current pool metrics for monitoring."""
        return {
            "status": self.status.value,
            "active_requests": self._metrics.active_requests,
            "queued_requests": self._metrics.queued_requests,
            "requests_last_minute": self._metrics.requests_last_minute,
            "total_requests": self._metrics.total_requests,
            "total_successes": self._metrics.total_successes,
            "total_failures": self._metrics.total_failures,
            "total_timeouts": self._metrics.total_timeouts,
            "total_rejections": self._metrics.total_rejections,
            "avg_latency_ms": round(self._metrics.avg_latency_ms, 2),
            "config": {
                "max_concurrent": self.config.max_concurrent,
                "max_queue_size": self.config.max_queue_size,
                "timeout_seconds": self.config.timeout_seconds,
                "rate_limit_rpm": self.config.rate_limit_rpm
            }
        }

    def reset_metrics(self):
        """Reset metrics (useful for testing)."""
        self._metrics = PoolMetrics()
        self._latencies.clear()
        self._request_times.clear()


# Global pool instance (singleton pattern)
_pool_instance: Optional[LLMConnectionPool] = None


def get_llm_pool(config: Optional[LLMPoolConfig] = None) -> LLMConnectionPool:
    """
    Get the singleton LLM pool instance.

    Creates pool on first call with provided config or defaults.
    Subsequent calls return the same instance.

    Args:
        config: Optional pool configuration (only used on first call)

    Returns:
        Shared LLM pool instance
    """
    global _pool_instance

    if _pool_instance is None:
        # Read config from environment if not provided
        if config is None:
            import os
            config = LLMPoolConfig(
                max_concurrent=int(os.getenv("LLM_MAX_CONCURRENT", "10")),
                max_queue_size=int(os.getenv("LLM_MAX_QUEUE_SIZE", "50")),
                timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "120")),
                rate_limit_rpm=int(os.getenv("LLM_RATE_LIMIT_RPM", "300"))
            )
        _pool_instance = LLMConnectionPool(config)

    return _pool_instance


def reset_pool():
    """Reset the global pool instance (for testing)."""
    global _pool_instance
    _pool_instance = None
