# LLM Service Scalability Architecture

## Applicable Services
This architecture applies to ALL LLM-based microservices in the Deckster platform:
- **Text Service** (text_table_builder) - Content generation for slides
- **Illustrator Service** - SVG/visual element generation
- **Diagram Service** - Chart and diagram generation
- **Analytics Service** - Data analysis and insights generation

---

## 1. Problem Analysis

### 1.1 Root Cause: Sequential LLM Processing

**Critical Finding**: Despite using async/await patterns and FastAPI's async handlers, LLM requests are processed **sequentially** due to synchronous SDK calls.

```python
# Current Implementation in llm_client.py (PROBLEMATIC)
async def generate(self, prompt: str) -> LLMResponse:
    # ...
    # THIS IS SYNCHRONOUS - BLOCKS THE EVENT LOOP
    response = self.client.generate_content(
        prompt,
        generation_config=generation_config
    )
```

**Why This Blocks Everything**:
1. Python's `asyncio` event loop runs in a single thread
2. When `generate_content()` is called, it performs synchronous I/O
3. The entire event loop is blocked until the LLM responds (~7-15 seconds)
4. ALL other requests wait, even though FastAPI received them concurrently

### 1.2 The Request Queue Cascade

When Director sends 9 slide requests in parallel:

```
Timeline (actual from logs):
├── T+0.0s    Director sends all 9 requests simultaneously
├── T+0.0s    Text Service receives Request 1, starts LLM call
├── T+0.0s    Requests 2-9 arrive but WAIT (event loop blocked)
├── T+7.5s    Request 1 LLM completes, Request 2 starts
├── T+15.0s   Request 2 LLM completes, Request 3 starts
├── T+22.5s   Request 3 completes, Request 4 starts
├── T+30.0s   Request 4 completes, Request 5 starts
├── T+37.5s   Request 5 completes, Request 6 starts
├── T+45.0s   Request 6 completes, Request 7 starts
├── T+52.5s   Request 7 completes, Request 8 starts  ← Director timeout!
├── T+55.0s   Director times out on Requests 7, 8, 9
├── T+60.0s   Request 8 completes (but Director already gave up)
```

### 1.3 Evidence from Production Logs

```
# Director sent request at 20:26:01.644
[TEXT-SVC] POST /v1.2/generate variant=grid_2x2_centered

# Text Service received 55 SECONDS LATER at 20:26:56.543
[GEN-REQ] variant=grid_2x2_centered, title='Slide 2 Title'

# Director timed out 0.1 seconds later at 20:26:56.660
[TEXT-SVC-ERROR] Request error for /v1.2/generate:

# Text Service succeeded 7 seconds after starting
[GEN-OK] variant=grid_2x2_centered, time=7101ms, html=4806 chars
```

**The 55-second gap** = Time spent waiting for 7 other LLM requests to complete sequentially

---

## 2. Solution Architecture

### 2.1 Immediate Fix: True Async LLM Calls

**Goal**: Allow multiple LLM requests to execute concurrently

**Implementation**: Use `asyncio.to_thread()` to offload blocking LLM calls

```python
# Fixed Implementation in llm_client.py
import asyncio

async def generate(self, prompt: str) -> LLMResponse:
    """Generate content using Gemini with true async execution."""
    generation_config = GenerationConfig(
        temperature=self.temperature,
        max_output_tokens=self.max_tokens,
    )

    # Run synchronous SDK call in a thread pool (non-blocking)
    response = await asyncio.to_thread(
        self.client.generate_content,
        prompt,
        generation_config=generation_config
    )

    return LLMResponse(
        content=response.text,
        model=self.model_name,
        tokens_used=response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
    )
```

**Benefits**:
- Zero code changes to callers (same async interface)
- Immediate concurrency improvement
- Each LLM call runs in its own thread
- Event loop remains responsive

