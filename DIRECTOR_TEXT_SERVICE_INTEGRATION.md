# Director Agent - Text Service v1.2 Integration Guide

**Date**: 2025-12-01
**From**: Text Service Team
**To**: Director Agent Team
**Re**: Fixing 400 Errors for Content Slide Variants

---

## Executive Summary

Testing revealed that **13 content slide variants** return `400: Unknown variant_id` errors. Investigation shows:

- **12 variants** are naming mismatches (the functionality exists, but under different names)
- **1 variant** (`grid_3x3`) does not exist and should be removed from the Director registry

This document provides the correct `variant_id` values to use and the complete catalog of available Text Service variants.

---

## Immediate Fixes Required

### 1. Naming Corrections (12 variants)

Update your variant registry to use the correct `variant_id` values:

| Currently Using (WRONG) | Correct variant_id | Category |
|-------------------------|-------------------|----------|
| `sequential_3_step` | `sequential_3col` | Sequential |
| `sequential_4_step` | `sequential_4col` | Sequential |
| `sequential_5_step` | `sequential_5col` | Sequential |
| `bilateral_comparison` | `comparison_2col` | Comparison |
| `trilateral_comparison` | `comparison_3col` | Comparison |
| `single_column_3_section` | `single_column_3section` | Single Column |
| `single_column_4_section` | `single_column_4section` | Single Column |
| `single_column_5_section` | `single_column_5section` | Single Column |
| `metrics_3_kpi` | `metrics_3col` | Metrics |
| `metrics_4_kpi` | `metrics_4col` | Metrics |
| `table_3_column` | `table_3col` | Table |
| `table_4_column` | `table_4col` | Table |

### 2. Variants to Remove (1 variant)

The following variant does **NOT exist** in Text Service and should be removed from the Director registry:

| variant_id | Status | Recommendation |
|------------|--------|----------------|
| `grid_3x3` | Not implemented | Remove from registry. Use `grid_3x2` (6 cards) or `grid_2x3` (6 cards) instead. |

---

## Complete Text Service v1.2 Variant Catalog

Text Service supports **34 content slide variants** across 10 categories:

### Matrix (2 variants)

| variant_id | Description | Layout |
|------------|-------------|--------|
| `matrix_2x2` | Matrix with 4 boxes | 2 columns × 2 rows |
| `matrix_2x3` | Matrix with 6 boxes | 2 columns × 3 rows |

### Grid (9 variants)

| variant_id | Description | Layout |
|------------|-------------|--------|
| `grid_2x3` | Centered grid with icons | 2 columns × 3 rows (6 boxes, 35% extended) |
| `grid_3x2` | Centered grid with icons | 3 columns × 2 rows (6 boxes, 35% extended) |
| `grid_2x2_centered` | Centered grid with icons | 2 columns × 2 rows (4 boxes, 70% extended) |
| `grid_2x3_left` | Left-aligned grid with icons | 2 columns × 3 rows (6 boxes) |
| `grid_3x2_left` | Left-aligned grid with icons | 3 columns × 2 rows (6 boxes) |
| `grid_2x2_left` | Left-aligned grid with icons | 2 columns × 2 rows (4 boxes) |
| `grid_2x3_numbered` | Numbered grid | 2 columns × 3 rows (numbers 1-6) |
| `grid_3x2_numbered` | Numbered grid | 3 columns × 2 rows (numbers 1-6) |
| `grid_2x2_numbered` | Numbered grid | 2 columns × 2 rows (numbers 1-4) |

### Comparison (3 variants)

| variant_id | Description | Layout |
|------------|-------------|--------|
| `comparison_2col` | 2-way comparison | 2 columns with headers and item lists |
| `comparison_3col` | 3-way comparison | 3 columns with headers and item lists |
| `comparison_4col` | 4-way comparison | 4 columns with headers and item lists |

### Sequential (3 variants)

| variant_id | Description | Layout |
|------------|-------------|--------|
| `sequential_3col` | 3-step process | 3 numbered steps with titles and paragraphs |
| `sequential_4col` | 4-step process | 4 numbered steps with titles and paragraphs |
| `sequential_5col` | 5-step process | 5 numbered steps with titles and paragraphs |

