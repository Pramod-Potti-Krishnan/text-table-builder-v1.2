"""
Service Coordination Models for Text & Table Builder v1.2

Pydantic models for Director Agent integration endpoints:
- GET /v1.2/capabilities - Service capabilities discovery
- POST /v1.2/can-handle - Content negotiation
- POST /v1.2/recommend-variant - Variant recommendations

These endpoints support the 4-Step Strawman Process:
1. Determine Storyline & Messages
2. Select Layouts
3. Select Content Variants (uses these endpoints)
4. Refine & Personalize
"""

from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field


# =============================================================================
# Service Capabilities (GET /capabilities)
# =============================================================================

class ServiceCapabilities(BaseModel):
    """Text Service capabilities for content generation."""
    slide_types: List[str] = Field(
        ...,
        description="Slide types this service can handle"
    )
    variants: List[str] = Field(
        ...,
        description="Content variants this service supports"
    )
    max_items_per_slide: int = Field(
        default=8,
        description="Maximum topic items per slide"
    )
    supports_themes: bool = Field(
        default=False,
        description="Whether service supports theme integration"
    )
    parallel_generation: bool = Field(
        default=True,
        description="Whether service supports parallel content generation"
    )


class ContentSignals(BaseModel):
    """Signals for content routing decisions."""
    handles_well: List[str] = Field(
        ...,
        description="Content types this service excels at"
    )
    handles_poorly: List[str] = Field(
        ...,
        description="Content types to avoid routing to this service"
    )
    keywords: List[str] = Field(
        ...,
        description="Keywords that suggest this service"
    )


class ServiceEndpoints(BaseModel):
    """Available endpoints for this service."""
    # Coordination endpoints
    capabilities: str = Field(..., description="Capabilities endpoint")
    generate: str = Field(..., description="Main generation endpoint (34 variants)")
    can_handle: str = Field(..., description="Content negotiation endpoint")
    recommend_variant: str = Field(..., description="Variant recommendation endpoint")

    # =========================================================================
    # UNIFIED SLIDES API (RECOMMENDED - Layout Service aligned)
    # =========================================================================
    # H-series: Hero/title slides with SPEC-compliant structured fields
    slides_H1_generated: str = Field(default="POST /v1.2/slides/H1-generated", description="Full-bleed hero with AI background (hero_content)")
    slides_H1_structured: str = Field(default="POST /v1.2/slides/H1-structured", description="Title slide with structured fields + background_color")
    slides_H2_section: str = Field(default="POST /v1.2/slides/H2-section", description="Section divider with section_number + background_color")
    slides_H3_closing: str = Field(default="POST /v1.2/slides/H3-closing", description="Closing slide with contact_info + background_color")
    # C-series: Content slides with combined generation (67% LLM savings)
    slides_C1_text: str = Field(default="POST /v1.2/slides/C1-text", description="Content slide - combined title+subtitle+body generation")
    # I-series via unified router
    slides_I1: str = Field(default="POST /v1.2/slides/I1", description="I1 layout via unified router")
    slides_I2: str = Field(default="POST /v1.2/slides/I2", description="I2 layout via unified router")
    slides_I3: str = Field(default="POST /v1.2/slides/I3", description="I3 layout via unified router")
    slides_I4: str = Field(default="POST /v1.2/slides/I4", description="I4 layout via unified router")
    # L-series aliases for Layout Service compatibility
    slides_L29: str = Field(default="POST /v1.2/slides/L29", description="Alias for H1-generated (Layout Service naming)")
    slides_L25: str = Field(default="POST /v1.2/slides/L25", description="Alias for C1-text (Layout Service naming)")

    # =========================================================================
    # LEGACY ENDPOINTS (DEPRECATED - scheduled for removal ~March 2025)
    # =========================================================================
    # Hero slide endpoints - use /v1.2/slides/* instead
    hero_title: str = Field(..., description="[DEPRECATED] Use slides_H1_structured instead")
    hero_section: str = Field(..., description="[DEPRECATED] Use slides_H2_section instead")
    hero_closing: str = Field(..., description="[DEPRECATED] Use slides_H3_closing instead")
    # I-series layout endpoints - use /v1.2/slides/I* instead
    iseries_generate: str = Field(default="POST /v1.2/iseries/generate", description="[DEPRECATED] Use slides_I* instead")
    iseries_I1: str = Field(default="POST /v1.2/iseries/I1", description="[DEPRECATED] Use slides_I1 instead")
    iseries_I2: str = Field(default="POST /v1.2/iseries/I2", description="[DEPRECATED] Use slides_I2 instead")
    iseries_I3: str = Field(default="POST /v1.2/iseries/I3", description="[DEPRECATED] Use slides_I3 instead")
    iseries_I4: str = Field(default="POST /v1.2/iseries/I4", description="[DEPRECATED] Use slides_I4 instead")

    # =========================================================================
    # ELEMENT-LEVEL ENDPOINTS (Active - for granular generation)
    # =========================================================================
    element_text: str = Field(default="POST /api/ai/element/text", description="Generic text element generation")
    table_generate: str = Field(default="POST /api/ai/table/generate", description="Table generation endpoint")


