"""
Theme Module for Text Service v1.3.0

Provides theme presets and utilities for theme-aware content generation.
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

__all__ = [
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
]
