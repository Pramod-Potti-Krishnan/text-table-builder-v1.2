"""
LLM Services for v1.2

Provides LLM client and service wrappers for element-based content generation.
Includes connection pool for concurrency control and rate limiting.
"""

from .llm_client import (
    get_llm_client,
    LLMClientFactory,
    BaseLLMClient,
    GeminiClient,
    LLMResponse,
    LLMProvider
)
from .llm_service import (
    get_llm_service,
    create_llm_callable,
    create_llm_callable_async,
    create_llm_callable_pooled,
    get_pool_metrics,
    LLMService,
    ModelComplexity
)
from .llm_pool import (
    get_llm_pool,
    LLMConnectionPool,
    LLMPoolConfig,
    QueueFullError,
    PoolStatus
)

__all__ = [
    # LLM Client
    "get_llm_client",
    "LLMClientFactory",
    "BaseLLMClient",
    "GeminiClient",
    "LLMResponse",
    "LLMProvider",
    # LLM Service
    "get_llm_service",
    "create_llm_callable",
    "create_llm_callable_async",
    "create_llm_callable_pooled",
    "get_pool_metrics",
    "LLMService",
    "ModelComplexity",
    # Connection Pool
    "get_llm_pool",
    "LLMConnectionPool",
    "LLMPoolConfig",
    "QueueFullError",
    "PoolStatus",
]
