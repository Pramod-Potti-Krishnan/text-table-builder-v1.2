"""
Request Models for Text and Table Content Builder
==================================================

Pydantic models for incoming API requests from Content Orchestrator.

v1.2.1: Added ThemeConfig for Theme Service integration.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ThemeConfig(BaseModel):
    """
    Theme configuration from Theme Service (v1.2.1).

    Optional field that allows Director Agent to pass theme-specific
    styling to Text Service for consistent slide appearance.
    """
    theme_id: str = Field(
        default="professional",
        description="Theme identifier (professional, executive, educational, children_young, children_older)"
    )

    # Text colors
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

    # Border colors
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

    class Config:
        json_schema_extra = {
            "example": {
                "theme_id": "executive",
                "text_primary": "#111827",
                "text_secondary": "#1f2937",
                "text_muted": "#4b5563",
                "border_light": "#e2e8f0",
                "char_multiplier": 0.7,
                "max_bullets": 3
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