### Asymmetric (3 variants)

| variant_id | Description | Layout |
|------------|-------------|--------|
| `asymmetric_8_4_3section` | Main content + sidebar | 3 colored sections (3 bullets each) + sidebar |
| `asymmetric_8_4_4section` | Main content + sidebar | 4 colored sections (2 bullets each) + sidebar |
| `asymmetric_8_4_5section` | Main content + sidebar | 5 colored sections (2 bullets each) + sidebar |

### Hybrid (2 variants)

| variant_id | Description | Layout |
|------------|-------------|--------|
| `hybrid_top_2x2` | Grid above text | 2x2 grid on top, text box at bottom |
| `hybrid_left_2x2` | Grid beside text | 2x2 grid on left, text box on right |

### Metrics (4 variants)

| variant_id | Description | Layout |
|------------|-------------|--------|
| `metrics_3col` | 3 metric cards | 3 cards in a row + insights box |
| `metrics_4col` | 4 metric cards | 4 cards in a row + insights box |
| `metrics_3x2_grid` | 6 metric cards | 3 columns × 2 rows + insights |
| `metrics_2x2_grid` | 4 large metric cards | 2 columns × 2 rows |

### Impact Quote (1 variant)

| variant_id | Description | Layout |
|------------|-------------|--------|
| `impact_quote` | Large centered quote | Quote text with attribution |

### Table (4 variants)

| variant_id | Description | Layout |
|------------|-------------|--------|
| `table_2col` | 2-column table | Category + 1 data column, 5 rows |
| `table_3col` | 3-column table | Category + 2 data columns, 5 rows |
| `table_4col` | 4-column table | Category + 3 data columns, 5 rows |
| `table_5col` | 5-column table | Category + 4 data columns, 5 rows |

### Single Column (3 variants)

| variant_id | Description | Layout |
|------------|-------------|--------|
| `single_column_3section` | 3 vertical sections | 3 sections with 4 bullets each |
| `single_column_4section` | 4 vertical sections | 4 sections with 3 bullets each |
| `single_column_5section` | 5 vertical sections | 5 sections with 2 bullets each |

---

## Variants You May Be Missing (16 Detailed Specifications)

Based on the test report, Director tested only 18 variants. The following **16 variants** may not be in your registry. Below are detailed specifications for each, including expected content structure.

---

### Grid Variants (7 variants)

#### 1. `grid_2x2_centered`
**Description**: 2×2 centered grid with 4 icon cards (70% extended content area)

**Visual Layout**:
```
┌─────────────────────────────────────────┐
│         [icon] Box 1  │  [icon] Box 2   │
│         Title         │  Title          │
│         Description   │  Description    │
├─────────────────────────────────────────┤
│         [icon] Box 3  │  [icon] Box 4   │
│         Title         │  Title          │
│         Description   │  Description    │
└─────────────────────────────────────────┘
```

**Expected Content** (4 items in `target_points`):
| Element | Character Limits | Description |
|---------|------------------|-------------|
| icon | 1-2 chars | Professional emoji icon (e.g., 📊, ⚙️, 🔒) |
| title | 24-26 chars | Card heading |
| description | 154-171 chars | Card body text |

**Use Case**: Core capabilities, key features, strategic pillars

---

#### 2. `grid_2x3_left`
**Description**: 2×3 left-aligned grid with 6 icon cards

**Visual Layout**:
```
┌──────────────────────────────────────────────────┐
│ [icon] Box 1      │ [icon] Box 2      │          │
│ Title             │ Title             │          │
│ Description       │ Description       │  (empty) │
├───────────────────┼───────────────────┤          │
│ [icon] Box 3      │ [icon] Box 4      │          │
│ Title             │ Title             │          │
│ Description       │ Description       │          │
├───────────────────┼───────────────────┤          │
│ [icon] Box 5      │ [icon] Box 6      │          │
│ Title             │ Title             │          │
│ Description       │ Description       │          │
└──────────────────────────────────────────────────┘
```