**Concurrency with Thread Pool**:
```python
# In main.py or service initialization
import asyncio

# Configure thread pool size based on expected concurrency
# Default is min(32, os.cpu_count() + 4)
# For I/O-bound LLM calls, can increase significantly
asyncio.get_event_loop().set_default_executor(
    concurrent.futures.ThreadPoolExecutor(max_workers=20)
)
```

### 2.2 Better Fix: Connection Pool + Rate Limiting

**Goal**: Manage LLM connections efficiently and prevent overload

```python
# app/services/llm_pool.py
import asyncio
from typing import Optional
from dataclasses import dataclass
from collections import deque
import time

@dataclass
class LLMPoolConfig:
    max_concurrent: int = 10          # Max parallel LLM calls
    max_queue_size: int = 50          # Max pending requests
    timeout_seconds: float = 120.0    # Per-request timeout
    rate_limit_rpm: int = 300         # Requests per minute (Vertex AI limit)

class LLMConnectionPool:
    """
    Manages concurrent LLM requests with rate limiting.

    Features:
    - Semaphore-based concurrency control
    - Request queue with overflow protection
    - Rate limiting to respect API quotas
    - Request prioritization (optional)
    """

    def __init__(self, config: LLMPoolConfig = None):
        self.config = config or LLMPoolConfig()
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent)
        self._queue: deque = deque(maxlen=self.config.max_queue_size)
        self._request_times: deque = deque()  # For rate limiting
        self._lock = asyncio.Lock()

    async def execute(self, llm_client, prompt: str, priority: int = 0) -> str:
        """
        Execute an LLM request through the pool.

        Args:
            llm_client: The LLM client to use
            prompt: The prompt to send
            priority: Request priority (higher = more important)

        Returns:
            Generated content string

        Raises:
            QueueFullError: If queue is at capacity
            TimeoutError: If request times out
        """
        # Check queue capacity
        if len(self._queue) >= self.config.max_queue_size:
            raise QueueFullError(
                f"LLM queue full ({self.config.max_queue_size} pending). "
                "Try again later."
            )

        # Wait for rate limit
        await self._wait_for_rate_limit()

        # Acquire semaphore slot
        async with self._semaphore:
            # Track request time for rate limiting
            async with self._lock:
                self._request_times.append(time.time())

            # Execute with timeout
            try:
                return await asyncio.wait_for(
                    asyncio.to_thread(llm_client.generate_sync, prompt),
                    timeout=self.config.timeout_seconds
                )
            except asyncio.TimeoutError:
                raise TimeoutError(
                    f"LLM request timed out after {self.config.timeout_seconds}s"
                )

    async def _wait_for_rate_limit(self):
        """Wait if we're exceeding rate limits."""
        async with self._lock:
            now = time.time()
            # Remove requests older than 60 seconds
            while self._request_times and now - self._request_times[0] > 60:
                self._request_times.popleft()

            # If at limit, wait for oldest request to age out
            if len(self._request_times) >= self.config.rate_limit_rpm:
                wait_time = 60 - (now - self._request_times[0])
                if wait_time > 0:
                    await asyncio.sleep(wait_time)

    @property
    def status(self) -> dict:
        """Return current pool status for monitoring."""
        return {
            "active_requests": self.config.max_concurrent - self._semaphore._value,
            "queue_size": len(self._queue),
            "requests_last_minute": len(self._request_times),
            "max_concurrent": self.config.max_concurrent,
            "max_queue": self.config.max_queue_size,
            "rate_limit_rpm": self.config.rate_limit_rpm
        }

class QueueFullError(Exception):
    """Raised when the LLM request queue is full."""
    pass
```

### 2.3 Best Fix: Redis Queue with Progress Feedback

