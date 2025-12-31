"""
Atomic Component API Routes for Text & Table Builder v1.2
==========================================================

Provides dedicated endpoints for direct atomic component generation
at /v1.2/atomic/{TYPE} paths. These endpoints bypass the Chain of Thought
reasoning layer for deterministic, fast generation with explicit parameterization.

Endpoints:
- POST /v1.2/atomic/METRICS - Generate 2-4 metric cards
- POST /v1.2/atomic/SEQUENTIAL - Generate 2-6 numbered steps
- POST /v1.2/atomic/COMPARISON - Generate 2-4 comparison columns
- POST /v1.2/atomic/SECTIONS - Generate 2-5 colored sections
- POST /v1.2/atomic/CALLOUT - Generate 1-2 callout boxes

Features:
- Explicit control over component type and count
- Flexible bullet/item counts for SECTIONS, COMPARISON, CALLOUT
- Grid-based space calculation (32x18 system)
- Context-aware content generation

v1.0.0: Initial atomic component endpoints
"""

import asyncio
import logging
from typing import Callable

from fastapi import APIRouter, Depends, HTTPException

from app.core.components.atomic_generator import AtomicComponentGenerator
from app.models.atomic_models import (
    AtomicType,
    ATOMIC_TYPE_MAP,
    AtomicComponentResponse,
    AtomicMetadata,
    MetricsAtomicRequest,
    SequentialAtomicRequest,
    ComparisonAtomicRequest,
    SectionsAtomicRequest,
    CalloutAtomicRequest
)
from app.services import create_llm_callable_async

logger = logging.getLogger(__name__)

# Create router for Atomic Component endpoints
router = APIRouter(prefix="/v1.2/atomic", tags=["atomic", "components"])


# =============================================================================
# Dependencies
# =============================================================================

def get_async_llm_service() -> Callable:
    """
    Get async LLM service for atomic component generation.

    Uses Vertex AI with Application Default Credentials (ADC).

    Returns:
        Async callable that takes prompt string and returns content string
    """
    return create_llm_callable_async()


def get_atomic_generator(
    llm_service: Callable = Depends(get_async_llm_service)
) -> AtomicComponentGenerator:
    """Create AtomicComponentGenerator instance."""
    return AtomicComponentGenerator(llm_service=llm_service)


# =============================================================================
# Helper Functions
# =============================================================================

def _build_response(result) -> AtomicComponentResponse:
    """Convert AtomicResult to AtomicComponentResponse."""
    return AtomicComponentResponse(
        success=result.success,
        html=result.html if result.success else None,
        component_type=result.component_type,
        instance_count=result.instance_count,
        arrangement=result.arrangement,
        variants_used=result.variants_used,
        character_counts=result.character_counts,
        metadata=result.metadata,
        error=result.error
    )


# =============================================================================
# POST /v1.2/atomic/METRICS
# =============================================================================

@router.post("/METRICS", response_model=AtomicComponentResponse)
async def generate_metrics(
    request: MetricsAtomicRequest,
    generator: AtomicComponentGenerator = Depends(get_atomic_generator)
) -> AtomicComponentResponse:
    """
    Generate METRICS atomic component (2-4 gradient metric cards).

    Each metric card contains:
    - metric_number: The main value (e.g., "95%", "$2.4M", "1.2x")
    - metric_label: Short UPPERCASE label (e.g., "REVENUE GROWTH")
    - metric_description: Supporting context sentence

    **Request Body**:
    - prompt: Content request describing metrics to generate
    - count: Number of metric cards (2-4, default: 3)
    - gridWidth: Available width in grid units (4-32)
    - gridHeight: Available height in grid units (4-18)
    - context: Optional slide/presentation context
    - variant: Optional specific color variant

    **Example Request**:
    ```json
    {
        "prompt": "Q4 performance: revenue up 23%, customers grew 45%, margin improved to 18%",
        "count": 3,
        "gridWidth": 28,
        "gridHeight": 8
    }
    ```

    **Color Variants**: purple, pink, cyan, green
    """
    try:
        result = await generator.generate(
            component_type=ATOMIC_TYPE_MAP[AtomicType.METRICS],
            prompt=request.prompt,
            count=request.count,
            grid_width=request.gridWidth,
            grid_height=request.gridHeight,
            items_per_instance=None,  # Metrics don't have flexible items
            context=request.context,
            variant=request.variant
        )
        return _build_response(result)

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="LLM request timed out")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ATOMIC-METRICS-ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# POST /v1.2/atomic/SEQUENTIAL
# =============================================================================