class CapabilitiesResponse(BaseModel):
    """
    Response for GET /v1.2/capabilities endpoint.

    Returns service capabilities for Director Agent coordination.
    """
    service: str = Field(
        ...,
        description="Service identifier (kebab-case)"
    )
    version: str = Field(
        ...,
        description="Semantic version (e.g., '1.2.0')"
    )
    status: Literal["healthy", "degraded"] = Field(
        default="healthy",
        description="Current operational status"
    )
    capabilities: ServiceCapabilities = Field(
        ...,
        description="Service-specific capabilities"
    )
    content_signals: ContentSignals = Field(
        ...,
        description="Content routing signals"
    )
    endpoints: ServiceEndpoints = Field(
        ...,
        description="Available endpoints"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "service": "text-service",
                "version": "1.2.0",
                "status": "healthy",
                "capabilities": {
                    "slide_types": ["matrix", "grid", "comparison", "sequential", "metrics", "table", "hero", "timeline", "process"],
                    "variants": ["matrix_2x2", "matrix_2x3", "grid_2x3", "comparison_3col", "metrics_3col"],
                    "max_items_per_slide": 8,
                    "supports_themes": False,
                    "parallel_generation": True
                },
                "content_signals": {
                    "handles_well": ["structured_content", "bullet_points", "comparisons"],
                    "handles_poorly": ["charts", "data_visualization", "diagrams"],
                    "keywords": ["compare", "features", "benefits", "steps", "process"]
                },
                "endpoints": {
                    # Coordination
                    "capabilities": "GET /v1.2/capabilities",
                    "generate": "POST /v1.2/generate",
                    "can_handle": "POST /v1.2/can-handle",
                    "recommend_variant": "POST /v1.2/recommend-variant",
                    # UNIFIED SLIDES API (RECOMMENDED)
                    "slides_H1_generated": "POST /v1.2/slides/H1-generated",
                    "slides_H1_structured": "POST /v1.2/slides/H1-structured",
                    "slides_H2_section": "POST /v1.2/slides/H2-section",
                    "slides_H3_closing": "POST /v1.2/slides/H3-closing",
                    "slides_C1_text": "POST /v1.2/slides/C1-text",
                    "slides_I1": "POST /v1.2/slides/I1",
                    "slides_I2": "POST /v1.2/slides/I2",
                    "slides_I3": "POST /v1.2/slides/I3",
                    "slides_I4": "POST /v1.2/slides/I4",
                    "slides_L29": "POST /v1.2/slides/L29",
                    "slides_L25": "POST /v1.2/slides/L25",
                    # DEPRECATED (use unified slides instead)
                    "hero_title": "POST /v1.2/hero/title-with-image",
                    "hero_section": "POST /v1.2/hero/section-with-image",
                    "hero_closing": "POST /v1.2/hero/closing-with-image",
                    "iseries_generate": "POST /v1.2/iseries/generate",
                    "iseries_I1": "POST /v1.2/iseries/I1",
                    "iseries_I2": "POST /v1.2/iseries/I2",
                    "iseries_I3": "POST /v1.2/iseries/I3",
                    "iseries_I4": "POST /v1.2/iseries/I4",
                    # Element-level
                    "element_text": "POST /api/ai/element/text",
                    "table_generate": "POST /api/ai/table/generate"
                }
            }
        }


# =============================================================================
# Can-Handle (POST /can-handle)
# =============================================================================

class SlideContent(BaseModel):
    """Content for a single slide."""
    title: str = Field(
        ...,
        description="Slide title"
    )
    topics: List[str] = Field(
        ...,
        description="List of topic items/bullet points"
    )
    topic_count: int = Field(
        ...,
        ge=0,
        description="Number of topics"
    )


class ContentHints(BaseModel):
    """Hints about content type for routing decisions."""
    has_numbers: bool = Field(
        default=False,
        description="Content contains numerical data"
    )
    is_comparison: bool = Field(
        default=False,
        description="Content is comparative in nature"
    )
    is_time_based: bool = Field(
        default=False,
        description="Content represents time series data"
    )
    detected_keywords: List[str] = Field(
        default_factory=list,
        description="Keywords detected in content"
    )


class SubZone(BaseModel):
    """Sub-zone within a content area."""
    zone_id: str = Field(
        ...,
        description="Zone identifier (e.g., 'col_1', 'col_2')"
    )
    width: int = Field(
        ...,
        ge=0,
        description="Zone width in pixels"
    )
    height: int = Field(
        ...,
        ge=0,
        description="Zone height in pixels"
    )


class AvailableSpace(BaseModel):
    """Available space from layout for content placement."""
    width: int = Field(
        ...,
        ge=0,
        description="Available width in pixels"
    )
    height: int = Field(
        ...,
        ge=0,
        description="Available height in pixels"
    )
    sub_zones: Optional[List[SubZone]] = Field(
        default=None,
        description="Sub-zones for multi-column layouts"
    )
    layout_id: Optional[str] = Field(
        default=None,
        description="Layout identifier (e.g., 'L25', 'C01')"
    )


