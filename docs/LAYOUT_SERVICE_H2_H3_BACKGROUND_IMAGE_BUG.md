# Layout Service Bug Report: H2-section and H3-closing Background Images Not Rendering

**Date:** December 27, 2025
**Reporter:** Text Service Team
**Priority:** High
**Affects:** H2-section, H3-closing layouts with background images

---

## Summary

The Layout Service is correctly **storing** `background_image` data for H2-section and H3-closing slides, but the **frontend renderers are not using this data**. Instead, they display a placeholder "Generate image..." even when a valid image URL is present.

---

## What We're Doing

The Text Service generates AI background images for H-series hero slides:
- **H1-generated**: Title slide with full `hero_content` HTML (image embedded in HTML)
- **H1-structured**: Title slide with structured fields + `background_image`
- **H2-section**: Section divider with `background_image`
- **H3-closing**: Closing slide with `background_image`

We followed the **Layout Service API Reference** (`director_agent/v4.0/docs/LAYOUT_SERVICE_API_REFERENCE.md`) which specifies:

### H2-section Expected Input (from API Reference, lines 400-435):
```json
{
  "layout": "H2-section",
  "content": {
    "section_number": "01",
    "slide_title": "Section Title"
  },
  "background_color": "#374151",
  "background_image": "https://example.com/section-background.jpg"
}
```

### H3-closing Expected Input (from API Reference, lines 438-477):
```json
{
  "layout": "H3-closing",
  "content": {
    "slide_title": "Thank You",
    "subtitle": "Questions & Discussion",
    "contact_info": "email@company.com | www.company.com"
  },
  "background_color": "#1e3a5f",
  "background_image": "https://example.com/closing-background.jpg"
}
```

---

## What We Sent to Layout Service

**Test Presentation:** `3b38e5e9-4381-45b8-80c7-f4f15243770b`

### H2-section (Slide 3):
```json
{
  "layout": "H2-section",
  "content": {
    "section_number": "01",
    "slide_title": "Strategic Overview"
  },
  "background_image": "https://eshvntffcestlfuofwhv.supabase.co/storage/v1/object/public/generated-images/generated/b613d864-af24-484f-a29b-e81431a3c330_original.png"
}
```

### H3-closing (Slide 4):
```json
{
  "layout": "H3-closing",
  "content": {
    "slide_title": "Thank You",
    "subtitle": "Questions & Discussion",
    "contact_info": "contact@company.com | www.company.com"
  },
  "background_image": "https://eshvntffcestlfuofwhv.supabase.co/storage/v1/object/public/generated-images/generated/8035182d-ec83-4588-a604-dff8a7701cdc_original.png"
}
```

---

## Evidence: Data is Stored Correctly

Querying the presentation API shows the data is stored correctly:

```bash
curl -s "https://web-production-f0d13.up.railway.app/api/presentations/3b38e5e9-4381-45b8-80c7-f4f15243770b" | jq '.slides[2], .slides[3]'
```

**Response (H2-section):**
```json
{
  "slide_id": "slide_785a5e80b936",
  "layout": "H2-section",
  "content": {
    "section_number": "01",
    "slide_title": "Strategic Overview"
  },
  "background_color": null,
  "background_image": "https://eshvntffcestlfuofwhv.supabase.co/storage/v1/object/public/generated-images/generated/b613d864-af24-484f-a29b-e81431a3c330_original.png",
  ...
}
```

**Response (H3-closing):**
```json
{
  "slide_id": "slide_933b27cceec8",
  "layout": "H3-closing",
  "content": {
    "slide_title": "Thank You",
    "subtitle": "Questions & Discussion",
    "contact_info": "contact@company.com | www.company.com"
  },
  "background_color": null,
  "background_image": "https://eshvntffcestlfuofwhv.supabase.co/storage/v1/object/public/generated-images/generated/8035182d-ec83-4588-a604-dff8a7701cdc_original.png",
  ...
}
```

---

## Evidence: Images Are Valid

The image URLs are accessible and return valid PNG images:

```bash
curl -sI "https://eshvntffcestlfuofwhv.supabase.co/storage/v1/object/public/generated-images/generated/b613d864-af24-484f-a29b-e81431a3c330_original.png" | head -5

HTTP/2 200
content-type: image/png
content-length: 1185484
```

---

## What's Happening (Screenshots)

Instead of rendering the background image, both H2-section and H3-closing show:
- A placeholder image icon
- "Generate image..." text

**H2-section Screenshot:**
- Shows: "01 Strategic Overview" with blue background and "Generate image..." placeholder
- Should show: Same text overlaid on the AI-generated background image

**H3-closing Screenshot:**
- Shows: "Thank You / Questions & Discussion" with blue background and "Generate image..." placeholder
- Should show: Same text overlaid on the AI-generated background image

---

## Root Cause (Hypothesis)

The frontend renderers for H2-section (likely `L60.js`) and H3-closing (likely `L61.js`) are not checking for or using the `background_image` field from the slide data.

The renderers appear to:
1. Only use `background_color` for the background
2. Display a placeholder when no image is in `content.hero_content` or similar
3. Ignore the slide-level `background_image` field entirely

---

## Suggested Fix

Update the H2-section and H3-closing renderers to:

1. **Check for `background_image`** at the slide level (not inside `content`)
2. **If `background_image` exists and is a valid URL:**
   - Set it as the slide's background image
   - Apply appropriate overlay/gradient for text readability
3. **If `background_image` is null/empty:**
   - Fall back to `background_color`
   - Or show the "Generate image..." placeholder

### Pseudo-code:
```javascript
// In L60.js (H2-section) and L61.js (H3-closing) renderers
const slideData = getSlideData();

if (slideData.background_image) {
  // Use the provided background image
  setBackgroundImage(slideData.background_image);
  applyGradientOverlay(); // For text readability
} else if (slideData.background_color) {
  // Fall back to solid color
  setBackgroundColor(slideData.background_color);
} else {
  // Show placeholder
  showImagePlaceholder();
}
```

---

## Test After Fix

Use the same presentation to verify:
- **URL:** https://web-production-f0d13.up.railway.app/p/3b38e5e9-4381-45b8-80c7-f4f15243770b
- **Slide 3 (H2-section):** Should show AI image background
- **Slide 4 (H3-closing):** Should show AI image background

Or create a new test with our test script:
```bash
cd agents/text_table_builder/v1.2/tests
./test_hseries_variants.sh
```

---

## Contact

For questions about this issue, contact the Text Service team.

**Related Files:**
- Test script: `agents/text_table_builder/v1.2/tests/test_hseries_variants.sh`
- API Reference used: `agents/director_agent/v4.0/docs/LAYOUT_SERVICE_API_REFERENCE.md`
- Test output: `agents/text_table_builder/v1.2/tests/test_outputs/hseries_20251227_182124/`
