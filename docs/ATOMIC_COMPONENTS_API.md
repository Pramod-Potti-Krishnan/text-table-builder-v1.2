# Atomic Components API v1.2

## Overview

The Atomic Components API provides direct access to slide component generation without Chain of Thought reasoning. These endpoints offer deterministic, fast generation with explicit parameterization.

**Base URL**: `/v1.2/atomic`

**Grid System**: 32 columns x 18 rows, 60px per cell (1920x1080 slides)

---

## Common Request Parameters

All atomic endpoints share these common fields:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | Content request (10-1000 chars) |
| `gridWidth` | int | Yes | - | Available width in grid units (4-32) |
| `gridHeight` | int | Yes | - | Available height in grid units (4-18) |
| `context` | object | No | null | Slide/presentation context |
| `variant` | string | No | null | Specific color variant |
| `placeholder_mode` | bool | No | false | Skip LLM call, use placeholders |
| `layout` | string | No | "horizontal" | Layout: horizontal, vertical, grid |
| `grid_cols` | int | No | null | Columns for grid layout (1-6) |
| `transparency` | float | No | varies | Box opacity (0.0-1.0) |

### Context Object

```json
{
  "slide_title": "Quarterly Review",
  "slide_purpose": "inform",
  "key_message": "Strong growth across all regions",
  "audience": "executive",
  "tone": "professional",
  "presentation_title": "Q4 2024 Results",
  "industry": "technology",
  "company": "Acme Corp"
}
```

---

## Endpoints

### 1. METRICS

**Endpoint**: `POST /v1.2/atomic/METRICS`

Generates 1-4 gradient-filled metric cards with large numbers, labels, and descriptions.

**Default Transparency**: 1.0 (solid - gradient backgrounds)

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `count` | int | 3 | 1-4 | Number of metric cards |

**Slots per Instance**:
- `metric_number`: Main value (e.g., "95%", "$2.4M")
- `metric_label`: UPPERCASE label
- `metric_description`: Supporting context

**Variants**: purple, pink, cyan, green

**Example Request**:
```json
{
  "prompt": "Q4 performance: revenue up 23%, customers grew 45%, margin improved to 18%",
  "count": 3,
  "gridWidth": 28,
  "gridHeight": 8,
  "layout": "horizontal"
}
```

---

### 2. SEQUENTIAL

**Endpoint**: `POST /v1.2/atomic/SEQUENTIAL`

Generates 1-6 numbered step cards for processes, phases, or sequential items.

**Default Transparency**: 0.6 (60% transparent)

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `count` | int | 4 | 1-6 | Number of steps |

**Slots per Instance**:
- `card_number`: Step number (1-6)
- `card_title`: Step title
- `card_description`: Detailed explanation

**Variants**: blue, green, yellow, pink

**Example Request**:
```json
{
  "prompt": "4-step employee onboarding: orientation, training, mentorship, evaluation",
  "count": 4,
  "gridWidth": 28,
  "gridHeight": 10,
  "layout": "horizontal"
}
```

---

### 3. COMPARISON

**Endpoint**: `POST /v1.2/atomic/COMPARISON`

Generates 1-4 comparison columns with headings and flexible item lists.

**Default Transparency**: 0.6

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `count` | int | 3 | 1-4 | Number of columns |
| `items_per_column` | int | 5 | 1-7 | Items per column |

**Slots per Instance**:
- `column_heading`: Column title
- `item_1` through `item_N`: Comparison points

**Variants**: blue, red, green, purple, orange

**Example Request**:
```json
{
  "prompt": "Compare Standard, Professional, and Enterprise pricing plans",
  "count": 3,
  "items_per_column": 5,
  "gridWidth": 28,
  "gridHeight": 14,
  "layout": "horizontal"
}
```

---

### 4. SECTIONS

**Endpoint**: `POST /v1.2/atomic/SECTIONS`

Generates 1-5 colored sections with headings and flexible bullet lists.

**Default Transparency**: 0.6

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `count` | int | 3 | 1-5 | Number of sections |
| `bullets_per_section` | int | 3 | 1-5 | Bullets per section |

**Slots per Instance**:
- `section_heading`: Section title
- `bullet_1` through `bullet_N`: Bullet points

