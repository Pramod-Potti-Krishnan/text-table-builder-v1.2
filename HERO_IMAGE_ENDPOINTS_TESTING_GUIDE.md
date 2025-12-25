# Hero Image Endpoints - Testing & Integration Guide

**Document Version:** 1.0
**Date:** 2025-11-27
**For:** Text Service v1.2 Team
**Status:** 🔴 CRITICAL - Endpoints returning 404 in production

---

## 🚨 Issue Summary

**Problem:** Image-enhanced hero slide endpoints (`/v1.2/hero/title-with-image`, `/v1.2/hero/section-with-image`, `/v1.2/hero/closing-with-image`) are **not being registered** in the Railway deployment, causing 404 errors when Director Agent attempts to generate hero slides with background images.

**Impact:**
- Hero slides (title, closing) fall back to placeholder/strawman content
- Frontend displays text outline instead of visually rich slides
- Image generation feature completely non-functional in production

**Root Cause:** Missing Google Cloud credentials in Railway deployment → Image Service client fails to initialize → Image-enhanced routes never register

---

## 📋 Prerequisites Checklist

Before testing these endpoints, ensure the following are configured:

### Required Environment Variables

```bash
# Google Cloud Platform (REQUIRED for image generation)
GCP_PROJECT_ID=deckster-xyz
GCP_LOCATION=us-central1
GCP_SERVICE_ACCOUNT_JSON=<your-service-account-json-here>

# Image Service Configuration
IMAGE_SERVICE_ENABLED=true
IMAGE_SERVICE_MODEL=imagen-3.0-generate-001  # Default: photorealistic
IMAGE_SERVICE_TIMEOUT=30  # Seconds
```

### Required Dependencies

Verify these are installed (check `requirements.txt`):
```
google-cloud-aiplatform>=1.40.0
Pillow>=10.0.0
```

### Service Account Permissions

The GCP service account must have:
- `roles/aiplatform.user` - For Vertex AI Imagen API
- Access to project: `deckster-xyz`
- Region: `us-central1`

---

## 📚 API Endpoint Specifications

### 1. Title Slide with Image

**Endpoint:** `POST /v1.2/hero/title-with-image`

**Description:** Generates a title slide with AI-generated background image based on presentation topic

**Request Schema:**
```json
{
  "slide_number": 1,
  "slide_type": "title_slide",
  "narrative": "Brief description of the presentation topic",
  "topics": ["Main Topic", "Subtopic 1", "Subtopic 2"],
  "context": {
    "theme": "professional",
    "presentation_title": "My Presentation",
    "audience": "executives",
    "total_slides": 10
  },
  "visual_style": "professional"  // Options: "professional" | "illustrated" | "kids"
}
```

**Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `slide_number` | `int` | ✅ Yes | Slide position in deck (usually 1 for title) |
| `slide_type` | `string` | ✅ Yes | Must be `"title_slide"` |
| `narrative` | `string` | ✅ Yes | Brief summary of presentation topic (used for image generation) |
| `topics` | `array[string]` | ❌ No | Key topics covered (enhances image relevance) |
| `context` | `object` | ❌ No | Additional presentation metadata |
| `visual_style` | `string` | ❌ No | Image generation style (default: `"professional"`) |

**Visual Style Options:**

| Style | Image Model | Use Case | Generation Time | Example Prompts |
|-------|-------------|----------|-----------------|-----------------|
| `professional` | Imagen 3.0 | Corporate, business, formal | ~10s | Photorealistic, abstract, minimal |
| `illustrated` | Imagen 3.0 Fast | Creative, marketing, education | ~5s | Artistic, colorful, stylized |
| `kids` | Imagen 3.0 Fast | Children's content | ~5s | Playful, cartoonish, vibrant |

**Response Schema:**
```json
{
  "content": "<div class=\"hero-slide\">\n  <div class=\"hero-content\">\n    <h1>Presentation Title</h1>\n    <p class=\"subtitle\">Subtitle or tagline</p>\n  </div>\n</div>",
  "metadata": {
    "slide_type": "title_slide",
    "slide_number": 1,
    "layout_type": "hero_full_bleed",
    "background_image": "https://storage.googleapis.com/deckster-xyz/images/abc123.png",
    "image_prompt": "High-quality professional presentation background: ...",
    "visual_style": "professional",
    "generation_time_ms": 10243,
    "has_gradient_overlay": true,
    "text_color": "#FFFFFF"
  }
}
```

---

### 2. Section Divider with Image

**Endpoint:** `POST /v1.2/hero/section-with-image`