**Goal**: Decouple request acceptance from processing, provide real-time progress

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Director  │────▶│  Text API   │────▶│ Redis Queue │────▶│  Worker(s)  │
│   Agent     │     │  (FastAPI)  │     │             │     │  (LLM Pool) │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │                   │
       │                   ▼                   ▼                   │
       │            ┌─────────────┐     ┌─────────────┐           │
       │            │  Job ID     │     │  Job Status │           │
       │            │  Response   │     │  Updates    │           │
       │            └─────────────┘     └─────────────┘           │
       │                   │                   ▲                   │
       │                   │                   │                   │
       └───────────────────┴───────────────────┴───────────────────┘
                          Progress Polling / WebSocket
```

**API Design**:

```python
# app/api/async_routes.py
from fastapi import APIRouter, BackgroundTasks
from redis import asyncio as aioredis
import uuid

router = APIRouter(prefix="/v1.2/async", tags=["async"])

@router.post("/generate")
async def submit_generation_job(
    request: V1_2_GenerationRequest,
    background_tasks: BackgroundTasks,
    redis: aioredis.Redis = Depends(get_redis)
) -> JobSubmissionResponse:
    """
    Submit a content generation job to the queue.

    Returns immediately with a job_id for tracking.
    """
    job_id = str(uuid.uuid4())

    # Store job in Redis queue
    job_data = {
        "id": job_id,
        "status": "queued",
        "variant_id": request.variant_id,
        "slide_spec": request.slide_spec.model_dump(),
        "presentation_spec": request.presentation_spec.model_dump() if request.presentation_spec else None,
        "submitted_at": time.time(),
        "progress": 0
    }

    await redis.hset(f"job:{job_id}", mapping=job_data)
    await redis.lpush("generation_queue", job_id)

    # Get queue position
    queue_length = await redis.llen("generation_queue")

    return JobSubmissionResponse(
        job_id=job_id,
        status="queued",
        queue_position=queue_length,
        estimated_wait_seconds=queue_length * 8  # ~8s per job average
    )

@router.get("/status/{job_id}")
async def get_job_status(
    job_id: str,
    redis: aioredis.Redis = Depends(get_redis)
) -> JobStatusResponse:
    """Get the current status of a generation job."""
    job_data = await redis.hgetall(f"job:{job_id}")

    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job_id,
        status=job_data["status"],
        progress=int(job_data.get("progress", 0)),
        result=job_data.get("result"),
        error=job_data.get("error"),
        processing_time_ms=job_data.get("processing_time_ms")
    )

@router.get("/result/{job_id}")
async def get_job_result(
    job_id: str,
    redis: aioredis.Redis = Depends(get_redis)
) -> V1_2_GenerationResponse:
    """Get the result of a completed generation job."""
    job_data = await redis.hgetall(f"job:{job_id}")

    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")

    if job_data["status"] != "completed":
        raise HTTPException(
            status_code=202,
            detail=f"Job not complete. Status: {job_data['status']}"
        )

    return V1_2_GenerationResponse(**json.loads(job_data["result"]))
```

**Worker Process**:

```python
# app/workers/generation_worker.py
import asyncio
from redis import asyncio as aioredis