**Expected Content** (6 items in `target_points`):
| Element | Character Limits | Description |
|---------|------------------|-------------|
| icon | 1-2 chars | Professional emoji icon |
| title | 24-26 chars | Card heading |
| description | 95-105 chars | Card body text |

**Use Case**: Feature lists, capabilities overview, service offerings

---

#### 3. `grid_3x2_left`
**Description**: 3×2 left-aligned grid with 6 icon cards

**Visual Layout**:
```
┌──────────────────────────────────────────────────┐
│ [icon] Box 1  │ [icon] Box 2  │ [icon] Box 3     │
│ Title         │ Title         │ Title            │
│ Description   │ Description   │ Description      │
├───────────────┼───────────────┼──────────────────┤
│ [icon] Box 4  │ [icon] Box 5  │ [icon] Box 6     │
│ Title         │ Title         │ Title            │
│ Description   │ Description   │ Description      │
└──────────────────────────────────────────────────┘
```

**Expected Content** (6 items in `target_points`):
| Element | Character Limits | Description |
|---------|------------------|-------------|
| icon | 1-2 chars | Professional emoji icon |
| title | 24-26 chars | Card heading |
| description | 95-105 chars | Card body text |

**Use Case**: Process steps, team capabilities, product features

---

#### 4. `grid_2x2_left`
**Description**: 2×2 left-aligned grid with 4 icon cards

**Visual Layout**:
```
┌──────────────────────────────────────────────────┐
│ [icon] Box 1      │ [icon] Box 2      │          │
│ Title             │ Title             │          │
│ Description       │ Description       │  (empty) │
├───────────────────┼───────────────────┤          │
│ [icon] Box 3      │ [icon] Box 4      │          │
│ Title             │ Title             │          │
│ Description       │ Description       │          │
└──────────────────────────────────────────────────┘
```

**Expected Content** (4 items in `target_points`):
| Element | Character Limits | Description |
|---------|------------------|-------------|
| icon | 1-2 chars | Professional emoji icon |
| title | 24-26 chars | Card heading |
| description | 128-142 chars | Card body text |

**Use Case**: Core values, key differentiators, main benefits

---

#### 5. `grid_2x3_numbered`
**Description**: 2×3 numbered grid with 6 cards (numbers 1-6 auto-generated)

**Visual Layout**:
```
┌──────────────────────────────────────────────────┐
│   ① Box 1         │   ② Box 2         │          │
│   Title           │   Title           │          │
│   Description     │   Description     │  (70%)   │
├───────────────────┼───────────────────┤          │
│   ③ Box 3         │   ④ Box 4         │          │
│   Title           │   Title           │          │
│   Description     │   Description     │          │
├───────────────────┼───────────────────┤          │
│   ⑤ Box 5         │   ⑥ Box 6         │          │
│   Title           │   Title           │          │
│   Description     │   Description     │          │
└──────────────────────────────────────────────────┘
```

**Expected Content** (6 items in `target_points`):
| Element | Character Limits | Description |
|---------|------------------|-------------|
| title | 24-26 chars | Card heading |
| description | 167-184 chars | Card body text |

**Note**: Numbers (1-6) are auto-generated by the template; do NOT include in content.

**Use Case**: Numbered steps, prioritized items, ranked features

---

#### 6. `grid_3x2_numbered`
**Description**: 3×2 numbered grid with 6 cards (numbers 1-6 auto-generated)

**Visual Layout**:
```
┌────────────────────────────────────────────────────────┐
│   ① Box 1     │   ② Box 2     │   ③ Box 3     │        │
│   Title       │   Title       │   Title       │        │
│   Description │   Description │   Description │  (70%) │
├───────────────┼───────────────┼───────────────┤        │
│   ④ Box 4     │   ⑤ Box 5     │   ⑥ Box 6     │        │
│   Title       │   Title       │   Title       │        │
│   Description │   Description │   Description │        │
└────────────────────────────────────────────────────────┘
```

**Expected Content** (6 items in `target_points`):
| Element | Character Limits | Description |
|---------|------------------|-------------|
| title | 24-26 chars | Card heading |
| description | 167-184 chars | Card body text |

**Use Case**: Sequential processes, implementation phases, action items

---

