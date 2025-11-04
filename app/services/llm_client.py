"""
LLM Client for Text and Table Generation
========================================

Multi-provider LLM client supporting Gemini, OpenAI, and Anthropic.
"""

import os
import time
import logging
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

# Provider SDKs
# v3.3 Security Update: Using Vertex AI SDK (google-cloud-aiplatform) instead of
# the old google-generativeai SDK. Vertex AI provides secure ADC authentication.

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

try:
    from anthropic import AsyncAnthropic
except ImportError:
    AsyncAnthropic = None


logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class LLMResponse:
    """
    Standardized LLM response.

    Tracks content, usage metrics, and metadata.
    """
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    model: str = ""
    provider: str = ""
    latency_ms: float = 0.0
    finish_reason: str = ""
    raw_response: Optional[Any] = None


class BaseLLMClient(ABC):
    """
    Abstract base class for LLM clients.

    All provider-specific clients inherit from this.
    """

    def __init__(
        self,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 60000,
        **kwargs
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.kwargs = kwargs

    @abstractmethod
    async def generate(self, prompt: str) -> LLMResponse:
        """
        Generate content from prompt.

        Args:
            prompt: System prompt + user input

        Returns:
            LLMResponse with generated content and metrics
        """
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if provider is properly configured (API keys, etc.)."""
        pass


class GeminiClient(BaseLLMClient):
    """
    Google Gemini LLM client using Vertex AI.

    v3.3 Security Update: Uses service account authentication instead of API keys.
    """

    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        **kwargs
    ):
        super().__init__(model, **kwargs)

        # Import Vertex AI dependencies
        try:
            import vertexai
            from google.oauth2 import service_account
            from vertexai.preview.generative_models import GenerativeModel, GenerationConfig
        except ImportError:
            raise ImportError(
                "Vertex AI not installed. "
                "Install with: pip install google-cloud-aiplatform>=1.70.0"
            )

        # Initialize Vertex AI with service account credentials
        service_account_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
        project_id = os.getenv("GCP_PROJECT_ID")
        location = os.getenv("GCP_LOCATION", "us-central1")

        if not project_id:
            raise ValueError("GCP_PROJECT_ID environment variable required")

        try:
            if service_account_json:
                # Railway/Production: Use service account JSON from environment
                import json
                credentials_dict = json.loads(service_account_json)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_dict,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )

                vertexai.init(
                    project=project_id,
                    location=location,
                    credentials=credentials
                )
                logger.info(f"Initialized Vertex AI with service account (project: {project_id})")
            else:
                # Local development: Use Application Default Credentials
                vertexai.init(
                    project=project_id,
                    location=location
                )
                logger.info(f"Initialized Vertex AI with ADC (project: {project_id})")

            # Create Gemini model instance
            self.client = GenerativeModel(self.model)
            logger.info(f"Initialized Gemini model: {self.model}")

        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            raise ValueError(f"Vertex AI initialization failed: {e}")

    async def generate(self, prompt: str) -> LLMResponse:
        """Generate content using Gemini via Vertex AI."""
        start_time = time.time()

        try:
            # Import GenerationConfig
            from vertexai.preview.generative_models import GenerationConfig

            generation_config = GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )

            # Generate content
            response = self.client.generate_content(
                prompt,
                generation_config=generation_config
            )

            latency_ms = (time.time() - start_time) * 1000

            # Extract content and token usage
            content = response.text if hasattr(response, 'text') else str(response)

            # Token usage (if available)
            prompt_tokens = 0
            completion_tokens = 0
            if hasattr(response, 'usage_metadata'):
                prompt_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
                completion_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)

            return LLMResponse(
                content=content,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                model=self.model,
                provider="gemini-vertex",
                latency_ms=latency_ms,
                finish_reason="",
                raw_response=response
            )

        except Exception as e:
            logger.error(f"Gemini Vertex AI generation error: {e}")
            raise

    def is_configured(self) -> bool:
        """Check if Gemini Vertex AI is configured."""
        return os.getenv("GCP_PROJECT_ID") is not None


class OpenAIClient(BaseLLMClient):
    """
    OpenAI LLM client.

    Uses openai SDK with async support.
    """

    def __init__(
        self,
        model: str = "gpt-4-turbo-preview",
        api_key: Optional[str] = None,
        **kwargs
    ):
        super().__init__(model, **kwargs)

        if AsyncOpenAI is None:
            raise ImportError(
                "openai not installed. "
                "Install with: pip install openai"
            )

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not provided")

        self.client = AsyncOpenAI(api_key=self.api_key)

        logger.info(f"Initialized OpenAI client with model: {self.model}")

    async def generate(self, prompt: str) -> LLMResponse:
        """Generate content using OpenAI."""
        start_time = time.time()

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional presentation content generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            latency_ms = (time.time() - start_time) * 1000

            choice = response.choices[0]
            usage = response.usage

            return LLMResponse(
                content=choice.message.content,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                model=self.model,
                provider="openai",
                latency_ms=latency_ms,
                finish_reason=choice.finish_reason,
                raw_response=response
            )

        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise

    def is_configured(self) -> bool:
        """Check if OpenAI is configured."""
        return self.api_key is not None and AsyncOpenAI is not None


class AnthropicClient(BaseLLMClient):
    """
    Anthropic Claude LLM client.

    Uses anthropic SDK with async support.
    """

    def __init__(
        self,
        model: str = "claude-3-sonnet-20240229",
        api_key: Optional[str] = None,
        **kwargs
    ):
        super().__init__(model, **kwargs)

        if AsyncAnthropic is None:
            raise ImportError(
                "anthropic not installed. "
                "Install with: pip install anthropic"
            )

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not provided")

        self.client = AsyncAnthropic(api_key=self.api_key)

        logger.info(f"Initialized Anthropic client with model: {self.model}")

    async def generate(self, prompt: str) -> LLMResponse:
        """Generate content using Anthropic Claude."""
        start_time = time.time()

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            latency_ms = (time.time() - start_time) * 1000

            # Extract content from response
            content = response.content[0].text if response.content else ""

            return LLMResponse(
                content=content,
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens,
                model=self.model,
                provider="anthropic",
                latency_ms=latency_ms,
                finish_reason=response.stop_reason,
                raw_response=response
            )

        except Exception as e:
            logger.error(f"Anthropic generation error: {e}")
            raise

    def is_configured(self) -> bool:
        """Check if Anthropic is configured."""
        return self.api_key is not None and AsyncAnthropic is not None


class LLMClientFactory:
    """
    Factory for creating LLM clients.

    Automatically selects provider based on configuration.
    """

    @staticmethod
    def create_client(
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 60000,
        **kwargs
    ) -> BaseLLMClient:
        """
        Create an LLM client.

        Args:
            provider: Provider name (gemini, openai, anthropic).
                     If None, reads from LLM_PROVIDER env var.
            model: Model name. If None, reads from LLM_MODEL env var.
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific arguments

        Returns:
            Configured LLM client

        Raises:
            ValueError: If provider is invalid or not configured
        """
        # Get provider from env if not specified
        provider = provider or os.getenv("LLM_PROVIDER", "gemini")
        provider = provider.lower()

        # Get provider-specific defaults
        if provider == "gemini":
            model = model or os.getenv("LLM_MODEL", "gemini-2.0-flash-exp")
            return GeminiClient(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

        elif provider == "openai":
            model = model or os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
            return OpenAIClient(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

        elif provider == "anthropic":
            model = model or os.getenv("LLM_MODEL", "claude-3-sonnet-20240229")
            return AnthropicClient(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

        else:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Supported: {[p.value for p in LLMProvider]}"
            )

    @staticmethod
    def get_available_providers() -> List[str]:
        """
        Get list of available (properly configured) providers.

        Returns:
            List of provider names
        """
        available = []

        # Check Gemini (v3.3: Vertex AI with service account or ADC)
        if os.getenv("GCP_PROJECT_ID"):
            available.append("gemini")

        # Check OpenAI
        if AsyncOpenAI is not None and os.getenv("OPENAI_API_KEY"):
            available.append("openai")

        # Check Anthropic
        if AsyncAnthropic is not None and os.getenv("ANTHROPIC_API_KEY"):
            available.append("anthropic")

        return available


# Singleton instance for application-wide use
_llm_client_instance: Optional[BaseLLMClient] = None


def get_llm_client() -> BaseLLMClient:
    """
    Get the singleton LLM client instance.

    Configured from environment variables:
    - LLM_PROVIDER: gemini, openai, or anthropic
    - LLM_MODEL: Provider-specific model name
    - LLM_TEMPERATURE: Sampling temperature (default: 0.7)
    - LLM_MAX_TOKENS: Max output tokens (default: 60000)

    Returns:
        Shared LLM client instance
    """
    global _llm_client_instance

    if _llm_client_instance is None:
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        max_tokens = int(os.getenv("LLM_MAX_TOKENS", "60000"))

        _llm_client_instance = LLMClientFactory.create_client(
            temperature=temperature,
            max_tokens=max_tokens
        )

    return _llm_client_instance


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_client():
        """Test LLM client."""
        print("Available providers:", LLMClientFactory.get_available_providers())

        client = get_llm_client()
        print(f"Using provider: {client.__class__.__name__}")

        test_prompt = "Generate a brief professional summary about Q3 revenue growth."

        response = await client.generate(test_prompt)

        print("\n" + "="*80)
        print("LLM RESPONSE:")
        print("="*80)
        print(f"Content: {response.content[:200]}...")
        print(f"Model: {response.model}")
        print(f"Provider: {response.provider}")
        print(f"Tokens: {response.total_tokens} (prompt: {response.prompt_tokens}, completion: {response.completion_tokens})")
        print(f"Latency: {response.latency_ms:.2f}ms")

    asyncio.run(test_client())