@router.post("/SEQUENTIAL", response_model=AtomicComponentResponse)
async def generate_sequential(
    request: SequentialAtomicRequest,
    generator: AtomicComponentGenerator = Depends(get_atomic_generator)
) -> AtomicComponentResponse:
    """
    Generate SEQUENTIAL atomic component (2-6 numbered step cards).

    Each numbered card contains:
    - card_number: Step number (1-6)
    - card_title: Step title (e.g., "Discovery Phase")
    - card_description: Detailed explanation

    **Request Body**:
    - prompt: Content request describing the process/steps
    - count: Number of steps (2-6, default: 4)
    - gridWidth: Available width in grid units (4-32)
    - gridHeight: Available height in grid units (4-18)
    - context: Optional slide/presentation context
    - variant: Optional specific color variant

    **Example Request**:
    ```json
    {
        "prompt": "Employee onboarding process: orientation, training, mentorship, evaluation",
        "count": 4,
        "gridWidth": 28,
        "gridHeight": 10
    }
    ```

    **Color Variants**: blue, green, yellow, pink
    """
    try:
        result = await generator.generate(
            component_type=ATOMIC_TYPE_MAP[AtomicType.SEQUENTIAL],
            prompt=request.prompt,
            count=request.count,
            grid_width=request.gridWidth,
            grid_height=request.gridHeight,
            items_per_instance=None,  # Sequential cards don't have flexible items
            context=request.context,
            variant=request.variant
        )
        return _build_response(result)

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="LLM request timed out")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ATOMIC-SEQUENTIAL-ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# POST /v1.2/atomic/COMPARISON
# =============================================================================

@router.post("/COMPARISON", response_model=AtomicComponentResponse)
async def generate_comparison(
    request: ComparisonAtomicRequest,
    generator: AtomicComponentGenerator = Depends(get_atomic_generator)
) -> AtomicComponentResponse:
    """
    Generate COMPARISON atomic component (2-4 comparison columns).

    Each comparison column contains:
    - column_heading: Column title (e.g., "Option A", "Pros", "Before")
    - item_1 through item_N: Comparison points (1-7 items per column)

    **Request Body**:
    - prompt: Content request describing comparison
    - count: Number of columns (2-4, default: 3)
    - items_per_column: Items per column (1-7, default: 5)
    - gridWidth: Available width in grid units (4-32)
    - gridHeight: Available height in grid units (4-18)
    - context: Optional slide/presentation context
    - variant: Optional specific color variant

    **Example Request**:
    ```json
    {
        "prompt": "Compare Standard, Professional, and Enterprise pricing plans",
        "count": 3,
        "items_per_column": 5,
        "gridWidth": 28,
        "gridHeight": 14
    }
    ```

    **Color Variants**: blue, red, green, purple, orange
    """
    try:
        result = await generator.generate(
            component_type=ATOMIC_TYPE_MAP[AtomicType.COMPARISON],
            prompt=request.prompt,
            count=request.count,
            grid_width=request.gridWidth,
            grid_height=request.gridHeight,
            items_per_instance=request.items_per_column,
            context=request.context,
            variant=request.variant
        )
        return _build_response(result)

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="LLM request timed out")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ATOMIC-COMPARISON-ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# POST /v1.2/atomic/SECTIONS
# =============================================================================

@router.post("/SECTIONS", response_model=AtomicComponentResponse)
async def generate_sections(
    request: SectionsAtomicRequest,
    generator: AtomicComponentGenerator = Depends(get_atomic_generator)
) -> AtomicComponentResponse:
    """
    Generate SECTIONS atomic component (2-5 colored sections with bullets).

    Each section contains:
    - section_heading: Section title (e.g., "Key Benefits", "Phase 1")
    - bullet_1 through bullet_N: Bullet points (1-5 bullets per section)

    **Request Body**:
    - prompt: Content request describing sections
    - count: Number of sections (2-5, default: 3)
    - bullets_per_section: Bullets per section (1-5, default: 3)
    - gridWidth: Available width in grid units (4-32)
    - gridHeight: Available height in grid units (4-18)
    - context: Optional slide/presentation context
    - variant: Optional specific color variant

    **Example Request**:
    ```json
    {
        "prompt": "Sustainability initiative benefits: cost savings, brand reputation, environmental impact",
        "count": 3,
        "bullets_per_section": 4,
        "gridWidth": 24,
        "gridHeight": 12
    }
    ```

    **Color Variants**: blue, red, green, amber, purple
    """
    try:
        result = await generator.generate(
            component_type=ATOMIC_TYPE_MAP[AtomicType.SECTIONS],
            prompt=request.prompt,
            count=request.count,
            grid_width=request.gridWidth,
            grid_height=request.gridHeight,
            items_per_instance=request.bullets_per_section,
            context=request.context,
            variant=request.variant
        )
        return _build_response(result)

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="LLM request timed out")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ATOMIC-SECTIONS-ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# POST /v1.2/atomic/CALLOUT
# =============================================================================