#### 7. `grid_2x2_numbered`
**Description**: 2×2 numbered grid with 4 cards (numbers 1-4 auto-generated)

**Visual Layout**:
```
┌──────────────────────────────────────────────────┐
│   ① Box 1         │   ② Box 2         │          │
│   Title           │   Title           │          │
│   Description     │   Description     │  (70%)   │
├───────────────────┼───────────────────┤          │
│   ③ Box 3         │   ④ Box 4         │          │
│   Title           │   Title           │          │
│   Description     │   Description     │          │
└──────────────────────────────────────────────────┘
```

**Expected Content** (4 items in `target_points`):
| Element | Character Limits | Description |
|---------|------------------|-------------|
| title | 24-26 chars | Card heading |
| description | 167-184 chars | Card body text |

**Use Case**: Four-step processes, core pillars, key phases

---

### Comparison Variants (1 variant)

#### 8. `comparison_4col`
**Description**: 4-way comparison with headers and bullet lists

**Visual Layout**:
```
┌────────────────────────────────────────────────────────────┐
│   Column 1    │   Column 2    │   Column 3    │  Column 4  │
│   Heading     │   Heading     │   Heading     │  Heading   │
├───────────────┼───────────────┼───────────────┼────────────┤
│   • Item 1    │   • Item 1    │   • Item 1    │  • Item 1  │
│   • Item 2    │   • Item 2    │   • Item 2    │  • Item 2  │
│   • Item 3    │   • Item 3    │   • Item 3    │  • Item 3  │
│   • Item 4    │   • Item 4    │   • Item 4    │  • Item 4  │
└────────────────────────────────────────────────────────────┘
```

**Expected Content** (4 comparison groups in `target_points`):
| Element | Character Limits | Description |
|---------|------------------|-------------|
| heading | 19-21 chars | Column header |
| items | 190-210 chars total | HTML list format (`<li>item</li>`) |

**Use Case**: Product comparison, tier comparison, competitive analysis, option evaluation

---

### Asymmetric Variants (3 variants)

#### 9. `asymmetric_8_4_3section`
**Description**: 3 colored sections (4 bullets each) + sidebar with 7 items

**Visual Layout**:
```
┌────────────────────────────────────────┬─────────────────┐
│ Section 1 Heading                      │ Sidebar Heading │
│ • Bullet 1    • Bullet 2               │ • Item 1        │
│ • Bullet 3    • Bullet 4               │ • Item 2        │
├────────────────────────────────────────┤ • Item 3        │
│ Section 2 Heading                      │ • Item 4        │
│ • Bullet 1    • Bullet 2               │ • Item 5        │
│ • Bullet 3    • Bullet 4               │ • Item 6        │
├────────────────────────────────────────┤ • Item 7        │
│ Section 3 Heading                      │                 │
│ • Bullet 1    • Bullet 2               │                 │
│ • Bullet 3    • Bullet 4               │                 │
└────────────────────────────────────────┴─────────────────┘
         (8 columns - 67%)                   (4 columns - 33%)
```

**Expected Content**:
| Element | Character Limits | Description |
|---------|------------------|-------------|
| section_heading | 29-32 chars | Section title |
| bullet (×4 per section) | 90-100 chars each | Section bullet points |
| sidebar_heading | 24-26 chars | Sidebar title |
| sidebar_item (×7) | 71-79 chars each | Sidebar list items |

**Use Case**: Strategic overview with key takeaways, implementation plan with milestones

---

#### 10. `asymmetric_8_4_4section`
**Description**: 4 colored sections (2 bullets each) + sidebar with 7 items

**Visual Layout**:
```
┌────────────────────────────────────────┬─────────────────┐
│ Section 1 Heading                      │ Sidebar Heading │
│ • Bullet 1    • Bullet 2               │ • Item 1        │
├────────────────────────────────────────┤ • Item 2        │
│ Section 2 Heading                      │ • Item 3        │
│ • Bullet 1    • Bullet 2               │ • Item 4        │
├────────────────────────────────────────┤ • Item 5        │
│ Section 3 Heading                      │ • Item 6        │
│ • Bullet 1    • Bullet 2               │ • Item 7        │
├────────────────────────────────────────┤                 │
│ Section 4 Heading                      │                 │
│ • Bullet 1    • Bullet 2               │                 │
└────────────────────────────────────────┴─────────────────┘
```

