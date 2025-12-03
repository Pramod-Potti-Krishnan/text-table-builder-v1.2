# Layout Service AI API Integration

**Version**: 1.2.0
**Service**: Text & Table Builder
**Base URL**: `http://localhost:8000/api/ai`

## Overview

The Layout Service AI API provides 6 endpoints for generating and manipulating text and table content within the Deckster presentation builder. All endpoints accept grid-based constraints (12x8 grid system) and return HTML with inline CSS suitable for reveal.js slides.

## Files Created

All files are located in:
```
/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/text_table_builder/v1.2/
```

### New Files

| File | Description |
|------|-------------|
| `app/models/layout_models.py` | Pydantic request/response models and enums |
| `app/core/layout/__init__.py` | Module exports |
| `app/core/layout/grid_calculator.py` | Grid-to-character constraint calculations |
| `app/core/layout/base_layout_generator.py` | Abstract base class for all generators |
| `app/core/layout/text_generator.py` | TextGenerate, TextTransform, TextAutofit generators |
| `app/core/layout/table_generator.py` | TableGenerate, TableTransform, TableAnalyze generators |
| `app/api/layout_routes.py` | FastAPI router with all 6 endpoints |

### Modified Files

| File | Changes |
|------|---------|
| `main.py` | Added import and router registration for layout_routes |

## Complete File Paths

```
/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/text_table_builder/v1.2/
├── main.py                                    # Modified - added layout_router
├── LAYOUT_SERVICE_API.md                      # This documentation
├── app/
│   ├── api/
│   │   ├── layout_routes.py                   # NEW - 6 Layout Service endpoints
│   │   ├── hero_routes.py                     # Existing
│   │   └── v1_2_routes.py                     # Existing
│   ├── core/
│   │   ├── layout/                            # NEW directory
│   │   │   ├── __init__.py                    # Module exports
│   │   │   ├── base_layout_generator.py       # Abstract base class
│   │   │   ├── grid_calculator.py             # Grid constraint calculations
│   │   │   ├── table_generator.py             # Table generators (3)
│   │   │   └── text_generator.py              # Text generators (3)
│   │   └── hero/                              # Existing
│   └── models/
│       ├── layout_models.py                   # NEW - All Pydantic models
│       └── requests.py                        # Existing
└── .env.example                               # Environment configuration
```

---

## Endpoints

### Text Endpoints

#### 1. POST `/api/ai/text/generate`

Generate new text content from a prompt.

**Request**:
```json
{
    "prompt": "Write 3 bullet points about AI benefits",
    "presentationId": "550e8400-e29b-41d4-a716-446655440000",
    "slideId": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "elementId": "elem-001",
    "context": {
        "presentationTitle": "AI Strategy",
        "slideIndex": 2,
        "slideCount": 10
    },
    "constraints": {
        "gridWidth": 6,
        "gridHeight": 4
    },
    "options": {
        "tone": "professional",
        "format": "bullets"
    }
}
```

**Response**:
```json
{
    "success": true,
    "data": {
        "generationId": "uuid",
        "content": {
            "html": "<ul style=\"...\"><li>...</li></ul>"
        },
        "metadata": {
            "characterCount": 353,
            "wordCount": 42,
            "estimatedReadTime": 12.6,
            "format": "bullets",
            "tone": "professional"
        },
        "suggestions": {
            "alternativeVersions": ["<ul>...</ul>", "<ul>...</ul>"],
            "expandable": true,
            "reducible": true
        }
    },
    "error": null
}
```

#### 2. POST `/api/ai/text/transform`

Transform existing text content.

**Transformations**: `expand`, `condense`, `simplify`, `formalize`, `casualize`, `bulletize`, `paragraphize`, `rephrase`, `proofread`, `translate`