@router.post("/CALLOUT", response_model=AtomicComponentResponse)
async def generate_callout(
    request: CalloutAtomicRequest,
    generator: AtomicComponentGenerator = Depends(get_atomic_generator)
) -> AtomicComponentResponse:
    """
    Generate CALLOUT atomic component (1-2 sidebar/callout boxes).

    Each callout box contains:
    - sidebar_heading: Box heading (e.g., "Key Insights", "Remember")
    - item_1 through item_N: Bullet points (1-7 items per box)

    **Request Body**:
    - prompt: Content request describing callout content
    - count: Number of callout boxes (1-2, default: 1)
    - items_per_box: Items per box (1-7, default: 4)
    - gridWidth: Available width in grid units (4-32)
    - gridHeight: Available height in grid units (4-18)
    - context: Optional slide/presentation context
    - variant: Optional specific color variant

    **Example Request**:
    ```json
    {
        "prompt": "Key takeaways from our market analysis",
        "count": 1,
        "items_per_box": 5,
        "gridWidth": 10,
        "gridHeight": 12
    }
    ```

    **Color Variants**: blue, green, purple, amber
    """
    try:
        result = await generator.generate(
            component_type=ATOMIC_TYPE_MAP[AtomicType.CALLOUT],
            prompt=request.prompt,
            count=request.count,
            grid_width=request.gridWidth,
            grid_height=request.gridHeight,
            items_per_instance=request.items_per_box,
            context=request.context,
            variant=request.variant
        )
        return _build_response(result)

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="LLM request timed out")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ATOMIC-CALLOUT-ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# GET /v1.2/atomic/health
# =============================================================================

@router.get("/health")
async def atomic_health():
    """
    Health check for atomic component endpoints.

    Returns available atomic component types and their configurations.
    """
    return {
        "status": "healthy",
        "service": "atomic-components",
        "version": "1.0.0",
        "endpoints": {
            "METRICS": {
                "path": "/v1.2/atomic/METRICS",
                "component_id": "metrics_card",
                "count_range": "2-4",
                "flexible_items": False
            },
            "SEQUENTIAL": {
                "path": "/v1.2/atomic/SEQUENTIAL",
                "component_id": "numbered_card",
                "count_range": "2-6",
                "flexible_items": False
            },
            "COMPARISON": {
                "path": "/v1.2/atomic/COMPARISON",
                "component_id": "comparison_column",
                "count_range": "2-4",
                "flexible_items": True,
                "items_range": "1-7 items per column"
            },
            "SECTIONS": {
                "path": "/v1.2/atomic/SECTIONS",
                "component_id": "colored_section",
                "count_range": "2-5",
                "flexible_items": True,
                "items_range": "1-5 bullets per section"
            },
            "CALLOUT": {
                "path": "/v1.2/atomic/CALLOUT",
                "component_id": "sidebar_box",
                "count_range": "1-2",
                "flexible_items": True,
                "items_range": "1-7 items per box"
            }
        },
        "grid_system": {
            "columns": 32,
            "rows": 18,
            "cell_size_px": 60,
            "slide_dimensions": "1920x1080"
        }
    }


# =============================================================================
# GET /v1.2/atomic/components
# =============================================================================

@router.get("/components")
async def list_atomic_components():
    """
    List all available atomic component types.

    Returns detailed specifications for each atomic component.
    """
    return {
        "components": [
            {
                "type": "METRICS",
                "component_id": "metrics_card",
                "description": "Gradient-filled metric cards with large numbers, labels, and descriptions",
                "use_cases": ["KPIs", "statistics", "performance metrics", "data points"],
                "slots": ["metric_number", "metric_label", "metric_description"],
                "instance_range": {"min": 2, "max": 4},
                "variants": ["purple", "pink", "cyan", "green"],
                "flexible_items": False
            },
            {
                "type": "SEQUENTIAL",
                "component_id": "numbered_card",
                "description": "Numbered step cards for processes, phases, or sequential items",
                "use_cases": ["steps", "phases", "workflows", "processes"],
                "slots": ["card_number", "card_title", "card_description"],
                "instance_range": {"min": 2, "max": 6},
                "variants": ["blue", "green", "yellow", "pink"],
                "flexible_items": False
            },
            {
                "type": "COMPARISON",
                "component_id": "comparison_column",
                "description": "Comparison columns with headings and flexible item lists",
                "use_cases": ["comparisons", "pros/cons", "options", "alternatives"],
                "slots": ["column_heading", "item_1..item_N"],
                "instance_range": {"min": 2, "max": 4},
                "items_per_instance_range": {"min": 1, "max": 7},
                "variants": ["blue", "red", "green", "purple", "orange"],
                "flexible_items": True
            },
            {
                "type": "SECTIONS",
                "component_id": "colored_section",
                "description": "Colored sections with headings and flexible bullet lists",
                "use_cases": ["categories", "topics", "grouped content", "key points"],
                "slots": ["section_heading", "bullet_1..bullet_N"],
                "instance_range": {"min": 2, "max": 5},
                "items_per_instance_range": {"min": 1, "max": 5},
                "variants": ["blue", "red", "green", "amber", "purple"],
                "flexible_items": True
            },
            {
                "type": "CALLOUT",
                "component_id": "sidebar_box",
                "description": "Gradient callout boxes with headings and flexible item lists",
                "use_cases": ["key insights", "highlights", "takeaways", "tips"],
                "slots": ["sidebar_heading", "item_1..item_N"],
                "instance_range": {"min": 1, "max": 2},
                "items_per_instance_range": {"min": 1, "max": 7},
                "variants": ["blue", "green", "purple", "amber"],
                "flexible_items": True
            }
        ]
    }
