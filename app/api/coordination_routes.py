"""
Service Coordination Routes for Text & Table Builder v1.3

Implements Director Agent integration endpoints:
- GET /v1.2/capabilities - Service capabilities discovery
- POST /v1.2/can-handle - Content negotiation
- POST /v1.2/recommend-variant - Variant recommendations

These endpoints support the 4-Step Strawman Process for intelligent
content routing and layout selection.

v1.3.0 Updates:
- supports_themes=True (theme_config, content_context, styling_mode, available_space)
- Multi-step content generation with ~85% space utilization
- CSS class output mode (styling_mode="css_classes")
- Theme registry sync with Layout Service
"""

from fastapi import APIRouter
from app.models.coordination_models import (
    CapabilitiesResponse,
    ServiceCapabilities,
    ContentSignals,
    ServiceEndpoints,
    CanHandleRequest,
    CanHandleResponse,
    SpaceUtilization,
    RecommendVariantRequest,
    RecommendVariantResponse,
    VariantRecommendation,
    NotRecommended,
)
from app.core.coordination import ContentAnalyzer


# =============================================================================
# Router Configuration
# =============================================================================

router = APIRouter(prefix="/v1.2", tags=["coordination"])


# =============================================================================
# Service Configuration
# =============================================================================

SERVICE_VERSION = "1.3.0"

# 10 slide types supported by Text Service
SUPPORTED_SLIDE_TYPES = [
    "matrix",        # 2 variants
    "grid",          # 9 variants
    "comparison",    # 3 variants
    "sequential",    # 3 variants
    "asymmetric",    # 3 variants
    "hybrid",        # 2 variants
    "metrics",       # 4 variants
    "impact_quote",  # 1 variant
    "table",         # 4 variants
    "single_column"  # 3 variants
]

# All 34 content variants from variant_index.json
SUPPORTED_VARIANTS = [
    # Matrix (2)
    "matrix_2x2", "matrix_2x3",
    # Grid (9)
    "grid_2x3", "grid_3x2", "grid_2x2_centered",
    "grid_2x3_left", "grid_3x2_left", "grid_2x2_left",
    "grid_2x3_numbered", "grid_3x2_numbered", "grid_2x2_numbered",
    # Comparison (3)
    "comparison_2col", "comparison_3col", "comparison_4col",
    # Sequential (3)
    "sequential_3col", "sequential_4col", "sequential_5col",
    # Asymmetric (3)
    "asymmetric_8_4_3section", "asymmetric_8_4_4section", "asymmetric_8_4_5section",
    # Hybrid (2)
    "hybrid_top_2x2", "hybrid_left_2x2",
    # Metrics (4)
    "metrics_3col", "metrics_4col", "metrics_3x2_grid", "metrics_2x2_grid",
    # Impact Quote (1)
    "impact_quote",
    # Table (4)
    "table_2col", "table_3col", "table_4col", "table_5col",
    # Single Column (3)
    "single_column_3section", "single_column_4section", "single_column_5section"
]

# Hero slide endpoints (6 endpoints: 3 standard + 3 image-enhanced)
# Standard hero (gradient backgrounds): title, section, closing
# Image-enhanced (3 visual styles each): title-with-image, section-with-image, closing-with-image
HERO_SLIDE_TYPES = ["title_slide", "section_divider", "closing_slide"]
HERO_VISUAL_STYLES = ["professional", "illustrated", "kids"]
# Total hero variations: 3 standard + (3 types × 3 styles) = 3 + 9 = 12

# I-series layout endpoints (7 endpoints: 5 generation + 2 info)
# Combined image + text generation with portrait images (9:16 aspect ratio)
ISERIES_LAYOUT_TYPES = ["I1", "I2", "I3", "I4"]
ISERIES_VISUAL_STYLES = ["professional", "illustrated", "kids"]
ISERIES_CONTENT_STYLES = ["bullets", "paragraphs", "mixed"]
# Total I-series variations: 4 layouts × 3 visual styles = 12 variations

HANDLES_WELL = [
    "structured_content",
    "bullet_points",
    "comparisons",
    "processes",
    "features_benefits",
    "step_by_step",
    "key_metrics",
    "tabular_data"
]