**Expected Content**:
| Element | Character Limits | Description |
|---------|------------------|-------------|
| section_heading | 29-32 chars | Section title |
| bullet (×2 per section) | 90-100 chars each | Section bullet points |
| sidebar_heading | 24-26 chars | Sidebar title |
| sidebar_item (×7) | 71-79 chars each | Sidebar list items |

**Use Case**: Quarterly review with highlights, department overview with key metrics

---

#### 11. `asymmetric_8_4_5section`
**Description**: 5 colored sections (2 bullets each) + sidebar with 7 items

**Visual Layout**:
```
┌────────────────────────────────────────┬─────────────────┐
│ Section 1 Heading  • Bullet 1, 2       │ Sidebar Heading │
├────────────────────────────────────────┤ • Item 1        │
│ Section 2 Heading  • Bullet 1, 2       │ • Item 2        │
├────────────────────────────────────────┤ • Item 3        │
│ Section 3 Heading  • Bullet 1, 2       │ • Item 4        │
├────────────────────────────────────────┤ • Item 5        │
│ Section 4 Heading  • Bullet 1, 2       │ • Item 6        │
├────────────────────────────────────────┤ • Item 7        │
│ Section 5 Heading  • Bullet 1, 2       │                 │
└────────────────────────────────────────┴─────────────────┘
```

**Expected Content**:
| Element | Character Limits | Description |
|---------|------------------|-------------|
| section_heading | 29-32 chars | Section title |
| bullet (×2 per section) | 90-100 chars each | Section bullet points |
| sidebar_heading | 24-26 chars | Sidebar title |
| sidebar_item (×7) | 71-79 chars each | Sidebar list items |

**Use Case**: Five-pillar strategy, comprehensive overview, multi-department summary

---

### Hybrid Variants (2 variants)

#### 12. `hybrid_top_2x2`
**Description**: 2×2 grid on top + text content box at bottom

**Visual Layout**:
```
┌──────────────────────┬──────────────────────┐
│ Box 1                │ Box 2                │
│ Heading              │ Heading              │
│ Description          │ Description          │
├──────────────────────┼──────────────────────┤
│ Box 3                │ Box 4                │
│ Heading              │ Heading              │
│ Description          │ Description          │
├──────────────────────┴──────────────────────┤
│                                             │
│            Text Box Content                 │
│         (supporting narrative)              │
│                                             │
└─────────────────────────────────────────────┘
```

**Expected Content**:
| Element | Character Limits | Description |
|---------|------------------|-------------|
| box_heading (×4) | 24-26 chars | Card heading |
| box_description (×4) | 128-142 chars | Card body text |
| text_box_content | 285-315 chars | Bottom text narrative |

**Use Case**: Key points with summary, features with call-to-action

---

#### 13. `hybrid_left_2x2`
**Description**: 2×2 grid on left + text content box on right

**Visual Layout**:
```
┌──────────────────────┬──────────────────────────┐
│ Box 1                │                          │
│ Heading              │                          │
│ Description          │                          │
├──────────────────────┤      Text Box Content    │
│ Box 2                │                          │
│ Heading              │    (extended narrative   │
│ Description          │     or detailed info)    │
├──────────────────────┤                          │
│ Box 3                │                          │
│ Heading              │                          │
│ Description          │                          │
├──────────────────────┤                          │
│ Box 4                │                          │
│ Heading              │                          │
│ Description          │                          │
└──────────────────────┴──────────────────────────┘
```

**Expected Content**:
| Element | Character Limits | Description |
|---------|------------------|-------------|
| box_heading (×4) | 24-26 chars | Card heading |
| box_description (×4) | 128-142 chars | Card body text |
| text_box_content | 285-315 chars | Right-side text narrative |

**Use Case**: Features with detailed explanation, capabilities with context

---

### Metrics Variants (2 variants)

#### 14. `metrics_3x2_grid`
**Description**: 3×2 grid with 6 metric cards (no insights box)