**Variants**: blue, red, green, amber, purple

**Example Request**:
```json
{
  "prompt": "Key benefits of sustainability: cost savings, brand reputation, environmental impact",
  "count": 3,
  "bullets_per_section": 4,
  "gridWidth": 24,
  "gridHeight": 12,
  "layout": "vertical"
}
```

---

### 5. CALLOUT

**Endpoint**: `POST /v1.2/atomic/CALLOUT`

Generates 1-2 gradient callout/sidebar boxes with headings and item lists.

**Default Transparency**: 0.6

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `count` | int | 1 | 1-2 | Number of callout boxes |
| `items_per_box` | int | 4 | 1-7 | Items per box |

**Slots per Instance**:
- `sidebar_heading`: Box heading
- `item_1` through `item_N`: Bullet items

**Variants**: blue, green, purple, amber

**Example Request**:
```json
{
  "prompt": "Key takeaways from our market analysis",
  "count": 1,
  "items_per_box": 5,
  "gridWidth": 10,
  "gridHeight": 12
}
```

---

### 6. TEXT_BULLETS

**Endpoint**: `POST /v1.2/atomic/TEXT_BULLETS`

Generates 1-4 simple text boxes with subtitle and bullet points. Clean, minimal design.

**Default Transparency**: 0.6

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `count` | int | 2 | 1-4 | Number of text boxes |
| `bullets_per_box` | int | 4 | 1-7 | Bullets per box |

**Slots per Instance**:
- `subtitle`: Section subtitle/heading
- `bullet_1` through `bullet_N`: Bullet points

**Variants**: white, light_gray, light_blue, light_purple

**Example Request**:
```json
{
  "prompt": "Key features of our new product: performance, reliability, ease of use",
  "count": 2,
  "bullets_per_box": 4,
  "gridWidth": 24,
  "gridHeight": 10,
  "layout": "horizontal"
}
```

---

### 7. BULLET_BOX

**Endpoint**: `POST /v1.2/atomic/BULLET_BOX`

Generates 1-4 rectangular boxes with sharp corners and borders. Professional, structured appearance.

**Default Transparency**: 0.6

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `count` | int | 2 | 1-4 | Number of boxes |
| `items_per_box` | int | 5 | 1-7 | Items per box |

**Slots per Instance**:
- `box_heading`: Box heading/title
- `item_1` through `item_N`: Bullet items

**Variants**: gray, blue, green, purple, amber

**Example Request**:
```json
{
  "prompt": "Project requirements and deliverables for Q1",
  "count": 2,
  "items_per_box": 5,
  "gridWidth": 24,
  "gridHeight": 12,
  "layout": "horizontal"
}
```

---

### 8. TABLE

**Endpoint**: `POST /v1.2/atomic/TABLE`

Generates 1-2 HTML tables with header row and data rows. Professional styling with alternating row colors.

**Default Transparency**: 0.6

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `count` | int | 1 | 1-2 | Number of tables |
| `columns` | int | 3 | 2-6 | Columns per table |
| `rows` | int | 4 | 2-10 | Data rows per table |

**Slots per Instance**:
- `header_1` through `header_N`: Column headers
- `rowX_colY`: Cell content (e.g., `row1_col1`, `row2_col3`)

**Variants**: gray, blue, green, purple

**Example Request**:
```json
{
  "prompt": "Compare pricing plans: Basic, Pro, Enterprise with features and pricing",
  "count": 1,
  "columns": 3,
  "rows": 4,
  "gridWidth": 28,
  "gridHeight": 10
}
```

---

### 9. NUMBERED_LIST

**Endpoint**: `POST /v1.2/atomic/NUMBERED_LIST`

Generates 1-4 numbered lists with title and ordered items. Clean numbered format for sequential or prioritized content.

**Default Transparency**: 0.6

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `count` | int | 2 | 1-4 | Number of lists |
| `items_per_list` | int | 5 | 1-10 | Items per list |

**Slots per Instance**:
- `list_title`: List title/heading
- `item_1` through `item_N`: Numbered items

**Variants**: blue, green, purple, amber, gray

**Example Request**:
```json
{
  "prompt": "Top 5 priorities for Q1: hiring, product launch, market expansion...",
  "count": 2,
  "items_per_list": 5,
  "gridWidth": 24,
  "gridHeight": 12,
  "layout": "horizontal"
}
```

