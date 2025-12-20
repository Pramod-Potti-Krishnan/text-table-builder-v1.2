# Note to Director Team: API Contract Discrepancies

**From**: Text Service Team
**To**: Director Team
**Date**: December 20, 2024
**Subject**: API Contract Verification Results - Guidance Requested

---

## Context

We completed a verification of the API contract documented in:

```
/agents/director_agent/v4.0/docs/TEXT_SERVICE_CAPABILITIES.md
```

The goal was to confirm that the documentation is **exact** - meaning:
- Input requires ONLY the documented fields (no hidden required fields)
- Output returns EXACTLY the documented fields (no extra, no missing)

---

## Summary of Findings

| Endpoint | Input | Output |
|----------|-------|--------|
| GET /v1.2/slides/health | EXACT | EXACT |
| GET /v1.2/capabilities | EXACT | EXACT |
| POST /v1.2/can-handle | EXACT | EXACT |
| POST /v1.2/slides/H1-generated | EXACT | Discrepancies |
| POST /v1.2/slides/C1-text | EXACT | Discrepancies |
| POST /v1.2/slides/I1 | EXACT | Discrepancies |
| POST /v1.2/iseries/generate | EXACT | Discrepancies |

**Good news**: All inputs work correctly with only the documented required fields.

**Issue**: Some responses contain extra undocumented fields, and a few documented fields are missing.

---

## Detailed Discrepancies

### 1. Extra Fields Returned (Not in Documentation)

| Endpoint | Extra Fields Being Returned |
|----------|----------------------------|
| `/v1.2/slides/H1-generated` | `metadata.background_image`, `metadata.image_generation_time_ms`, `metadata.fallback_to_gradient`, `metadata.validation`, `metadata.generation_mode`, `metadata.layout_type` |
| `/v1.2/slides/C1-text` | `metadata.visual_style` |
| `/v1.2/slides/I1` | `metadata.validation` |
| `/v1.2/iseries/generate` | `background_color`, `metadata.generation_time_ms`, `metadata.validation` |

### 2. Missing Fields (Documented but Not Returned)

| Endpoint | Missing Fields |
|----------|----------------|
| `/v1.2/slides/H1-generated` | `metadata.visual_style` |
| `/v1.2/iseries/generate` | `metadata.image_generation_time_ms`, `metadata.content_generation_time_ms`, `metadata.total_generation_time_ms` |

---

## Questions for Director Team

### Q1: Are any of these discrepancies breaking for you?

If Director is already consuming any of these fields (documented or undocumented), removing them would be breaking. Please confirm:

- Are you using `metadata.validation` from any endpoint?
- Are you using `metadata.image_generation_time_ms` / `metadata.content_generation_time_ms` / `metadata.total_generation_time_ms` from `/v1.2/iseries/generate`?
- Are you relying on any other undocumented fields listed above?

### Q2: What is your preference for resolution?

**Option A: Documentation-Only Update (Non-Breaking)**
- Add the extra fields to documentation
- Remove references to missing fields from documentation
- No code changes

**Option B: Code Cleanup (Recommended if Non-Breaking)**
- Remove unnecessary extra fields from responses
- Add missing documented fields to responses
- Update documentation to match final state

Our recommendation leans toward **Option B** because:
- Extra fields add noise to responses
- Makes future debugging and error analysis harder
- Cleaner contract = easier maintenance for both teams

However, we will follow your guidance based on what Director is actually consuming.

---

## Proposed Path Forward

1. **Director team reviews** this note and confirms which fields are being used
2. **If non-breaking**: We clean up the responses (remove extras, add missing)
3. **If breaking**: We coordinate a migration path
4. **Final step**: Update TEXT_SERVICE_CAPABILITIES.md to be exact

---

## Reference Files

- **API Documentation**: `/agents/director_agent/v4.0/docs/TEXT_SERVICE_CAPABILITIES.md`
- **Test Report**: `/agents/text_table_builder/v1.2/tests/CONTRACT_EXACTNESS_REPORT.md`
- **Test Outputs**: `/agents/text_table_builder/v1.2/tests/api_test_outputs_20251220/`

---

Please advise on how you'd like us to proceed.

**Text Service Team**
