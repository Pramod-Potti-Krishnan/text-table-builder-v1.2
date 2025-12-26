# Image Rate Limiting Solutions for Imagen API

## Problem Statement

When generating multiple I-series slides with images, the Text Service may hit Google Vertex AI Imagen API quota limits, resulting in:

```
429 Quota exceeded for aiplatform.googleapis.com/online_prediction_requests_per_base_model
with base model: imagen-3.0-generate
```

### Impact
- Image generation fails for some slides
- Fallback gradient placeholders are used instead of real images
- User experience degraded in production with concurrent users

---

## GCP Quota Information

### Default Quotas

| Model | Quota Property | Typical Default |
|-------|---------------|-----------------|
| `imagen-3.0-generate-001` (standard) | `online_prediction_requests_per_base_model` | ~5-10 RPM |
| `imagen-3.0-fast-generate-001` (fast) | `online_prediction_requests_per_base_model` | ~5-10 RPM |
| `imagen-3.0-generate-002` (high) | `online_prediction_requests_per_base_model` | ~5-10 RPM |

**Key insight**: Each model has its **own separate quota**, so using multiple models effectively multiplies your quota.

### Check Your Current Quota

**Option 1: GCP Console**
1. Go to: https://console.cloud.google.com/iam-admin/quotas
2. Filter for: `imagen` or `online_prediction_requests`
3. View current limit and usage

**Option 2: gcloud CLI**
```bash
gcloud alpha services quota list \
  --service=aiplatform.googleapis.com \
  --filter="metric:online_prediction_requests"
```

### Request Quota Increase

1. Go to: GCP Console → IAM & Admin → Quotas
2. Find the Imagen quota
3. Click "Edit Quotas"
4. Request increase to: 60-100 RPM per model
5. Justification: "Production presentation generation with 100+ concurrent users"

**Expected wait**: 24-48 hours for approval

---

## Solution Layers

### Layer 1: Smart Model Fallback

**Concept**: When standard model hits quota, automatically fall back to fast model.

**Location**: `image_builder/v2.0/src/services/vertex_ai_service.py`

```python
async def generate_with_fallback(
    self,
    prompt: str,
    model: str = "imagen-3.0-generate-001",
    **kwargs
) -> Dict[str, Any]:
    """
    Try primary model, fall back to alternative on quota error.

    This doubles effective quota by using both models.
    """
    try:
        return await self._generate_image(prompt, model=model, **kwargs)
    except QuotaExceededError:
        if model == "imagen-3.0-generate-001":
            logger.warning("Standard quota exceeded, falling back to fast model")
            return await self._generate_image(
                prompt,
                model="imagen-3.0-fast-generate-001",
                **kwargs
            )
        elif model == "imagen-3.0-generate-002":
            logger.warning("High quality quota exceeded, falling back to standard")
            return await self._generate_image(
                prompt,
                model="imagen-3.0-generate-001",
                **kwargs
            )
        raise
```

**Fallback Chain**:
```
imagen-3.0-generate-002 (high)
    ↓ quota exceeded
imagen-3.0-generate-001 (standard)
    ↓ quota exceeded
imagen-3.0-fast-generate-001 (fast)
    ↓ quota exceeded
Fallback gradient placeholder
```

---

### Layer 2: Rate Limiter with Request Queuing

**Concept**: Limit requests client-side to avoid hitting quota.

**Location**: `image_builder/v2.0/src/services/rate_limiter.py` (NEW)

```python
import asyncio
from collections import deque
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ImagenRateLimiter:
    """
    Rate limiter for Imagen API requests.

    Implements a sliding window rate limiter that queues requests
    to stay within quota limits.
    """

    def __init__(
        self,
        max_requests_per_minute: int = 5,
        max_queue_size: int = 100,
        per_model: bool = True
    ):
        """
        Initialize rate limiter.

        Args:
            max_requests_per_minute: Maximum requests allowed per minute
            max_queue_size: Maximum pending requests before rejection
            per_model: Track limits per model (recommended)
        """
        self.max_rpm = max_requests_per_minute
        self.max_queue_size = max_queue_size
        self.per_model = per_model

        # Per-model request tracking
        self.request_times: Dict[str, deque] = {}
        self._lock = asyncio.Lock()

    async def acquire(self, model: str = "default") -> bool:
        """
        Wait until rate limit allows request.

        Args:
            model: Model name for per-model tracking

        Returns:
            True when ready to proceed
        """
        async with self._lock:
            now = datetime.now()
            window = timedelta(minutes=1)

            # Initialize model tracking if needed
            if model not in self.request_times:
                self.request_times[model] = deque()

            times = self.request_times[model]

            # Remove requests outside 1-minute window
            while times and times[0] < now - window:
                times.popleft()

            # If under limit, proceed immediately
            if len(times) < self.max_rpm:
                times.append(now)
                return True

            # Calculate wait time
            wait_seconds = (times[0] + window - now).total_seconds()

        # Wait outside lock
        logger.info(f"Rate limit reached for {model}, waiting {wait_seconds:.1f}s")
        await asyncio.sleep(max(0.1, wait_seconds))
        return await self.acquire(model)

    def get_usage(self, model: str = "default") -> Dict[str, int]:
        """Get current usage statistics."""
        times = self.request_times.get(model, deque())
        now = datetime.now()
        window = timedelta(minutes=1)

        # Count recent requests
        recent = sum(1 for t in times if t > now - window)

        return {
            "model": model,
            "requests_last_minute": recent,
            "limit": self.max_rpm,
            "available": max(0, self.max_rpm - recent)
        }
```

