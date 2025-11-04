"""
LLM Service Wrapper for v1.2 Element-Based Content Generation

This module provides a synchronous wrapper around the async LLM client
specifically designed for v1.2's element-based architecture.

Features:
- Synchronous interface for element generation
- Model routing (Flash for simple elements, Pro for complex)
- JSON response parsing and validation
- Retry logic for character count violations
- Token usage tracking
"""

import asyncio
import json
import logging
import os
from typing import Optional, Dict, Any, Callable
from enum import Enum

from .llm_client import get_llm_client, BaseLLMClient, LLMClientFactory

logger = logging.getLogger(__name__)


class ModelComplexity(str, Enum):
    """Element complexity levels for model routing."""
    SIMPLE = "simple"      # Flash model (fast, cheap)
    COMPLEX = "complex"    # Pro model (slower, better quality)


class LLMService:
    """
    LLM service wrapper for v1.2 element generation.

    Provides synchronous interface and handles JSON parsing, validation,
    and model routing.
    """

    def __init__(
        self,
        enable_model_routing: bool = True,
        flash_model: str = "gemini-2.0-flash-exp",
        pro_model: str = "gemini-1.5-pro",
        temperature: float = 0.7,
        max_tokens: int = 8192
    ):
        """
        Initialize LLM service.

        Args:
            enable_model_routing: Whether to use different models based on complexity
            flash_model: Model for simple elements (fast)
            pro_model: Model for complex elements (better quality)
            temperature: Sampling temperature
            max_tokens: Max output tokens
        """
        self.enable_model_routing = enable_model_routing
        self.flash_model = flash_model
        self.pro_model = pro_model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize clients
        self.flash_client = None
        self.pro_client = None

        # Create event loop for async operations
        self.loop = None

        # Usage tracking
        self.total_calls = 0
        self.flash_calls = 0
        self.pro_calls = 0
        self.total_tokens = 0

    def _get_or_create_loop(self):
        """Get or create event loop for async operations."""
        if self.loop is None or self.loop.is_closed():
            try:
                self.loop = asyncio.get_event_loop()
            except RuntimeError:
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
        return self.loop

    def _get_or_create_client(self, complexity: ModelComplexity = ModelComplexity.SIMPLE) -> BaseLLMClient:
        """
        Get or create LLM client based on complexity.

        Args:
            complexity: Element complexity level

        Returns:
            LLM client instance
        """
        if not self.enable_model_routing or complexity == ModelComplexity.SIMPLE:
            if self.flash_client is None:
                self.flash_client = LLMClientFactory.create_client(
                    provider="gemini",
                    model=self.flash_model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
            return self.flash_client
        else:
            if self.pro_client is None:
                self.pro_client = LLMClientFactory.create_client(
                    provider="gemini",
                    model=self.pro_model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
            return self.pro_client

    def _get_client(self, complexity: ModelComplexity = ModelComplexity.SIMPLE) -> BaseLLMClient:
        """
        DEPRECATED: Use _get_or_create_client instead.
        Kept for backward compatibility.
        """
        return self._get_or_create_client(complexity)

    def _determine_complexity(self, prompt: str) -> ModelComplexity:
        """
        Determine element complexity from prompt.

        Args:
            prompt: Element generation prompt

        Returns:
            Complexity level
        """
        # Simple heuristics for model routing
        complexity_indicators = {
            ModelComplexity.COMPLEX: [
                "table_row",
                "table_headers",
                "comparison_column",
                "colored_section",
                "sequential_step",
                "insights_box"
            ],
            ModelComplexity.SIMPLE: [
                "text_box",
                "metric_card",
                "quote_content"
            ]
        }

        prompt_lower = prompt.lower()

        # Check for complex indicators
        for indicator in complexity_indicators[ModelComplexity.COMPLEX]:
            if indicator in prompt_lower:
                return ModelComplexity.COMPLEX

        # Default to simple (Flash model)
        return ModelComplexity.SIMPLE

    def generate(self, prompt: str, complexity: Optional[ModelComplexity] = None) -> str:
        """
        Generate content synchronously.

        Args:
            prompt: Element generation prompt
            complexity: Optional complexity override

        Returns:
            Generated content as JSON string

        Raises:
            Exception: If generation fails
        """
        # Auto-determine complexity if not specified
        if complexity is None:
            complexity = self._determine_complexity(prompt)

        # Get appropriate client
        client = self._get_or_create_client(complexity)

        # Track usage
        self.total_calls += 1
        if complexity == ModelComplexity.SIMPLE:
            self.flash_calls += 1
        else:
            self.pro_calls += 1

        # Run async generation in sync context
        loop = self._get_or_create_loop()

        try:
            response = loop.run_until_complete(client.generate(prompt))

            # Track tokens
            self.total_tokens += response.total_tokens

            logger.info(
                f"Generated content using {client.model} "
                f"({response.total_tokens} tokens, {response.latency_ms:.0f}ms)"
            )

            return response.content

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise

    def generate_with_retry(
        self,
        prompt: str,
        max_retries: int = 2,
        complexity: Optional[ModelComplexity] = None
    ) -> str:
        """
        Generate content with retry logic.

        Args:
            prompt: Element generation prompt
            max_retries: Maximum retry attempts
            complexity: Optional complexity override

        Returns:
            Generated content as JSON string

        Raises:
            Exception: If all retries fail
        """
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                return self.generate(prompt, complexity)
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    logger.warning(f"Generation attempt {attempt + 1} failed, retrying...")
                else:
                    logger.error(f"All {max_retries + 1} attempts failed")

        raise last_error

    # ===== ASYNC METHODS (Production-Quality) =====

    async def generate_async(
        self,
        prompt: str,
        complexity: Optional[ModelComplexity] = None
    ) -> str:
        """
        Generate content asynchronously (works within FastAPI event loop).

        This is the production-quality async method that properly integrates
        with FastAPI's existing event loop without creating conflicts.

        Args:
            prompt: Element generation prompt
            complexity: Optional complexity override

        Returns:
            Generated content as JSON string

        Raises:
            Exception: If generation fails
        """
        # Auto-determine complexity if not specified
        if complexity is None:
            complexity = self._determine_complexity(prompt)

        # Get appropriate client
        client = self._get_or_create_client(complexity)

        # Track usage
        self.total_calls += 1
        if complexity == ModelComplexity.SIMPLE:
            self.flash_calls += 1
        else:
            self.pro_calls += 1

        # Call async client directly (no event loop creation needed)
        try:
            response = await client.generate(prompt)

            # Track tokens
            self.total_tokens += response.total_tokens

            logger.info(
                f"Generated content using {client.model} "
                f"({response.total_tokens} tokens, {response.latency_ms:.0f}ms)"
            )

            return response.content

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise

    async def generate_with_retry_async(
        self,
        prompt: str,
        max_retries: int = 2,
        complexity: Optional[ModelComplexity] = None
    ) -> str:
        """
        Generate content asynchronously with retry logic.

        This is the recommended method for FastAPI endpoints as it properly
        handles retries in an async context.

        Args:
            prompt: Element generation prompt
            max_retries: Maximum retry attempts
            complexity: Optional complexity override

        Returns:
            Generated content as JSON string

        Raises:
            Exception: If all retries fail
        """
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                return await self.generate_async(prompt, complexity)
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    logger.warning(f"Generation attempt {attempt + 1} failed, retrying...")
                    # Async sleep between retries
                    await asyncio.sleep(1.0 * (attempt + 1))
                else:
                    logger.error(f"All {max_retries + 1} attempts failed")

        raise last_error

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics.

        Returns:
            Dictionary with usage stats
        """
        return {
            "total_calls": self.total_calls,
            "flash_calls": self.flash_calls,
            "pro_calls": self.pro_calls,
            "total_tokens": self.total_tokens,
            "flash_percentage": (self.flash_calls / self.total_calls * 100) if self.total_calls > 0 else 0,
            "pro_percentage": (self.pro_calls / self.total_calls * 100) if self.total_calls > 0 else 0
        }

    def reset_stats(self):
        """Reset usage statistics."""
        self.total_calls = 0
        self.flash_calls = 0
        self.pro_calls = 0
        self.total_tokens = 0


# Singleton instance
_llm_service_instance: Optional[LLMService] = None


def get_llm_service(
    enable_model_routing: Optional[bool] = None,
    flash_model: Optional[str] = None,
    pro_model: Optional[str] = None
) -> LLMService:
    """
    Get singleton LLM service instance.

    Args:
        enable_model_routing: Whether to use model routing (from env if None)
        flash_model: Flash model name (from env if None)
        pro_model: Pro model name (from env if None)

    Returns:
        LLM service instance
    """
    global _llm_service_instance

    if _llm_service_instance is None:
        # Get configuration from environment
        enable_routing = enable_model_routing if enable_model_routing is not None else \
            os.getenv("ENABLE_MODEL_ROUTING", "true").lower() == "true"

        flash = flash_model or os.getenv("GEMINI_FLASH_MODEL", "gemini-2.0-flash-exp")
        pro = pro_model or os.getenv("GEMINI_PRO_MODEL", "gemini-1.5-pro")
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        max_tokens = int(os.getenv("LLM_MAX_TOKENS", "8192"))

        _llm_service_instance = LLMService(
            enable_model_routing=enable_routing,
            flash_model=flash,
            pro_model=pro,
            temperature=temperature,
            max_tokens=max_tokens
        )

        logger.info(
            f"Initialized LLM service (routing: {enable_routing}, "
            f"flash: {flash}, pro: {pro})"
        )

    return _llm_service_instance


def create_llm_callable() -> Callable[[str], str]:
    """
    Create a callable function for v1.2 ElementBasedContentGenerator.

    DEPRECATED: Use create_llm_callable_async for FastAPI endpoints.
    This sync version is kept for backward compatibility only.

    Returns:
        Callable that takes prompt string and returns content string
    """
    service = get_llm_service()

    def llm_callable(prompt: str) -> str:
        """Generate content from prompt (sync)."""
        return service.generate_with_retry(prompt)

    return llm_callable


def create_llm_callable_async():
    """
    Create an async callable function for v1.2 ElementBasedContentGenerator.

    This is the production-quality version for FastAPI endpoints that properly
    works within the existing event loop without conflicts.

    Returns:
        Async callable that takes prompt string and returns content string
    """
    service = get_llm_service()

    async def async_llm_callable(prompt: str) -> str:
        """Generate content from prompt (async)."""
        return await service.generate_with_retry_async(prompt)

    return async_llm_callable