class GenerationWorker:
    """
    Background worker that processes generation jobs from Redis queue.

    Can run multiple workers for horizontal scaling.
    """

    def __init__(self, redis_url: str, worker_id: str):
        self.redis_url = redis_url
        self.worker_id = worker_id
        self.llm_pool = LLMConnectionPool(LLMPoolConfig(max_concurrent=5))
        self.running = False

    async def start(self):
        """Start processing jobs from the queue."""
        self.running = True
        redis = await aioredis.from_url(self.redis_url)

        print(f"[WORKER-{self.worker_id}] Started, waiting for jobs...")

        while self.running:
            try:
                # Block waiting for job (with timeout for graceful shutdown)
                result = await redis.brpop("generation_queue", timeout=5)

                if result is None:
                    continue  # Timeout, check if still running

                _, job_id = result
                job_id = job_id.decode()

                await self._process_job(redis, job_id)

            except Exception as e:
                print(f"[WORKER-{self.worker_id}] Error: {e}")
                await asyncio.sleep(1)  # Back off on error

    async def _process_job(self, redis: aioredis.Redis, job_id: str):
        """Process a single generation job."""
        start_time = time.time()

        # Update status to processing
        await redis.hset(f"job:{job_id}", mapping={
            "status": "processing",
            "worker_id": self.worker_id,
            "started_at": start_time
        })

        try:
            # Get job data
            job_data = await redis.hgetall(f"job:{job_id}")

            # Update progress: Building prompt
            await redis.hset(f"job:{job_id}", "progress", 10)

            # Generate content
            generator = ElementBasedContentGenerator(...)

            # Update progress: Calling LLM
            await redis.hset(f"job:{job_id}", "progress", 30)

            result = await generator.generate_slide_content_async(
                variant_id=job_data["variant_id"],
                slide_spec=json.loads(job_data["slide_spec"]),
                presentation_spec=json.loads(job_data["presentation_spec"]) if job_data.get("presentation_spec") else None
            )

            # Update progress: Assembling HTML
            await redis.hset(f"job:{job_id}", "progress", 90)

            # Store result
            processing_time = int((time.time() - start_time) * 1000)
            await redis.hset(f"job:{job_id}", mapping={
                "status": "completed",
                "progress": 100,
                "result": json.dumps(result),
                "processing_time_ms": processing_time
            })

            print(f"[WORKER-{self.worker_id}] Job {job_id} completed in {processing_time}ms")

        except Exception as e:
            await redis.hset(f"job:{job_id}", mapping={
                "status": "failed",
                "error": str(e),
                "processing_time_ms": int((time.time() - start_time) * 1000)
            })
            print(f"[WORKER-{self.worker_id}] Job {job_id} failed: {e}")
```

**Director Integration**:

```python
# Director's text_service_client_v1_2.py (enhanced)

class TextServiceClientV1_2:
    """Enhanced client with async job support."""

    async def generate_slide_content_async(
        self,
        request: dict,
        use_queue: bool = True,
        max_wait_seconds: int = 300
    ) -> dict:
        """
        Generate slide content with optional queue-based processing.

        Args:
            request: Generation request
            use_queue: If True, use async queue; if False, use sync endpoint
            max_wait_seconds: Maximum time to wait for result

        Returns:
            Generated content response
        """
        if not use_queue:
            # Legacy sync call (direct)
            return await self._generate_sync(request)

        # Submit to queue
        async with httpx.AsyncClient(timeout=30) as client:
            submit_response = await client.post(
                f"{self.base_url}/v1.2/async/generate",
                json=request
            )
            submit_response.raise_for_status()
            job_info = submit_response.json()

        job_id = job_info["job_id"]
        print(f"[TEXT-SVC] Job submitted: {job_id}, queue position: {job_info['queue_position']}")

        # Poll for completion
        start_time = time.time()
        poll_interval = 1.0  # Start with 1 second

        while time.time() - start_time < max_wait_seconds:
            async with httpx.AsyncClient(timeout=10) as client:
                status_response = await client.get(
                    f"{self.base_url}/v1.2/async/status/{job_id}"
                )
                status = status_response.json()

            if status["status"] == "completed":
                # Fetch result
                async with httpx.AsyncClient(timeout=30) as client:
                    result_response = await client.get(
                        f"{self.base_url}/v1.2/async/result/{job_id}"
                    )
                    return result_response.json()

            elif status["status"] == "failed":
                raise Exception(f"Generation failed: {status.get('error', 'Unknown error')}")

            # Log progress
            print(f"[TEXT-SVC] Job {job_id}: {status['status']}, progress: {status.get('progress', 0)}%")

            await asyncio.sleep(poll_interval)
            poll_interval = min(poll_interval * 1.2, 5.0)  # Backoff up to 5s

        raise TimeoutError(f"Job {job_id} did not complete within {max_wait_seconds}s")
