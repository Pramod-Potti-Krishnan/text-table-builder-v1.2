"""
Theme Service Client for Text Service v1.2

This module provides an async client for fetching typography tokens from
the Layout Service Theme Service. When the Theme Service is unavailable,
it provides sensible default typography tokens.

Features:
- Async typography token fetching with httpx
- Default typography tokens for all typography levels (h1-h4, body, subtitle, caption)
- List/bullet styling defaults
- Text box styling defaults
- Character width ratios for font-aware calculations
- Graceful fallback when Theme Service is unavailable
- Caching of typography tokens to reduce API calls
"""

import os
import logging
import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict

try:
    import httpx
except ImportError:
    raise ImportError(
        "httpx is required for Theme Service Client. "
        "Install it with: pip install httpx>=0.24.0"
    )

logger = logging.getLogger(__name__)


# =============================================================================
# Typography Data Classes
# =============================================================================

@dataclass
class TypographyToken:
    """Typography token for a specific text level."""
    size: int  # Font size in pixels
    weight: int  # Font weight (100-900)
    line_height: float  # Line height multiplier
    color: str  # Text color (hex)
    letter_spacing: str = "0"  # Letter spacing (CSS value)
    text_transform: Optional[str] = None  # CSS text-transform

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ListStyleTokens:
    """List/bullet styling tokens."""
    bullet_type: str = "disc"
    bullet_color: str = "#1e40af"  # Theme primary
    bullet_size: str = "0.4em"
    list_indent: str = "1.5em"
    item_spacing: str = "0.5em"
    numbered_style: str = "decimal"
    nested_indent: str = "1.5em"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TextBoxDefaults:
    """Text box styling defaults."""
    background: str = "transparent"
    background_gradient: Optional[str] = None
    border_width: str = "0px"
    border_color: str = "transparent"
    border_radius: str = "8px"
    padding: str = "16px"
    box_shadow: str = "none"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TypographyTheme:
    """Complete typography theme data."""
    theme_id: str
    font_family: str
    font_family_heading: str
    tokens: Dict[str, TypographyToken]
    list_styles: ListStyleTokens
    textbox_defaults: TextBoxDefaults
    char_width_ratio: float = 0.5

    def get_token(self, level: str) -> TypographyToken:
        """Get typography token for a specific level."""
        return self.tokens.get(level, self.tokens["body"])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "theme_id": self.theme_id,
            "font_family": self.font_family,
            "font_family_heading": self.font_family_heading,
            "tokens": {k: v.to_dict() for k, v in self.tokens.items()},
            "list_styles": self.list_styles.to_dict(),
            "textbox_defaults": self.textbox_defaults.to_dict(),
            "char_width_ratio": self.char_width_ratio
        }


# =============================================================================
# Default Typography Tokens
# =============================================================================

# Default typography tokens (Corporate Blue theme defaults)
DEFAULT_TYPOGRAPHY_TOKENS = {
    "h1": TypographyToken(
        size=72,
        weight=700,
        line_height=1.2,
        color="#1f2937",
        letter_spacing="-0.02em"
    ),
    "h2": TypographyToken(
        size=48,
        weight=600,
        line_height=1.3,
        color="#1f2937",
        letter_spacing="-0.01em"
    ),
    "h3": TypographyToken(
        size=32,
        weight=600,
        line_height=1.4,
        color="#1f2937"
    ),
    "h4": TypographyToken(
        size=24,
        weight=600,
        line_height=1.4,
        color="#374151"
    ),
    "body": TypographyToken(
        size=20,
        weight=400,
        line_height=1.6,
        color="#374151"
    ),
    "subtitle": TypographyToken(
        size=28,
        weight=400,
        line_height=1.5,
        color="#6b7280"
    ),
    "caption": TypographyToken(
        size=16,
        weight=400,
        line_height=1.4,
        color="#9ca3af",
        letter_spacing="0.01em"
    ),
    "emphasis": TypographyToken(
        size=20,
        weight=600,
        line_height=1.6,
        color="#1f2937"
    )
}

# Character width ratios for common fonts
FONT_CHAR_WIDTH_RATIOS = {
    "poppins": 0.50,
    "inter": 0.48,
    "roboto": 0.47,
    "open sans": 0.49,
    "montserrat": 0.52,
    "lato": 0.47,
    "default": 0.50
}

# Mapping from SlideTextType to typography level
SLIDE_TEXT_TYPE_TO_LEVEL = {
    "slide_title": "h2",
    "slide_subtitle": "subtitle",
    "title_slide_title": "h1",
    "title_slide_subtitle": "subtitle",
    "title_slide_content": "body",
    "section_title": "h1",
    "section_subtitle": "subtitle",
    "closing_title": "h1",
    "closing_subtitle": "subtitle",
    "closing_content": "body",
    "body_text": "body",
    "caption": "caption"
}


# =============================================================================
# Theme Service Client
# =============================================================================

