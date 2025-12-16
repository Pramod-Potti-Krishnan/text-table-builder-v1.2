"""
Async Queue Routes for v1.2 Content Generation

Provides non-blocking job submission with progress tracking for high-load scenarios.

Endpoints:
    POST /v1.2/async/generate - Submit generation job to queue
    GET /v1.2/async/status/{job_id} - Get job status and progress
    GET /v1.2/async/result/{job_id} - Get completed job result
    DELETE /v1.2/async/job/{job_id} - Cancel/cleanup a job

Architecture:
    1. Client submits job → Returns job_id immediately
    2. Job queued in Redis → Worker processes when ready
    3. Client polls status → Gets progress updates
    4. Job completes → Client fetches result

Benefits:
    - Non-blocking: Director can continue with other tasks
    - Progress visibility: Real-time status updates
    - Scalable: Multiple workers can process queue
    - Resilient: Jobs persist across service restarts
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import uuid
import time
import logging
import os
import asyncio

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/v1.2/async", tags=["v1.2-async"])


# =============================================================================
# Models
# =============================================================================

class AsyncJobSubmission(BaseModel):
    """Request to submit an async generation job."""
    variant_id: str
    slide_spec: Dict[str, Any]
    presentation_spec: Optional[Dict[str, Any]] = None
    element_relationships: Optional[Dict[str, str]] = None


class JobSubmissionResponse(BaseModel):
    """Response when job is submitted."""
    job_id: str
    status: str
    queue_position: int
    estimated_wait_seconds: Optional[int] = None
    message: str


class JobStatusResponse(BaseModel):
    """Response for job status query."""
    job_id: str
    status: str  # queued, processing, completed, failed
    progress: int  # 0-100
    stage: Optional[str] = None  # Current processing stage
    queue_position: Optional[int] = None
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None


class JobResultResponse(BaseModel):
    """Response containing completed job result."""
    job_id: str
    success: bool
    html: Optional[str] = None
    variant_id: Optional[str] = None
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None


# =============================================================================
# Redis Connection
# =============================================================================

_redis_client = None


async def get_redis():
    """
    Get Redis client (lazy initialization).

    Uses REDIS_URL environment variable or defaults to localhost.
    """
    global _redis_client

    if _redis_client is None:
        try:
            import redis.asyncio as aioredis
        except ImportError:
            raise HTTPException(
                status_code=503,
                detail="Redis not available. Install with: pip install redis"
            )

        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

        try:
            _redis_client = await aioredis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await _redis_client.ping()
            logger.info(f"Connected to Redis: {redis_url[:30]}...")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Redis unavailable: {str(e)}"
            )

    return _redis_client


def is_redis_enabled() -> bool:
    """Check if Redis queue is enabled."""
    return os.getenv("ENABLE_REDIS_QUEUE", "false").lower() == "true"


# =============================================================================
# Job Queue Keys
# =============================================================================

JOB_KEY_PREFIX = "text_service:job:"
QUEUE_KEY = "text_service:generation_queue"
JOB_TTL_SECONDS = 3600  # 1 hour retention for completed jobs


# =============================================================================
# Routes
# =============================================================================

@router.post("/generate", response_model=JobSubmissionResponse)
async def submit_generation_job(
    request: AsyncJobSubmission,
    background_tasks: BackgroundTasks
) -> JobSubmissionResponse:
    """
    Submit a content generation job to the async queue.

    Returns immediately with a job_id for tracking progress.
    The job will be processed by a worker when capacity is available.

    Use GET /v1.2/async/status/{job_id} to track progress.
    Use GET /v1.2/async/result/{job_id} to fetch the completed result.
    """
    if not is_redis_enabled():
        raise HTTPException(
            status_code=503,
            detail="Async queue not enabled. Set ENABLE_REDIS_QUEUE=true"
        )

    redis = await get_redis()

    # Generate unique job ID
    job_id = str(uuid.uuid4())

    # Prepare job data
    job_data = {
        "id": job_id,
        "status": "queued",
        "progress": 0,
        "stage": "waiting",
        "variant_id": request.variant_id,
        "slide_spec": json.dumps(request.slide_spec),
        "presentation_spec": json.dumps(request.presentation_spec) if request.presentation_spec else "",
        "element_relationships": json.dumps(request.element_relationships) if request.element_relationships else "",
        "submitted_at": str(time.time()),
        "started_at": "",
        "completed_at": "",
        "result": "",
        "error": ""
    }

    # Store job in Redis
    job_key = f"{JOB_KEY_PREFIX}{job_id}"
    await redis.hset(job_key, mapping=job_data)
    await redis.expire(job_key, JOB_TTL_SECONDS * 2)  # Keep job data longer than TTL

    # Add to queue
    await redis.lpush(QUEUE_KEY, job_id)

    # Get queue position
    queue_length = await redis.llen(QUEUE_KEY)

    # Estimate wait time (~8s per job average)
    estimated_wait = queue_length * 8

    print(f"[QUEUE-SUBMIT] job_id={job_id}, variant={request.variant_id}, queue_pos={queue_length}")

    return JobSubmissionResponse(
        job_id=job_id,
        status="queued",
        queue_position=queue_length,
        estimated_wait_seconds=estimated_wait,
        message=f"Job queued. Poll /v1.2/async/status/{job_id} for progress."
    )


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """
    Get the current status and progress of a generation job.

    Progress values:
    - 0: Queued, waiting for processing
    - 10: Started, building prompt
    - 30: Calling LLM
    - 70: LLM complete, parsing response
    - 90: Assembling HTML
    - 100: Complete

    Status values:
    - queued: Waiting in queue
    - processing: Currently being processed
    - completed: Successfully completed
    - failed: Failed with error
    """
    if not is_redis_enabled():
        raise HTTPException(
            status_code=503,
            detail="Async queue not enabled. Set ENABLE_REDIS_QUEUE=true"
        )

    redis = await get_redis()
    job_key = f"{JOB_KEY_PREFIX}{job_id}"

    # Get job data
    job_data = await redis.hgetall(job_key)

    if not job_data:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    # Calculate processing time if started
    processing_time_ms = None
    if job_data.get("started_at"):
        start = float(job_data["started_at"])
        if job_data.get("completed_at"):
            end = float(job_data["completed_at"])
        else:
            end = time.time()
        processing_time_ms = int((end - start) * 1000)

    # Get queue position if still queued
    queue_position = None
    if job_data["status"] == "queued":
        # Find position in queue (0-indexed)
        queue_items = await redis.lrange(QUEUE_KEY, 0, -1)
        try:
            queue_position = queue_items.index(job_id) + 1
        except ValueError:
            queue_position = None

    return JobStatusResponse(
        job_id=job_id,
        status=job_data["status"],
        progress=int(job_data.get("progress", 0)),
        stage=job_data.get("stage"),
        queue_position=queue_position,
        processing_time_ms=processing_time_ms,
        error=job_data.get("error") or None
    )


@router.get("/result/{job_id}", response_model=JobResultResponse)
async def get_job_result(job_id: str) -> JobResultResponse:
    """
    Get the result of a completed generation job.

    Returns 202 Accepted if job is not yet complete.
    Returns 200 OK with result if job completed successfully.
    Returns 200 OK with error if job failed.
    """
    if not is_redis_enabled():
        raise HTTPException(
            status_code=503,
            detail="Async queue not enabled. Set ENABLE_REDIS_QUEUE=true"
        )

    redis = await get_redis()
    job_key = f"{JOB_KEY_PREFIX}{job_id}"

    # Get job data
    job_data = await redis.hgetall(job_key)

    if not job_data:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    status = job_data["status"]

    # If not complete, return 202
    if status not in ["completed", "failed"]:
        raise HTTPException(
            status_code=202,
            detail=f"Job not complete. Status: {status}, Progress: {job_data.get('progress', 0)}%"
        )

    # Calculate processing time
    processing_time_ms = None
    if job_data.get("started_at") and job_data.get("completed_at"):
        processing_time_ms = int(
            (float(job_data["completed_at"]) - float(job_data["started_at"])) * 1000
        )

    if status == "completed":
        # Parse result
        result = json.loads(job_data["result"]) if job_data.get("result") else {}

        return JobResultResponse(
            job_id=job_id,
            success=True,
            html=result.get("html"),
            variant_id=job_data.get("variant_id"),
            processing_time_ms=processing_time_ms
        )
    else:
        # Failed job
        return JobResultResponse(
            job_id=job_id,
            success=False,
            error=job_data.get("error", "Unknown error"),
            variant_id=job_data.get("variant_id"),
            processing_time_ms=processing_time_ms
        )


@router.delete("/job/{job_id}")
async def cancel_job(job_id: str):
    """
    Cancel a queued job or cleanup a completed job.

    Only queued jobs can be cancelled. Completed/failed jobs are cleaned up.
    """
    if not is_redis_enabled():
        raise HTTPException(
            status_code=503,
            detail="Async queue not enabled. Set ENABLE_REDIS_QUEUE=true"
        )

    redis = await get_redis()
    job_key = f"{JOB_KEY_PREFIX}{job_id}"

    # Get job status
    job_data = await redis.hgetall(job_key)

    if not job_data:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    status = job_data["status"]

    if status == "queued":
        # Remove from queue
        await redis.lrem(QUEUE_KEY, 0, job_id)
        await redis.hset(job_key, "status", "cancelled")
        print(f"[QUEUE-CANCEL] job_id={job_id}")
        return {"message": f"Job {job_id} cancelled"}

    elif status == "processing":
        # Can't cancel processing job
        raise HTTPException(
            status_code=409,
            detail="Cannot cancel job that is currently processing"
        )

    else:
        # Cleanup completed/failed job
        await redis.delete(job_key)
        print(f"[QUEUE-CLEANUP] job_id={job_id}")
        return {"message": f"Job {job_id} cleaned up"}


@router.get("/queue/stats")
async def get_queue_stats():
    """
    Get queue statistics and health.

    Returns current queue depth, processing stats, and health status.
    """
    if not is_redis_enabled():
        raise HTTPException(
            status_code=503,
            detail="Async queue not enabled. Set ENABLE_REDIS_QUEUE=true"
        )

    redis = await get_redis()

    # Get queue length
    queue_length = await redis.llen(QUEUE_KEY)

    # Get all job keys to count by status
    # Note: This is expensive for large queues, use with caution
    job_keys = []
    cursor = 0
    while True:
        cursor, keys = await redis.scan(cursor, match=f"{JOB_KEY_PREFIX}*", count=100)
        job_keys.extend(keys)
        if cursor == 0:
            break

    # Count jobs by status
    status_counts = {
        "queued": 0,
        "processing": 0,
        "completed": 0,
        "failed": 0,
        "cancelled": 0
    }

    for key in job_keys[:100]:  # Limit to prevent timeout
        status = await redis.hget(key, "status")
        if status in status_counts:
            status_counts[status] += 1

    return {
        "queue_length": queue_length,
        "total_jobs_tracked": len(job_keys),
        "status_counts": status_counts,
        "healthy": queue_length < 50  # Degraded if queue > 50
    }