```

---

## 3. Implementation Roadmap

### Phase 1: Immediate Fix (1-2 hours)
**Goal**: Enable concurrent LLM processing

1. **Modify `llm_client.py`**:
   - Wrap `generate_content()` with `asyncio.to_thread()`
   - This single change enables true async concurrency

2. **Test locally**:
   - Send 5 parallel requests
   - Verify they complete in ~8s total (not 40s)

3. **Deploy and monitor**:
   - Deploy to Railway
   - Watch logs for concurrent `[GEN-REQ]` entries

### Phase 2: Connection Pool (3-4 hours)
**Goal**: Manage concurrency and prevent overload

1. **Create `llm_pool.py`**:
   - Implement semaphore-based concurrency control
   - Add rate limiting for Vertex AI quotas

2. **Integrate with service**:
   - Replace direct LLM calls with pool execution
   - Configure max_concurrent based on Railway instance size

3. **Add monitoring endpoint**:
   - `/health/llm-pool` returning pool status
   - Track active requests, queue depth, rate limit status

### Phase 3: Redis Queue (1-2 days)
**Goal**: Full async architecture with progress feedback

1. **Add Redis dependency**:
   - Add `redis[asyncio]` to requirements.txt
   - Configure Redis connection (Railway provides Redis add-on)

2. **Implement async endpoints**:
   - POST `/v1.2/async/generate` - Submit job
   - GET `/v1.2/async/status/{job_id}` - Get progress
   - GET `/v1.2/async/result/{job_id}` - Get result

3. **Create worker process**:
   - Implement `GenerationWorker` class
   - Add worker startup to Railway deployment

4. **Update Director**:
   - Modify client to use async endpoints
   - Implement polling with progress logging

---

## 4. Configuration Reference

### Environment Variables

```bash
# LLM Pool Configuration
LLM_MAX_CONCURRENT=10           # Max parallel LLM calls
LLM_MAX_QUEUE_SIZE=50           # Max pending requests
LLM_TIMEOUT_SECONDS=120         # Per-request timeout
LLM_RATE_LIMIT_RPM=300          # Requests per minute

# Redis Configuration (for Phase 3)
REDIS_URL=redis://default:xxx@redis.railway.internal:6379
REDIS_JOB_TTL_SECONDS=3600      # Job data retention (1 hour)

# Worker Configuration (for Phase 3)
WORKER_COUNT=3                  # Number of worker processes
WORKER_ID_PREFIX=text-worker    # Worker identification prefix

# Director Configuration
TEXT_SERVICE_TIMEOUT=300        # HTTP timeout for text service calls
TEXT_SERVICE_USE_QUEUE=true     # Enable async queue mode
TEXT_SERVICE_POLL_INTERVAL=2    # Seconds between status polls
```

### Railway Scaling Recommendations

| Concurrent Users | Instance Type | Workers | Max Concurrent LLM |
|-----------------|---------------|---------|-------------------|
| 1-5             | Hobby ($5/mo) | 1       | 5                 |
| 5-20            | Pro ($20/mo)  | 2       | 10                |
| 20-50           | Pro + Redis   | 3       | 15                |
| 50+             | Enterprise    | 5+      | 25+               |

---

## 5. Monitoring & Observability

### Key Metrics to Track

```python
# Suggested Prometheus metrics (if using prometheus-client)
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
llm_requests_total = Counter('llm_requests_total', 'Total LLM requests', ['status'])
llm_request_duration = Histogram('llm_request_duration_seconds', 'LLM request duration')
llm_queue_depth = Gauge('llm_queue_depth', 'Current queue depth')
llm_active_requests = Gauge('llm_active_requests', 'Currently processing requests')

