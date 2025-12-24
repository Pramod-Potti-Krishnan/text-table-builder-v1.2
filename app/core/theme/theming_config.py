"""
Theming Configuration for Text Service v1.2

Feature flags and configuration for the CSS variable-based theming system.
Part of the phased rollout strategy - see docs/THEME_SYSTEM_REQUIREMENTS.md

Phase 1: 5 pilot templates with CSS variables
Phase 2: All 34 templates
Phase 3: Full integration with Audience/Purpose

Version: 1.0.0
"""

import os
from typing import List, Optional
from functools import lru_cache


class ThemingSettings:
    """
    Feature flag settings for the CSS variable theming system.

    Environment Variables:
        USE_CSS_VARIABLES: bool - Enable CSS variable templates (default: false)
        CSS_VARIABLE_TEMPLATES: str - Comma-separated list of variant_ids
        THEME_VERSION: int - Version for compatibility tracking
    """

    def __init__(self):
        self._use_css_variables: bool = self._parse_bool(
            os.environ.get("USE_CSS_VARIABLES", "false")
        )
        self._css_variable_templates: str = os.environ.get(
            "CSS_VARIABLE_TEMPLATES", ""
        )
        self._theme_version: int = int(os.environ.get("THEME_VERSION", "1"))

    @staticmethod
    def _parse_bool(value: str) -> bool:
        """Parse boolean from environment variable string."""
        return value.lower() in ("true", "1", "yes", "on")

    @property
    def use_css_variables(self) -> bool:
        """Check if CSS variable theming is enabled."""
        return self._use_css_variables

    @property
    def theme_version(self) -> int:
        """Get theme system version for compatibility tracking."""
        return self._theme_version

    @property
    def css_variable_template_list(self) -> List[str]:
        """Get list of variant_ids that should use CSS variable templates."""
        if not self._css_variable_templates:
            return []
        return [t.strip() for t in self._css_variable_templates.split(",") if t.strip()]

    def uses_css_variables(self, variant_id: str) -> bool:
        """
        Check if a specific variant should use CSS variable templates.

        Args:
            variant_id: The variant identifier (e.g., "metrics_3col_c1")

        Returns:
            True if the variant should use CSS variables, False otherwise
        """
        if not self._use_css_variables:
            return False
        return variant_id in self.css_variable_template_list

    def get_themed_template_suffix(self) -> str:
        """Get the suffix for themed template files."""
        return "_themed"


# Singleton instance
_theming_settings: Optional[ThemingSettings] = None


def get_theming_settings() -> ThemingSettings:
    """
    Get the global theming settings instance.

    Returns:
        ThemingSettings singleton instance
    """
    global _theming_settings
    if _theming_settings is None:
        _theming_settings = ThemingSettings()
    return _theming_settings


def reload_theming_settings() -> ThemingSettings:
    """
    Force reload of theming settings from environment.
    Useful for testing or dynamic configuration updates.

    Returns:
        New ThemingSettings instance
    """
    global _theming_settings
    _theming_settings = ThemingSettings()
    return _theming_settings


# CSS Variable Mapping Reference (for documentation)
# These are the CSS variables that themed templates should use:
CSS_VARIABLE_MAPPING = {
    # Text Colors
    "--text-primary": {"light": "#1f2937", "dark": "#f8fafc"},
    "--text-secondary": {"light": "#374151", "dark": "#e2e8f0"},
    "--text-body": {"light": "#4b5563", "dark": "#cbd5e1"},
    "--text-muted": {"light": "#6b7280", "dark": "#94a3b8"},
    "--text-on-dark": {"light": "#ffffff", "dark": "#ffffff"},

    # Box Backgrounds (for grid/hybrid layouts)
    "--box-1-bg": {"light": "#dbeafe", "dark": "#1e3a8a"},
    "--box-2-bg": {"light": "#d1fae5", "dark": "#065f46"},
    "--box-3-bg": {"light": "#fef3c7", "dark": "#78350f"},
    "--box-4-bg": {"light": "#fce7f3", "dark": "#831843"},
    "--box-5-bg": {"light": "#ede9fe", "dark": "#4c1d95"},

    # Borders
    "--border-default": {"light": "#d1d5db", "dark": "#4b5563"},
    "--border-accent": {"light": "#667eea", "dark": "#667eea"},
    "--border-light": {"light": "#e5e7eb", "dark": "#374151"},

    # Table-specific
    "--table-row-alt": {"light": "#f9fafb", "dark": "#1e293b"},

    # Accent Colors (for column headers, highlights)
    "--accent-blue": {"light": "#2563eb", "dark": "#60a5fa"},
    "--accent-green": {"light": "#10b981", "dark": "#34d399"},
    "--accent-red": {"light": "#dc2626", "dark": "#f87171"},
    "--accent-purple": {"light": "#667eea", "dark": "#a78bfa"},
    "--accent-amber": {"light": "#f59e0b", "dark": "#fbbf24"},
}
