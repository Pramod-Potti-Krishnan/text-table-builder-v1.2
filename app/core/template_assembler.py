"""
Template Assembler for v1.2 Deterministic Assembly Architecture

This module loads HTML templates and assembles them with generated content
by replacing placeholders. Templates are cached for performance.

Architecture:
    Load template by variant_id → Replace placeholders with content
    → Apply theme overrides → Return assembled HTML → Cache for future use

v1.2.1: Added theme override support for Theme Service integration.
v1.2.2: Added CSS variable themed template support (Phase 1).
"""

from pathlib import Path
from typing import Dict, Optional, Any
import re
import logging

from app.core.theme.theming_config import get_theming_settings

logger = logging.getLogger(__name__)


class TemplateAssembler:
    """Loads and assembles HTML templates with generated content."""

    def __init__(self, templates_dir: str = "app/templates"):
        """
        Initialize the TemplateAssembler.

        Args:
            templates_dir: Base directory containing template files
        """
        self.templates_dir = Path(templates_dir)
        self._template_cache: Dict[str, str] = {}
        self._theming_settings = get_theming_settings()

    def get_themed_template_path(
        self,
        template_path: str,
        variant_id: Optional[str] = None
    ) -> str:
        """
        Get the themed template path if CSS variable theming is enabled for the variant.

        This is part of Phase 1 CSS variable theming rollout. When USE_CSS_VARIABLES=true
        and the variant_id is in the CSS_VARIABLE_TEMPLATES list, this method returns
        the path to the _themed.html version of the template.

        Args:
            template_path: Original template path (e.g., "metrics/metrics_3col_c1.html")
            variant_id: The variant identifier (e.g., "metrics_3col_c1")

        Returns:
            The themed template path if applicable, otherwise the original path
        """
        # If no variant_id provided, can't determine if theming applies
        if not variant_id:
            return template_path

        # Check if this variant should use CSS variables
        if not self._theming_settings.uses_css_variables(variant_id):
            return template_path

        # Build themed template path
        themed_suffix = self._theming_settings.get_themed_template_suffix()
        if template_path.endswith('.html'):
            themed_path = template_path.replace('.html', f'{themed_suffix}.html')
        else:
            themed_path = f"{template_path}{themed_suffix}.html"

        # Check if themed template exists
        full_themed_path = self.templates_dir / themed_path
        if full_themed_path.exists():
            logger.debug(f"Using themed template for {variant_id}: {themed_path}")
            return themed_path

        # Fall back to original if themed version doesn't exist
        logger.warning(
            f"Themed template not found for {variant_id}: {themed_path}. "
            f"Using original: {template_path}"
        )
        return template_path

    def load_template(self, template_path: str, variant_id: Optional[str] = None) -> str:
        """
        Load an HTML template from file.

        Args:
            template_path: Relative path to template (e.g., "matrix/matrix_2x2.html")
            variant_id: Optional variant identifier for themed template selection (v1.2.2)

        Returns:
            Template HTML string with placeholders

        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        # Normalize template_path (remove base directory if it's included)
        # This handles cases where variant specs include "app/templates/" in path
        template_path_str = str(template_path)
        base_dir_str = str(self.templates_dir) + "/"
        if template_path_str.startswith(base_dir_str):
            template_path = template_path_str[len(base_dir_str):]
        elif template_path_str.startswith("app/templates/"):
            template_path = template_path_str[len("app/templates/"):]

        # Check for themed template (v1.2.2 CSS variable theming)
        actual_template_path = self.get_themed_template_path(template_path, variant_id)

        # Check cache first (using actual path for cache key)
        if actual_template_path in self._template_cache:
            return self._template_cache[actual_template_path]

        # Load from file
        full_path = self.templates_dir / actual_template_path

        if not full_path.exists():
            raise FileNotFoundError(f"Template not found: {full_path}")

        with open(full_path, 'r', encoding='utf-8') as f:
            template_html = f.read()

        # Cache for future use
        self._template_cache[actual_template_path] = template_html

        return template_html

    def assemble_template(
        self,
        template_path: str,
        content_map: Dict[str, str],
        variant_id: Optional[str] = None
    ) -> str:
        """
        Assemble template by replacing placeholders with content.

        Args:
            template_path: Relative path to template
            content_map: Dictionary mapping placeholder names to content values
                        e.g., {"box_1_title": "Innovation", "box_1_description": "..."}
            variant_id: Optional variant identifier for themed template selection (v1.2.2)

        Returns:
            Assembled HTML with all placeholders replaced

        Raises:
            ValueError: If required placeholders are missing
        """
        # Load template (will use themed version if enabled for variant)
        template_html = self.load_template(template_path, variant_id)

        # Find all placeholders in template
        # Match only valid placeholder names: letters, numbers, underscores
        # This prevents matching CSS curly braces like { color: #xxx; }
        placeholder_pattern = r'\{([a-z_][a-z0-9_]*)\}'
        placeholders = set(re.findall(placeholder_pattern, template_html, re.IGNORECASE))

        # Check for missing placeholders
        missing = placeholders - set(content_map.keys())
        if missing:
            raise ValueError(
                f"Missing content for placeholders: {', '.join(sorted(missing))}"
            )

        # Replace placeholders
        assembled_html = template_html
        for placeholder, content in content_map.items():
            # Escape the placeholder for regex
            placeholder_pattern = '{' + placeholder + '}'
            assembled_html = assembled_html.replace(placeholder_pattern, content)

        return assembled_html

    def get_template_placeholders(self, template_path: str) -> set:
        """
        Extract all placeholders from a template.

        Args:
            template_path: Relative path to template

        Returns:
            Set of placeholder names found in template
        """
        template_html = self.load_template(template_path)
        # Match only valid placeholder names: letters, numbers, underscores
        # This prevents matching CSS curly braces like { color: #xxx; }
        placeholder_pattern = r'\{([a-z_][a-z0-9_]*)\}'
        placeholders = set(re.findall(placeholder_pattern, template_html, re.IGNORECASE))
        return placeholders

    def validate_content_map(
        self,
        template_path: str,
        content_map: Dict[str, str]
    ) -> Dict[str, list]:
        """
        Validate that content map matches template requirements.

        Args:
            template_path: Relative path to template
            content_map: Dictionary of placeholder -> content mappings

        Returns:
            Dictionary with "missing" and "extra" keys containing lists of placeholders
        """
        template_placeholders = self.get_template_placeholders(template_path)
        content_keys = set(content_map.keys())

        return {
            "missing": sorted(template_placeholders - content_keys),
            "extra": sorted(content_keys - template_placeholders)
        }

    def clear_cache(self):
        """Clear the template cache."""
        self._template_cache.clear()

    def get_cache_stats(self) -> Dict:
        """
        Get statistics about the template cache.

        Returns:
            Dictionary with cache statistics
        """
        return {
            "cached_templates": len(self._template_cache),
            "template_paths": sorted(self._template_cache.keys())
        }

    def apply_theme_overrides(
        self,
        html: str,
        theme_config: Optional[Any] = None
    ) -> str:
        """
        Apply theme-specific color overrides to assembled HTML (v1.2.1).

        This method replaces default colors with theme-specific colors
        in the inline CSS of the assembled HTML.

        Args:
            html: Assembled HTML string
            theme_config: ThemeConfig object from request (optional)

        Returns:
            HTML string with theme colors applied
        """
        if theme_config is None:
            return html

        # Define color mappings (default -> theme)
        color_mappings = []

        # Text colors
        if hasattr(theme_config, 'text_primary') and theme_config.text_primary:
            color_mappings.extend([
                ("color: #1f2937", f"color: {theme_config.text_primary}"),
                ("color:#1f2937", f"color:{theme_config.text_primary}"),
            ])

        if hasattr(theme_config, 'text_secondary') and theme_config.text_secondary:
            color_mappings.extend([
                ("color: #374151", f"color: {theme_config.text_secondary}"),
                ("color:#374151", f"color:{theme_config.text_secondary}"),
            ])

        if hasattr(theme_config, 'text_muted') and theme_config.text_muted:
            color_mappings.extend([
                ("color: #6b7280", f"color: {theme_config.text_muted}"),
                ("color:#6b7280", f"color:{theme_config.text_muted}"),
            ])

        # Border colors
        if hasattr(theme_config, 'border_light') and theme_config.border_light:
            color_mappings.extend([
                ("border-color: #e5e7eb", f"border-color: {theme_config.border_light}"),
                ("border: 1px solid #e5e7eb", f"border: 1px solid {theme_config.border_light}"),
                ("border: 2px solid #e5e7eb", f"border: 2px solid {theme_config.border_light}"),
            ])

        # Apply all color mappings
        themed_html = html
        for old_value, new_value in color_mappings:
            themed_html = themed_html.replace(old_value, new_value)

        return themed_html

    def assemble_with_theme(
        self,
        template_path: str,
        content_map: Dict[str, str],
        theme_config: Optional[Any] = None,
        variant_id: Optional[str] = None
    ) -> str:
        """
        Assemble template and apply theme overrides in one step (v1.2.1, v1.2.2).

        Convenience method that combines assemble_template and apply_theme_overrides.
        v1.2.2: Added variant_id support for CSS variable themed templates.

        Args:
            template_path: Relative path to template
            content_map: Dictionary mapping placeholder names to content values
            theme_config: ThemeConfig object from request (optional)
            variant_id: Optional variant identifier for themed template selection (v1.2.2)

        Returns:
            Assembled HTML with theme colors applied
        """
        # First assemble the template (will use themed version if enabled)
        assembled_html = self.assemble_template(template_path, content_map, variant_id)

        # Then apply theme overrides if provided
        return self.apply_theme_overrides(assembled_html, theme_config)