**Integration**:
```python
class VertexAIService:
    def __init__(self):
        self.rate_limiter = ImagenRateLimiter(
            max_requests_per_minute=5,
            per_model=True
        )

    async def generate_image(self, prompt: str, model: str, ...):
        # Wait for rate limit
        await self.rate_limiter.acquire(model)

        # Generate image
        return await self._generate_image_internal(prompt, model, ...)
```

---

### Layer 3: Retry with Exponential Backoff

**Concept**: Automatically retry failed requests with increasing delays.

**Location**: `image_builder/v2.0/src/services/vertex_ai_service.py`

```python
import asyncio
from typing import Optional


class QuotaExceededError(Exception):
    """Raised when Imagen API quota is exceeded."""
    pass


async def generate_with_retry(
    self,
    prompt: str,
    model: str,
    max_retries: int = 3,
    base_delay: float = 5.0,
    backoff_multiplier: float = 3.0
) -> Dict[str, Any]:
    """
    Generate image with exponential backoff on quota errors.

    Retry schedule (with defaults):
    - Attempt 1: immediate
    - Attempt 2: wait 5s
    - Attempt 3: wait 15s
    - Attempt 4: wait 45s

    Args:
        prompt: Image generation prompt
        model: Imagen model to use
        max_retries: Maximum retry attempts
        base_delay: Initial delay in seconds
        backoff_multiplier: Delay multiplier per retry

    Returns:
        Image generation result

    Raises:
        QuotaExceededError: If all retries exhausted
    """
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            return await self._generate_image(prompt, model=model)
        except QuotaExceededError as e:
            last_error = e

            if attempt == max_retries:
                logger.error(f"Max retries ({max_retries}) exceeded for {model}")
                raise

            # Calculate backoff delay
            wait_time = base_delay * (backoff_multiplier ** attempt)
            logger.warning(
                f"Quota exceeded, waiting {wait_time:.1f}s "
                f"(attempt {attempt + 1}/{max_retries + 1})"
            )
            await asyncio.sleep(wait_time)

    raise last_error
```

---

### Layer 4: Redis-Based Distributed Rate Limiter (Production)

**Concept**: For multi-instance deployments, use Redis for shared rate limiting.

**Location**: `image_builder/v2.0/src/services/distributed_rate_limiter.py` (NEW)

```python
import redis.asyncio as redis
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DistributedRateLimiter:
    """
    Redis-based distributed rate limiter for multi-instance deployments.

    Uses Redis sorted sets with timestamp scores for sliding window.
    """

    def __init__(
        self,
        redis_url: str,
        max_requests_per_minute: int = 5,
        key_prefix: str = "imagen_rate_limit"
    ):
        self.redis = redis.from_url(redis_url)
        self.max_rpm = max_requests_per_minute
        self.key_prefix = key_prefix
        self.window_seconds = 60

    def _get_key(self, model: str) -> str:
        """Get Redis key for model."""
        return f"{self.key_prefix}:{model}"

    async def acquire(self, model: str = "default") -> bool:
        """
        Attempt to acquire rate limit slot.

        Uses Redis MULTI/EXEC for atomic operations.
        """
        key = self._get_key(model)
        now = datetime.now().timestamp()
        window_start = now - self.window_seconds

        async with self.redis.pipeline() as pipe:
            try:
                # Remove old entries
                await pipe.zremrangebyscore(key, 0, window_start)

                # Count current entries
                await pipe.zcard(key)

                results = await pipe.execute()
                current_count = results[1]

                if current_count < self.max_rpm:
                    # Add new entry and set expiry
                    await self.redis.zadd(key, {str(now): now})
                    await self.redis.expire(key, self.window_seconds + 10)
                    return True
                else:
                    # Get oldest entry for wait calculation
                    oldest = await self.redis.zrange(key, 0, 0, withscores=True)
                    if oldest:
                        wait_time = oldest[0][1] + self.window_seconds - now
                        logger.info(f"Distributed rate limit: waiting {wait_time:.1f}s")
                        await asyncio.sleep(max(0.1, wait_time))
                        return await self.acquire(model)
                    return False

            except redis.RedisError as e:
                logger.error(f"Redis error in rate limiter: {e}")
                # Fail open - allow request if Redis is down
                return True
```

**Requirements**:
```bash
pip install redis[hiredis]
```

**Environment**:
```env
REDIS_URL=redis://localhost:6379/0
```

---

## Implementation Priority

### Phase 1: Immediate (Quick Fixes)
1. Request GCP quota increase (do first)
2. Use `skip_image_generation` flag for testing

### Phase 2: Image Service Updates
1. Implement Layer 1: Model fallback
2. Implement Layer 3: Retry with backoff
3. Add quota usage logging

### Phase 3: Production Hardening
1. Implement Layer 2: Rate limiter
2. Deploy Layer 4: Redis distributed limiter
3. Add monitoring and alerts

---

## Monitoring & Alerting

### Metrics to Track
- `imagen_requests_total` - Total requests by model
- `imagen_requests_failed` - Failed requests by error type
- `imagen_quota_exceeded_total` - 429 errors
- `imagen_fallback_total` - Fallback to alternative model
- `imagen_queue_depth` - Pending requests in queue

### Alert Thresholds
- Quota exceeded rate > 10% in 5 minutes
- Queue depth > 50 requests
- Fallback rate > 30%

---

## References

- [Vertex AI Quotas Documentation](https://cloud.google.com/vertex-ai/docs/quotas)
- [Generative AI Quotas](https://cloud.google.com/vertex-ai/generative-ai/docs/quotas)
- [Imagen Quota Issues Forum](https://discuss.google.dev/t/imagen-on-vertex-ai-hitting-quota-limits-over-and-over-for-just-1-image-generation/189522)
- [GCP Quota Increase Request](https://cloud.google.com/docs/quotas/increase-quota)
