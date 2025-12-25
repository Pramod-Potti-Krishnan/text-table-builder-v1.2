# Director Integration Guide: Image-Enhanced Hero Slides

## Overview

The Text & Table Builder v1.2 now supports **image-enhanced hero slides** with AI-generated 16:9 background images. This guide explains how the Director Agent should integrate these new endpoints into its slide generation workflow.

---

## New Endpoints

### 1. Title Slide with Image
**Endpoint:** `POST /v1.2/hero/title-with-image`

**Use When:**
- Creating presentation title/cover slides (slide #1)
- Want visually striking opening with AI-generated background
- Need left-aligned text layout for better readability

**Text Layout:**
- Title and subtitle positioned on **LEFT** side (max-width: 60%)
- Gradient overlay: dark left → light right (ensures white text readability)
- Background image optimized with LEFT crop anchor

---

### 2. Section Divider with Image
**Endpoint:** `POST /v1.2/hero/section-with-image`

**Use When:**
- Creating section breaks between major topics
- Transitioning to new chapter/theme
- Need visual separation with right-aligned emphasis

**Text Layout:**
- Section title positioned on **RIGHT** side (max-width: 50%)
- Gradient overlay: dark right → light left
- Background image optimized with RIGHT crop anchor

---

### 3. Closing Slide with Image
**Endpoint:** `POST /v1.2/hero/closing-with-image`

**Use When:**
- Creating final slide with call-to-action
- Thank you slides
- Contact information slides

**Text Layout:**
- All content **CENTER-aligned**
- Radial gradient overlay: light center → dark edges (vignette effect)
- Background image optimized with CENTER crop anchor

---

## Request Format

All three endpoints use the same request schema as standard hero slides:

```json
{
  "slide_number": 1,
  "slide_type": "title_slide",  // or "section_divider", "closing_slide"
  "narrative": "AI transforming healthcare diagnostics through advanced machine learning",
  "topics": ["Machine Learning", "Patient Outcomes", "Diagnostic Accuracy"],
  "context": {
    "theme": "professional",
    "audience": "healthcare professionals",
    "presentation_title": "AI in Healthcare: Transforming Diagnostics",
    "contact_info": "contact@healthtech.com"  // for closing slides
  }
}
```

**Important Notes:**
- `slide_type` should match the endpoint purpose (title_slide, section_divider, or closing_slide)
- `narrative` is used for both content generation AND image prompt engineering
- `topics` help contextualize the AI-generated background image
- `context.theme` influences image style (professional, modern, creative, etc.)

---

## Response Format

### Standard Response Structure

```json
{
  "content": "<div style=\"width: 100%; height: 100%; ...\">...</div>",
  "metadata": {
    "slide_type": "title_slide_with_image",
    "slide_number": 1,
    "background_image": "https://storage.googleapis.com/.../image.png",
    "image_generation_time_ms": 12450,
    "fallback_to_gradient": false,
    "validation": {
      "valid": true,
      "violations": [],
      "warnings": [],
      "metrics": {...}
    },
    "generation_mode": "hero_slide_with_image_async"
  }
}
```

### Key Metadata Fields

| Field | Type | Description |
|-------|------|-------------|
| `background_image` | string\|null | GCS URL of generated image. `null` if graceful fallback occurred. |
| `image_generation_time_ms` | number\|null | Time taken to generate image (parallel with content). |
| `fallback_to_gradient` | boolean | `true` if image generation failed and gradient fallback was used. |
| `slide_type` | string | Includes "_with_image" suffix to differentiate from standard endpoints. |

---

## Layout Builder Integration

### Step 1: Extract Background Image URL

When Director receives the response from Text Service:

```python
response = await text_service.generate_hero_with_image(request)
content = response["content"]
metadata = response["metadata"]

background_image_url = metadata.get("background_image")  # Can be None
fallback_used = metadata.get("fallback_to_gradient", False)
```

### Step 2: Determine Layout Template

All image-enhanced slides should use **L29 (Hero Full Bleed)** layout:

```python
layout_id = "L29"  # Hero full bleed layout
```

### Step 3: Build Layout Request

**Option A: With Background Image**

If `background_image_url` is not `None`:

```json
{
  "layout_id": "L29",
  "narrative": "...",
  "content_blocks": [
    {
      "type": "hero_with_background",
      "html_content": "<content from text service>",
      "background_image": "https://storage.googleapis.com/.../image.png",
      "overlay_gradient": true  // L29 should apply gradient overlay via CSS
    }
  ]
}
```

**Option B: Fallback to Gradient**

If `background_image_url` is `None` (fallback occurred):

```json
{
  "layout_id": "L29",
  "narrative": "...",
  "content_blocks": [
    {
      "type": "hero_with_gradient",
      "html_content": "<content from text service>",
      // No background_image field
      // Content already includes gradient as inline styles
    }
  ]
}
```

### Step 4: L29 Layout Implementation

The L29 layout in Layout Builder should:

1. **When `background_image` provided:**
   ```html
   <section data-layout="L29" class="hero-full-bleed">
     <div class="slide-background">
       <img src="{{background_image}}"
            style="width: 100%; height: 100%; object-fit: cover;">
     </div>
     <div class="slide-content">
       {{{html_content}}}  <!-- Text content with gradient overlay -->
     </div>
   </section>
   ```

2. **When fallback to gradient:**
   ```html
   <section data-layout="L29" class="hero-gradient-fallback">
     <div class="slide-content">
       {{{html_content}}}  <!-- Content already has gradient background -->
     </div>
   </section>
   ```

---

## Image Generation Behavior

### Automatic Image Prompt Engineering

The Text Service automatically creates contextual image prompts from:
- **Narrative**: Primary source for image theme
- **Topics**: Keywords to include in image
- **Slide Type**: Influences composition (title = dramatic, section = transitional, closing = inspirational)
- **Context Theme**: Affects visual style (professional = clean, modern = abstract, etc.)

**Example Auto-Generated Prompt (Title Slide):**
```
"Professional photorealistic image: AI transforming healthcare diagnostics
through advanced machine learning. Themes: Machine Learning, Patient Outcomes,
Diagnostic Accuracy. Style: professional, high-quality, presentation-ready.
16:9 aspect ratio, left-aligned composition for title slide."
```

### Image Generation Performance

- **Timing**: Image and content generation run **in parallel** via `asyncio.gather()`
- **Typical Duration**: 10-15 seconds for image generation
- **Total Slide Time**: ~10-15 seconds (since parallel)
- **Retry Logic**: 3 attempts with exponential backoff
- **Timeout**: 20 seconds per attempt

### Graceful Fallback

If image generation fails (API error, timeout, 500 status):
1. Service logs warning with error details
2. Falls back to gradient background (already in content HTML)
3. Sets `fallback_to_gradient: true` in metadata
4. Slide generation continues successfully
5. **User experience**: Still gets beautiful slide, just without AI image

---

## Director Agent Decision Logic

### When to Use Image-Enhanced Endpoints?

**Use Image-Enhanced Variants When:**
- ✅ Slide is title/opening slide (slide #1)
- ✅ Slide is section divider (between major topics)
- ✅ Slide is closing/CTA slide (final slide)
- ✅ User requested "visually striking" or "professional" presentation
- ✅ Image Service is available and configured

**Use Standard Hero Endpoints When:**
- ❌ Image Service unavailable or disabled
- ❌ User requested "simple" or "text-only" presentation
- ❌ Presentation has very tight time constraints (standard = ~2s vs image = ~15s)
- ❌ Slide is in middle of content (not opening/section/closing)

### Example Director Logic

```python
async def select_hero_endpoint(slide_context: dict) -> str:
    """Determine which hero endpoint to use."""

    slide_num = slide_context["slide_number"]
    slide_type = slide_context["slide_type"]
    user_prefs = slide_context.get("user_preferences", {})

    # Check if image service is enabled
    image_service_enabled = config.get("IMAGE_SERVICE_ENABLED", True)

    # Check user preference
    visual_style = user_prefs.get("visual_style", "professional")
    wants_images = visual_style in ["professional", "modern", "creative"]

    # Decision tree
    if not image_service_enabled or not wants_images:
        # Use standard endpoints
        if slide_type == "title_slide":
            return "/v1.2/hero/title"
        elif slide_type == "section_divider":
            return "/v1.2/hero/section"
        elif slide_type == "closing_slide":
            return "/v1.2/hero/closing"
    else:
        # Use image-enhanced endpoints for key slides
        if slide_type == "title_slide" and slide_num == 1:
            return "/v1.2/hero/title-with-image"
        elif slide_type == "section_divider":
            return "/v1.2/hero/section-with-image"
        elif slide_type == "closing_slide":
            return "/v1.2/hero/closing-with-image"
        else:
            # Fallback to standard for mid-deck slides
            if slide_type == "title_slide":
                return "/v1.2/hero/title"
            elif slide_type == "section_divider":
                return "/v1.2/hero/section"
            elif slide_type == "closing_slide":
                return "/v1.2/hero/closing"
```

---

## CSS Gradient Overlays (Built into Content)

The Text Service embeds gradient overlays directly in the HTML content to ensure text readability regardless of background image:

### Title Slide (LEFT-aligned)
```css
background: linear-gradient(to right,
  rgba(0,0,0,0.75) 0%,    /* Dark left for white text */
  rgba(0,0,0,0.3) 50%,
  rgba(0,0,0,0.1) 100%);  /* Light right */
```

### Section Slide (RIGHT-aligned)
```css
background: linear-gradient(to left,
  rgba(0,0,0,0.75) 0%,    /* Dark right for white text */
  rgba(0,0,0,0.3) 50%,
  rgba(0,0,0,0.1) 100%);  /* Light left */
```

### Closing Slide (CENTER-aligned)
```css
background: radial-gradient(circle,
  rgba(0,0,0,0.2) 0%,     /* Light center */
  rgba(0,0,0,0.5) 60%,
  rgba(0,0,0,0.75) 100%); /* Dark edges (vignette) */
```

**Important:** These gradients are applied to the content `<div>`, NOT the background image. The L29 layout should layer:
1. Background image (full bleed)
2. Content div with gradient overlay (ensures text readability)

---

## Error Handling

### Image Service Errors

**Scenario 1: Image API Returns 500**
- Text Service retries 3 times
- Falls back to gradient background
- Metadata: `"fallback_to_gradient": true, "background_image": null`
- Director should proceed normally (graceful degradation)

**Scenario 2: Image API Timeout**
- Text Service waits max 20 seconds per attempt
- After 3 attempts (60s total), falls back to gradient
- Director should not retry - accept fallback

**Scenario 3: Image Service Completely Down**
- Text Service detects connection errors
- Immediately falls back to gradient (no retries)
- Log warning but don't fail slide generation

### Recommended Director Error Handling

```python
try:
    response = await text_service.generate_hero_with_image(request)

    if response["metadata"].get("fallback_to_gradient"):
        logger.warning(
            f"Slide {slide_num}: Image generation failed, using gradient fallback"
        )

    # Proceed with layout building regardless
    layout_response = await layout_builder.build_slide(
        layout_id="L29",
        content=response["content"],
        background_image=response["metadata"].get("background_image")
    )

except Exception as e:
    logger.error(f"Slide {slide_num}: Text service error - {e}")
    # Fallback to standard hero endpoint
    response = await text_service.generate_hero_standard(request)
    ...
```

---

## Testing & Validation

### Local Testing

The v1.2 directory includes `test_image_endpoints.py`:

```bash
cd agents/text_table_builder/v1.2
python3 test_image_endpoints.py
```

This generates:
- `test_outputs/title_slide.html` - Title slide HTML
- `test_outputs/section_slide.html` - Section slide HTML
- `test_outputs/closing_slide.html` - Closing slide HTML
- `test_outputs/demo.html` - Combined demo page
- `test_outputs/*.json` - Full API responses with metadata

### Validation Checklist

**Before integrating into Director:**
- [ ] Verify all three endpoints return 200 status
- [ ] Check `background_image` URL is valid GCS URL (when not fallback)
- [ ] Confirm gradient overlays render correctly
- [ ] Test with Image Service disabled (should fallback gracefully)
- [ ] Validate L29 layout displays background images correctly
- [ ] Check text is readable over both images and gradients
- [ ] Verify response times are acceptable (~15s with images, ~2s fallback)

---

## Configuration

### Required Environment Variables

```bash
# Image Service Configuration
IMAGE_SERVICE_URL=https://web-production-1b5df.up.railway.app
IMAGE_SERVICE_API_KEY=  # Optional, not currently required
IMAGE_SERVICE_TIMEOUT=20.0
IMAGE_SERVICE_ENABLED=true
```

### Director Configuration

Director should expose user-configurable options:

```json
{
  "presentation_config": {
    "use_image_enhanced_slides": true,  // Enable/disable feature
    "image_quality": "high",            // high, medium, low
    "visual_style": "professional",     // professional, modern, creative, minimal
    "fallback_behavior": "graceful"     // graceful (use gradients) or skip (use standard)
  }
}
```

---

## Performance Considerations

### Parallel Generation

The image-enhanced generators use `asyncio.gather()` to run image and content generation **in parallel**:

```python
image_task = asyncio.create_task(generate_image())
content_task = asyncio.create_task(generate_content())
results = await asyncio.gather(image_task, content_task)
```

**Performance Impact:**
- Standard hero slide: ~2 seconds (content only)
- Image-enhanced slide: ~12-15 seconds (image + content in parallel)
- If run sequentially: ~17 seconds (2s content + 15s image)
- **Speedup: 13% faster** due to parallelization

### Director Optimization Strategies

**Strategy 1: Selective Use**
- Use image-enhanced only for slide #1, section breaks, and final slide
- Use standard endpoints for middle slides
- Typical deck (10 slides): 3 image-enhanced + 7 standard = ~51s vs ~20s all standard

**Strategy 2: Progress Indicators**
- Show user: "Generating AI backgrounds for key slides..." during long operations
- Update progress: "Slide 1/10 complete (with AI background)..."

**Strategy 3: Caching**
- If user regenerates same slide, check if image already exists
- Layout Builder could cache GCS URLs by content hash

---

## Examples

### Example 1: Title Slide Request

**Director sends to Text Service:**
```json
POST /v1.2/hero/title-with-image
{
  "slide_number": 1,
  "slide_type": "title_slide",
  "narrative": "Revolutionizing Supply Chain with AI and Blockchain",
  "topics": ["Artificial Intelligence", "Blockchain", "Supply Chain", "Transparency"],
  "context": {
    "theme": "professional",
    "audience": "executives",
    "presentation_title": "Supply Chain 2024: AI + Blockchain"
  }
}
```

**Text Service returns:**
```json
{
  "content": "<div style=\"...\">...</div>",
  "metadata": {
    "slide_type": "title_slide_with_image",
    "slide_number": 1,
    "background_image": "https://storage.googleapis.com/deckster-images/abc123.png",
    "image_generation_time_ms": 13200,
    "fallback_to_gradient": false,
    "validation": {"valid": true, ...}
  }
}
```

**Director sends to Layout Builder:**
```json
POST /v7.5/slides/build
{
  "layout_id": "L29",
  "narrative": "Revolutionizing Supply Chain with AI and Blockchain",
  "content_blocks": [
    {
      "type": "hero_with_background",
      "html_content": "<div style=\"...\">...</div>",
      "background_image": "https://storage.googleapis.com/deckster-images/abc123.png"
    }
  ]
}
```

### Example 2: Section Divider Request

**Director sends to Text Service:**
```json
POST /v1.2/hero/section-with-image
{
  "slide_number": 5,
  "slide_type": "section_divider",
  "narrative": "Market Analysis: Growth Trends and Opportunities",
  "topics": ["Market Growth", "Opportunities", "Revenue Projections"],
  "context": {
    "theme": "modern"
  }
}
```

**Text Service returns:**
```json
{
  "content": "<div style=\"...\">...</div>",
  "metadata": {
    "slide_type": "section_divider_with_image",
    "slide_number": 5,
    "background_image": "https://storage.googleapis.com/deckster-images/xyz789.png",
    "image_generation_time_ms": 11800,
    "fallback_to_gradient": false,
    "validation": {"valid": true, ...}
  }
}
```

### Example 3: Closing Slide with Fallback

**Director sends to Text Service:**
```json
POST /v1.2/hero/closing-with-image
{
  "slide_number": 12,
  "slide_type": "closing_slide",
  "narrative": "Let's build the future together",
  "topics": ["Partnership", "Innovation", "Success"],
  "context": {
    "theme": "professional",
    "contact_info": "hello@company.com | www.company.com"
  }
}
```

**Text Service returns (Image API down):**
```json
{
  "content": "<div style=\"background: radial-gradient(...)\">...</div>",
  "metadata": {
    "slide_type": "closing_slide_with_image",
    "slide_number": 12,
    "background_image": null,  // Image generation failed
    "image_generation_time_ms": null,
    "fallback_to_gradient": true,  // Graceful fallback
    "validation": {"valid": true, ...}
  }
}
```

**Director sends to Layout Builder (fallback):**
```json
POST /v7.5/slides/build
{
  "layout_id": "L29",
  "narrative": "Let's build the future together",
  "content_blocks": [
    {
      "type": "hero_with_gradient",
      "html_content": "<div style=\"background: radial-gradient(...)\">...</div>"
      // No background_image - content has gradient
    }
  ]
}
```

---

## Summary

### Key Takeaways for Director Integration

1. **Three new endpoints** for image-enhanced hero slides (title, section, closing)
2. **Same request format** as standard hero endpoints
3. **Response includes `background_image` URL** in metadata (or `null` if fallback)
4. **Always use L29 layout** for image-enhanced slides
5. **Graceful fallback to gradients** if image generation fails
6. **Parallel generation** keeps performance reasonable (~15s vs ~17s sequential)
7. **Automatic image prompt engineering** from narrative/topics/context
8. **Built-in gradient overlays** ensure text readability
9. **Decision logic**: Use for opening/section/closing slides, standard for middle slides
10. **Error handling**: Accept fallbacks gracefully, don't retry Text Service failures

### Next Steps

1. Update Director's slide type router to recognize image-enhanced requests
2. Implement L29 layout with background image support in Layout Builder
3. Add user configuration for enabling/disabling image-enhanced slides
4. Test end-to-end with sample presentations
5. Monitor performance and adjust caching/optimization strategies

---

## Support & Troubleshooting

**Common Issues:**

| Issue | Cause | Solution |
|-------|-------|----------|
| All slides fallback to gradient | Image Service down | Check `IMAGE_SERVICE_ENABLED=true` in .env |
| Slow generation (~60s) | Sequential execution | Verify async/await implementation in Director |
| Text unreadable over images | Missing gradient overlay | Ensure L29 applies gradients from content HTML |
| 400 Bad Request | Missing required fields | Verify `slide_type` matches endpoint purpose |
| GCS URL returns 404 | Image not stored | Check Image Builder v2.0 storage configuration |

**Logs to Monitor:**
- `app.services.image_service_client` - Image generation attempts and failures
- `app.core.hero.*_with_image_generator` - Parallel execution and fallback logic
- `app.api.hero_routes` - Endpoint validation errors

---

**Version:** Text & Table Builder v1.2
**Last Updated:** 2024-11-24
**Contact:** Layout Builder Team