**Description:** Generates a section divider slide with AI-generated background image

**Request Schema:**
```json
{
  "slide_number": 5,
  "slide_type": "section_divider",
  "narrative": "Brief description of this section's focus",
  "topics": ["Section Topic"],
  "context": {
    "theme": "professional",
    "section_title": "Part II: Analysis"
  },
  "visual_style": "professional"
}
```

**Response:** Similar to title slide response

---

### 3. Closing Slide with Image

**Endpoint:** `POST /v1.2/hero/closing-with-image`

**Description:** Generates a closing/thank-you slide with AI-generated background image

**Request Schema:**
```json
{
  "slide_number": 10,
  "slide_type": "closing_slide",
  "narrative": "Brief summary of key takeaways or call-to-action",
  "topics": ["Key Takeaway 1", "Key Takeaway 2"],
  "context": {
    "theme": "professional",
    "presentation_title": "My Presentation"
  },
  "visual_style": "professional"
}
```

**Response:** Similar to title slide response

---

## 🧪 Testing Procedures

### Step 1: Verify Service is Running

```bash
# Check health endpoint
curl https://web-production-5daf.up.railway.app/health

# Expected: 200 OK with JSON response
```

### Step 2: Check Endpoint Registration

```bash
# Review startup logs in Railway dashboard
# Look for these messages:

✓ v1.2 Hero API (image-enhanced):
  - /v1.2/hero/title-with-image (title with AI background)
  - /v1.2/hero/section-with-image (section with AI background)
  - /v1.2/hero/closing-with-image (closing with AI background)
```

**If you DON'T see these lines:**
- Image Service client failed to initialize
- Check GCP credentials are set correctly
- Review error logs for Image Service initialization

**If you see these lines instead:**
```
✓ v1.2 Hero API:
  - /v1.2/hero/title (title slides)
  - /v1.2/hero/section (section dividers)
  - /v1.2/hero/closing (closing slides)
```
⚠️ **Only basic endpoints registered** - image-enhanced routes are missing!

---

### Step 3: Test Title Slide with Image (Basic)

```bash
curl -X POST https://web-production-5daf.up.railway.app/v1.2/hero/title-with-image \
  -H "Content-Type: application/json" \
  -d '{
    "slide_number": 1,
    "slide_type": "title_slide",
    "narrative": "AI in Healthcare: Transforming Patient Care",
    "topics": ["Machine Learning", "Diagnostics", "Patient Outcomes"],
    "context": {
      "theme": "professional"
    },
    "visual_style": "professional"
  }'
```

**Expected Response:**
- Status: `200 OK`
- Response body contains:
  - `content`: HTML string with hero slide markup
  - `metadata.background_image`: Valid GCS URL (e.g., `https://storage.googleapis.com/...`)
  - `metadata.image_prompt`: The prompt sent to Imagen
  - `metadata.generation_time_ms`: Image generation duration

**Possible Errors:**

| Status | Error | Cause | Fix |
|--------|-------|-------|-----|
| `404` | Not Found | Route not registered | Add GCP credentials, restart service |
| `500` | Internal Server Error | Image generation failed | Check GCP credentials, Imagen API quota |
| `422` | Validation Error | Invalid request payload | Check request schema matches spec |
| `503` | Service Unavailable | Imagen API timeout | Increase `IMAGE_SERVICE_TIMEOUT` |

---

### Step 4: Test with Different Visual Styles

**Professional Style (Photorealistic):**
```bash
curl -X POST https://web-production-5daf.up.railway.app/v1.2/hero/title-with-image \
  -H "Content-Type: application/json" \
  -d '{
    "slide_number": 1,
    "slide_type": "title_slide",
    "narrative": "Corporate Strategy 2024",
    "visual_style": "professional"
  }'
```

**Illustrated Style (Artistic):**
```bash
curl -X POST https://web-production-5daf.up.railway.app/v1.2/hero/title-with-image \
  -H "Content-Type: application/json" \
  -d '{
    "slide_number": 1,
    "slide_type": "title_slide",
    "narrative": "Creative Marketing Campaigns",
    "visual_style": "illustrated"
  }'
```

**Kids Style (Playful):**
```bash
curl -X POST https://web-production-5daf.up.railway.app/v1.2/hero/title-with-image \
  -H "Content-Type: application/json" \
  -d '{
    "slide_number": 1,
    "slide_type": "title_slide",
    "narrative": "The Wonderful Stories of Little Krishna",
    "visual_style": "kids"
  }'
```

---

### Step 5: Test Section Divider