class CanHandleRequest(BaseModel):
    """
    Request for POST /v1.2/can-handle endpoint.

    Ask service: "Can you handle this specific content within the given space?"
    """
    slide_content: SlideContent = Field(
        ...,
        description="Content to be placed"
    )
    content_hints: ContentHints = Field(
        ...,
        description="Hints about content type"
    )
    available_space: AvailableSpace = Field(
        ...,
        description="Available space from layout"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "slide_content": {
                    "title": "Q4 Revenue Analysis",
                    "topics": ["Revenue grew 15%", "New markets contributed 30%", "Cost reduction achieved"],
                    "topic_count": 3
                },
                "content_hints": {
                    "has_numbers": True,
                    "is_comparison": False,
                    "is_time_based": False,
                    "detected_keywords": ["revenue", "growth", "percentage"]
                },
                "available_space": {
                    "width": 1800,
                    "height": 750,
                    "sub_zones": [
                        {"zone_id": "col_1", "width": 560, "height": 750},
                        {"zone_id": "col_2", "width": 560, "height": 750},
                        {"zone_id": "col_3", "width": 560, "height": 750}
                    ]
                }
            }
        }


class SpaceUtilization(BaseModel):
    """Space utilization assessment."""
    fits_well: bool = Field(
        ...,
        description="Whether content fits well in available space"
    )
    estimated_fill_percent: int = Field(
        ...,
        ge=0,
        le=100,
        description="Estimated space utilization percentage"
    )


class CanHandleResponse(BaseModel):
    """
    Response for POST /v1.2/can-handle endpoint.

    Returns confidence score and reasoning for content handling.
    """
    can_handle: bool = Field(
        ...,
        description="Whether service can handle this content"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0 - 1.0)"
    )
    reason: str = Field(
        ...,
        description="Human-readable explanation"
    )
    suggested_approach: str = Field(
        ...,
        description="Suggested slide type/approach"
    )
    space_utilization: SpaceUtilization = Field(
        ...,
        description="Space utilization assessment"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "can_handle": True,
                "confidence": 0.85,
                "reason": "3 KPI metrics with numerical data - fits well in 3-column 560px zones",
                "suggested_approach": "metrics",
                "space_utilization": {
                    "fits_well": True,
                    "estimated_fill_percent": 85
                }
            }
        }


# =============================================================================
# Recommend-Variant (POST /recommend-variant)
# =============================================================================

class RecommendVariantRequest(BaseModel):
    """
    Request for POST /v1.2/recommend-variant endpoint.

    Ask service: "What variants do you recommend for this content?"
    """
    slide_content: SlideContent = Field(
        ...,
        description="Content to be placed"
    )
    available_space: AvailableSpace = Field(
        ...,
        description="Available space from layout"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "slide_content": {
                    "title": "Key Metrics",
                    "topics": ["Revenue: $4.2M", "Users: 50K", "NPS: 72"],
                    "topic_count": 3
                },
                "available_space": {
                    "width": 1800,
                    "height": 750,
                    "layout_id": "C01"
                }
            }
        }


class VariantRecommendation(BaseModel):
    """A recommended variant with confidence and reasoning."""
    variant_id: str = Field(
        ...,
        description="Variant identifier (e.g., 'metrics_3col')"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0 - 1.0)"
    )
    reason: str = Field(
        ...,
        description="Why this variant is recommended"
    )
    requires_space: Dict[str, int] = Field(
        ...,
        description="Space required for this variant {'width': px, 'height': px}"
    )


class NotRecommended(BaseModel):
    """A variant that is not recommended with reasoning."""
    variant_id: str = Field(
        ...,
        description="Variant identifier"
    )
    reason: str = Field(
        ...,
        description="Why this variant is not recommended"
    )


class RecommendVariantResponse(BaseModel):
    """
    Response for POST /v1.2/recommend-variant endpoint.

    Returns ranked variant recommendations and excluded variants.
    """
    recommended_variants: List[VariantRecommendation] = Field(
        ...,
        description="Ranked list of recommended variants"
    )
    not_recommended: List[NotRecommended] = Field(
        default_factory=list,
        description="Variants not recommended with reasons"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "recommended_variants": [
                    {
                        "variant_id": "metrics_3col",
                        "confidence": 0.92,
                        "reason": "3 KPIs with numbers, fits perfectly in 1800x750 space",
                        "requires_space": {"width": 1680, "height": 600}
                    },
                    {
                        "variant_id": "comparison_3col",
                        "confidence": 0.70,
                        "reason": "3 items could compare",
                        "requires_space": {"width": 1680, "height": 650}
                    }
                ],
                "not_recommended": [
                    {"variant_id": "grid_2x3", "reason": "Needs 6 topics, only 3 provided"}
                ]
            }
        }