HANDLES_POORLY = [
    "charts",
    "data_visualization",
    "diagrams",
    "infographics",
    "time_series",
    "statistical_analysis"
]

KEYWORDS = [
    "compare", "features", "benefits", "steps", "process",
    "matrix", "grid", "table", "metrics", "KPIs",
    "overview", "summary", "highlights", "pros", "cons",
    "timeline", "sequence", "workflow"
]


# =============================================================================
# Content Analyzer Instance
# =============================================================================

content_analyzer = ContentAnalyzer()


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/capabilities", response_model=CapabilitiesResponse)
async def get_capabilities():
    """
    Return Text Service capabilities for Director Agent coordination.

    This endpoint is called by Strawman Service at startup to cache
    service capabilities and inform content routing decisions.

    Returns:
        CapabilitiesResponse: Service capabilities, content signals, and endpoints
    """
    return CapabilitiesResponse(
        service="text-service",
        version=SERVICE_VERSION,
        status="healthy",
        capabilities=ServiceCapabilities(
            slide_types=SUPPORTED_SLIDE_TYPES,
            variants=SUPPORTED_VARIANTS,
            max_items_per_slide=8,
            supports_themes=True,  # v1.3.0: theme_config, content_context, styling_mode
            parallel_generation=True
        ),
        content_signals=ContentSignals(
            handles_well=HANDLES_WELL,
            handles_poorly=HANDLES_POORLY,
            keywords=KEYWORDS
        ),
        endpoints=ServiceEndpoints(
            # Coordination endpoints
            capabilities="GET /v1.2/capabilities",
            generate="POST /v1.2/generate",
            can_handle="POST /v1.2/can-handle",
            recommend_variant="POST /v1.2/recommend-variant",
            # UNIFIED SLIDES API (RECOMMENDED - Layout Service aligned)
            slides_H1_generated="POST /v1.2/slides/H1-generated",
            slides_H1_structured="POST /v1.2/slides/H1-structured",
            slides_H2_section="POST /v1.2/slides/H2-section",
            slides_H3_closing="POST /v1.2/slides/H3-closing",
            slides_C1_text="POST /v1.2/slides/C1-text",
            slides_I1="POST /v1.2/slides/I1",
            slides_I2="POST /v1.2/slides/I2",
            slides_I3="POST /v1.2/slides/I3",
            slides_I4="POST /v1.2/slides/I4",
            slides_L29="POST /v1.2/slides/L29",
            slides_L25="POST /v1.2/slides/L25",
            # DEPRECATED endpoints (use unified slides instead, removal ~March 2025)
            hero_title="POST /v1.2/hero/title-with-image",
            hero_section="POST /v1.2/hero/section-with-image",
            hero_closing="POST /v1.2/hero/closing-with-image",
            iseries_generate="POST /v1.2/iseries/generate",
            iseries_I1="POST /v1.2/iseries/I1",
            iseries_I2="POST /v1.2/iseries/I2",
            iseries_I3="POST /v1.2/iseries/I3",
            iseries_I4="POST /v1.2/iseries/I4",
            # Element-level endpoints
            element_text="POST /api/ai/element/text",
            table_generate="POST /api/ai/table/generate"
        )
    )