```bash
curl -X POST https://web-production-5daf.up.railway.app/v1.2/hero/section-with-image \
  -H "Content-Type: application/json" \
  -d '{
    "slide_number": 5,
    "slide_type": "section_divider",
    "narrative": "Financial Analysis and Projections",
    "topics": ["Revenue Growth", "Cost Optimization"],
    "visual_style": "professional"
  }'
```

---

### Step 6: Test Closing Slide

```bash
curl -X POST https://web-production-5daf.up.railway.app/v1.2/hero/closing-with-image \
  -H "Content-Type: application/json" \
  -d '{
    "slide_number": 10,
    "slide_type": "closing_slide",
    "narrative": "Thank you for your time. Questions welcome.",
    "topics": ["Key Takeaways", "Next Steps"],
    "visual_style": "professional"
  }'
```

---

## 🔧 Troubleshooting Guide

### Issue: Endpoints return 404

**Symptoms:**
```
INFO: "POST /v1.2/hero/title-with-image HTTP/1.1" 404 Not Found
```

**Diagnosis:**
1. Check startup logs - do you see image-enhanced endpoint registration messages?
2. If no, check for these error messages:
   ```
   ERROR - Google Cloud credentials not found
   ERROR - Image Service initialization failed
   ```

**Solution:**
1. Add required environment variables to Railway:
   - `GCP_PROJECT_ID=deckster-xyz`
   - `GCP_SERVICE_ACCOUNT_JSON=<json-content>`
2. Redeploy the service
3. Verify startup logs show all 6 hero endpoints (3 basic + 3 image-enhanced)

---

### Issue: Endpoints return 500

**Symptoms:**
```
INFO: "POST /v1.2/hero/title-with-image HTTP/1.1" 500 Internal Server Error
```

**Diagnosis:**
1. Check application logs for full error traceback
2. Look for Imagen API errors:
   - Permission denied
   - Quota exceeded
   - Invalid request
   - Timeout

**Common Causes:**

**1. Invalid GCP Credentials**
```
Error: Permission denied on resource project deckster-xyz
```
**Fix:** Verify service account has `roles/aiplatform.user`

**2. Imagen API Quota Exceeded**
```
Error: Quota exceeded for quota metric 'Generate requests'
```
**Fix:** Check quota in GCP Console → Vertex AI → Quotas

**3. Image Generation Timeout**
```
Error: Timeout waiting for image generation
```
**Fix:** Increase `IMAGE_SERVICE_TIMEOUT` environment variable

**4. Network Issues**
```
Error: Failed to connect to Vertex AI endpoint
```
**Fix:** Check Railway → GCP network connectivity

---

### Issue: Images not appearing in response

**Symptoms:**
- Status: 200 OK
- Response contains `content` but `metadata.background_image` is missing or null

**Diagnosis:**
1. Check if Image Service is enabled: `IMAGE_SERVICE_ENABLED=true`
2. Review logs for image upload errors
3. Check GCS bucket permissions

**Solution:**
1. Verify Image Service client is initialized:
   ```python
   # In logs, look for:
   "Image Service client initialized successfully"
   ```
2. Check GCS bucket configuration in `app/services/image_service_client.py`
3. Verify service account has write access to GCS bucket

---

### Issue: Wrong visual style applied

**Symptoms:**
- Request specifies `"visual_style": "kids"`
- Generated image looks corporate/professional

**Diagnosis:**
1. Check if `visual_style` parameter is being read correctly
2. Review image prompt in response metadata
3. Verify style config mapping

**Debug:**
```python
# In logs, look for:
"Using visual style: kids"
"Image prompt: <should mention playful/cartoon/vibrant>"
```

**Solution:**
1. Verify `app/core/hero/style_config.py` has correct mappings
2. Check `visual_style` validation in request schema
3. Test with explicit style parameter

---

## 📊 Performance Benchmarks

**Expected Generation Times:**

| Endpoint | Visual Style | Avg Time | 95th Percentile |
|----------|--------------|----------|-----------------|
| `/v1.2/hero/title-with-image` | professional | 10s | 15s |
| `/v1.2/hero/title-with-image` | illustrated | 5s | 8s |
| `/v1.2/hero/title-with-image` | kids | 5s | 8s |
| `/v1.2/hero/section-with-image` | professional | 10s | 15s |
| `/v1.2/hero/closing-with-image` | professional | 10s | 15s |

**Timeout Configuration:**
- Default: `30s` (set via `IMAGE_SERVICE_TIMEOUT`)
- Recommended minimum: `20s`
- Production: `30s` (allows for retry + buffer)