class ThemeServiceClient:
    """
    Async client for Theme Service typography tokens.

    Fetches typography configuration from the Layout Service Theme Service,
    with intelligent fallback to default tokens when unavailable.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = 5.0,
        cache_ttl: int = 300  # 5 minutes cache
    ):
        """
        Initialize Theme Service Client.

        Args:
            base_url: Theme Service API base URL (from env if None)
            timeout: Request timeout in seconds (default: 5)
            cache_ttl: Cache time-to-live in seconds (default: 300)
        """
        self.base_url = base_url or os.getenv(
            "THEME_SERVICE_URL",
            os.getenv("LAYOUT_SERVICE_URL", "http://localhost:8080")
        )
        self.timeout = timeout
        self.cache_ttl = cache_ttl

        # Token cache: theme_id -> (timestamp, TypographyTheme)
        self._cache: Dict[str, tuple] = {}

        # Track usage
        self.total_requests = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.fallback_count = 0

        logger.info(
            f"Initialized Theme Service Client (base_url={self.base_url}, "
            f"timeout={self.timeout}s, cache_ttl={self.cache_ttl}s)"
        )

    def _get_default_theme(self, theme_id: str = "corporate-blue") -> TypographyTheme:
        """
        Get default typography theme.

        Returns:
            TypographyTheme with default tokens
        """
        return TypographyTheme(
            theme_id=theme_id,
            font_family="Poppins, sans-serif",
            font_family_heading="Poppins, sans-serif",
            tokens=DEFAULT_TYPOGRAPHY_TOKENS.copy(),
            list_styles=ListStyleTokens(),
            textbox_defaults=TextBoxDefaults(),
            char_width_ratio=0.5
        )

    def _parse_theme_response(self, data: Dict[str, Any], theme_id: str) -> TypographyTheme:
        """
        Parse Theme Service response into TypographyTheme.

        Args:
            data: Response data from Theme Service
            theme_id: Theme ID for reference

        Returns:
            Parsed TypographyTheme
        """
        tokens = {}
        raw_tokens = data.get("tokens", {})

        for level in ["h1", "h2", "h3", "h4", "body", "subtitle", "caption", "emphasis"]:
            if level in raw_tokens:
                t = raw_tokens[level]
                tokens[level] = TypographyToken(
                    size=int(str(t.get("size", "20")).replace("px", "")),
                    weight=t.get("weight", 400),
                    line_height=t.get("line_height", 1.6),
                    color=t.get("color", "#374151"),
                    letter_spacing=t.get("letter_spacing", "0"),
                    text_transform=t.get("text_transform")
                )
            else:
                # Use default token for missing levels
                tokens[level] = DEFAULT_TYPOGRAPHY_TOKENS.get(level, DEFAULT_TYPOGRAPHY_TOKENS["body"])

        # Parse list styles
        raw_list = data.get("list_styles", {})
        list_styles = ListStyleTokens(
            bullet_type=raw_list.get("bullet_type", "disc"),
            bullet_color=raw_list.get("bullet_color", "#1e40af"),
            bullet_size=raw_list.get("bullet_size", "0.4em"),
            list_indent=raw_list.get("list_indent", "1.5em"),
            item_spacing=raw_list.get("item_spacing", "0.5em"),
            numbered_style=raw_list.get("numbered_style", "decimal"),
            nested_indent=raw_list.get("nested_indent", "1.5em")
        )

        # Parse textbox defaults
        raw_tb = data.get("textbox_defaults", {})
        textbox_defaults = TextBoxDefaults(
            background=raw_tb.get("background", "transparent"),
            background_gradient=raw_tb.get("background_gradient"),
            border_width=raw_tb.get("border_width", "0px"),
            border_color=raw_tb.get("border_color", "transparent"),
            border_radius=raw_tb.get("border_radius", "8px"),
            padding=raw_tb.get("padding", "16px"),
            box_shadow=raw_tb.get("box_shadow", "none")
        )

        # Get char width ratio
        font_family = data.get("font_family", "Poppins, sans-serif").lower()
        char_ratio = data.get("char_width_ratio")
        if char_ratio is None:
            # Try to match font family
            for font, ratio in FONT_CHAR_WIDTH_RATIOS.items():
                if font in font_family:
                    char_ratio = ratio
                    break
            if char_ratio is None:
                char_ratio = FONT_CHAR_WIDTH_RATIOS["default"]

        return TypographyTheme(
            theme_id=theme_id,
            font_family=data.get("font_family", "Poppins, sans-serif"),
            font_family_heading=data.get("font_family_heading", data.get("font_family", "Poppins, sans-serif")),
            tokens=tokens,
            list_styles=list_styles,
            textbox_defaults=textbox_defaults,
            char_width_ratio=char_ratio
        )

    def _is_cache_valid(self, theme_id: str) -> bool:
        """Check if cached theme is still valid."""
        if theme_id not in self._cache:
            return False
        import time
        timestamp, _ = self._cache[theme_id]
        return (time.time() - timestamp) < self.cache_ttl

    def _get_from_cache(self, theme_id: str) -> Optional[TypographyTheme]:
        """Get theme from cache if valid."""
        if self._is_cache_valid(theme_id):
            self.cache_hits += 1
            _, theme = self._cache[theme_id]
            return theme
        self.cache_misses += 1
        return None

    def _set_cache(self, theme_id: str, theme: TypographyTheme):
        """Set theme in cache."""
        import time
        self._cache[theme_id] = (time.time(), theme)

    async def get_typography(
        self,
        theme_id: Optional[str] = None,
        use_cache: bool = True
    ) -> TypographyTheme:
        """
        Get typography tokens for a theme.

        Args:
            theme_id: Theme ID to fetch (uses default if None)
            use_cache: Whether to use cached tokens (default: True)

        Returns:
            TypographyTheme with all typography tokens
        """
        self.total_requests += 1
        theme_id = theme_id or "corporate-blue"

        # Check cache first
        if use_cache:
            cached = self._get_from_cache(theme_id)
            if cached:
                logger.debug(f"Using cached typography for theme: {theme_id}")
                return cached

        # Try to fetch from Theme Service
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/api/themes/{theme_id}/typography"
                logger.debug(f"Fetching typography from: {url}")

                response = await client.get(url)

                if response.status_code == 200:
                    data = response.json()
                    theme = self._parse_theme_response(data, theme_id)
                    self._set_cache(theme_id, theme)
                    logger.info(f"Fetched typography from Theme Service for: {theme_id}")
                    return theme
                else:
                    logger.warning(
                        f"Theme Service returned {response.status_code} for {theme_id}, "
                        "using defaults"
                    )
                    self.fallback_count += 1
                    return self._get_default_theme(theme_id)

        except httpx.TimeoutException:
            logger.warning(f"Theme Service timeout for {theme_id}, using defaults")
            self.fallback_count += 1
            return self._get_default_theme(theme_id)

        except httpx.ConnectError:
            logger.warning(f"Theme Service unavailable for {theme_id}, using defaults")
            self.fallback_count += 1
            return self._get_default_theme(theme_id)

        except Exception as e:
            logger.error(f"Error fetching typography for {theme_id}: {e}")
            self.fallback_count += 1
            return self._get_default_theme(theme_id)

    def get_typography_sync(
        self,
        theme_id: Optional[str] = None,
        use_cache: bool = True
    ) -> TypographyTheme:
        """
        Synchronous version of get_typography.

        Uses asyncio.run() for synchronous contexts.
        """
        return asyncio.run(self.get_typography(theme_id, use_cache))

    def get_typography_for_text_type(
        self,
        text_type: str,
        theme: TypographyTheme
    ) -> TypographyToken:
        """
        Get typography token for a specific slide text type.

        Args:
            text_type: Slide text type (e.g., 'slide_title', 'body_text')
            theme: Typography theme to use

        Returns:
            TypographyToken for the text type
        """
        level = SLIDE_TEXT_TYPE_TO_LEVEL.get(text_type, "body")
        return theme.get_token(level)

    def get_char_width_ratio(self, font_family: str) -> float:
        """
        Get character width ratio for a font family.

        Args:
            font_family: CSS font-family value

        Returns:
            Character width ratio (avg char width / font size)
        """
        font_lower = font_family.lower()
        for font, ratio in FONT_CHAR_WIDTH_RATIOS.items():
            if font in font_lower:
                return ratio
        return FONT_CHAR_WIDTH_RATIOS["default"]

    def get_stats(self) -> Dict[str, Any]:
        """Get client usage statistics."""
        return {
            "total_requests": self.total_requests,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "fallback_count": self.fallback_count,
            "cache_hit_rate": (
                self.cache_hits / max(self.cache_hits + self.cache_misses, 1)
            ) * 100,
            "cached_themes": list(self._cache.keys())
        }

    def clear_cache(self):
        """Clear the theme cache."""
        self._cache.clear()
        logger.info("Theme cache cleared")


# =============================================================================
# Module-level convenience functions
# =============================================================================

# Singleton client instance
_client: Optional[ThemeServiceClient] = None


def get_client() -> ThemeServiceClient:
    """Get or create singleton Theme Service Client."""
    global _client
    if _client is None:
        _client = ThemeServiceClient()
    return _client


async def get_typography(theme_id: Optional[str] = None) -> TypographyTheme:
    """
    Convenience function to get typography tokens.

    Args:
        theme_id: Theme ID to fetch (uses default if None)

    Returns:
        TypographyTheme with all typography tokens
    """
    return await get_client().get_typography(theme_id)


def get_default_typography() -> TypographyTheme:
    """
    Get default typography theme without API call.

    Returns:
        TypographyTheme with default tokens
    """
    return get_client()._get_default_theme()


def get_typography_token(text_type: str, theme_id: Optional[str] = None) -> TypographyToken:
    """
    Get typography token for a text type synchronously.

    Args:
        text_type: Slide text type (e.g., 'slide_title')
        theme_id: Theme ID (uses default if None)

    Returns:
        TypographyToken for the text type
    """
    client = get_client()
    theme = client.get_typography_sync(theme_id)
    return client.get_typography_for_text_type(text_type, theme)