**Visual Layout**:
```
┌────────────────┬────────────────┬────────────────┐
│     98%        │     $2.4M      │     15K        │
│   Metric 1     │   Metric 2     │   Metric 3     │
│   Label        │   Label        │   Label        │
│   Description  │   Description  │   Description  │
├────────────────┼────────────────┼────────────────┤
│     42%        │     3.5x       │     99.9%      │
│   Metric 4     │   Metric 5     │   Metric 6     │
│   Label        │   Label        │   Label        │
│   Description  │   Description  │   Description  │
└────────────────┴────────────────┴────────────────┘
```

**Expected Content** (6 metrics in `target_points`):
| Element | Character Limits | Description |
|---------|------------------|-------------|
| number | 1-10 chars | Metric value (e.g., "98%", "$2.4M", "15K") |
| label | 17-19 chars | Metric name |
| description | 62-68 chars | Metric context |

**Use Case**: Dashboard-style KPI display, performance metrics, quarterly results

---

#### 15. `metrics_2x2_grid`
**Description**: 2×2 grid with 4 large metric cards

**Visual Layout**:
```
┌──────────────────────────┬──────────────────────────┐
│          98%             │         $2.4M            │
│       Metric 1           │       Metric 2           │
│       Label              │       Label              │
│       Description        │       Description        │
├──────────────────────────┼──────────────────────────┤
│          42%             │         3.5x             │
│       Metric 3           │       Metric 4           │
│       Label              │       Label              │
│       Description        │       Description        │
└──────────────────────────┴──────────────────────────┘
```

**Expected Content** (4 metrics in `target_points`):
| Element | Character Limits | Description |
|---------|------------------|-------------|
| number | 1-10 chars | Metric value |
| label | 17-19 chars | Metric name |
| description | 90-110 chars | Extended metric context |

**Use Case**: Key highlights, executive summary metrics, quarterly scorecard

---

### Table Variants (2 variants)

#### 16. `table_2col`
**Description**: 2-column table (category + 1 data column), 5 rows

**Visual Layout**:
```
┌────────────────────┬────────────────────────────────────────┐
│  Header Category   │           Header Column 1              │
├────────────────────┼────────────────────────────────────────┤
│  Row 1 Category    │           Row 1 Data                   │
├────────────────────┼────────────────────────────────────────┤
│  Row 2 Category    │           Row 2 Data                   │
├────────────────────┼────────────────────────────────────────┤
│  Row 3 Category    │           Row 3 Data                   │
├────────────────────┼────────────────────────────────────────┤
│  Row 4 Category    │           Row 4 Data                   │
├────────────────────┼────────────────────────────────────────┤
│  Row 5 Category    │           Row 5 Data                   │
└────────────────────┴────────────────────────────────────────┘
       (25%)                        (75%)
```

**Expected Content**:
| Element | Character Limits | Description |
|---------|------------------|-------------|
| header_category | 19-21 chars | First column header |
| header_col_1 | 24-26 chars | Second column header |
| row_category (×5) | 19-21 chars | Row label |
| row_col_1 (×5) | 114-126 chars | Row data (longer text) |

**Use Case**: Feature descriptions, definitions, key-value pairs

---

#### 17. `table_5col`
**Description**: 5-column table (category + 4 data columns), 5 rows

**Visual Layout**:
```
┌──────────────┬──────────┬──────────┬──────────┬──────────┐
│  Category    │  Col 1   │  Col 2   │  Col 3   │  Col 4   │
├──────────────┼──────────┼──────────┼──────────┼──────────┤
│  Row 1       │  Data    │  Data    │  Data    │  Data    │
├──────────────┼──────────┼──────────┼──────────┼──────────┤
│  Row 2       │  Data    │  Data    │  Data    │  Data    │
├──────────────┼──────────┼──────────┼──────────┼──────────┤
│  Row 3       │  Data    │  Data    │  Data    │  Data    │
├──────────────┼──────────┼──────────┼──────────┼──────────┤
│  Row 4       │  Data    │  Data    │  Data    │  Data    │
├──────────────┼──────────┼──────────┼──────────┼──────────┤
│  Row 5       │  Data    │  Data    │  Data    │  Data    │
└──────────────┴──────────┴──────────┴──────────┴──────────┘
    (25%)        (18.75%×4)
```