# Rate limiting metrics
llm_rate_limit_waits = Counter('llm_rate_limit_waits_total', 'Times waited for rate limit')
llm_queue_full_rejections = Counter('llm_queue_full_rejections_total', 'Requests rejected due to full queue')
```

### Log Patterns for Analysis

```bash
# Successful concurrent processing
[GEN-REQ] variant=grid_2x2_centered, title='Slide 1'
[GEN-REQ] variant=matrix_2x2, title='Slide 2'        # Same timestamp = concurrent
[GEN-REQ] variant=timeline_horizontal, title='Slide 3'
[GEN-OK] variant=grid_2x2_centered, time=7523ms
[GEN-OK] variant=matrix_2x2, time=8102ms
[GEN-OK] variant=timeline_horizontal, time=7891ms

# Queue-based processing
[QUEUE-SUBMIT] job_id=abc123, variant=grid_2x2_centered, queue_pos=3
[WORKER-1] Processing job abc123
[WORKER-1] Job abc123 completed in 7523ms
[QUEUE-RESULT] job_id=abc123, status=completed
```

---

## 6. Error Handling Strategy

### Client-Side (Director)

```python
class TextServiceError(Exception):
    """Base exception for Text Service errors."""
    pass

class TextServiceQueueFull(TextServiceError):
    """Queue is at capacity."""
    pass

class TextServiceTimeout(TextServiceError):
    """Request timed out."""
    pass

class TextServiceRateLimited(TextServiceError):
    """Rate limit exceeded."""
    pass

# Retry logic with exponential backoff
async def generate_with_retry(self, request: dict, max_retries: int = 3) -> dict:
    for attempt in range(max_retries):
        try:
            return await self.generate_slide_content_async(request)
        except TextServiceQueueFull:
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            print(f"[TEXT-SVC] Queue full, waiting {wait_time:.1f}s...")
            await asyncio.sleep(wait_time)
        except TextServiceTimeout:
            if attempt < max_retries - 1:
                print(f"[TEXT-SVC] Timeout, retrying ({attempt + 1}/{max_retries})...")
                continue
            raise
    raise TextServiceError("Max retries exceeded")
```

### Service-Side (Text Service)

```python
# HTTP status codes for different scenarios
# 200 - Success
# 202 - Accepted (job queued, poll for result)
# 400 - Bad request (validation error)
# 429 - Too Many Requests (rate limited or queue full)
# 503 - Service Unavailable (LLM service down)
# 504 - Gateway Timeout (LLM call timed out)

@router.post("/v1.2/generate")
async def generate_slide_content(...):
    try:
        result = await pool.execute(llm_client, prompt)
        return V1_2_GenerationResponse(success=True, ...)
    except QueueFullError:
        raise HTTPException(
            status_code=429,
            detail="Service at capacity. Please retry in 30 seconds.",
            headers={"Retry-After": "30"}
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="LLM request timed out. Please retry."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}"
        )
```

---

## 7. Testing Strategy

### Load Testing Script

```python
# test_concurrent_load.py
import asyncio
import httpx
import time
from statistics import mean, stdev

async def send_request(client: httpx.AsyncClient, i: int) -> dict:
    """Send a single generation request."""
    start = time.time()
    request = {
        "variant_id": "grid_2x2_centered",
        "slide_spec": {
            "slide_title": f"Test Slide {i}",
            "slide_purpose": "Load testing",
            "key_message": f"Testing concurrent request {i}"
        }
    }

    try:
        response = await client.post("/v1.2/generate", json=request)
        elapsed = time.time() - start
        return {
            "request_id": i,
            "status": response.status_code,
            "elapsed_seconds": elapsed,
            "success": response.status_code == 200
        }
    except Exception as e:
        return {
            "request_id": i,
            "status": "error",
            "elapsed_seconds": time.time() - start,
            "success": False,
            "error": str(e)
        }