**Request**:
```json
{
    "sourceContent": "<p>AI helps businesses grow.</p>",
    "transformation": "expand",
    "presentationId": "test-001",
    "slideId": "slide-001",
    "elementId": "elem-001",
    "context": {
        "presentationTitle": "AI",
        "slideIndex": 1,
        "slideCount": 5
    },
    "constraints": {
        "gridWidth": 8,
        "gridHeight": 4
    }
}
```

**Response**:
```json
{
    "success": true,
    "data": {
        "transformationId": "uuid",
        "content": {
            "html": "<p>AI helps businesses grow significantly by...</p>"
        },
        "changes": {
            "characterDelta": 459,
            "significantChanges": ["Content expanded by 459 characters", "Applied expand transformation"]
        },
        "metadata": {
            "characterCount": 484,
            "wordCount": 60,
            "estimatedReadTime": 18.0,
            "format": "mixed",
            "tone": "professional"
        }
    },
    "error": null
}
```

#### 3. POST `/api/ai/text/autofit`

Fit text to element dimensions.

**Strategies**: `reduce_font`, `truncate`, `smart_condense`, `overflow`

**Request**:
```json
{
    "content": "<p>Long paragraph that needs to be condensed...</p>",
    "presentationId": "test-001",
    "slideId": "slide-001",
    "elementId": "elem-001",
    "targetFit": {
        "gridWidth": 3,
        "gridHeight": 2
    },
    "strategy": "smart_condense",
    "preserveFormatting": true
}
```

**Response**:
```json
{
    "success": true,
    "data": {
        "content": "<p>Condensed paragraph...</p>",
        "recommendedFontSize": null,
        "fits": true,
        "overflow": null
    },
    "error": null
}
```

### Table Endpoints

#### 4. POST `/api/ai/table/generate`

Generate a table from a prompt.

**Style Presets**: `minimal`, `bordered`, `striped`, `modern`, `professional`, `colorful`

**Request**:
```json
{
    "prompt": "Create a comparison of Q3 vs Q4 revenue by region",
    "presentationId": "test-001",
    "slideId": "slide-001",
    "elementId": "elem-001",
    "context": {
        "presentationTitle": "Quarterly Review",
        "slideIndex": 3,
        "slideCount": 10
    },
    "constraints": {
        "gridWidth": 10,
        "gridHeight": 5
    },
    "style": {
        "preset": "professional"
    }
}
```

**Response**:
```json
{
    "success": true,
    "data": {
        "generationId": "uuid",
        "content": {
            "html": "<table style=\"...\">...</table>"
        },
        "metadata": {
            "rowCount": 5,
            "columnCount": 4,
            "hasHeader": true,
            "hasFooter": false,
            "columnTypes": ["text", "text", "text", "text"],
            "hasNumericData": false,
            "hasDateData": false
        },
        "editInfo": {
            "editableCells": true,
            "suggestedColumnWidths": [20.0, 20.0, 20.0, 20.0]
        }
    },
    "error": null
}
```

#### 5. POST `/api/ai/table/transform`

Transform table structure.

**Transformations**: `add_column`, `add_row`, `remove_column`, `remove_row`, `sort`, `summarize`, `transpose`, `expand`, `merge_cells`, `split_column`

**Request**:
```json
{
    "sourceTable": "<table>...</table>",
    "transformation": "add_column",
    "presentationId": "test-001",
    "slideId": "slide-001",
    "elementId": "elem-001",
    "constraints": {
        "gridWidth": 10,
        "gridHeight": 5
    },
    "options": {
        "content": "Add Q4 revenue column"
    }
}
```

**Response**:
```json
{
    "success": true,
    "data": {
        "transformationId": "uuid",
        "content": {
            "html": "<table>...</table>"
        },
        "metadata": {
            "rowCount": 1,
            "columnCount": 3,
            "hasHeader": true,
            "hasFooter": false,
            "columnTypes": ["text", "text", "text"],
            "hasNumericData": false,
            "hasDateData": false
        }
    },
    "error": null
}
```

#### 6. POST `/api/ai/table/analyze`