**Expected Content**:
| Element | Character Limits | Description |
|---------|------------------|-------------|
| header_category | 19-21 chars | First column header |
| header_col_1-4 | 14-16 chars each | Data column headers |
| row_category (×5) | 19-21 chars | Row label |
| row_col_1-4 (×5) | 43-47 chars each | Row data cells |

**Use Case**: Multi-dimensional comparison, feature matrix, pricing tiers, timeline with phases

---

## API Reference

### Endpoint

```
POST https://web-production-5daf.up.railway.app/v1.2/generate
```

### Request Format

```json
{
  "variant_id": "sequential_3col",
  "slide_spec": {
    "slide_title": "Implementation Timeline",
    "slide_purpose": "Show three-phase implementation",
    "key_message": "Structured approach for successful deployment",
    "target_points": [
      "Phase 1: Discovery and planning",
      "Phase 2: Development and testing",
      "Phase 3: Deployment and optimization"
    ],
    "tone": "professional",
    "audience": "project stakeholders"
  },
  "presentation_spec": {
    "presentation_title": "Project Plan",
    "presentation_type": "Project Review",
    "current_slide_number": 6,
    "total_slides": 12
  },
  "enable_parallel": true,
  "validate_character_counts": true
}
```

### Headers

```
Content-Type: application/json
```

### Response Format (Success)

```json
{
  "content": "<div>...generated HTML...</div>",
  "metadata": {
    "variant_id": "sequential_3col",
    "slide_type": "sequential",
    "generation_time_ms": 7234,
    "character_counts": {...}
  }
}
```

### Response Format (Error - Unknown Variant)

```json
{
  "detail": "Unknown variant_id: sequential_3_step"
}
```

**Status Code**: 400 Bad Request

---

## Quick Reference: Name Mapping

For easy reference, here's the complete mapping from common naming patterns to correct variant_ids:

```javascript
const variantNameMapping = {
  // Sequential (use *col suffix)
  "sequential_3_step": "sequential_3col",
  "sequential_4_step": "sequential_4col",
  "sequential_5_step": "sequential_5col",

  // Comparison (use *col suffix)
  "bilateral_comparison": "comparison_2col",
  "trilateral_comparison": "comparison_3col",

  // Single Column (no underscore before number)
  "single_column_3_section": "single_column_3section",
  "single_column_4_section": "single_column_4section",
  "single_column_5_section": "single_column_5section",

  // Metrics (use *col suffix)
  "metrics_3_kpi": "metrics_3col",
  "metrics_4_kpi": "metrics_4col",

  // Table (use *col suffix)
  "table_3_column": "table_3col",
  "table_4_column": "table_4col",
};
```

---

## Testing Verification

You can verify each variant works using curl:

```bash
# Test sequential_3col
curl -X POST "https://web-production-5daf.up.railway.app/v1.2/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "variant_id": "sequential_3col",
    "slide_spec": {
      "slide_title": "Test Title",
      "slide_purpose": "Test purpose",
      "key_message": "Test message",
      "target_points": ["Point 1", "Point 2", "Point 3"],
      "tone": "professional",
      "audience": "test"
    },
    "enable_parallel": true,
    "validate_character_counts": true
  }'
```

Expected: 200 OK with HTML content

---

## List Available Variants Endpoint

To get the current list of all available variants:

```bash
GET https://web-production-5daf.up.railway.app/v1.2/variants
```

This returns the complete variant catalog with descriptions and layouts.

---

## Summary of Required Changes

1. **Update 12 variant_ids** in your registry (see mapping table above)
2. **Remove 1 variant** (`grid_3x3`) - does not exist
3. **Consider adding 16 variants** that may be missing from your registry

---

## Contact

For questions about this integration guide or Text Service API:
- **Service**: Text Table Builder v1.2
- **Endpoint**: https://web-production-5daf.up.railway.app
- **Documentation**: This file

---

*Document generated: 2025-12-01*
