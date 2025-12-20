# API Contract Exactness Verification Report

**Date**: December 20, 2024
**Production URL**: https://web-production-5daf.up.railway.app
**Documentation**: TEXT_SERVICE_CAPABILITIES.md v1.2.2

---

## Executive Summary

| Endpoint | Input Status | Output Status |
|----------|-------------|---------------|
| GET /v1.2/slides/health | EXACT | EXACT |
| GET /v1.2/capabilities | EXACT | EXACT |
| POST /v1.2/can-handle | EXACT | EXACT |
| POST /v1.2/slides/H1-generated | EXACT | **EXTRA + MISSING** |
| POST /v1.2/slides/C1-text | EXACT | **EXTRA** |
| POST /v1.2/slides/I1 | EXACT | **EXTRA** |
| POST /v1.2/iseries/generate | EXACT | **EXTRA + MISSING** |

**Result**: 3 of 7 endpoints are EXACT. 4 endpoints have output deviations.

---

## Detailed Findings

### Test 1: GET /v1.2/slides/health

**Input**: N/A (GET request)
**Status**: EXACT

| Documented Fields | Actual Fields | Status |
|-------------------|---------------|--------|
| status, router, version | status, router, version | EXACT |
| features.combined_generation | features.combined_generation | EXACT |
| features.structured_fields | features.structured_fields | EXACT |
| features.layout_aliases | features.layout_aliases | EXACT |
| layouts.h_series | layouts.h_series | EXACT |
| layouts.c_series | layouts.c_series | EXACT |
| layouts.i_series | layouts.i_series | EXACT |
| layouts.aliases | layouts.aliases | EXACT |

---

### Test 2: GET /v1.2/capabilities

**Input**: N/A (GET request)
**Status**: EXACT

All documented fields present. No extra fields.

---

### Test 3: POST /v1.2/can-handle

**Input Sent** (ONLY documented required fields):
```json
{
  "slide_content": {"title": "...", "topics": [...], "topic_count": 3},
  "content_hints": {"has_numbers": true, "is_comparison": false, "detected_keywords": [...]},
  "available_space": {"width": 1800, "height": 750, "layout_id": "C01"}
}
```

**Status**: EXACT

All documented response fields present:
- can_handle, confidence, reason, suggested_approach
- space_utilization.fits_well, space_utilization.estimated_fill_percent

---

### Test 4: POST /v1.2/slides/H1-generated

**Input Sent** (ONLY documented required fields):
```json
{
  "slide_number": 1,
  "narrative": "AI revolutionizing healthcare"
}
```

**Input Status**: EXACT - request accepted with only required fields

**Output Status**: **EXTRA + MISSING**

| Issue | Field | Documentation Says | Actual |
|-------|-------|-------------------|--------|
| MISSING | `metadata.visual_style` | Required | Not returned |
| EXTRA | `metadata.background_image` | Not documented | Returned |
| EXTRA | `metadata.image_generation_time_ms` | Not documented | Returned |
| EXTRA | `metadata.fallback_to_gradient` | Not documented | Returned |
| EXTRA | `metadata.validation` | Not documented | Full object returned |
| EXTRA | `metadata.generation_mode` | Not documented | Returned |
| EXTRA | `metadata.layout_type` | Not documented | Returned |

---

### Test 5: POST /v1.2/slides/C1-text

**Input Sent** (ONLY documented required fields):
```json
{
  "slide_number": 3,
  "narrative": "Our solution delivers three core advantages"
}
```

**Input Status**: EXACT - request accepted with only required fields

**Output Status**: **EXTRA**

| Issue | Field | Documentation Says | Actual |
|-------|-------|-------------------|--------|
| EXTRA | `metadata.visual_style` | Not documented in Part 1.5 | Returned ("illustrated") |

All other documented fields present and correct.

---

### Test 6: POST /v1.2/slides/I1

**Input Sent** (ONLY documented required fields):
```json
{
  "slide_number": 4,
  "narrative": "Our team brings diverse expertise"
}
```

**Input Status**: EXACT - request accepted with only required fields

**Output Status**: **EXTRA**

| Issue | Field | Documentation Says | Actual |
|-------|-------|-------------------|--------|
| EXTRA | `metadata.validation` | Not documented in Part 1.6 | Full object returned |

All other documented fields present and correct.

---

### Test 7: POST /v1.2/iseries/generate

**Input Sent** (ONLY documented required fields):
```json
{
  "slide_number": 4,
  "layout_type": "I1",
  "title": "Key Benefits",
  "narrative": "Our solution provides three advantages",
  "topics": ["Speed", "Reliability", "Cost"]
}
```

**Input Status**: EXACT - request accepted with only required fields

**Output Status**: **EXTRA + MISSING**

| Issue | Field | Documentation Says | Actual |
|-------|-------|-------------------|--------|
| MISSING | `metadata.image_generation_time_ms` | Required | Not returned |
| MISSING | `metadata.content_generation_time_ms` | Required | Not returned |
| MISSING | `metadata.total_generation_time_ms` | Required | Not returned |
| EXTRA | `background_color` | Not documented in Part 5.1 | Returned at top level |
| EXTRA | `metadata.generation_time_ms` | Not documented (uses different name) | Returned |
| EXTRA | `metadata.validation` | Not documented | Full object returned |

---

## Summary of Contract Deviations

### Fields Returned But NOT Documented (EXTRA)

| Endpoint | Undocumented Fields |
|----------|---------------------|
| H1-generated | `metadata.background_image`, `metadata.image_generation_time_ms`, `metadata.fallback_to_gradient`, `metadata.validation`, `metadata.generation_mode`, `metadata.layout_type` |
| C1-text | `metadata.visual_style` |
| I1 | `metadata.validation` |
| iseries/generate | `background_color`, `metadata.generation_time_ms`, `metadata.validation` |

### Fields Documented But NOT Returned (MISSING)

| Endpoint | Missing Fields |
|----------|----------------|
| H1-generated | `metadata.visual_style` |
| iseries/generate | `metadata.image_generation_time_ms`, `metadata.content_generation_time_ms`, `metadata.total_generation_time_ms` |

---

## Recommendations

### Option A: Update Documentation to Match Code
1. Add undocumented fields to TEXT_SERVICE_CAPABILITIES.md
2. Remove references to fields that don't exist

### Option B: Update Code to Match Documentation
1. Remove undocumented fields from responses
2. Add missing documented fields

### Field-Specific Analysis

| Field | Appears In | Recommendation |
|-------|------------|----------------|
| `metadata.validation` | H1-generated, I1, iseries | Either document or remove - validation info may be useful for debugging |
| `metadata.visual_style` | C1-text (undoc), H1-generated (doc but missing) | Normalize across all endpoints |
| `background_color` | iseries/generate (undoc) | Document it (already in Part 1.6 for /slides/I1) |
| Timing fields | iseries/generate uses single `generation_time_ms` instead of 3 separate | Code has simplified timing; update docs |

---

## Test Artifacts

All response JSONs saved to: `tests/api_test_outputs_20251220/`