Analyze table data for insights.

**Analysis Types**: `summary`, `trends`, `outliers`, `visualization`

**Request**:
```json
{
    "sourceTable": "<table><thead><tr><th>Region</th><th>Q3</th><th>Q4</th></tr></thead><tbody><tr><td>North</td><td>12M</td><td>14M</td></tr></tbody></table>",
    "analysisType": "summary",
    "presentationId": "test-001",
    "slideId": "slide-001",
    "elementId": "elem-001"
}
```

**Response**:
```json
{
    "success": true,
    "data": {
        "analysisId": "uuid",
        "summary": "The table presents sales performance for two regions...",
        "insights": [
            {
                "type": "trend",
                "title": "North Region Growth",
                "description": "The North region demonstrated positive growth...",
                "confidence": 0.95
            }
        ],
        "statistics": {
            "Q3": {"min": 8, "max": 12, "average": 10},
            "Q4": {"min": 7, "max": 14, "average": 10.5}
        },
        "recommendations": {
            "suggestedChartType": "bar",
            "suggestedHighlights": [0],
            "suggestedSorting": {"column": 2, "direction": "desc"}
        },
        "metadata": {
            "rowCount": 2,
            "columnCount": 3,
            "hasHeader": true,
            "hasFooter": false,
            "columnTypes": ["text", "text", "text"],
            "hasNumericData": false,
            "hasDateData": false
        }
    },
    "error": null
}
```

---

## Utility Endpoints

### GET `/api/ai/health`

Health check endpoint.

**Response**:
```json
{
    "status": "healthy",
    "service": "Text & Table Builder v1.2 - Layout Service Integration",
    "endpoints": {
        "text": {
            "generate": "/api/ai/text/generate",
            "transform": "/api/ai/text/transform",
            "autofit": "/api/ai/text/autofit"
        },
        "table": {
            "generate": "/api/ai/table/generate",
            "transform": "/api/ai/table/transform",
            "analyze": "/api/ai/table/analyze"
        }
    },
    "grid_system": {
        "columns": 12,
        "rows": 8,
        "description": "12-column x 8-row grid system for element sizing"
    },
    "capabilities": {
        "text_tones": ["professional", "conversational", "academic", "persuasive", "casual", "technical"],
        "text_formats": ["paragraph", "bullets", "numbered", "headline", "quote", "mixed"],
        "text_transformations": ["expand", "condense", "simplify", "formalize", "casualize", "bulletize", "paragraphize", "rephrase", "proofread", "translate"],
        "table_styles": ["minimal", "bordered", "striped", "modern", "professional", "colorful"],
        "table_transformations": ["add_column", "add_row", "remove_column", "remove_row", "sort", "summarize", "transpose", "expand", "merge_cells", "split_column"]
    }
}
```

### GET `/api/ai/constraints/{grid_width}/{grid_height}`

Get content guidelines for specific grid dimensions.

**Example**: `GET /api/ai/constraints/6/4`

**Response**:
```json
{
    "valid": true,
    "grid": {
        "width": 6,
        "height": 4,
        "area": 24
    },
    "text": {
        "characters": {"min": 122, "max": 612, "target": 367},
        "words": {"min": 20, "max": 104, "target": 62},
        "layout": {"lines": 9, "chars_per_line": 80},
        "read_time_seconds": 18.6,
        "recommendations": {
            "preferred_format": "mixed",
            "bullet_count": 6,
            "paragraph_count": 2,
            "suggestion": "Use paragraph with supporting bullets"
        }
    },
    "table": {
        "max_columns": 5,
        "max_rows": 7,
        "cell_char_limit": 10,
        "header_char_limit": 8,
        "total_cells": 40
    },
    "warnings": []
}
```

---

## Grid System

The API uses a 12-column x 8-row grid system:

