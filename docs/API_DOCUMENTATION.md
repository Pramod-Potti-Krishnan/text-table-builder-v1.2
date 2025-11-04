# Text Service v1.2 - API Documentation

**Base URL:** `https://web-production-5daf.up.railway.app`

**Version:** 1.2.0

**Architecture:** Deterministic Assembly with Element-Based Content Generation

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
   - [Health Check](#health-check)
   - [List Variants](#list-variants)
   - [Get Variant Details](#get-variant-details)
   - [Generate Content](#generate-content)
4. [Request Models](#request-models)
5. [Response Models](#response-models)
6. [Error Handling](#error-handling)
7. [Examples](#examples)

---

## Overview

The Text Service v1.2 provides AI-powered content generation for presentation slides using a deterministic template assembly architecture. It supports 34 platinum-approved variants across 10 slide types with precise character count control (baseline ± 5%).

**Key Features:**
- 34 platinum variants across 10 slide types
- Single-call generation for content coherence
- Parallel processing (3-5x speedup)
- Character count validation (baseline ± 5%)
- Gemini Flash/Pro model routing
- Template caching for performance

---

## Authentication

**Current Version:** No authentication required.

**Future Versions:** Will support API key authentication.

---

## Endpoints

### Health Check

Check service health and configuration.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "version": "1.2.0",
  "llm_service": {
    "initialized": true,
    "model_routing": true,
    "flash_model": "gemini-2.0-flash-exp",
    "pro_model": "gemini-1.5-pro"
  }
}
```

**Example:**
```bash
curl https://web-production-5daf.up.railway.app/health
```

---

### List Variants

Get a list of all available variants organized by slide type.

**Endpoint:** `GET /v1.2/variants`

**Response:**
```json
{
  "total_variants": 34,
  "slide_types": {
    "matrix": [
      {
        "variant_id": "matrix_2x2",
        "slide_type": "matrix",
        "description": "Matrix layouts with boxes in grid formation",
        "layout": "2x2 grid (4 boxes)"
      },
      {
        "variant_id": "matrix_2x3",
        "slide_type": "matrix",
        "description": "Matrix layouts with boxes in grid formation",
        "layout": "2x3 grid (6 boxes)"
      }
    ],
    "grid": [...],
    "comparison": [...],
    "sequential": [...],
    "asymmetric": [...],
    "hybrid": [...],
    "metrics": [...],
    "impact_quote": [...],
    "table": [...],
    "single_column": [...]
  }
}
```

**Example:**
```bash
curl https://web-production-5daf.up.railway.app/v1.2/variants
```

**Available Slide Types:**
- `matrix` (2 variants): Grid-based matrix layouts
- `grid` (9 variants): Icon/numbered grid layouts
- `comparison` (3 variants): Multi-column comparisons
- `sequential` (3 variants): Numbered sequential steps
- `asymmetric` (3 variants): 8:4 asymmetric layouts with sidebar
- `hybrid` (2 variants): Combined grid and text layouts
- `metrics` (4 variants): KPI metric displays
- `impact_quote` (1 variant): Customer success story quote
- `table` (4 variants): Multi-column data tables
- `single_column` (3 variants): Full-width sectioned layouts

---

### Get Variant Details

Get detailed information about a specific variant.

**Endpoint:** `GET /v1.2/variant/{variant_id}`

**Path Parameters:**
- `variant_id` (string, required): The variant identifier (e.g., "matrix_2x2")

**Response:**
```json
{
  "variant_id": "matrix_2x2",
  "slide_type": "matrix",
  "description": "2x2 matrix layout with 4 equal boxes",
  "layout": "2x2 grid (4 boxes)",
  "elements": [
    {
      "element_id": "box_1",
      "element_type": "text_box",
      "fields": {
        "title": {
          "baseline": 30,
          "min": 27,
          "max": 32
        },
        "description": {
          "baseline": 240,
          "min": 228,
          "max": 252
        }
      }
    }
  ]
}
```

**Example:**
```bash
curl https://web-production-5daf.up.railway.app/v1.2/variant/matrix_2x2
```

---

### Generate Content

Generate slide content for a specific variant using AI.

**Endpoint:** `POST /v1.2/generate`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:** See [Request Models](#request-models)

**Response:** See [Response Models](#response-models)

**Example:**
```bash
curl -X POST https://web-production-5daf.up.railway.app/v1.2/generate \
  -H "Content-Type: application/json" \
  -d '{
    "variant_id": "matrix_2x2",
    "slide_spec": {
      "slide_title": "Digital Transformation Strategy",
      "slide_purpose": "Present our four-pillar transformation approach",
      "key_message": "Transform business across all dimensions"
    }
  }'
```

---

## Request Models

### V1_2_GenerationRequest

Main request model for content generation.

```typescript
{
  // REQUIRED: Variant identifier
  "variant_id": string,  // e.g., "matrix_2x2", "table_3col", "grid_2x3"

  // REQUIRED: Slide-level specifications
  "slide_spec": {
    "slide_title": string,        // Title of the slide
    "slide_purpose": string,       // Purpose or goal of this slide
    "key_message": string,         // Main message to convey
    "target_points"?: string[],    // Optional: Specific points to include
    "tone"?: string,               // Default: "professional"
    "audience"?: string            // Default: "business stakeholders"
  },

  // OPTIONAL: Presentation-level context
  "presentation_spec"?: {
    "presentation_title": string,
    "presentation_type": string,   // e.g., "Business Proposal", "Product Demo"
    "industry"?: string,           // e.g., "Technology", "Healthcare"
    "company"?: string,
    "prior_slides_summary"?: string,
    "current_slide_number"?: number,
    "total_slides"?: number
  },

  // OPTIONAL: Element relationships
  "element_relationships"?: {
    "element_id": "relationship description"
  },

  // OPTIONAL: Generation settings
  "enable_parallel"?: boolean,              // Default: true
  "validate_character_counts"?: boolean     // Default: true
}
```

### SlideSpecification

Detailed slide-level context:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `slide_title` | string | Yes | - | Title of the slide |
| `slide_purpose` | string | Yes | - | Purpose or goal of this slide |
| `key_message` | string | Yes | - | Main message to convey |
| `target_points` | string[] | No | null | Specific points to include |
| `tone` | string | No | "professional" | Desired tone |
| `audience` | string | No | "business stakeholders" | Target audience |

### PresentationSpecification

Optional presentation-level context:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `presentation_title` | string | Yes | Title of the presentation |
| `presentation_type` | string | Yes | Type (e.g., "Business Proposal") |
| `industry` | string | No | Industry context |
| `company` | string | No | Company name |
| `prior_slides_summary` | string | No | Summary of prior slides |
| `current_slide_number` | number | No | Current slide number |
| `total_slides` | number | No | Total slides in deck |

---

## Response Models

### V1_2_GenerationResponse

Success response from content generation:

```typescript
{
  // Status
  "success": boolean,

  // Generated HTML (complete, ready to use)
  "html": string,

  // Element details
  "elements": [
    {
      "element_id": string,
      "element_type": string,
      "placeholders": {
        "field_name": "placeholder_name"
      },
      "generated_content": {
        "field_name": "generated text"
      },
      "character_counts": {
        "field_name": number
      }
    }
  ],

  // Metadata
  "metadata": {
    "variant_id": string,
    "template_path": string,
    "element_count": number,
    "generation_mode": "parallel" | "sequential"
  },

  // Validation (if enabled)
  "validation": {
    "valid": boolean,
    "violations": [
      {
        "element_id": string,
        "field": string,
        "actual_count": number,
        "required_min": number,
        "required_max": number
      }
    ]
  },

  // Error (if failed)
  "error"?: string,
  "variant_id"?: string,
  "template_path"?: string
}
```

### Success Response Example

```json
{
  "success": true,
  "html": "<div style=\"display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px;\">...</div>",
  "elements": [
    {
      "element_id": "box_1",
      "element_type": "text_box",
      "placeholders": {
        "title": "{box_1_title}",
        "description": "{box_1_description}"
      },
      "generated_content": {
        "title": "Innovation Leadership",
        "description": "Drive transformative change through cutting-edge technology adoption..."
      },
      "character_counts": {
        "title": 30,
        "description": 245
      }
    },
    {
      "element_id": "box_2",
      "element_type": "text_box",
      "placeholders": {
        "title": "{box_2_title}",
        "description": "{box_2_description}"
      },
      "generated_content": {
        "title": "Customer Centricity",
        "description": "Put customers at the heart of every decision through data-driven insights..."
      },
      "character_counts": {
        "title": 29,
        "description": 238
      }
    }
  ],
  "metadata": {
    "variant_id": "matrix_2x2",
    "template_path": "app/templates/matrix/matrix_2x2.html",
    "element_count": 4,
    "generation_mode": "parallel"
  },
  "validation": {
    "valid": true,
    "violations": []
  }
}
```

### Error Response Example

```json
{
  "success": false,
  "error": "Invalid variant_id: unknown_variant",
  "variant_id": "unknown_variant"
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid input) |
| 404 | Not Found (invalid variant_id) |
| 500 | Internal Server Error |
| 503 | Service Unavailable (health check failed) |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Invalid variant_id" | Unknown variant | Check `/v1.2/variants` for valid IDs |
| "Missing required field" | Incomplete request | Ensure all required fields provided |
| "Character count validation failed" | Content exceeds limits | Adjust `slide_spec` for shorter content |
| "Generation failed" | LLM service error | Retry request, check service health |

---

## Examples

### Example 1: Simple Matrix 2×2 Generation

**Request:**
```bash
curl -X POST https://web-production-5daf.up.railway.app/v1.2/generate \
  -H "Content-Type: application/json" \
  -d '{
    "variant_id": "matrix_2x2",
    "slide_spec": {
      "slide_title": "Our Values",
      "slide_purpose": "Communicate core company values",
      "key_message": "Four pillars guide everything we do"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "html": "<div style=\"display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px;\">...</div>",
  "elements": [...],
  "metadata": {
    "variant_id": "matrix_2x2",
    "element_count": 4,
    "generation_mode": "parallel"
  },
  "validation": {
    "valid": true,
    "violations": []
  }
}
```

---

### Example 2: Table with Presentation Context

**Request:**
```bash
curl -X POST https://web-production-5daf.up.railway.app/v1.2/generate \
  -H "Content-Type: application/json" \
  -d '{
    "variant_id": "table_3col",
    "slide_spec": {
      "slide_title": "Q4 Performance Metrics",
      "slide_purpose": "Compare performance across three regions",
      "key_message": "All regions exceeded targets",
      "tone": "data-driven",
      "audience": "executive team"
    },
    "presentation_spec": {
      "presentation_title": "Q4 2024 Business Review",
      "presentation_type": "Quarterly Business Review",
      "industry": "Technology",
      "company": "Acme Corp",
      "current_slide_number": 5,
      "total_slides": 12
    }
  }'
```

---

### Example 3: Comparison with Target Points

**Request:**
```bash
curl -X POST https://web-production-5daf.up.railway.app/v1.2/generate \
  -H "Content-Type: application/json" \
  -d '{
    "variant_id": "comparison_3col",
    "slide_spec": {
      "slide_title": "Cloud Provider Comparison",
      "slide_purpose": "Compare three cloud platforms",
      "key_message": "Each provider has distinct strengths",
      "target_points": [
        "Pricing model differences",
        "Regional availability",
        "Service portfolio breadth",
        "Enterprise support quality"
      ]
    }
  }'
```

---

### Example 4: Sequential Process Flow

**Request:**
```bash
curl -X POST https://web-production-5daf.up.railway.app/v1.2/generate \
  -H "Content-Type: application/json" \
  -d '{
    "variant_id": "sequential_4col",
    "slide_spec": {
      "slide_title": "Customer Onboarding Journey",
      "slide_purpose": "Outline the 4-step onboarding process",
      "key_message": "Seamless onboarding in 4 simple steps",
      "tone": "friendly",
      "audience": "new customers"
    },
    "enable_parallel": true,
    "validate_character_counts": true
  }'
```

---

### Example 5: Metrics Dashboard

**Request:**
```bash
curl -X POST https://web-production-5daf.up.railway.app/v1.2/generate \
  -H "Content-Type: application/json" \
  -d '{
    "variant_id": "metrics_3col",
    "slide_spec": {
      "slide_title": "Key Performance Indicators",
      "slide_purpose": "Display top 3 metrics with insights",
      "key_message": "Strong performance across all KPIs"
    }
  }'
```

---

## Integration Guide for Director Agent

### Director v3.4 Integration

When calling Text Service v1.2 from Director Agent:

```python
import requests

# Text Service configuration
TEXT_SERVICE_URL = "https://web-production-5daf.up.railway.app"

def generate_slide_content(variant_id: str, slide_spec: dict, presentation_spec: dict = None):
    """
    Generate slide content using Text Service v1.2

    Args:
        variant_id: Variant identifier (e.g., "matrix_2x2")
        slide_spec: Slide-level specifications
        presentation_spec: Optional presentation context

    Returns:
        dict: Response with HTML and metadata
    """
    payload = {
        "variant_id": variant_id,
        "slide_spec": slide_spec,
        "presentation_spec": presentation_spec,
        "enable_parallel": True,
        "validate_character_counts": True
    }

    response = requests.post(
        f"{TEXT_SERVICE_URL}/v1.2/generate",
        json=payload,
        timeout=60
    )

    response.raise_for_status()
    return response.json()

# Example usage
result = generate_slide_content(
    variant_id="matrix_2x2",
    slide_spec={
        "slide_title": "Digital Strategy",
        "slide_purpose": "Present transformation pillars",
        "key_message": "Four-pillar approach"
    }
)

# Extract HTML for Layout Builder
html_content = result["html"]
```

### Variant Selection Logic

Map slide types to variants:

```python
VARIANT_MAPPING = {
    "title": "impact_quote",  # or create dedicated title variant
    "section": "impact_quote",
    "closing": "impact_quote",
    "matrix": "matrix_2x2",  # or "matrix_2x3" based on content
    "grid": "grid_2x3",  # Choose based on item count
    "comparison": "comparison_2col",  # "comparison_3col", "comparison_4col"
    "table": "table_2col",  # "table_3col", "table_4col", "table_5col"
    "sequential": "sequential_3col",  # "sequential_4col", "sequential_5col"
    "metrics": "metrics_3col",  # "metrics_4col", "metrics_2x2_grid", "metrics_3x2_grid"
    "hybrid": "hybrid_top_2x2",  # or "hybrid_left_2x2"
    "asymmetric": "asymmetric_8_4_3section",  # or 4/5 sections
    "single_column": "single_column_3section"  # or 4/5 sections
}
```

---

## Rate Limits & Performance

**Current Limits:** No rate limits enforced

**Performance:**
- Average response time: 2-5 seconds per slide
- Parallel generation: 3-5x faster than sequential
- Template caching reduces overhead by ~30%

**Best Practices:**
- Use `enable_parallel: true` for faster generation
- Cache variant details locally to reduce `/v1.2/variants` calls
- Implement retry logic with exponential backoff for 500 errors

---

## Support & Feedback

**Issues:** Report bugs or feature requests via GitHub repository

**Documentation Updates:** This document reflects API version 1.2.0

**Last Updated:** November 4, 2025
