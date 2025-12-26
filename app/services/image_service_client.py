"""
Image Service Client for v1.2 Hero Slides with Background Images

This module provides an async client for the Image Builder v2.0 API,
specifically designed to generate 16:9 background images for hero slides.

Features:
- Async image generation with httpx
- 16:9 aspect ratio for slide backgrounds
- Context-aware prompt engineering
- Crop anchor positioning for text placement
- Retry logic with exponential backoff
- Timeout handling (20 seconds max)
- Graceful error handling

Version: 1.1.0 - Added context-aware style params and improved negative prompts
"""

import os
import logging
import asyncio
from typing import Optional, Dict, Any
from enum import Enum

try:
    import httpx
except ImportError:
    raise ImportError(
        "httpx is required for Image Service Client. "
        "Install it with: pip install httpx>=0.24.0"
    )

logger = logging.getLogger(__name__)


class SlideType(str, Enum):
    """Slide types for image generation positioning."""
    TITLE = "title"
    SECTION = "section"
    CLOSING = "closing"


class ISeriesLayoutType(str, Enum):
    """I-series layout types for portrait image generation."""
    I1 = "I1"  # Wide image left (660x1080)
    I2 = "I2"  # Wide image right (660x1080)
    I3 = "I3"  # Narrow image left (360x1080)
    I4 = "I4"  # Narrow image right (360x1080)


