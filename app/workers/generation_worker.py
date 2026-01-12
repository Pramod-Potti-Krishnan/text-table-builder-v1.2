"""
Generation Worker - Processes async content generation jobs from Redis queue.

This worker:
1. Connects to Redis queue
2. Waits for jobs using BRPOP (blocking pop)
3. Processes each job using ElementBasedContentGenerator
4. Updates job status and progress in Redis
5. Stores result or error in job data

Can run multiple workers for horizontal scaling.

Usage:
    # As standalone script
    python -m app.workers.generation_worker

    # Programmatically
    from app.workers import run_worker
    import asyncio
    asyncio.run(run_worker("worker-1"))

Environment Variables:
    REDIS_URL: Redis connection URL (default: redis://localhost:6379)
    WORKER_ID: Unique worker identifier (default: worker-{hostname})
    GCP_PROJECT_ID: Required for Vertex AI
"""

import asyncio
import json
import time
import logging
import os
import signal
import sys
from typing import Optional

logger = logging.getLogger(__name__)

# Queue keys (must match async_routes.py)
JOB_KEY_PREFIX = "text_service:job:"
QUEUE_KEY = "text_service:generation_queue"


class GenerationWorker:
    """
    Background worker that processes generation jobs from Redis queue.

    Features:
    - Blocking wait for jobs (efficient, no polling)
    - Progress updates during processing
    - Graceful shutdown on SIGTERM/SIGINT
    - Error handling with job failure recording
    """

    def __init__(
        self,
        redis_url: str,
        worker_id: str,
        max_concurrent: int = 3
    ):
        """
        Initialize the worker.

        Args:
            redis_url: Redis connection URL
            worker_id: Unique worker identifier
            max_concurrent: Max jobs to process concurrently
        """
        self.redis_url = redis_url
        self.worker_id = worker_id
        self.max_concurrent = max_concurrent
        self.running = False
        self.redis = None
        self._semaphore = None
        self._generator = None

    async def start(self):
        """Start the worker and begin processing jobs."""
        self.running = True
        self._semaphore = asyncio.Semaphore(self.max_concurrent)

        # Connect to Redis
        try:
            import redis.asyncio as aioredis
        except ImportError:
            print(f"[WORKER-{self.worker_id}] ERROR: redis package not installed")
            return

        try:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis.ping()
            print(f"[WORKER-{self.worker_id}] Connected to Redis")
        except Exception as e:
            print(f"[WORKER-{self.worker_id}] Failed to connect to Redis: {e}")
            return

        # Initialize generator (lazy, will be created on first job)
        print(f"[WORKER-{self.worker_id}] Started, waiting for jobs...")

        # Process jobs
        while self.running:
            try:
                # Block waiting for job (with timeout for graceful shutdown check)
                result = await self.redis.brpop(QUEUE_KEY, timeout=5)

                if result is None:
                    continue  # Timeout, check if still running

                _, job_id = result

                # Process job (with semaphore for concurrency control)
                asyncio.create_task(self._process_job_with_semaphore(job_id))

            except asyncio.CancelledError:
                print(f"[WORKER-{self.worker_id}] Cancelled")
                break
            except Exception as e:
                print(f"[WORKER-{self.worker_id}] Error: {e}")
                await asyncio.sleep(1)  # Back off on error

        print(f"[WORKER-{self.worker_id}] Stopped")

    async def _process_job_with_semaphore(self, job_id: str):
        """Process job with semaphore for concurrency control."""
        async with self._semaphore:
            await self._process_job(job_id)

    async def _process_job(self, job_id: str):
        """Process a single generation job."""
        job_key = f"{JOB_KEY_PREFIX}{job_id}"
        start_time = time.time()

        print(f"[WORKER-{self.worker_id}] Processing job {job_id}")

        try:
            # Update status to processing
            await self.redis.hset(job_key, mapping={
                "status": "processing",
                "stage": "initializing",
                "progress": "10",
                "started_at": str(start_time),
                "worker_id": self.worker_id
            })

            # Get job data
            job_data = await self.redis.hgetall(job_key)

            if not job_data:
                print(f"[WORKER-{self.worker_id}] Job {job_id} not found")
                return

            # Parse job parameters
            variant_id = job_data["variant_id"]
            slide_spec = json.loads(job_data["slide_spec"])
            presentation_spec = json.loads(job_data["presentation_spec"]) if job_data.get("presentation_spec") else None
            element_relationships = json.loads(job_data["element_relationships"]) if job_data.get("element_relationships") else None

            # Update progress: Building prompt
            await self.redis.hset(job_key, mapping={
                "stage": "building_prompt",
                "progress": "20"
            })

            # Initialize generator if needed
            if self._generator is None:
                from ..core import ElementBasedContentGenerator
                from ..services import create_llm_callable_async

                llm_callable = create_llm_callable_async()
                self._generator = ElementBasedContentGenerator(
                    llm_service=llm_callable,
                    variant_specs_dir="app/variant_specs",
                    templates_dir="app/templates"
                )

            # Update progress: Calling LLM
            await self.redis.hset(job_key, mapping={
                "stage": "calling_llm",
                "progress": "30"
            })

            # Generate content
            result = await self._generator.generate_slide_content_async(
                variant_id=variant_id,
                slide_spec=slide_spec,
                presentation_spec=presentation_spec,
                element_relationships=element_relationships
            )

            # Update progress: Parsing response
            await self.redis.hset(job_key, mapping={
                "stage": "parsing_response",
                "progress": "70"
            })

            # Update progress: Assembling HTML
            await self.redis.hset(job_key, mapping={
                "stage": "assembling_html",
                "progress": "90"
            })

            # Store result
            processing_time_ms = int((time.time() - start_time) * 1000)

            # Prepare result (only include serializable fields)
            serialized_result = {
                "html": result.get("html", ""),
                "variant_id": result.get("variant_id", ""),
                "template_path": result.get("template_path", ""),
                "metadata": result.get("metadata", {})
            }

            await self.redis.hset(job_key, mapping={
                "status": "completed",
                "stage": "complete",
                "progress": "100",
                "completed_at": str(time.time()),
                "result": json.dumps(serialized_result),
                "processing_time_ms": str(processing_time_ms)
            })

            print(f"[WORKER-{self.worker_id}] Job {job_id} completed in {processing_time_ms}ms")

        except Exception as e:
            # Record failure
            processing_time_ms = int((time.time() - start_time) * 1000)
            error_msg = str(e)[:500]  # Truncate long errors

            await self.redis.hset(job_key, mapping={
                "status": "failed",
                "stage": "error",
                "completed_at": str(time.time()),
                "error": error_msg,
                "processing_time_ms": str(processing_time_ms)
            })

            print(f"[WORKER-{self.worker_id}] Job {job_id} failed: {error_msg[:100]}")

    async def stop(self):
        """Stop the worker gracefully."""
        print(f"[WORKER-{self.worker_id}] Stopping...")
        self.running = False

        # Wait for current jobs to complete (with timeout)
        if self._semaphore:
            # Wait for all semaphore slots to be available (jobs complete)
            try:
                await asyncio.wait_for(
                    self._wait_for_jobs_complete(),
                    timeout=30
                )
            except asyncio.TimeoutError:
                print(f"[WORKER-{self.worker_id}] Timeout waiting for jobs")

        if self.redis:
            await self.redis.close()

    async def _wait_for_jobs_complete(self):
        """Wait for all current jobs to complete."""
        while True:
            # Check if all semaphore slots are available
            if self._semaphore._value == self.max_concurrent:
                break
            await asyncio.sleep(0.5)


async def run_worker(
    worker_id: Optional[str] = None,
    redis_url: Optional[str] = None,
    max_concurrent: int = 3
):
    """
    Run a generation worker.

    Args:
        worker_id: Unique worker ID (auto-generated if not provided)
        redis_url: Redis URL (from REDIS_URL env if not provided)
        max_concurrent: Max concurrent jobs
    """
    import socket

    # Get configuration
    worker_id = worker_id or os.getenv("WORKER_ID", f"worker-{socket.gethostname()[:8]}")
    redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")

    # Create worker
    worker = GenerationWorker(
        redis_url=redis_url,
        worker_id=worker_id,
        max_concurrent=max_concurrent
    )

    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_event_loop()

    def signal_handler():
        print(f"\n[WORKER-{worker_id}] Received shutdown signal")
        asyncio.create_task(worker.stop())

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)

    # Run worker
    await worker.start()


# Main entry point for running as script
if __name__ == "__main__":
    # Add parent directory to path for imports
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Run worker
    asyncio.run(run_worker())
