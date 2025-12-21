"""
Request Models for Text and Table Content Builder
==================================================

Pydantic models for incoming API requests from Content Orchestrator.

v1.2.1: Added ThemeConfig for Theme Service integration.
v1.3.0: Expanded ThemeConfig with full color palette and typography specs.
        Added ContentContext support for Audience/Purpose/Time.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# =============================================================================
# Typography Specification Models (v1.3.0)
# =============================================================================

class TypographySpec(BaseModel):
    """
    Typography specification for a single text level.

    Per THEME_SYSTEM_DESIGN.md Section 4.5:
    - t1: 32px, weight 700, line_height 1.2 (headings)
    - t2: 24px, weight 600, line_height 1.3 (subheadings)
    - t3: 20px, weight 500, line_height 1.4 (body emphasized)
    - t4: 16px, weight 400, line_height 1.5 (body normal)
    """
    size: int = Field(
        description="Font size in pixels"
    )
    weight: int = Field(
        default=400,
        description="Font weight (100-900)"
    )
    color: str = Field(
        description="Text color (hex)"
    )
    line_height: float = Field(
        default=1.5,
        description="Line height multiplier"
    )
    letter_spacing: Optional[str] = Field(
        default=None,
        description="Letter spacing (CSS value)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "size": 32,
                "weight": 700,
                "color": "#1f2937",
                "line_height": 1.2
            }
        }


class TypographyConfig(BaseModel):
    """
    Complete typography configuration with t1-t4 hierarchy.

    Per THEME_SYSTEM_DESIGN.md Section 1.3:
    - 3 Groups: Hero (72-96px), Slide-level (42-48px), Content (t1-t4)
    - t1 MUST be smaller than slide_subtitle
    - All 34 variants map to t1-t4 levels
    """
    t1: TypographySpec = Field(
        default_factory=lambda: TypographySpec(size=32, weight=700, color="#1f2937", line_height=1.2),
        description="Level 1: Headings (32px)"
    )
    t2: TypographySpec = Field(
        default_factory=lambda: TypographySpec(size=24, weight=600, color="#374151", line_height=1.3),
        description="Level 2: Subheadings (24px)"
    )
    t3: TypographySpec = Field(
        default_factory=lambda: TypographySpec(size=20, weight=500, color="#4b5563", line_height=1.4),
        description="Level 3: Body emphasized (20px)"
    )
    t4: TypographySpec = Field(
        default_factory=lambda: TypographySpec(size=16, weight=400, color="#6b7280", line_height=1.5),
        description="Level 4: Body normal (16px)"
    )
    font_family: str = Field(
        default="Poppins, sans-serif",
        description="Primary font family"
    )
    font_family_heading: Optional[str] = Field(
        default=None,
        description="Optional heading font family (uses font_family if None)"
    )

    def get_spec(self, level: str) -> TypographySpec:
        """Get typography spec for a level (t1-t4)."""
        specs = {"t1": self.t1, "t2": self.t2, "t3": self.t3, "t4": self.t4}
        return specs.get(level, self.t3)

    class Config:
        json_schema_extra = {
            "example": {
                "t1": {"size": 32, "weight": 700, "color": "#1f2937", "line_height": 1.2},
                "t2": {"size": 24, "weight": 600, "color": "#374151", "line_height": 1.3},
                "t3": {"size": 20, "weight": 500, "color": "#4b5563", "line_height": 1.4},
                "t4": {"size": 16, "weight": 400, "color": "#6b7280", "line_height": 1.5},
                "font_family": "Poppins, sans-serif"
            }
        }


# =============================================================================
# Color Palette Models (v1.3.0)
# =============================================================================

class ColorPalette(BaseModel):
    """
    Complete color palette for a theme.

    Per THEME_SYSTEM_DESIGN.md Section 1.4-1.6:
    - All keys use snake_case (Layout Service agreement)
    - 25 color keys for full theme coverage
    """
    # Primary colors
    primary: str = Field(
        default="#1e3a5f",
        description="Primary brand color"
    )
    primary_dark: str = Field(
        default="#152a45",
        description="Darker primary variant"
    )
    primary_light: str = Field(
        default="#2d4a6f",
        description="Lighter primary variant"
    )

    # Accent colors
    accent: str = Field(
        default="#3b82f6",
        description="Accent color for CTAs and highlights"
    )
    accent_dark: str = Field(
        default="#2563eb",
        description="Darker accent variant"
    )
    accent_light: str = Field(
        default="#60a5fa",
        description="Lighter accent variant"
    )

    # Tertiary colors (for variety in charts, boxes)
    tertiary_1: str = Field(
        default="#8b5cf6",
        description="Tertiary color 1 (purple)"
    )
    tertiary_2: str = Field(
        default="#ec4899",
        description="Tertiary color 2 (pink)"
    )
    tertiary_3: str = Field(
        default="#f59e0b",
        description="Tertiary color 3 (amber)"
    )

    # Background and surface colors
    background: str = Field(
        default="#ffffff",
        description="Page/slide background"
    )
    surface: str = Field(
        default="#f8fafc",
        description="Elevated surface background"
    )
    border: str = Field(
        default="#e5e7eb",
        description="Border color"
    )

    # Text colors
    text_primary: str = Field(
        default="#1f2937",
        description="Primary text color"
    )
    text_secondary: str = Field(
        default="#374151",
        description="Secondary text color"
    )
    text_muted: str = Field(
        default="#6b7280",
        description="Muted/caption text color"
    )

    # Chart colors (for data visualization)
    chart_1: str = Field(
        default="#3b82f6",
        description="Chart color 1 (blue)"
    )
    chart_2: str = Field(
        default="#10b981",
        description="Chart color 2 (green)"
    )
    chart_3: str = Field(
        default="#f59e0b",
        description="Chart color 3 (amber)"
    )
    chart_4: str = Field(
        default="#ef4444",
        description="Chart color 4 (red)"
    )
    chart_5: str = Field(
        default="#8b5cf6",
        description="Chart color 5 (purple)"
    )
    chart_6: str = Field(
        default="#ec4899",
        description="Chart color 6 (pink)"
    )

    # Semantic colors
    success: str = Field(
        default="#10b981",
        description="Success/positive color"
    )
    warning: str = Field(
        default="#f59e0b",
        description="Warning color"
    )
    error: str = Field(
        default="#ef4444",
        description="Error/negative color"
    )

    def get_chart_colors(self) -> List[str]:
        """Get list of chart colors in order."""
        return [self.chart_1, self.chart_2, self.chart_3,
                self.chart_4, self.chart_5, self.chart_6]

    class Config:
        json_schema_extra = {
            "example": {
                "primary": "#1e3a5f",
                "accent": "#3b82f6",
                "tertiary_1": "#8b5cf6",
                "background": "#ffffff",
                "text_primary": "#1f2937",
                "chart_1": "#3b82f6"
            }
        }


# =============================================================================
# Theme Configuration (v1.3.0 - Expanded)
# =============================================================================

class ThemeConfig(BaseModel):
    """
    Complete theme configuration for Text Service v1.3.0.

    Per THEME_SYSTEM_DESIGN.md Section 12:
    - Passed from Director to Text Service
    - Contains typography (t1-t4) and full color palette
    - Theme is VISUAL ONLY, orthogonal to Audience/Purpose

    Backward compatible: legacy fields still supported.
    """
    theme_id: str = Field(
        default="professional",
        description="Theme identifier (professional, executive, educational, children)"
    )

    # v1.3.0: Full typography configuration
    typography: Optional[TypographyConfig] = Field(
        default=None,
        description="Typography configuration with t1-t4 hierarchy"
    )

    # v1.3.0: Full color palette
    colors: Optional[ColorPalette] = Field(
        default=None,
        description="Complete color palette"
    )

    # Legacy text colors (backward compatibility)
    text_primary: str = Field(
        default="#1f2937",
        description="Primary text color for headings"
    )
    text_secondary: str = Field(
        default="#374151",
        description="Secondary text color for body"
    )
    text_muted: str = Field(
        default="#6b7280",
        description="Muted text color for subtitles/captions"
    )

    # Legacy border color
    border_light: str = Field(
        default="#e5e7eb",
        description="Light border color"
    )

    # Box gradients (for grid layouts)
    box_gradients: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Gradient pairs for box backgrounds [{start, end}, ...]"
    )

    # Matrix colors (for matrix layouts)
    matrix_colors: List[str] = Field(
        default_factory=list,
        description="Solid colors for matrix cells"
    )

    # Content density
    char_multiplier: float = Field(
        default=1.0,
        description="Character limit multiplier (1.0 = full, 0.5 = half)"
    )
    max_bullets: int = Field(
        default=5,
        description="Maximum bullets per section"
    )

    # Font scaling
    font_scale: float = Field(
        default=1.0,
        description="Font size multiplier"
    )

    # v1.3.0: Theme version for cache validation
    version: Optional[str] = Field(
        default=None,
        description="Theme version from Layout Service"
    )

    def get_typography_spec(self, level: str) -> TypographySpec:
        """
        Get typography spec for a level, with fallback.

        Args:
            level: Typography level (t1, t2, t3, t4)

        Returns:
            TypographySpec for the level
        """
        if self.typography:
            return self.typography.get_spec(level)

        # Fallback: construct from legacy fields
        defaults = {
            "t1": TypographySpec(size=32, weight=700, color=self.text_primary, line_height=1.2),
            "t2": TypographySpec(size=24, weight=600, color=self.text_secondary, line_height=1.3),
            "t3": TypographySpec(size=20, weight=500, color=self.text_secondary, line_height=1.4),
            "t4": TypographySpec(size=16, weight=400, color=self.text_muted, line_height=1.5),
        }
        return defaults.get(level, defaults["t3"])

    def get_color(self, key: str) -> str:
        """
        Get color by key, with fallback to legacy fields.

        Args:
            key: Color key (e.g., 'primary', 'accent', 'text_primary')

        Returns:
            Hex color string
        """
        if self.colors:
            return getattr(self.colors, key, "#000000")

        # Fallback to legacy fields
        legacy_map = {
            "text_primary": self.text_primary,
            "text_secondary": self.text_secondary,
            "text_muted": self.text_muted,
            "border": self.border_light,
        }
        return legacy_map.get(key, "#000000")

    class Config:
        json_schema_extra = {
            "example": {
                "theme_id": "professional",
                "typography": {
                    "t1": {"size": 32, "weight": 700, "color": "#1f2937", "line_height": 1.2},
                    "t2": {"size": 24, "weight": 600, "color": "#374151", "line_height": 1.3},
                    "t3": {"size": 20, "weight": 500, "color": "#4b5563", "line_height": 1.4},
                    "t4": {"size": 16, "weight": 400, "color": "#6b7280", "line_height": 1.5}
                },
                "colors": {
                    "primary": "#1e3a5f",
                    "accent": "#3b82f6",
                    "text_primary": "#1f2937",
                    "chart_1": "#3b82f6"
                }
            }
        }


class TextGenerationRequest(BaseModel):
    """
    Request model for text content generation.

    Matches Content Orchestrator's text request format.
    """
    # Session tracking
    presentation_id: str = Field(
        description="Unique presentation identifier for session tracking"
    )

    # Slide identification
    slide_id: str = Field(
        description="Unique slide identifier like 'slide_001'"
    )
    slide_number: int = Field(
        description="Slide number in presentation sequence"
    )

    # Content source
    topics: List[str] = Field(
        description="Key points to expand into full content"
    )
    narrative: str = Field(
        description="Overall narrative/story for this slide",
        default=""
    )

    # Context for generation
    context: Dict[str, Any] = Field(
        description="Presentation context (theme, audience, slide_title)",
        default_factory=dict
    )

    # Generation constraints
    constraints: Dict[str, Any] = Field(
        description="Generation constraints (max_characters, style, tone)",
        default_factory=dict
    )

    # v3.3 Layout Metadata (explicit fields for prompt conditionals)
    layout_id: Optional[str] = Field(
        default=None,
        description="Layout ID (L25, L29) - enables layout-specific prompt rules"
    )
    slide_purpose: Optional[str] = Field(
        default=None,
        description="L29 slide purpose: title_slide, section_divider, closing_slide, regular_hero"
    )
    suggested_pattern: Optional[str] = Field(
        default=None,
        description="Suggested visual pattern: 3-card-metrics-grid, styled-table, 2-column-split-lists, etc."
    )

    # Session context (optional - populated by session manager if not provided)
    previous_slides_context: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Context from previous slides for content flow"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "presentation_id": "pres_12345",
                "slide_id": "slide_001",
                "slide_number": 1,
                "topics": ["Revenue growth", "Market expansion", "Cost efficiency"],
                "narrative": "Strong financial performance driven by strategic initiatives",
                "context": {
                    "theme": "professional",
                    "audience": "executives",
                    "slide_title": "Q3 Financial Results"
                },
                "constraints": {
                    "max_characters": 300,
                    "style": "professional",
                    "tone": "data-driven"
                }
            }
        }


class TableGenerationRequest(BaseModel):
    """
    Request model for table generation.

    LLM will analyze description and data to create optimal table structure.
    """
    # Session tracking
    presentation_id: str = Field(
        description="Unique presentation identifier for session tracking"
    )

    # Slide identification
    slide_id: str = Field(
        description="Unique slide identifier"
    )
    slide_number: int = Field(
        description="Slide number in presentation sequence"
    )

    # Table specification
    description: str = Field(
        description="Description of what the table should display"
    )
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Raw data to be structured into table (can be dict, list, or nested)"
    )

    # Context
    context: Dict[str, Any] = Field(
        description="Presentation context",
        default_factory=dict
    )

    # Constraints
    constraints: Dict[str, Any] = Field(
        description="Table constraints (max_rows, max_columns, style)",
        default_factory=dict
    )

    # Session context
    previous_slides_context: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Context from previous slides"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "presentation_id": "pres_12345",
                "slide_id": "slide_003",
                "slide_number": 3,
                "description": "Quarterly revenue breakdown by region showing Q2 vs Q3 comparison",
                "data": {
                    "Q2": {"North America": 45.2, "Europe": 32.1, "Asia": 28.7},
                    "Q3": {"North America": 58.3, "Europe": 39.4, "Asia": 35.6}
                },
                "context": {
                    "theme": "professional",
                    "audience": "executives",
                    "slide_title": "Regional Performance"
                },
                "constraints": {
                    "max_rows": 10,
                    "max_columns": 5,
                    "style": "clean"
                }
            }
        }


class BatchTextGenerationRequest(BaseModel):
    """
    Batch request for generating multiple text contents.
    """
    requests: List[TextGenerationRequest] = Field(
        description="List of text generation requests"
    )
    parallel: bool = Field(
        default=True,
        description="Whether to process requests in parallel"
    )


class BatchTableGenerationRequest(BaseModel):
    """
    Batch request for generating multiple tables.
    """
    requests: List[TableGenerationRequest] = Field(
        description="List of table generation requests"
    )
    parallel: bool = Field(
        default=True,
        description="Whether to process requests in parallel"
    )


# v1.1 Structured Generation Models (Format Ownership Architecture)
# ====================================================================

class FieldSpec(BaseModel):
    """
    Field specification with format ownership (v1.1).

    Defines whether a field should be generated as plain_text or html,
    and who owns the formatting responsibility.
    """
    format_type: str = Field(
        description="Format type: 'plain_text' or 'html'"
    )
    format_owner: str = Field(
        description="Format owner: 'text_service' or 'layout_builder'"
    )

    # Validation constraints (90% threshold model)
    max_chars: Optional[int] = Field(
        default=None,
        description="Maximum characters allowed"
    )
    max_words: Optional[int] = Field(
        default=None,
        description="Maximum words allowed"
    )
    max_lines: Optional[int] = Field(
        default=None,
        description="Maximum lines allowed"
    )
    validation_threshold: Optional[float] = Field(
        default=0.9,
        description="Validation threshold (0.0-1.0). Hit 90% of ANY limit."
    )

    # HTML-specific specifications
    expected_structure: Optional[str] = Field(
        default=None,
        description="Expected HTML structure (e.g., 'ul>li', 'p', 'mixed')"
    )

    # Array specifications
    min_items: Optional[int] = Field(
        default=None,
        description="Minimum items for array fields"
    )
    max_items: Optional[int] = Field(
        default=None,
        description="Maximum items for array fields"
    )
    max_chars_per_item: Optional[int] = Field(
        default=None,
        description="Maximum characters per array item"
    )

    # Field type context
    type: Optional[str] = Field(
        default=None,
        description="Field type (string, array, object, etc.)"
    )

    # Nested structures
    item_structure: Optional[Dict[str, 'FieldSpec']] = Field(
        default=None,
        description="Structure for array_of_objects items"
    )
    structure: Optional[Dict[str, 'FieldSpec']] = Field(
        default=None,
        description="Structure for object fields"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "format_type": "html",
                "format_owner": "text_service",
                "max_chars": 500,
                "max_lines": 8,
                "validation_threshold": 0.9,
                "expected_structure": "ul>li or ol>li",
                "type": "array"
            }
        }


# Enable forward references for nested FieldSpec
FieldSpec.model_rebuild()


class StructuredTextGenerationRequest(BaseModel):
    """
    Enhanced text generation request with format specifications (v1.1).

    Replaces Content Orchestrator's text request format with explicit
    format ownership specifications for each field.
    """
    # Session tracking
    presentation_id: str = Field(
        description="Unique presentation identifier for session tracking"
    )

    # Slide identification
    slide_id: str = Field(
        description="Unique slide identifier like 'slide_001'"
    )
    slide_number: int = Field(
        description="Slide number in presentation sequence"
    )

    # Layout context (v1.1 - from Director's schema-driven architecture)
    layout_id: str = Field(
        description="Layout ID (e.g., L05, L07, L20) selected by Director"
    )
    layout_name: str = Field(
        description="Human-readable layout name"
    )
    layout_subtype: str = Field(
        description="Layout subtype (e.g., List, Quote, Comparison)"
    )

    # Format specifications (v1.1 - core enhancement)
    field_specifications: Dict[str, FieldSpec] = Field(
        description="Format specifications for each field"
    )

    # Full schema for reference
    layout_schema: Dict[str, Any] = Field(
        description="Complete layout schema from Director"
    )

    # Content guidance
    content_guidance: Dict[str, Any] = Field(
        description="Content guidance from slide (title, narrative, key_points)"
    )

    # Session context (optional)
    previous_slides_context: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Context from previous slides for content flow"
    )

    # Theme configuration (v1.2.1 - Theme Service integration)
    theme_config: Optional[ThemeConfig] = Field(
        default=None,
        description="Theme configuration from Theme Service for consistent styling"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "presentation_id": "pres_12345",
                "slide_id": "slide_005",
                "slide_number": 5,
                "layout_id": "L05",
                "layout_name": "Bullet List",
                "layout_subtype": "List",
                "field_specifications": {
                    "slide_title": {
                        "format_type": "plain_text",
                        "format_owner": "layout_builder",
                        "max_chars": 60,
                        "max_lines": 1,
                        "type": "string"
                    },
                    "bullets": {
                        "format_type": "html",
                        "format_owner": "text_service",
                        "max_chars": 800,
                        "max_lines": 8,
                        "validation_threshold": 0.9,
                        "expected_structure": "ul>li or ol>li",
                        "min_items": 5,
                        "max_items": 8,
                        "type": "array"
                    }
                },
                "layout_schema": {
                    "slide_title": {"type": "string", "max_chars": 60},
                    "bullets": {"type": "array", "min_items": 5, "max_items": 8}
                },
                "content_guidance": {
                    "title": "Key Benefits",
                    "narrative": "Overview of main advantages",
                    "key_points": ["Cost savings", "Efficiency", "Scalability"]
                }
            }
        }