| Grid Size | Description | Max Characters | Recommended Format |
|-----------|-------------|----------------|-------------------|
| 3x2 | Small callout | ~153 | Short phrase or 2 bullets |
| 6x4 | Half-width text block | ~612 | Paragraph with bullets |
| 12x4 | Full-width text | ~1224 | Multi-paragraph or long list |
| 10x5 | Large table area | ~1530 | Table with 8 columns, 9 rows |

---

## Error Handling

All endpoints return consistent error responses:

```json
{
    "success": false,
    "data": null,
    "error": {
        "code": "GENERATION_FAILED",
        "message": "Error description",
        "retryable": true
    }
}
```

**Error Codes**:
- `INVALID_PROMPT` - Invalid request data (not retryable)
- `GENERATION_FAILED` - LLM generation failed (retryable)
- `TRANSFORM_FAILED` - Transformation failed (retryable)
- `AUTOFIT_FAILED` - Autofit operation failed (retryable)
- `INVALID_STRUCTURE` - Invalid table structure (not retryable)
- `ANALYSIS_FAILED` - Table analysis failed (retryable)

---

## Environment Setup

Set the following environment variables:

```bash
# Required
export GCP_PROJECT_ID=your-project-id

# Optional
export GCP_LOCATION=us-central1
export GEMINI_FLASH_MODEL=gemini-2.5-flash
export GEMINI_PRO_MODEL=gemini-2.5-pro
export ENABLE_MODEL_ROUTING=true
export LOG_LEVEL=INFO
```

---

## Running the Service

```bash
cd /Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/text_table_builder/v1.2

# Set environment variables
export GCP_PROJECT_ID=deckster-xyz

# Start the server
python3 main.py

# Or with uvicorn directly
uvicorn main:app --reload --port 8000
```

---

## Testing

Quick test commands:

```bash
# Health check
curl http://localhost:8000/api/ai/health

# Get constraints
curl http://localhost:8000/api/ai/constraints/6/4

# Generate text
curl -X POST http://localhost:8000/api/ai/text/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Write 3 bullet points about AI","presentationId":"test","slideId":"slide","elementId":"elem","context":{"presentationTitle":"Test","slideIndex":0,"slideCount":5},"constraints":{"gridWidth":6,"gridHeight":4}}'

# Generate table
curl -X POST http://localhost:8000/api/ai/table/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Q3 vs Q4 revenue by region","presentationId":"test","slideId":"slide","elementId":"elem","context":{"presentationTitle":"Test","slideIndex":0,"slideCount":5},"constraints":{"gridWidth":10,"gridHeight":5}}'
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Layout Service (Frontend)                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Text & Table Builder v1.2                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                  /api/ai/* Endpoints                     │    │
│  │   text/generate  │  text/transform  │  text/autofit     │    │
│  │   table/generate │  table/transform │  table/analyze    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                │                                  │
│                                ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │               Layout Generator Classes                   │    │
│  │   TextGenerateGenerator  │  TableGenerateGenerator      │    │
│  │   TextTransformGenerator │  TableTransformGenerator     │    │
│  │   TextAutofitGenerator   │  TableAnalyzeGenerator       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                │                                  │
│                                ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                     Vertex AI (Gemini)                   │    │
│  │         gemini-2.5-flash  │  gemini-2.5-pro             │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Output Format

All content endpoints return HTML with inline CSS:

**Text Output**:
```html
<ul style="font-family: 'Inter', sans-serif; font-size: 1.1rem; line-height: 1.8; color: #1f2937; margin: 0; padding-left: 1.5em; list-style-type: disc;">
  <li style="margin-bottom: 0.5em;">First bullet point</li>
  <li style="margin-bottom: 0.5em;">Second bullet point</li>
</ul>
```

**Table Output**:
```html
<table style="width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif;">
  <thead>
    <tr>
      <th style="padding: 12px; background-color: #1e40af; color: white;">Header</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">Cell</td>
    </tr>
  </tbody>
</table>
```

The output is designed to render properly in reveal.js slides without external CSS dependencies.
