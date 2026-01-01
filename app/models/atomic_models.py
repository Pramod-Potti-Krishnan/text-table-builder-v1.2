"""
Atomic Component Models for Direct Component Generation
========================================================

Pydantic models for the /v1.2/atomic/{TYPE} endpoints that provide
direct access to atomic component generation without CoT reasoning.

Supports 5 atomic component types:
- METRICS (metrics_card): 1-4 metric cards
- SEQUENTIAL (numbered_card): 1-6 numbered steps
- COMPARISON (comparison_column): 1-4 columns with flexible items
- SECTIONS (colored_section): 1-5 sections with flexible bullets
- CALLOUT (sidebar_box): 1-2 callout boxes with flexible items

v1.1.0: Added count=1 support for all types + placeholder_mode

v1.0.0: Initial atomic component endpoints
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


# =============================================================================
# Enums
# =============================================================================

class AtomicType(str, Enum):
    """Atomic component type identifiers (UPPERCASE for URL paths)."""
    METRICS = "METRICS"
    SEQUENTIAL = "SEQUENTIAL"
    COMPARISON = "COMPARISON"
    SECTIONS = "SECTIONS"
    CALLOUT = "CALLOUT"
    TEXT_BULLETS = "TEXT_BULLETS"
    BULLET_BOX = "BULLET_BOX"
    TABLE = "TABLE"
    NUMBERED_LIST = "NUMBERED_LIST"


class LayoutType(str, Enum):
    """Layout arrangement options for atomic components."""
    HORIZONTAL = "horizontal"   # Side by side in a row
    VERTICAL = "vertical"       # Stacked in a column
    GRID = "grid"              # Grid layout (rows x cols)


# Map from atomic type to internal component_id
ATOMIC_TYPE_MAP = {
    AtomicType.METRICS: "metrics_card",
    AtomicType.SEQUENTIAL: "numbered_card",
    AtomicType.COMPARISON: "comparison_column",
    AtomicType.SECTIONS: "colored_section",
    AtomicType.CALLOUT: "sidebar_box",
    AtomicType.TEXT_BULLETS: "text_bullets",
    AtomicType.BULLET_BOX: "bullet_box",
    AtomicType.TABLE: "table_basic",
    AtomicType.NUMBERED_LIST: "numbered_list"
}


# =============================================================================
# Context Models
# =============================================================================

class AtomicContext(BaseModel):
    """
    Optional context for content generation.

    Provides slide-level and presentation-level context to guide
    the LLM in generating appropriate content.
    """
    # Slide-level context
    slide_title: Optional[str] = Field(
        None,
        max_length=100,
        description="Title of the slide this component appears on"
    )
    slide_purpose: Optional[str] = Field(
        None,
        max_length=200,
        description="Purpose of this slide (inform, persuade, compare, etc.)"
    )
    key_message: Optional[str] = Field(
        None,
        max_length=200,
        description="The key takeaway message for the audience"
    )
    audience: Optional[str] = Field(
        None,
        description="Target audience (executive, technical, general, etc.)"
    )
    tone: Optional[str] = Field(
        default="professional",
        description="Desired tone (professional, conversational, technical, etc.)"
    )

    # Presentation-level context
    presentation_title: Optional[str] = Field(
        None,
        max_length=100,
        description="Overall presentation title"
    )
    industry: Optional[str] = Field(
        None,
        description="Industry context (tech, healthcare, finance, etc.)"
    )
    company: Optional[str] = Field(
        None,
        description="Company name for context"
    )
    prior_slides_summary: Optional[str] = Field(
        None,
        max_length=500,
        description="Summary of prior slides for continuity"
    )


# =============================================================================
# Base Request Model
# =============================================================================

class AtomicComponentRequest(BaseModel):
    """
    Base request model for all atomic component endpoints.

    All atomic endpoints share these common fields.
    """
    prompt: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Content request describing what to generate",
        json_schema_extra={"example": "Show quarterly revenue growth across regions"}
    )
    gridWidth: int = Field(
        ...,
        ge=4,
        le=32,
        description="Available width in grid units (32-grid system, 60px per unit)"
    )
    gridHeight: int = Field(
        ...,
        ge=4,
        le=18,
        description="Available height in grid units (18-grid system, 60px per unit)"
    )
    context: Optional[AtomicContext] = Field(
        None,
        description="Optional slide/presentation context for content generation"
    )
    variant: Optional[str] = Field(
        None,
        description="Specific color variant to use (or auto-assign if null)"
    )
    placeholder_mode: bool = Field(
        default=False,
        description="If true, generate placeholder content without LLM call"
    )
    layout: LayoutType = Field(
        default=LayoutType.HORIZONTAL,
        description="Layout arrangement: horizontal (row), vertical (column), or grid"
    )
    grid_cols: Optional[int] = Field(
        default=None,
        ge=1,
        le=6,
        description="Number of columns for grid layout (auto-calculated if null)"
    )
    transparency: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Box opacity (0.0-1.0). Uses component default if null"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Key performance metrics for Q4 2024",
                "gridWidth": 24,
                "gridHeight": 10,
                "layout": "horizontal",
                "context": {
                    "audience": "executive",
                    "tone": "professional"
                }
            }
        }


# =============================================================================
# Endpoint-Specific Request Models
# =============================================================================

class MetricsAtomicRequest(AtomicComponentRequest):
    """
    Request model for POST /v1.2/atomic/METRICS

    Generates 1-4 metric cards with number, label, and description.
    Supports unitary elements (count=1) for modular composition.
    """
    count: int = Field(
        default=3,
        ge=1,
        le=4,
        description="Number of metric cards to generate (1-4)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Show Q4 performance: revenue growth 23%, customer acquisition up 45%, profit margin 18%",
                "count": 3,
                "gridWidth": 28,
                "gridHeight": 8
            }
        }


class SequentialAtomicRequest(AtomicComponentRequest):
    """
    Request model for POST /v1.2/atomic/SEQUENTIAL

    Generates 1-6 numbered cards for steps, phases, or sequential items.
    Supports unitary elements (count=1) for modular composition.
    """
    count: int = Field(
        default=4,
        ge=1,
        le=6,
        description="Number of sequential steps to generate (1-6)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "4-step employee onboarding process: orientation, training, mentorship, evaluation",
                "count": 4,
                "gridWidth": 28,
                "gridHeight": 10
            }
        }


class ComparisonAtomicRequest(AtomicComponentRequest):
    """
    Request model for POST /v1.2/atomic/COMPARISON

    Generates 1-4 comparison columns with flexible item counts.
    Supports unitary elements (count=1) for modular composition.
    """
    count: int = Field(
        default=3,
        ge=1,
        le=4,
        description="Number of comparison columns (1-4)"
    )
    items_per_column: int = Field(
        default=5,
        ge=1,
        le=7,
        description="Number of comparison items per column (1-7)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Compare our Standard, Professional, and Enterprise plans",
                "count": 3,
                "items_per_column": 5,
                "gridWidth": 28,
                "gridHeight": 14
            }
        }


class SectionsAtomicRequest(AtomicComponentRequest):
    """
    Request model for POST /v1.2/atomic/SECTIONS

    Generates 1-5 colored sections with flexible bullet counts.
    Supports unitary elements (count=1) for modular composition.
    """
    count: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Number of sections to generate (1-5)"
    )
    bullets_per_section: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Number of bullets per section (1-5)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Key benefits of our sustainability initiative: cost savings, brand reputation, environmental impact",
                "count": 3,
                "bullets_per_section": 4,
                "gridWidth": 24,
                "gridHeight": 12
            }
        }


class CalloutAtomicRequest(AtomicComponentRequest):
    """
    Request model for POST /v1.2/atomic/CALLOUT

    Generates 1-2 callout/sidebar boxes with flexible item counts.
    """
    count: int = Field(
        default=1,
        ge=1,
        le=2,
        description="Number of callout boxes (1-2)"
    )
    items_per_box: int = Field(
        default=4,
        ge=1,
        le=7,
        description="Number of items per callout box (1-7)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Key takeaways from our market analysis",
                "count": 1,
                "items_per_box": 5,
                "gridWidth": 10,
                "gridHeight": 12
            }
        }


class TextBulletsAtomicRequest(AtomicComponentRequest):
    """
    Request model for POST /v1.2/atomic/TEXT_BULLETS

    Generates 1-4 simple text boxes with subtitle and bullet points.
    Clean, minimal design for straightforward content presentation.
    """
    count: int = Field(
        default=2,
        ge=1,
        le=4,
        description="Number of text bullet boxes (1-4)"
    )
    bullets_per_box: int = Field(
        default=4,
        ge=1,
        le=7,
        description="Number of bullet points per box (1-7)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Key benefits and features of our new product line",
                "count": 2,
                "bullets_per_box": 4,
                "gridWidth": 24,
                "gridHeight": 10
            }
        }


class BulletBoxAtomicRequest(AtomicComponentRequest):
    """
    Request model for POST /v1.2/atomic/BULLET_BOX

    Generates 1-4 rectangular boxes with sharp corners and borders.
    Professional, structured appearance for formal content.
    """
    count: int = Field(
        default=2,
        ge=1,
        le=4,
        description="Number of bullet boxes (1-4)"
    )
    items_per_box: int = Field(
        default=5,
        ge=1,
        le=7,
        description="Number of items per box (1-7)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Project requirements and deliverables for Q1",
                "count": 2,
                "items_per_box": 5,
                "gridWidth": 24,
                "gridHeight": 12
            }
        }


class TableAtomicRequest(AtomicComponentRequest):
    """
    Request model for POST /v1.2/atomic/TABLE

    Generates 1-2 HTML tables with header row and data rows.
    Professional styling with alternating row colors.
    """
    count: int = Field(
        default=1,
        ge=1,
        le=2,
        description="Number of tables (1-2)"
    )
    columns: int = Field(
        default=3,
        ge=2,
        le=6,
        description="Number of columns per table (2-6)"
    )
    rows: int = Field(
        default=4,
        ge=2,
        le=10,
        description="Number of data rows per table (2-10)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Product comparison table: features, pricing, availability",
                "count": 1,
                "columns": 3,
                "rows": 4,
                "gridWidth": 28,
                "gridHeight": 10
            }
        }


class NumberedListAtomicRequest(AtomicComponentRequest):
    """
    Request model for POST /v1.2/atomic/NUMBERED_LIST

    Generates 1-4 numbered lists with title and ordered items.
    Clean numbered format for sequential or prioritized content.
    """
    count: int = Field(
        default=2,
        ge=1,
        le=4,
        description="Number of numbered lists (1-4)"
    )
    items_per_list: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of items per list (1-10)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Top priorities and action items for the quarter",
                "count": 2,
                "items_per_list": 5,
                "gridWidth": 24,
                "gridHeight": 12
            }
        }


# =============================================================================
# Response Models
# =============================================================================

class AtomicMetadata(BaseModel):
    """Metadata about atomic component generation."""

    model_config = {"protected_namespaces": ()}

    generation_time_ms: int = Field(
        ...,
        description="Time taken to generate content in milliseconds"
    )
    model_used: str = Field(
        ...,
        description="LLM model used for content generation"
    )
    grid_dimensions: Dict[str, int] = Field(
        ...,
        description="Grid dimensions used (width, height)"
    )
    space_category: str = Field(
        ...,
        description="Space category: 'small', 'medium', or 'large'"
    )
    scaling_factor: float = Field(
        ...,
        description="Character limit scaling factor applied (0.7-1.3)"
    )


class AtomicComponentResponse(BaseModel):
    """
    Response model for all atomic component endpoints.

    Returns generated HTML along with metadata about the generation.
    """
    success: bool = Field(
        ...,
        description="Whether generation succeeded"
    )
    html: Optional[str] = Field(
        None,
        description="Generated HTML string"
    )
    component_type: str = Field(
        ...,
        description="Atomic component type used (e.g., 'metrics_card')"
    )
    instance_count: int = Field(
        ...,
        description="Number of component instances generated"
    )
    arrangement: str = Field(
        ...,
        description="Layout arrangement used (e.g., 'row_3', 'stacked_4')"
    )
    variants_used: List[str] = Field(
        ...,
        description="Color variants applied to each instance"
    )
    character_counts: Dict[str, List[int]] = Field(
        ...,
        description="Character counts per slot per instance"
    )
    metadata: Optional[AtomicMetadata] = Field(
        None,
        description="Generation metadata (timing, model, scaling)"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if generation failed"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "html": "<div style=\"...\">...</div>",
                "component_type": "colored_section",
                "instance_count": 3,
                "arrangement": "stacked_3",
                "variants_used": ["blue", "green", "amber"],
                "character_counts": {
                    "section_heading": [18, 22, 20],
                    "bullet_1": [65, 58, 72],
                    "bullet_2": [61, 69, 64],
                    "bullet_3": [70, 62, 68]
                },
                "metadata": {
                    "generation_time_ms": 1250,
                    "model_used": "gemini-1.5-flash",
                    "grid_dimensions": {"width": 24, "height": 12},
                    "space_category": "large",
                    "scaling_factor": 1.05
                }
            }
        }