---

## Common Response Model

All endpoints return the same response structure:

```json
{
  "success": true,
  "html": "<div style=\"...\">...</div>",
  "component_type": "colored_section",
  "instance_count": 3,
  "arrangement": "row_3",
  "variants_used": ["blue", "green", "amber"],
  "character_counts": {
    "section_heading": [18, 22, 20],
    "bullet_1": [65, 58, 72],
    "bullet_2": [61, 69, 64],
    "bullet_3": [70, 62, 68]
  },
  "metadata": {
    "generation_time_ms": 1250,
    "model_used": "gemini-1.5-flash",
    "grid_dimensions": {"width": 24, "height": 12},
    "space_category": "large",
    "scaling_factor": 1.05
  },
  "error": null
}
```

---

## Layout Options

### Horizontal (default)
Components arranged side-by-side in a row.
```json
{"layout": "horizontal"}
```
Produces arrangement: `row_N` (e.g., `row_3`)

### Vertical
Components stacked in a column.
```json
{"layout": "vertical"}
```
Produces arrangement: `stacked_N` (e.g., `stacked_3`)

### Grid
Components in a grid with specified columns.
```json
{"layout": "grid", "grid_cols": 2}
```
Produces arrangement: `grid_RxC` (e.g., `grid_2x2`)

---

## Transparency Control

Each component type has a default transparency:

| Component | Default | Notes |
|-----------|---------|-------|
| METRICS | 1.0 | Solid (gradient backgrounds) |
| SEQUENTIAL | 0.6 | 60% transparent |
| COMPARISON | 0.6 | 60% transparent |
| SECTIONS | 0.6 | 60% transparent |
| CALLOUT | 0.6 | 60% transparent |
| TEXT_BULLETS | 0.6 | 60% transparent |
| BULLET_BOX | 0.6 | 60% transparent |
| TABLE | 0.6 | 60% transparent |
| NUMBERED_LIST | 0.6 | 60% transparent |

Override with the `transparency` parameter (0.0 - 1.0).

---

## Placeholder Mode

Use `placeholder_mode: true` to generate components instantly without LLM calls. Useful for:
- Layout previews
- Template design
- Testing

```json
{
  "prompt": "Any prompt",
  "count": 3,
  "gridWidth": 24,
  "gridHeight": 10,
  "placeholder_mode": true
}
```

---

## Utility Endpoints

### Health Check
`GET /v1.2/atomic/health`

Returns service status and endpoint configurations.

### List Components
`GET /v1.2/atomic/components`

Returns detailed specifications for all 9 atomic components.

---

## Style Specifications

### Typography (Non-METRICS)

| Element | Size | Weight |
|---------|------|--------|
| Headings | 28px | 700 |
| Body Text | 21px | 400 |
| Step Numbers | 62px | 900 |

### Text Colors

| Usage | Color |
|-------|-------|
| Primary (light bg) | #1f2937 |
| Secondary | #374151 |
| Muted | #6b7280 |
| Light (dark bg) | #ffffff |

### Bullets
All bullet lists use CSS `list-style-type: disc` with black/gray text (#374151).

---

## Error Responses

| Status | Description |
|--------|-------------|
| 400 | Bad Request - Invalid parameters |
| 504 | Gateway Timeout - LLM request timed out |
| 500 | Internal Server Error |

```json
{
  "success": false,
  "html": null,
  "component_type": "colored_section",
  "instance_count": 3,
  "arrangement": "none",
  "variants_used": [],
  "character_counts": {},
  "metadata": {...},
  "error": "Failed to generate content"
}
```

---

## Version History

### v1.2.0 (Current)
- Added 4 new endpoints: TEXT_BULLETS, BULLET_BOX, TABLE, NUMBERED_LIST
- Added layout options: horizontal, vertical, grid
- Added transparency control with component-specific defaults
- Black CSS disc bullets for all bullet lists
- Standardized fonts: 28px headings, 21px body

### v1.1.0
- Added `count=1` support for all types
- Added `placeholder_mode` for instant generation

### v1.0.0
- Initial atomic component endpoints (5 types)