@router.post("/can-handle", response_model=CanHandleResponse)
async def can_handle(request: CanHandleRequest):
    """
    Determine if Text Service can handle the given content.

    This endpoint answers "Can you handle this specific content within
    the given space?" for the Strawman Service content routing decision.

    Confidence Score Guidelines:
    - 0.90+: Excellent fit, high confidence
    - 0.70-0.89: Good fit, can handle well
    - 0.50-0.69: Acceptable, but other services might be better
    - < 0.50: Poor fit, prefer other service

    Args:
        request: CanHandleRequest with slide_content, content_hints, and available_space

    Returns:
        CanHandleResponse: can_handle flag, confidence score, and reasoning
    """
    # Extract request data
    slide_content = request.slide_content
    content_hints = request.content_hints
    available_space = request.available_space

    # Calculate confidence score
    confidence = content_analyzer.calculate_confidence(
        topic_count=slide_content.topic_count,
        detected_keywords=content_hints.detected_keywords,
        has_numbers=content_hints.has_numbers,
        is_comparison=content_hints.is_comparison,
        is_time_based=content_hints.is_time_based
    )

    # Analyze content type for approach suggestion
    suggested_approach = content_analyzer.analyze_content_type(
        topics=slide_content.topics,
        detected_keywords=content_hints.detected_keywords,
        has_numbers=content_hints.has_numbers,
        is_comparison=content_hints.is_comparison
    )

    # Check space utilization
    # Try to find a fitting variant to assess space usage
    sub_zones_list = None
    if available_space.sub_zones:
        sub_zones_list = [
            {"zone_id": z.zone_id, "width": z.width, "height": z.height}
            for z in available_space.sub_zones
        ]

    recommended, _ = content_analyzer.get_variant_recommendations(
        topic_count=slide_content.topic_count,
        available_width=available_space.width,
        available_height=available_space.height,
        layout_id=available_space.layout_id,
        suggested_type=suggested_approach
    )

    # Determine space utilization
    if recommended:
        best_variant = recommended[0]
        required_width = best_variant["requires_space"]["width"]
        required_height = best_variant["requires_space"]["height"]
        fill_percent = int(
            ((required_width / available_space.width) +
             (required_height / available_space.height)) / 2 * 100
        )
        fits_well = fill_percent >= 60
    else:
        fits_well = False
        fill_percent = 0

    # Determine can_handle threshold
    can_handle_flag = confidence >= 0.5 and len(recommended) > 0

    # Build reason string
    if can_handle_flag:
        zone_info = ""
        if sub_zones_list and len(sub_zones_list) > 0:
            zone_info = f" in {len(sub_zones_list)}-column {sub_zones_list[0]['width']}px zones"
        reason = f"{slide_content.topic_count} {suggested_approach} items{zone_info} - confidence {confidence:.2f}"
    else:
        if len(recommended) == 0:
            reason = f"No suitable variants for {slide_content.topic_count} topics in {available_space.width}x{available_space.height}px space"
        else:
            reason = f"Low confidence ({confidence:.2f}) - content may be better suited for another service"

    return CanHandleResponse(
        can_handle=can_handle_flag,
        confidence=round(confidence, 2),
        reason=reason,
        suggested_approach=suggested_approach,
        space_utilization=SpaceUtilization(
            fits_well=fits_well,
            estimated_fill_percent=fill_percent
        )
    )


@router.post("/recommend-variant", response_model=RecommendVariantResponse)
async def recommend_variant(request: RecommendVariantRequest):
    """
    Recommend best text variants for the content.

    This endpoint returns ranked variant recommendations based on
    topic count, content analysis, and available space from the layout.

    Args:
        request: RecommendVariantRequest with slide_content and available_space

    Returns:
        RecommendVariantResponse: Ranked recommendations and not-recommended variants
    """
    # Extract request data
    slide_content = request.slide_content
    available_space = request.available_space

    # Analyze content type
    suggested_type = content_analyzer.analyze_content_type(
        topics=slide_content.topics,
        detected_keywords=[],  # No hints in this request
        has_numbers=any(
            any(c.isdigit() for c in topic)
            for topic in slide_content.topics
        ),
        is_comparison=False
    )

    # Get recommendations
    recommended_raw, not_recommended_raw = content_analyzer.get_variant_recommendations(
        topic_count=slide_content.topic_count,
        available_width=available_space.width,
        available_height=available_space.height,
        layout_id=available_space.layout_id,
        suggested_type=suggested_type
    )

    # Convert to response models
    recommended_variants = [
        VariantRecommendation(
            variant_id=rec["variant_id"],
            confidence=rec["confidence"],
            reason=rec["reason"],
            requires_space=rec["requires_space"]
        )
        for rec in recommended_raw[:5]  # Top 5 recommendations
    ]

    not_recommended = [
        NotRecommended(
            variant_id=nr["variant_id"],
            reason=nr["reason"]
        )
        for nr in not_recommended_raw[:5]  # Top 5 not-recommended
    ]

    return RecommendVariantResponse(
        recommended_variants=recommended_variants,
        not_recommended=not_recommended
    )
