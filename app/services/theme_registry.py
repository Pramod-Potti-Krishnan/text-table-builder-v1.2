"""
Theme Registry - Theme Synchronization with Layout Service

Manages theme configurations by:
1. Syncing from Layout Service (preferred)
2. Falling back to embedded THEME_PRESETS
3. Caching themes with version tracking

Per THEME_SYSTEM_DESIGN.md Section 12.2:
- Bulk sync endpoint: GET /api/themes/sync
- snake_case naming for all color keys
- Periodic refresh with embedded fallback

Version: 1.3.0
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

import httpx

from app.models.requests import (
    ThemeConfig, TypographyConfig, TypographySpec, ColorPalette
)
from app.core.theme.presets import THEME_PRESETS, get_theme_preset

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

# Layout Service URL (from environment or default)
LAYOUT_SERVICE_URL = os.environ.get(
    "LAYOUT_SERVICE_URL",
    "https://layout-builder-production.up.railway.app"
)

# Sync settings
SYNC_INTERVAL_MINUTES = 15
SYNC_TIMEOUT_SECONDS = 10


# =============================================================================
# Theme Registry Class
# =============================================================================

class ThemeRegistry:
    """
    Centralized theme configuration registry.

    Syncs themes from Layout Service and provides fallback to embedded presets.
    Maintains version tracking for cache validation.

    Usage:
        registry = ThemeRegistry()
        await registry.sync()
        theme = registry.get("professional")
    """

    def __init__(self):
        """Initialize the theme registry."""
        self._cache: Dict[str, ThemeConfig] = {}
        self._version: Optional[str] = None
        self._last_sync: Optional[datetime] = None
        self._sync_source: str = "none"
        self._initialized = False

    @property
    def is_initialized(self) -> bool:
        """Check if registry has been initialized."""
        return self._initialized

    @property
    def theme_count(self) -> int:
        """Get number of themes in registry."""
        return len(self._cache)

    @property
    def version(self) -> Optional[str]:
        """Get current theme version."""
        return self._version

    @property
    def sync_source(self) -> str:
        """Get source of current themes (layout_service or fallback)."""
        return self._sync_source

    @property
    def needs_sync(self) -> bool:
        """Check if sync is needed based on interval."""
        if not self._initialized:
            return True
        if self._last_sync is None:
            return True
        elapsed = datetime.utcnow() - self._last_sync
        return elapsed > timedelta(minutes=SYNC_INTERVAL_MINUTES)

    async def sync(self, force: bool = False) -> bool:
        """
        Sync themes from Layout Service.

        Args:
            force: Force sync even if not needed

        Returns:
            True if sync successful, False if using fallback
        """
        if not force and not self.needs_sync:
            logger.debug("Theme sync not needed, skipping")
            return self._sync_source == "layout_service"

        logger.info(f"Syncing themes from {LAYOUT_SERVICE_URL}")

        try:
            async with httpx.AsyncClient(timeout=SYNC_TIMEOUT_SECONDS) as client:
                response = await client.get(f"{LAYOUT_SERVICE_URL}/api/themes/sync")

                if response.status_code == 200:
                    data = response.json()
                    self._parse_sync_response(data)
                    self._sync_source = "layout_service"
                    self._last_sync = datetime.utcnow()
                    self._initialized = True

                    logger.info(
                        f"Synced {len(self._cache)} themes v{self._version} from Layout Service"
                    )
                    return True
                else:
                    logger.warning(
                        f"Theme sync failed with status {response.status_code}, using fallback"
                    )
                    self._load_fallback()
                    return False

        except httpx.TimeoutException:
            logger.warning("Theme sync timeout, using fallback")
            self._load_fallback()
            return False

        except Exception as e:
            logger.warning(f"Theme sync error: {e}, using fallback")
            self._load_fallback()
            return False

    def _parse_sync_response(self, data: Dict[str, Any]) -> None:
        """Parse sync response and populate cache."""
        self._version = data.get("version", "1.0.0")
        themes = data.get("themes", {})

        self._cache = {}
        for theme_id, theme_data in themes.items():
            self._cache[theme_id] = self._build_theme_config(theme_id, theme_data)

    def _load_fallback(self) -> None:
        """Load fallback themes from embedded presets."""
        self._cache = {}
        for theme_id, theme_data in THEME_PRESETS.items():
            self._cache[theme_id] = self._build_theme_config(theme_id, theme_data)

        self._version = "1.0.0"
        self._sync_source = "fallback"
        self._last_sync = datetime.utcnow()
        self._initialized = True

        logger.info(f"Loaded {len(self._cache)} themes from fallback presets")

    def _build_theme_config(
        self,
        theme_id: str,
        data: Dict[str, Any]
    ) -> ThemeConfig:
        """Build ThemeConfig from raw data."""
        # Build typography config
        typography_data = data.get("typography", {})
        typography = TypographyConfig(
            t1=self._build_typography_spec(typography_data.get("t1", {})),
            t2=self._build_typography_spec(typography_data.get("t2", {})),
            t3=self._build_typography_spec(typography_data.get("t3", {})),
            t4=self._build_typography_spec(typography_data.get("t4", {})),
            font_family=typography_data.get("font_family", "Poppins, sans-serif"),
            font_family_heading=typography_data.get("font_family_heading")
        )

        # Build color palette
        colors_data = data.get("colors", {})
        colors = ColorPalette(
            primary=colors_data.get("primary", "#1e3a5f"),
            primary_dark=colors_data.get("primary_dark", "#152a45"),
            primary_light=colors_data.get("primary_light", "#2d4a6f"),
            accent=colors_data.get("accent", "#3b82f6"),
            accent_dark=colors_data.get("accent_dark", "#2563eb"),
            accent_light=colors_data.get("accent_light", "#60a5fa"),
            tertiary_1=colors_data.get("tertiary_1", "#8b5cf6"),
            tertiary_2=colors_data.get("tertiary_2", "#ec4899"),
            tertiary_3=colors_data.get("tertiary_3", "#f59e0b"),
            background=colors_data.get("background", "#ffffff"),
            surface=colors_data.get("surface", "#f8fafc"),
            border=colors_data.get("border", "#e5e7eb"),
            text_primary=colors_data.get("text_primary", "#1f2937"),
            text_secondary=colors_data.get("text_secondary", "#374151"),
            text_muted=colors_data.get("text_muted", "#6b7280"),
            chart_1=colors_data.get("chart_1", "#3b82f6"),
            chart_2=colors_data.get("chart_2", "#10b981"),
            chart_3=colors_data.get("chart_3", "#f59e0b"),
            chart_4=colors_data.get("chart_4", "#ef4444"),
            chart_5=colors_data.get("chart_5", "#8b5cf6"),
            chart_6=colors_data.get("chart_6", "#ec4899"),
            success=colors_data.get("success", "#10b981"),
            warning=colors_data.get("warning", "#f59e0b"),
            error=colors_data.get("error", "#ef4444")
        )

        return ThemeConfig(
            theme_id=theme_id,
            typography=typography,
            colors=colors,
            text_primary=colors.text_primary,
            text_secondary=colors.text_secondary,
            text_muted=colors.text_muted,
            border_light=colors.border,
            version=data.get("version", self._version)
        )

    def _build_typography_spec(self, data: Dict[str, Any]) -> TypographySpec:
        """Build TypographySpec from raw data."""
        return TypographySpec(
            size=data.get("size", 16),
            weight=data.get("weight", 400),
            color=data.get("color", "#1f2937"),
            line_height=data.get("line_height", 1.5),
            letter_spacing=data.get("letter_spacing")
        )

    def get(self, theme_id: str) -> ThemeConfig:
        """
        Get theme configuration by ID.

        Args:
            theme_id: Theme identifier

        Returns:
            ThemeConfig (defaults to 'professional' if not found)
        """
        if not self._initialized:
            # Load fallback synchronously if not initialized
            self._load_fallback()

        return self._cache.get(theme_id, self._cache.get("professional"))

    def get_all_theme_ids(self) -> List[str]:
        """Get list of all available theme IDs."""
        if not self._initialized:
            self._load_fallback()
        return list(self._cache.keys())

    def get_status(self) -> Dict[str, Any]:
        """Get registry status for diagnostics."""
        return {
            "initialized": self._initialized,
            "theme_count": len(self._cache),
            "version": self._version,
            "sync_source": self._sync_source,
            "last_sync": self._last_sync.isoformat() if self._last_sync else None,
            "needs_sync": self.needs_sync,
            "theme_ids": list(self._cache.keys())
        }


# =============================================================================
# Global Registry Instance
# =============================================================================

# Singleton instance
_registry: Optional[ThemeRegistry] = None


def get_theme_registry() -> ThemeRegistry:
    """Get the global theme registry instance."""
    global _registry
    if _registry is None:
        _registry = ThemeRegistry()
    return _registry


async def init_theme_registry() -> ThemeRegistry:
    """Initialize and sync the theme registry."""
    registry = get_theme_registry()
    await registry.sync()
    return registry


def get_theme(theme_id: str) -> ThemeConfig:
    """
    Get theme configuration by ID.

    Convenience function that uses the global registry.

    Args:
        theme_id: Theme identifier

    Returns:
        ThemeConfig
    """
    return get_theme_registry().get(theme_id)


# =============================================================================
# Background Sync Task
# =============================================================================

async def background_sync_task():
    """
    Background task to periodically sync themes.

    Run this as a background task in your application:
        asyncio.create_task(background_sync_task())
    """
    registry = get_theme_registry()

    while True:
        try:
            await asyncio.sleep(SYNC_INTERVAL_MINUTES * 60)
            await registry.sync()
        except asyncio.CancelledError:
            logger.info("Theme sync background task cancelled")
            break
        except Exception as e:
            logger.error(f"Theme sync background task error: {e}")
