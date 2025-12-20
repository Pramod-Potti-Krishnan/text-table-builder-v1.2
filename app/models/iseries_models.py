"""
I-Series Layout Models for Text Service v1.2

Pydantic models for I-series layout generation endpoints (I1, I2, I3, I4).
These layouts combine portrait images with text content side by side.

Layout Specifications:
- I1: Wide image (660x1080) on LEFT, content (1200x840) on right
- I2: Wide image (660x1080) on RIGHT, content (1140x840) on left
- I3: Narrow image (360x1080) on LEFT, content (1500x840) on right
- I4: Narrow image (360x1080) on RIGHT, content (1440x840) on left
"""

from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel, Field
from enum import Enum


class ISeriesLayoutType(str, Enum):
    """I-series layout variants."""
    I1 = "I1"  # Image left (wide) - 660x1080 image
    I2 = "I2"  # Image right (wide) - 660x1080 image
    I3 = "I3"  # Image left (narrow) - 360x1080 image
    I4 = "I4"  # Image right (narrow) - 360x1080 image


class ISeriesVisualStyle(str, Enum):
    """Visual styles for I-series images (same as hero slides)."""
    PROFESSIONAL = "professional"  # Photorealistic, corporate
    ILLUSTRATED = "illustrated"    # Ghibli-style, anime
    KIDS = "kids"                  # Bright, playful, cartoon


class ISeriesContentStyle(str, Enum):
    """Content style for the text area."""
    BULLETS = "bullets"       # Bullet point list
    PARAGRAPHS = "paragraphs" # Paragraph format
    MIXED = "mixed"           # Combination of both


class ISeriesGenerationRequest(BaseModel):
    """
    Request model for I-series layout generation.

    Generates both image and text content in parallel.
    """
    # Required fields
    slide_number: int = Field(
        ...,
        description="Slide number in presentation",
        ge=1
    )
    layout_type: ISeriesLayoutType = Field(
        ...,
        description="I-series layout: I1, I2, I3, I4"
    )
    title: str = Field(
        ...,
        description="Slide title text",
        min_length=1,
        max_length=200
    )
    narrative: str = Field(
        ...,
        description="Narrative/topic for content generation",
        min_length=1
    )

    # Optional content fields
    topics: List[str] = Field(
        default_factory=list,
        description="Key topics to cover in content"
    )
    subtitle: Optional[str] = Field(
        default=None,
        description="Optional subtitle text"
    )

    # Image configuration
    image_prompt_hint: Optional[str] = Field(
        default=None,
        description="Optional specific hint for image generation"
    )
    visual_style: ISeriesVisualStyle = Field(
        default=ISeriesVisualStyle.ILLUSTRATED,
        description="Visual style: illustrated (default), professional, kids"
    )

    # Content configuration
    content_style: ISeriesContentStyle = Field(
        default=ISeriesContentStyle.BULLETS,
        description="Content style for the text area"
    )
    max_bullets: int = Field(
        default=5,
        ge=3,
        le=8,
        description="Maximum bullet points (if bullets style)"
    )

    # Context
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context: theme, audience, presentation_title, etc."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "slide_number": 3,
                "layout_type": "I1",
                "title": "Key Benefits of Our Solution",
                "narrative": "Our platform delivers three core advantages: speed, reliability, and cost savings",
                "topics": ["50% faster processing", "99.9% uptime", "30% cost reduction"],
                "visual_style": "illustrated",
                "content_style": "bullets",
                "max_bullets": 5,
                "context": {
                    "theme": "professional",
                    "audience": "business executives"
                }
            }
        }


class ISeriesGenerationResponse(BaseModel):
    """
    Response model for I-series layout generation.

    Returns structured HTML content for each slot plus metadata.
    """
    # HTML content for each slot
    image_html: str = Field(
        ...,
        description="HTML for image slot with img tag or placeholder"
    )
    title_html: str = Field(
        ...,
        description="HTML for title slot"
    )
    subtitle_html: Optional[str] = Field(
        default=None,
        description="HTML for subtitle slot (if provided)"
    )
    content_html: str = Field(
        ...,
        description="HTML for main content area (bullets/paragraphs)"
    )

    # Image metadata
    image_url: Optional[str] = Field(
        default=None,
        description="Generated image URL (None if fallback)"
    )
    image_fallback: bool = Field(
        default=False,
        description="True if using placeholder instead of generated image"
    )

    # SPEC-COMPLIANT: Background color for I-series slides
    # Per SLIDE_GENERATION_INPUT_SPEC.md: default #ffffff for I-series
    # background_image NOT recommended (conflicts with layout's primary image)
    background_color: str = Field(
        default="#ffffff",
        description="Hex background color (default: #ffffff for I-series)"
    )

    # Generation metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Generation metadata: timings, validation, layout info"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "image_html": "<div style='width:100%;height:100%'><img src='https://...' style='width:100%;height:100%;object-fit:cover'/></div>",
                "title_html": "<h2 style='font-size:2.5rem;font-weight:600;color:#1f2937;'>Key Benefits</h2>",
                "subtitle_html": "<p style='font-size:1.5rem;color:#6b7280;'>Transform your operations</p>",
                "content_html": "<ul class='content-list' style='list-style-type:disc;margin-left:24px;'><li>50% faster processing</li><li>99.9% uptime</li></ul>",
                "image_url": "https://storage.googleapis.com/...",
                "image_fallback": False,
                "background_color": "#ffffff",
                "metadata": {
                    "layout_type": "I1",
                    "slide_number": 3,
                    "image_position": "left",
                    "image_dimensions": {"width": 660, "height": 1080},
                    "content_dimensions": {"width": 1200, "height": 840},
                    "generation_time_ms": 12500,
                    "visual_style": "illustrated"
                }
            }
        }


# Layout dimension constants for reference
ISERIES_DIMENSIONS = {
    "I1": {
        "image_position": "left",
        "image_width": 660,
        "image_height": 1080,
        "content_width": 1200,
        "content_height": 840,
        "description": "Wide image left, content right"
    },
    "I2": {
        "image_position": "right",
        "image_width": 660,
        "image_height": 1080,
        "content_width": 1140,
        "content_height": 840,
        "description": "Wide image right, content left"
    },
    "I3": {
        "image_position": "left",
        "image_width": 360,
        "image_height": 1080,
        "content_width": 1500,
        "content_height": 840,
        "description": "Narrow image left, content right"
    },
    "I4": {
        "image_position": "right",
        "image_width": 360,
        "image_height": 1080,
        "content_width": 1440,
        "content_height": 840,
        "description": "Narrow image right, content left"
    }
}


def get_layout_dimensions(layout_type: ISeriesLayoutType) -> Dict[str, Any]:
    """
    Get dimensions for a specific I-series layout type.

    Args:
        layout_type: I-series layout type (I1, I2, I3, I4)

    Returns:
        Dictionary with image and content dimensions
    """
    return ISERIES_DIMENSIONS.get(layout_type.value, ISERIES_DIMENSIONS["I1"])