class ImageServiceClient:
    """
    Async client for Image Builder v2.0 API.

    Generates 16:9 background images optimized for hero slides with
    appropriate dark areas for white text overlays.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 20.0,
        max_retries: int = 2
    ):
        """
        Initialize Image Service Client.

        Args:
            base_url: Image Builder API base URL (from env if None)
            api_key: Optional API key (from env if None)
            timeout: Request timeout in seconds (default: 20)
            max_retries: Maximum retry attempts (default: 2)
        """
        self.base_url = base_url or os.getenv(
            "IMAGE_SERVICE_URL",
            "https://web-production-1b5df.up.railway.app"
        )
        self.api_key = api_key or os.getenv("IMAGE_SERVICE_API_KEY")
        self.timeout = timeout
        self.max_retries = max_retries

        # Track usage
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0

        logger.info(
            f"Initialized Image Service Client (base_url={self.base_url}, "
            f"timeout={self.timeout}s, max_retries={self.max_retries})"
        )

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers including optional API key."""
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    def _get_crop_anchor(self, slide_type: SlideType) -> str:
        """
        Get appropriate crop anchor based on slide type.

        Args:
            slide_type: Type of hero slide

        Returns:
            Crop anchor string for Image API
        """
        crop_anchors = {
            SlideType.TITLE: "left",    # Text on left
            SlideType.SECTION: "right",  # Text on right
            SlideType.CLOSING: "center"  # Text centered
        }
        return crop_anchors.get(slide_type, "center")

    async def generate_background_image(
        self,
        prompt: str,
        slide_type: SlideType,
        negative_prompt: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
        archetype: str = "photorealistic"
    ) -> Dict[str, Any]:
        """
        Generate 16:9 background image for hero slide.

        Args:
            prompt: Image description/prompt
            slide_type: Type of hero slide (affects crop anchor)
            negative_prompt: What to avoid in image
            metadata: Custom metadata to store with image
            model: Imagen model to use (default: imagen-3.0-generate-001)
                   Options:
                   - imagen-3.0-fast-generate-001 (~5s, $0.02) - fastest/cheapest
                   - imagen-3.0-generate-001 (~11s, $0.04) - standard quality
                   - imagen-3.0-generate-002 (~11s, $0.04) - high quality
            archetype: Image style archetype (default: photorealistic)
                       Options:
                       - photorealistic: Realistic photography style
                       - spot_illustration: Illustrated/cartoon style
                       - minimalist_vector_art: Minimalist vector graphics

        Returns:
            API response dict with image URLs and metadata

        Raises:
            httpx.HTTPError: If request fails after retries
            ValueError: If response is invalid
        """
        self.total_requests += 1

        # Determine crop anchor based on slide type
        crop_anchor = self._get_crop_anchor(slide_type)

        # Use provided model or default to standard quality
        image_model = model or "imagen-3.0-generate-001"

        # Build request payload
        payload = {
            "prompt": prompt,
            "aspect_ratio": "16:9",  # Native for slides (1024x576)
            "model": image_model,
            "archetype": archetype,  # Style-aware archetype
            "negative_prompt": negative_prompt or self._get_default_negative_prompt(slide_type),
            "options": {
                "remove_background": False,  # We want backgrounds
                "crop_anchor": crop_anchor,
                "store_in_cloud": True,
                "return_base64": False  # URLs only, no base64
            },
            "metadata": metadata or {}
        }

        # Add slide type to metadata
        payload["metadata"]["slide_type"] = slide_type.value

        logger.info(
            f"Generating {slide_type.value} slide background image "
            f"(crop_anchor={crop_anchor})"
        )

        # Attempt generation with retries
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/api/v2/generate",
                        json=payload,
                        headers=self._get_headers()
                    )

                    # Check HTTP status
                    response.raise_for_status()

                    # Parse response
                    result = response.json()

                    # Check API success field
                    if not result.get("success", False):
                        error_msg = result.get("error", "Unknown error")
                        raise ValueError(f"Image generation failed: {error_msg}")

                    # Validate response structure
                    if "urls" not in result or "original" not in result["urls"]:
                        raise ValueError("Invalid response: missing image URLs")

                    # Success!
                    self.successful_requests += 1

                    generation_time = result.get("metadata", {}).get("generation_time_ms", 0)
                    logger.info(
                        f"Image generated successfully in {generation_time}ms "
                        f"(attempt {attempt + 1}/{self.max_retries + 1})"
                    )

                    return result

            except (httpx.HTTPError, ValueError) as e:
                last_error = e
                logger.warning(
                    f"Image generation attempt {attempt + 1} failed: {e}"
                )

                # Exponential backoff before retry
                if attempt < self.max_retries:
                    backoff_time = 2.0 * (attempt + 1)
                    logger.info(f"Retrying in {backoff_time}s...")
                    await asyncio.sleep(backoff_time)

        # All retries exhausted
        self.failed_requests += 1
        logger.error(
            f"Image generation failed after {self.max_retries + 1} attempts: "
            f"{last_error}"
        )
        raise last_error

    async def generate_iseries_image(
        self,
        prompt: str,
        layout_type: str,
        visual_style: str = "illustrated",
        metadata: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
        archetype: Optional[str] = None,
        aspect_ratio: str = "9:16",
        style_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate portrait-oriented image for I-series layouts.

        v1.3.1: Uses per-layout aspect ratio for correct image dimensions.
        - I1: 11:18 (660×1080) - wide portrait
        - I2: 2:3 (720×1080) - standard portrait
        - I3: 1:3 (360×1080) - very narrow
        - I4: 7:18 (420×1080) - narrow

        v1.1.0: Uses context-aware style_params for improved image relevance.

        Args:
            prompt: Image description/prompt
            layout_type: I-series layout type (I1, I2, I3, I4)
            visual_style: Visual style (professional, illustrated, kids)
            metadata: Custom metadata to store with image
            model: Imagen model to use (default based on visual_style)
            archetype: Image style archetype (default based on visual_style)
            aspect_ratio: Target aspect ratio (default 9:16, can be custom)
            style_params: Context-aware style parameters (style, color_scheme, lighting, domain)

        Returns:
            API response dict with image URLs and metadata

        Raises:
            httpx.HTTPError: If request fails after retries
            ValueError: If response is invalid
        """
        self.total_requests += 1

        # v1.1.0: Use style_params if provided, otherwise fall back to visual_style defaults
        context_style = None
        context_domain = None
        if style_params:
            context_style = style_params.get("style")
            context_domain = style_params.get("domain")

        # Determine archetype from visual style if not provided
        if archetype is None:
            # v1.1.0: Context-aware archetype selection
            if context_style == "photo":
                archetype = "photorealistic"
            elif context_style == "minimal":
                archetype = "minimalist_vector_art"
            else:
                archetype_map = {
                    "professional": "photorealistic",
                    "illustrated": "spot_illustration",
                    "kids": "spot_illustration"
                }
                archetype = archetype_map.get(visual_style, "spot_illustration")

        # Determine model from visual style if not provided
        if model is None:
            # v1.1.0: Use faster model for illustrations, standard for photo
            if archetype == "photorealistic":
                model = "imagen-3.0-generate-001"  # Standard quality for photos
            else:
                model = "imagen-3.0-fast-generate-001"  # Fast for illustrations

        # v1.1.0: Build context-aware negative prompt
        negative_prompt = self._get_iseries_negative_prompt(layout_type, context_domain)

        # Build request payload with per-layout aspect ratio
        # v1.3.1: Use passed aspect_ratio instead of hardcoded 9:16
        payload = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,  # Per-layout ratio (I1: 11:18, I2: 2:3, etc.)
            "model": model,
            "archetype": archetype,
            "negative_prompt": negative_prompt,
            "options": {
                "remove_background": False,
                "crop_anchor": "center",  # Center crop for portrait
                "store_in_cloud": True,
                "return_base64": False
            },
            "metadata": metadata or {}
        }

        # Add layout info to metadata
        payload["metadata"]["layout_type"] = layout_type
        payload["metadata"]["visual_style"] = visual_style
        payload["metadata"]["aspect_ratio"] = aspect_ratio  # v1.3.1: Use actual per-layout ratio

        # v1.1.0: Add context info to metadata
        if style_params:
            payload["metadata"]["context_style"] = context_style
            payload["metadata"]["context_domain"] = context_domain

        logger.info(
            f"Generating I-series {layout_type} portrait image "
            f"(style={visual_style}, archetype={archetype}, domain={context_domain})"
        )

        # Attempt generation with retries
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/api/v2/generate",
                        json=payload,
                        headers=self._get_headers()
                    )

                    # Check HTTP status
                    response.raise_for_status()

                    # Parse response
                    result = response.json()

                    # Check API success field
                    if not result.get("success", False):
                        error_msg = result.get("error", "Unknown error")
                        raise ValueError(f"I-series image generation failed: {error_msg}")

                    # Validate response structure
                    if "urls" not in result or "original" not in result["urls"]:
                        raise ValueError("Invalid response: missing image URLs")

                    # Success!
                    self.successful_requests += 1

                    generation_time = result.get("metadata", {}).get("generation_time_ms", 0)
                    logger.info(
                        f"I-series image generated successfully in {generation_time}ms "
                        f"(layout={layout_type}, attempt {attempt + 1}/{self.max_retries + 1})"
                    )

                    return result

            except (httpx.HTTPError, ValueError) as e:
                last_error = e
                logger.warning(
                    f"I-series image generation attempt {attempt + 1} failed: {e}"
                )

                # Exponential backoff before retry
                if attempt < self.max_retries:
                    backoff_time = 2.0 * (attempt + 1)
                    logger.info(f"Retrying in {backoff_time}s...")
                    await asyncio.sleep(backoff_time)

        # All retries exhausted
        self.failed_requests += 1
        logger.error(
            f"I-series image generation failed after {self.max_retries + 1} attempts: "
            f"{last_error}"
        )
        raise last_error

    def _get_iseries_negative_prompt(
        self,
        layout_type: str,
        domain: Optional[str] = None
    ) -> str:
        """
        Get context-aware negative prompt for I-series portrait images.

        v1.1.0: Domain-aware negative prompts to avoid irrelevant imagery.

        Args:
            layout_type: I-series layout type (I1, I2, I3, I4)
            domain: Content domain (technology, business, healthcare, etc.)

        Returns:
            Negative prompt string optimized for portrait composition
        """
        # v1.1.0: Strong base negative prompts - no text, no people, clean composition
        # FIXED: "characters" is ambiguous - explicitly say "human characters, anime characters"
        base_negatives = (
            "text, words, letters, numbers, typography, labels, titles, captions, "
            "watermarks, logos, brands, signatures, writing, symbols, "
            "human faces, people, persons, humans, portraits, bodies, crowds, "
            "anime characters, cartoon people, cartoon characters, illustrated people, "
            "low quality, blurry, pixelated, noisy, distorted, cluttered, busy, "
            "horizontal composition, landscape orientation"
        )

        # v1.1.0: Domain-specific negative prompts
        domain_negatives = {
            "technology": (
                ", clipart, generic stock photo, smiling businesspeople, "
                "office workers, meeting rooms with people, handshakes, "
                "outdated technology, old computers"
            ),
            "business": (
                ", anime style, cartoon style, childish imagery, "
                "casual settings, unprofessional imagery, "
                "generic clip art, outdated graphics"
            ),
            "healthcare": (
                ", graphic surgery, blood, patients in distress, "
                "scary medical imagery, needles close-up, "
                "hospital beds with patients"
            ),
            "education": (
                ", boring lecture halls, outdated classrooms, "
                "generic school clipart, childish cartoons for adult education"
            ),
            "science": (
                ", mad scientist tropes, dangerous experiments, "
                "unrealistic sci-fi, generic science clipart"
            ),
            "nature": (
                ", environmental damage, pollution, deforestation, "
                "dying animals, climate disaster imagery"
            ),
            "creative": (
                ", corporate sterility, generic stock photos, "
                "boring office settings, uncreative imagery"
            )
        }

        # Get domain-specific additions
        domain_addition = domain_negatives.get(domain, "")

        return base_negatives + domain_addition

    def _get_default_negative_prompt(self, slide_type: SlideType) -> str:
        """
        Get default negative prompt based on slide type.

        Args:
            slide_type: Type of hero slide

        Returns:
            Negative prompt string
        """
        # STRONG negative prompts - absolutely no text or people
        common = ("text, words, letters, numbers, typography, labels, titles, captions, "
                 "watermarks, logos, brands, signatures, writing, characters, symbols, "
                 "people, faces, persons, humans, portraits, bodies, crowds, "
                 "low quality, blurry, pixelated, noisy, distorted, cluttered, busy")

        # Type-specific additions
        type_specific = {
            SlideType.TITLE: ", bright left side, busy left area, distracting left elements",
            SlideType.SECTION: ", bright right side, busy right area, distracting right elements",
            SlideType.CLOSING: ", bright center, busy foreground, distracting central elements"
        }

        return common + type_specific.get(slide_type, "")

    async def health_check(self) -> Dict[str, Any]:
        """
        Check Image Service health.

        Returns:
            Health check response dict

        Raises:
            httpx.HTTPError: If health check fails
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/v2/health",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Image Service health check failed: {e}")
            raise

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics.

        Returns:
            Dictionary with usage stats
        """
        success_rate = (
            (self.successful_requests / self.total_requests * 100)
            if self.total_requests > 0 else 0
        )

        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": f"{success_rate:.1f}%"
        }

    def reset_stats(self):
        """Reset usage statistics."""
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0


# Singleton instance
_image_service_client_instance: Optional[ImageServiceClient] = None


def get_image_service_client(
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: Optional[float] = None
) -> ImageServiceClient:
    """
    Get singleton Image Service Client instance.

    Args:
        base_url: Image Builder API base URL (from env if None)
        api_key: Optional API key (from env if None)
        timeout: Request timeout in seconds (from env if None)

    Returns:
        ImageServiceClient instance
    """
    global _image_service_client_instance

    if _image_service_client_instance is None:
        # Get configuration from environment
        url = base_url or os.getenv(
            "IMAGE_SERVICE_URL",
            "https://web-production-1b5df.up.railway.app"
        )
        key = api_key or os.getenv("IMAGE_SERVICE_API_KEY")
        timeout_val = timeout or float(os.getenv("IMAGE_SERVICE_TIMEOUT", "20.0"))

        _image_service_client_instance = ImageServiceClient(
            base_url=url,
            api_key=key,
            timeout=timeout_val
        )

        logger.info("Created Image Service Client singleton instance")

    return _image_service_client_instance