---

## 🔗 Integration with Director Agent

### How Director Calls These Endpoints

**File:** `director_agent/v3.4/src/utils/hero_request_transformer.py`

**URL Construction (Lines 116-119):**
```python
if slide.use_image_background:
    endpoint = f"/v1.2/hero/{base_endpoint}-with-image"
else:
    endpoint = f"/v1.2/hero/{base_endpoint}"
```

**Full URL Example:**
```
https://web-production-5daf.up.railway.app/v1.2/hero/title-with-image
```

**Payload Building (Lines 130-148):**
```python
payload = {
    "slide_number": slide.slide_number,
    "slide_type": classification,
    "narrative": slide.narrative,
    "topics": self._extract_topics(slide),
    "context": context
}

# Add visual_style if slide has it
if slide.use_image_background and slide.visual_style:
    payload["visual_style"] = slide.visual_style
```

**Expected Response Handling:**
- Director expects `200 OK` with `{"content": "...", "metadata": {...}}`
- On 404: Director logs error and falls back to placeholder content
- On 500: Director retries once, then falls back
- On timeout: Director falls back after 30s

---

## ✅ Verification Checklist

Use this checklist to verify endpoints are working correctly:

### Environment Setup
- [ ] `GCP_PROJECT_ID` is set in Railway
- [ ] `GCP_SERVICE_ACCOUNT_JSON` is set in Railway
- [ ] `GCP_LOCATION=us-central1` is set
- [ ] Service account has `roles/aiplatform.user` permission
- [ ] `IMAGE_SERVICE_ENABLED=true` is set

### Service Startup
- [ ] Startup logs show "Image Service client initialized successfully"
- [ ] Startup logs list all 6 hero endpoints (3 basic + 3 with-image)
- [ ] No ERROR messages about GCP credentials
- [ ] Health endpoint returns 200 OK

### Endpoint Testing
- [ ] `/v1.2/hero/title-with-image` returns 200 OK (not 404)
- [ ] Response contains valid `content` HTML
- [ ] Response `metadata.background_image` is a valid GCS URL
- [ ] Image URL is accessible (returns actual image)
- [ ] `/v1.2/hero/section-with-image` returns 200 OK
- [ ] `/v1.2/hero/closing-with-image` returns 200 OK

### Visual Style Testing
- [ ] `visual_style: professional` generates photorealistic images
- [ ] `visual_style: illustrated` generates artistic images
- [ ] `visual_style: kids` generates playful/cartoon images
- [ ] Different visual styles have different image prompts in metadata

### Integration Testing
- [ ] Director Agent can successfully call endpoints
- [ ] Hero slides display generated content (not placeholder)
- [ ] Background images appear on frontend
- [ ] No 404 errors in Director logs
- [ ] Generation completes within 30s timeout

---

## 📝 Deployment Notes

### Railway Deployment Steps

1. **Set Environment Variables:**
   ```
   GCP_PROJECT_ID=deckster-xyz
   GCP_LOCATION=us-central1
   GCP_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
   IMAGE_SERVICE_ENABLED=true
   IMAGE_SERVICE_TIMEOUT=30
   ```

2. **Redeploy Service:**
   - Trigger deployment via Railway dashboard
   - Monitor deployment logs
   - Wait for "Application startup complete"

3. **Verify Registration:**
   - Check startup logs for image-enhanced endpoint messages
   - Test health endpoint
   - Run curl tests from this guide

4. **Monitor Production:**
   - Watch for 404 errors in logs
   - Track image generation times
   - Monitor Imagen API quota usage

---

## 🆘 Support & Contact

**If endpoints still fail after following this guide:**

1. **Collect Diagnostics:**
   - Full startup logs (first 100 lines)
   - Error logs from failed requests
   - Environment variable status (redact sensitive values)
   - curl test results

2. **Check Known Issues:**
   - Review `DIRECTOR_INTEGRATION_HERO_IMAGES.md`
   - Check GitHub issues for similar problems

3. **Contact:**
   - Create issue in project repository
   - Include diagnostics from step 1
   - Tag: `text-service`, `hero-slides`, `image-generation`

---

## 📖 Related Documentation

- `DIRECTOR_INTEGRATION_HERO_IMAGES.md` - Director integration guide
- `app/core/hero/README.md` - Hero slide generator architecture
- `app/services/image_service_client.py` - Image Service implementation
- `.env.example` - Complete environment variable reference

---

**Document Status:** ✅ Ready for testing
**Last Updated:** 2025-11-27
**Next Review:** After successful endpoint verification
