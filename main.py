#!/usr/bin/env python3
"""
Text & Table Builder v1.2 - Main Application Entry Point

This is the FastAPI application that serves the v1.2 deterministic assembly architecture
with Gemini integration via Vertex AI.

Run with:
    uvicorn main:app --reload --port 8000

Or:
    python3 main.py
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.api.v1_2_routes import router as v1_2_router
from app.api.hero_routes import router as hero_router
from app.api.layout_routes import router as layout_router
from app.api.async_routes import router as async_router
from app.api.coordination_routes import router as coordination_router
from app.api.iseries_routes import router as iseries_router
from app.api.slides_routes import router as slides_router

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("=" * 80)
    logger.info("Text & Table Builder v1.2 - Starting Up")
    logger.info("=" * 80)

    # Validate configuration
    validate_configuration()

    logger.info("✓ v1.2 Content API: /v1.2/generate (26 variants)")
    logger.info("✓ v1.2 Hero API (standard):")
    logger.info("  - /v1.2/hero/title (title slides)")
    logger.info("  - /v1.2/hero/section (section dividers)")
    logger.info("  - /v1.2/hero/closing (closing slides)")
    logger.info("✓ v1.2 Hero API (image-enhanced):")
    logger.info("  - /v1.2/hero/title-with-image (title with AI background)")
    logger.info("  - /v1.2/hero/section-with-image (section with AI background)")
    logger.info("  - /v1.2/hero/closing-with-image (closing with AI background)")
    logger.info("✓ Layout Service AI API:")
    logger.info("  - /api/ai/text/generate (generate text from prompt)")
    logger.info("  - /api/ai/text/transform (transform existing text)")
    logger.info("  - /api/ai/text/autofit (fit text to element)")
    logger.info("  - /api/ai/table/generate (generate table from prompt)")
    logger.info("  - /api/ai/table/transform (transform table structure)")
    logger.info("  - /api/ai/table/analyze (analyze table data)")
    logger.info("✓ Variant catalog: /v1.2/variants")
    logger.info("✓ Pool health: /v1.2/health/pool")
    logger.info("✓ Async Queue API (Redis-based):")
    logger.info("  - /v1.2/async/generate (submit job)")
    logger.info("  - /v1.2/async/status/{job_id} (poll progress)")
    logger.info("  - /v1.2/async/result/{job_id} (fetch result)")
    logger.info("  - /v1.2/async/queue/stats (queue health)")
    logger.info("✓ Service Coordination API (Director Agent):")
    logger.info("  - /v1.2/capabilities (service discovery)")
    logger.info("  - /v1.2/can-handle (content negotiation)")
    logger.info("  - /v1.2/recommend-variant (variant recommendations)")
    logger.info("✓ I-Series Layout API (image + text):")
    logger.info("  - /v1.2/iseries/generate (any I-series layout)")
    logger.info("  - /v1.2/iseries/I1 (wide image left)")
    logger.info("  - /v1.2/iseries/I2 (wide image right)")
    logger.info("  - /v1.2/iseries/I3 (narrow image left)")
    logger.info("  - /v1.2/iseries/I4 (narrow image right)")
    logger.info("✓ Unified Slides API (Layout Service aligned):")
    logger.info("  - /v1.2/slides/H1-generated (title with AI image)")
    logger.info("  - /v1.2/slides/H1-structured (title with gradient)")
    logger.info("  - /v1.2/slides/H2-section (section divider)")
    logger.info("  - /v1.2/slides/H3-closing (closing slide)")
    logger.info("  - /v1.2/slides/C1-text (combined generation - saves 2 LLM calls)")
    logger.info("  - /v1.2/slides/I1-I4 (image + text layouts)")
    logger.info("  - /v1.2/slides/L29 (alias for H1-generated)")
    logger.info("  - /v1.2/slides/L25 (alias for C1-text)")
    logger.info("✓ Gemini integration enabled")
    logger.info("✓ Image Builder API integration enabled")
    logger.info(f"✓ LLM Pool enabled: {os.getenv('USE_LLM_POOL', 'true')}")
    logger.info(f"✓ Redis Queue enabled: {os.getenv('ENABLE_REDIS_QUEUE', 'false')}")
    logger.info("=" * 80)

    yield

    # Shutdown
    logger.info("Text & Table Builder v1.2 - Shutting Down")


def validate_configuration():
    """Validate required configuration on startup."""
    issues = []

    # Check GCP_PROJECT_ID
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        issues.append("GCP_PROJECT_ID environment variable not set")
    else:
        logger.info(f"✓ GCP_PROJECT_ID: {project_id}")

    # Check credentials
    try:
        from google.auth import default
        credentials, project = default()
        logger.info(f"✓ Google Cloud credentials found")
        if project:
            logger.info(f"  Default project: {project}")
    except Exception as e:
        issues.append(f"Google Cloud credentials not found: {e}")

    # Check Vertex AI library
    try:
        import vertexai
        logger.info(f"✓ Vertex AI library installed")
    except ImportError:
        issues.append("Vertex AI library not installed (pip install google-cloud-aiplatform>=1.70.0)")

    # Log configuration
    logger.info(f"✓ Model routing: {os.getenv('ENABLE_MODEL_ROUTING', 'true')}")
    logger.info(f"✓ Flash model: {os.getenv('GEMINI_FLASH_MODEL', 'gemini-2.5-flash')}")
    logger.info(f"✓ Pro model: {os.getenv('GEMINI_PRO_MODEL', 'gemini-2.5-pro')}")
    logger.info(f"✓ Parallel generation: {os.getenv('ENABLE_PARALLEL_GENERATION', 'true')}")
    logger.info(f"✓ Max workers: {os.getenv('MAX_PARALLEL_WORKERS', '5')}")

    if issues:
        logger.error("⚠️  Configuration issues detected:")
        for issue in issues:
            logger.error(f"  - {issue}")
        logger.error("\nPlease check the README.md for setup instructions.")
        logger.error("For local development, ensure you have:")
        logger.error("  1. Google Cloud SDK installed")
        logger.error("  2. Authenticated: gcloud auth application-default login")
        logger.error("  3. Set GCP_PROJECT_ID environment variable")


# Create FastAPI app
app = FastAPI(
    title="Text & Table Builder v1.2",
    description="Deterministic assembly architecture with element-based content generation",
    version="1.2.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1.2 routes (content slides - element-based)
app.include_router(v1_2_router)

# Include v1.2 hero routes (hero slides with v1.2 architecture)
app.include_router(hero_router)

# Include Layout Service AI routes (text and table generation for Layout Service)
app.include_router(layout_router)

# Include async queue routes (Redis-based job queue for high-load scenarios)
app.include_router(async_router)

# Include coordination routes (Director Agent integration - service discovery)
app.include_router(coordination_router)

# Include I-series routes (image + text layouts)
app.include_router(iseries_router)

# Include unified slides routes (Layout Service aligned - H1, H2, H3, C1, I1-I4)
app.include_router(slides_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Text & Table Builder",
        "version": "1.2.0",
        "architecture": "Unified v1.2",
        "endpoints": {
            "content_slides": "POST /v1.2/generate",
            "hero_standard": {
                "title_slide": "POST /v1.2/hero/title",
                "section_divider": "POST /v1.2/hero/section",
                "closing_slide": "POST /v1.2/hero/closing"
            },
            "hero_image_enhanced": {
                "title_slide_with_image": "POST /v1.2/hero/title-with-image",
                "section_divider_with_image": "POST /v1.2/hero/section-with-image",
                "closing_slide_with_image": "POST /v1.2/hero/closing-with-image"
            },
            "layout_service_ai": {
                "text_generate": "POST /api/ai/text/generate",
                "text_transform": "POST /api/ai/text/transform",
                "text_autofit": "POST /api/ai/text/autofit",
                "table_generate": "POST /api/ai/table/generate",
                "table_transform": "POST /api/ai/table/transform",
                "table_analyze": "POST /api/ai/table/analyze",
                "health_check": "GET /api/ai/health",
                "constraints_info": "GET /api/ai/constraints/{grid_width}/{grid_height}"
            },
            "hero_health_check": "GET /v1.2/hero/health",
            "list_variants": "GET /v1.2/variants",
            "variant_details": "GET /v1.2/variant/{variant_id}",
            "service_coordination": {
                "capabilities": "GET /v1.2/capabilities",
                "can_handle": "POST /v1.2/can-handle",
                "recommend_variant": "POST /v1.2/recommend-variant"
            },
            "iseries_layouts": {
                "generate": "POST /v1.2/iseries/generate",
                "I1_wide_image_left": "POST /v1.2/iseries/I1",
                "I2_wide_image_right": "POST /v1.2/iseries/I2",
                "I3_narrow_image_left": "POST /v1.2/iseries/I3",
                "I4_narrow_image_right": "POST /v1.2/iseries/I4",
                "health": "GET /v1.2/iseries/health",
                "layouts_info": "GET /v1.2/iseries/layouts"
            }
        },
        "features": {
            "element_based_generation": True,
            "parallel_processing": True,
            "gemini_integration": True,
            "model_routing": True,
            "character_validation": True,
            "template_caching": True,
            "ai_generated_backgrounds": True,
            "layout_service_integration": True,
            "grid_based_constraints": True,
            "content_suggestions": True,
            "iseries_image_text_layouts": True
        },
        "total_variants": 26,
        "total_endpoints": 27,
        "hero_endpoints": 6,
        "layout_ai_endpoints": 8,
        "coordination_endpoints": 3,
        "iseries_endpoints": 7,
        "slide_types": [
            "matrix", "grid", "comparison", "sequential",
            "asymmetric", "hybrid", "metrics", "single_column",
            "impact_quote", "table"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check if we can create a generator
        from app.services import get_llm_service
        service = get_llm_service()

        return {
            "status": "healthy",
            "version": "1.2.0",
            "llm_service": {
                "initialized": True,
                "model_routing": service.enable_model_routing,
                "flash_model": service.flash_model,
                "pro_model": service.pro_model
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


if __name__ == "__main__":
    import asyncio

    # Check SERVICE_MODE to determine what to run
    service_mode = os.getenv("SERVICE_MODE", "web").lower()

    if service_mode == "worker":
        # Run as background worker (processes Redis queue)
        logger.info("=" * 80)
        logger.info("Text & Table Builder v1.2 - Starting WORKER Mode")
        logger.info("=" * 80)

        from app.workers import run_worker
        from aiohttp import web

        worker_id = os.getenv("WORKER_ID", None)
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        max_concurrent = int(os.getenv("WORKER_MAX_CONCURRENT", "3"))
        health_port = int(os.getenv("PORT", os.getenv("HEALTH_PORT", "8080")))

        logger.info(f"Worker ID: {worker_id or 'auto-generated'}")
        logger.info(f"Redis URL: {redis_url[:30]}...")
        logger.info(f"Max concurrent jobs: {max_concurrent}")
        logger.info(f"Health check port: {health_port}")
        logger.info("=" * 80)

        async def health_handler(request):
            """Minimal health endpoint for Railway health checks."""
            return web.json_response({
                "status": "healthy",
                "mode": "worker",
                "worker_id": worker_id or "auto"
            })

        async def run_worker_with_health():
            """Run worker and health server concurrently."""
            # Start minimal health server
            health_app = web.Application()
            health_app.router.add_get("/health", health_handler)
            runner = web.AppRunner(health_app)
            await runner.setup()
            site = web.TCPSite(runner, "0.0.0.0", health_port)
            await site.start()
            logger.info(f"Health endpoint available at http://0.0.0.0:{health_port}/health")

            # Run the worker (this blocks until shutdown)
            await run_worker(
                worker_id=worker_id,
                redis_url=redis_url,
                max_concurrent=max_concurrent
            )

            # Cleanup
            await runner.cleanup()

        asyncio.run(run_worker_with_health())
    else:
        # Run as web server (default)
        import uvicorn

        # Get configuration from environment
        # Railway sets PORT, fallback to API_PORT or 8000
        host = os.getenv("API_HOST", "0.0.0.0")
        port = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))
        reload = os.getenv("API_RELOAD", "false").lower() == "true"

        logger.info(f"Starting server at {host}:{port}")

        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=os.getenv("LOG_LEVEL", "info").lower()
        )
