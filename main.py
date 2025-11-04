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

    logger.info("✓ v1.2 API ready at /v1.2/generate")
    logger.info("✓ Variant catalog at /v1.2/variants")
    logger.info("✓ Gemini integration enabled")
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
    logger.info(f"✓ Flash model: {os.getenv('GEMINI_FLASH_MODEL', 'gemini-2.0-flash-exp')}")
    logger.info(f"✓ Pro model: {os.getenv('GEMINI_PRO_MODEL', 'gemini-1.5-pro')}")
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

# Include v1.2 routes
app.include_router(v1_2_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Text & Table Builder",
        "version": "1.2.0",
        "architecture": "Deterministic Assembly",
        "endpoints": {
            "generate": "POST /v1.2/generate",
            "list_variants": "GET /v1.2/variants",
            "variant_details": "GET /v1.2/variant/{variant_id}"
        },
        "features": {
            "element_based_generation": True,
            "parallel_processing": True,
            "gemini_integration": True,
            "model_routing": True,
            "character_validation": True,
            "template_caching": True
        },
        "total_variants": 26,
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
    import uvicorn

    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"

    logger.info(f"Starting server at {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