async def run_load_test(concurrent_requests: int = 10):
    """Run load test with specified concurrency."""
    print(f"\n{'='*60}")
    print(f"Load Test: {concurrent_requests} concurrent requests")
    print(f"{'='*60}\n")

    async with httpx.AsyncClient(
        base_url="http://localhost:8000",
        timeout=300.0
    ) as client:
        start = time.time()
        tasks = [send_request(client, i) for i in range(concurrent_requests)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start

    # Analyze results
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    print(f"Total time: {total_time:.2f}s")
    print(f"Successful: {len(successful)}/{concurrent_requests}")
    print(f"Failed: {len(failed)}/{concurrent_requests}")

    if successful:
        times = [r["elapsed_seconds"] for r in successful]
        print(f"Response times: min={min(times):.2f}s, max={max(times):.2f}s, "
              f"avg={mean(times):.2f}s, stdev={stdev(times) if len(times) > 1 else 0:.2f}s")

    if failed:
        print(f"Failures: {[r.get('error', r['status']) for r in failed]}")

    # Expected results with fixes:
    # - Without fix: total_time ≈ concurrent_requests * 8s (sequential)
    # - With asyncio.to_thread: total_time ≈ 8-12s (parallel)

    return results

if __name__ == "__main__":
    asyncio.run(run_load_test(10))
```

### Expected Results Comparison

| Scenario | 10 Requests | Sequential Time | Concurrent Time |
|----------|-------------|-----------------|-----------------|
| Before Fix (sync LLM) | 10 | ~80s | ~80s (no difference) |
| After Fix (to_thread) | 10 | ~80s | ~12s |
| With Pool (max=5) | 10 | ~80s | ~20s |
| With Queue + 3 Workers | 10 | ~80s | ~30s (but non-blocking) |

---

## 8. Migration Path

### For Text Service (Priority 1)

1. **Day 1**: Apply `asyncio.to_thread()` fix to `llm_client.py`
2. **Day 2**: Add connection pool, configure Railway for more memory
3. **Week 2**: Implement Redis queue for production scale

### For Other Services

Apply the same patterns:

```python
# Generic pattern for any LLM-based service

# Step 1: Make LLM calls truly async
async def generate(self, prompt: str) -> str:
    return await asyncio.to_thread(
        self.sync_llm_client.generate,
        prompt
    )

# Step 2: Add connection pooling
pool = LLMConnectionPool(LLMPoolConfig(max_concurrent=10))
result = await pool.execute(llm_client, prompt)

# Step 3: Add queue-based processing (if needed)
# Copy the Redis queue pattern from Text Service
```

---

## 9. Summary

### Root Cause
Synchronous LLM SDK calls blocking Python's async event loop, causing request queuing.

### Solution Hierarchy

| Fix Level | Implementation | Effort | Concurrency Improvement |
|-----------|----------------|--------|------------------------|
| Immediate | `asyncio.to_thread()` | 30 min | 5-10x |
| Better | Connection Pool | 3-4 hours | 10x + rate limiting |
| Best | Redis Queue | 1-2 days | Unlimited + progress |

### Key Code Change (Immediate Fix)

```python
# Before (blocking):
response = self.client.generate_content(prompt, generation_config=config)

# After (non-blocking):
response = await asyncio.to_thread(
    self.client.generate_content,
    prompt,
    generation_config=config
)
```

This single change transforms sequential processing into true parallel execution.

---

## Appendix: Full File Paths

```
text_table_builder/v1.2/
├── app/
│   ├── api/
│   │   ├── v1_2_routes.py          # Sync generation endpoint
│   │   └── async_routes.py         # NEW: Async queue endpoints
│   ├── services/
│   │   ├── llm_client.py           # MODIFY: Add asyncio.to_thread()
│   │   ├── llm_service.py          # MODIFY: Use pool
│   │   └── llm_pool.py             # NEW: Connection pool
│   └── workers/
│       └── generation_worker.py    # NEW: Queue worker
├── requirements.txt                 # ADD: redis[asyncio]
└── LLM_SERVICE_SCALABILITY_ARCHITECTURE.md  # This document
```
