"""
LLM Services for v1.2

Provides LLM client and service wrappers for element-based content generation.
Includes connection pool for concurrency control and rate limiting.
Also includes Theme Service client for typography tokens.
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
from .theme_service_client import (
    ThemeServiceClient,
    get_client as get_theme_client,
    get_typography,
    get_default_typography,
    get_typography_token,
    TypographyTheme,
    TypographyToken,
    ListStyleTokens,
    TextBoxDefaults,
    DEFAULT_TYPOGRAPHY_TOKENS,
    SLIDE_TEXT_TYPE_TO_LEVEL,
    FONT_CHAR_WIDTH_RATIOS
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
    # Theme Service
    "ThemeServiceClient",
    "get_theme_client",
    "get_typography",
    "get_default_typography",
    "get_typography_token",
    "TypographyTheme",
    "TypographyToken",
    "ListStyleTokens",
    "TextBoxDefaults",
    "DEFAULT_TYPOGRAPHY_TOKENS",
    "SLIDE_TEXT_TYPE_TO_LEVEL",
    "FONT_CHAR_WIDTH_RATIOS",
]
