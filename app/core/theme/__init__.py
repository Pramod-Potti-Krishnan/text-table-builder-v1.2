"""
Theme Module for Text Service v1.3.0

Provides theme presets and utilities for theme-aware content generation.
Includes CSS variable theming support for Phase 1 rollout.
"""

from app.core.theme.presets import (
    THEME_PRESETS,
    CSS_CLASS_MAP,
    get_theme_preset,
    get_typography_spec,
    get_color,
    get_chart_colors,
    get_css_class,
    build_inline_style,
    get_all_theme_ids,
    validate_theme_id,
)

from app.core.theme.theming_config import (
    ThemingSettings,
    get_theming_settings,
    reload_theming_settings,
    CSS_VARIABLE_MAPPING,
)

__all__ = [
    # Theme presets
    "THEME_PRESETS",
    "CSS_CLASS_MAP",
    "get_theme_preset",
    "get_typography_spec",
    "get_color",
    "get_chart_colors",
    "get_css_class",
    "build_inline_style",
    "get_all_theme_ids",
    "validate_theme_id",
    # CSS variable theming (Phase 1)
    "ThemingSettings",
    "get_theming_settings",
    "reload_theming_settings",
    "CSS_VARIABLE_MAPPING",
]
