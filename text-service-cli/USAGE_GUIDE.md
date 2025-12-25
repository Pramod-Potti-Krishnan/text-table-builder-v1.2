# Text Service CLI - Usage Guide

This guide provides detailed workflows for integrating new slide formats into Text Service v1.2.

## Table of Contents

1. [Overview](#overview)
2. [Creating a New Content Variant](#creating-a-new-content-variant)
3. [Creating a New Hero Slide Type](#creating-a-new-hero-slide-type)
4. [Understanding Placeholder Patterns](#understanding-placeholder-patterns)
5. [Character Constraints](#character-constraints)
6. [Interactive Mode vs Direct Write](#interactive-mode-vs-direct-write)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The Text Service CLI automates the process of adding new slide formats to Text Service v1.2. It generates:

- **For Content Variants**: JSON specs, HTML templates, tests
- **For Hero Slides**: Python generator classes, tests, route configurations

### Workflow Summary

```
1. Create input files (metadata, template/prompt)
      ↓
2. Validate inputs: `cli.py validate`
      ↓
3. Analyze template: `cli.py analyze` (optional)
      ↓
4. Generate files: `cli.py integrate`
      ↓
5. Review and copy to service directories
      ↓
6. Run tests to verify integration
```

---

## Creating a New Content Variant

Content variants are layout templates for slide content (e.g., matrix layouts, grids, comparison tables).

### Step 1: Create Input Directory

```bash
mkdir -p example_inputs/my_new_variant
```

### Step 2: Create metadata.json

Define the variant's identity and structure:

```json
{
  "variant_id": "grid_2x4",
  "slide_type": "grid",
  "display_name": "2x4 Grid Layout",
  "description": "A 2-row, 4-column grid perfect for showcasing 8 key points",
  "elements": [
    {
      "element_id": "box_1",
      "element_type": "text_box",
      "required_fields": ["title", "description"]
    },
    {
      "element_id": "box_2",
      "element_type": "text_box",
      "required_fields": ["title", "description"]
    }
    // ... repeat for all 8 boxes
  ],
  "layout": {
    "columns": 4,
    "rows": 2,
    "total_boxes": 8
  }
}
```

**Key fields:**
- `variant_id`: Unique identifier (snake_case)
- `slide_type`: Category (matrix, grid, comparison, etc.)
- `elements`: Array of element definitions
- `layout`: Grid/layout configuration

### Step 3: Create template.html

Design the HTML template with placeholders:

```html
<div style="width: 100%; height: 100%; padding: 40px; box-sizing: border-box;">
  <h1 style="margin-bottom: 20px;">{slide_title}</h1>

  <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;">
    <div class="box">
      <h3>{box_1_title}</h3>
      <p>{box_1_description}</p>
    </div>
    <div class="box">
      <h3>{box_2_title}</h3>
      <p>{box_2_description}</p>
    </div>
    <!-- ... more boxes ... -->
  </div>
</div>
```

**Placeholder naming convention:**
- `{element_N_field}` where:
  - `element` = box, column, metric, section, step, etc.
  - `N` = element number (1, 2, 3...)
  - `field` = title, description, heading, paragraph, etc.

### Step 4: Create constraints.json (Optional)

Override default character constraints:

```json
{
  "box_1": {
    "title": {"baseline": 20, "min": 15, "max": 25},
    "description": {"baseline": 80, "min": 60, "max": 100}
  },
  "box_2": {
    "title": {"baseline": 20, "min": 15, "max": 25},
    "description": {"baseline": 80, "min": 60, "max": 100}
  }
}
```

### Step 5: Validate and Generate

```bash
# Validate inputs
python cli.py validate example_inputs/my_new_variant --type variant

# Preview what will be generated
python cli.py integrate example_inputs/my_new_variant --type variant --dry-run

# Generate files (interactive mode)
python cli.py integrate example_inputs/my_new_variant --type variant
```

### Step 6: Complete Integration

The CLI will generate:
1. `app/variant_specs/grid/grid_2x4.json` - Variant specification
2. `app/templates/grid/grid_2x4.html` - HTML template
3. `tests/test_grid_2x4.py` - Integration test

Follow the CLI's instructions to:
1. Copy files to the Text Service
2. Update `variant_index.json`
3. Run the test script

---

## Creating a New Hero Slide Type

Hero slides are special-purpose slides (title, section dividers, closing slides, agenda).

### Step 1: Create Input Directory

```bash
mkdir -p example_inputs/my_hero_type
```

### Step 2: Create metadata.json

```json
{
  "hero_type": "quote",
  "display_name": "Quote Slide",
  "description": "A slide featuring a prominent quote with attribution",
  "endpoint_path": "/v1.2/hero/quote",
  "generator_class": "QuoteSlideGenerator",
  "html_structure": {
    "quote_text": "The main quote text, large and prominent",
    "attribution": "Author name and title/source",
    "context": "Optional context or introduction"
  },
  "character_constraints": {
    "quote_text": {"baseline": 150, "min": 100, "max": 200},
    "attribution": {"baseline": 50, "min": 30, "max": 70},
    "context": {"baseline": 60, "min": 40, "max": 80}
  },
  "style_options": ["minimal", "elegant", "bold", "modern"],
  "dependencies": {
    "requires_presentation_context": true,
    "requires_slide_spec": true
  }
}
```

### Step 3: Create prompt_template.md

```markdown
# Quote Slide Content Generation

You are generating content for a **Quote Slide** in a professional presentation.

## Context

**Presentation Title**: {presentation_title}
**Presentation Type**: {presentation_type}
**Tone**: {tone}
**Target Audience**: {audience}

## Slide Purpose

{slide_purpose}

## Content Requirements

Generate a quote that:
1. Reinforces the presentation's key message
2. Is memorable and impactful
3. Has clear attribution
4. Fits the presentation's tone

## Character Constraints

| Field | Target | Min | Max |
|-------|--------|-----|-----|
| Quote Text | 150 | 100 | 200 |
| Attribution | 50 | 30 | 70 |
| Context | 60 | 40 | 80 |

## Output Format

Return a JSON object:
```json
{
  "quote_text": "The quote goes here",
  "attribution": "Author Name, Title/Source",
  "context": "Brief context for the quote"
}
```
```

### Step 4: Create validation_rules.json

```json
{
  "required_fields": ["quote_text", "attribution"],
  "optional_fields": ["context"],
  "field_validations": {
    "quote_text": {
      "type": "string",
      "min_length": 50,
      "max_length": 200,
      "error_message": "Quote must be between 50 and 200 characters"
    },
    "attribution": {
      "type": "string",
      "min_length": 10,
      "max_length": 70,
      "error_message": "Attribution must be between 10 and 70 characters"
    },
    "context": {
      "type": "string",
      "min_length": 20,
      "max_length": 80,
      "error_message": "Context must be between 20 and 80 characters"
    }
  },
  "content_rules": {
    "no_placeholder_text": true,
    "no_lorem_ipsum": true
  },
  "retry_on_failure": true,
  "max_retries": 3
}
```

### Step 5: Generate Files

```bash
# Validate
python cli.py validate example_inputs/my_hero_type --type hero

# Generate (with image-enhanced variant)
python cli.py integrate example_inputs/my_hero_type --type hero --with-image
```

### Step 6: Complete Integration

Generated files:
1. `app/core/hero/quote_generator.py` - Base generator class
2. `app/core/hero/quote_with_image_generator.py` - Image-enhanced variant
3. `tests/test_quote_hero.py` - Integration test
4. Route and init snippets for manual integration

---

## Understanding Placeholder Patterns

### Supported Element Types

| Type | Pattern | Example |
|------|---------|---------|
| Text Box | `{box_N_field}` | `{box_1_title}`, `{box_3_description}` |
| Comparison Column | `{column_N_field}` | `{column_1_heading}`, `{column_2_items}` |
| Metric Card | `{metric_N_field}` | `{metric_1_value}`, `{metric_2_label}` |
| Colored Section | `{section_N_field}` | `{section_1_heading}`, `{section_2_bullet_1}` |
| Sequential Step | `{step_N_field}` | `{step_1_title}`, `{step_4_paragraph}` |
| Table Cell | `{cell_R_C}` | `{cell_1_2}`, `{cell_3_4}` |
| List Item | `{item_N_field}` | `{item_1_title}`, `{item_5_description}` |

### Common Field Names

| Field | Typical Use | Default Chars |
|-------|-------------|---------------|
| `title` | Heading/title text | 25-35 |
| `description` | Body/description text | 100-140 |
| `heading` | Section heading | 25-35 |
| `paragraph` | Long form text | 170-230 |
| `label` | Short label | 15-25 |
| `value` | Metric/number | 5-25 |
| `items` | Bullet list | 120-180 |
| `bullet_N` | Individual bullet | 50-70 |

---

## Character Constraints

Character constraints ensure content fits the visual design.

### Constraint Format

```json
{
  "field_name": {
    "baseline": 100,  // Target character count
    "min": 80,        // Minimum allowed
    "max": 120        // Maximum allowed
  }
}
```

### Default Constraints

The CLI applies intelligent defaults based on field names:

| Field Pattern | Baseline | Min | Max |
|---------------|----------|-----|-----|
| title/heading | 30 | 25 | 35 |
| description | 120 | 100 | 140 |
| paragraph | 200 | 170 | 230 |
| label | 20 | 15 | 25 |
| value | 15 | 5 | 25 |
| items | 150 | 120 | 180 |
| bullet | 60 | 50 | 70 |

---

## Interactive Mode vs Direct Write

### Interactive Mode (Default)

```bash
python cli.py integrate example_inputs/my_variant --type variant
```

The CLI will:
1. Show generated files
2. Ask where to write them:
   - Service directories (direct integration)
   - Output directory (for review)
   - Cancel

### Direct Write Mode

```bash
# Write directly to service directories
python cli.py integrate example_inputs/my_variant --type variant -y

# Write to output directory
python cli.py integrate example_inputs/my_variant --type variant --dry-run
```

### Dry Run Mode

```bash
python cli.py integrate example_inputs/my_variant --type variant --dry-run
```

Shows what would be generated without writing any files.

---

## Troubleshooting

### Common Issues

**"Missing required file"**
```
Error: Missing required file: template.html
```
Solution: Ensure all required files exist in the input directory.

**"Invalid placeholder format"**
```
Warning: Placeholder '{invalid_placeholder}' doesn't match expected patterns
```
Solution: Use the standard `{element_N_field}` naming convention.

**"Character constraint violation"**
```
Warning: box_1.title exceeds max (got 45, max 35)
```
Solution: Adjust constraints in `constraints.json` or modify content.

**"Duplicate element_id"**
```
Error: Duplicate element_id: box_1
```
Solution: Ensure all element IDs in metadata.json are unique.

### Validation Commands

```bash
# Validate variant inputs
python cli.py validate example_inputs/my_variant --type variant

# Validate hero inputs
python cli.py validate example_inputs/my_hero --type hero

# Analyze template structure
python cli.py analyze example_inputs/my_variant/template.html
```

### Getting Help

```bash
# CLI help
python cli.py --help

# Command help
python cli.py integrate --help
python cli.py validate --help
python cli.py analyze --help
```

---

## Examples

### Example 1: Simple 2x2 Matrix

```bash
# Input files already exist
python cli.py integrate example_inputs/new_variant --type variant

# Output:
# ✓ Generated: app/variant_specs/matrix/matrix_3x3.json
# ✓ Generated: app/templates/matrix/matrix_3x3.html
# ✓ Generated: tests/test_matrix_3x3.py
```

### Example 2: Hero Slide with Image Support

```bash
python cli.py integrate example_inputs/new_hero --type hero --with-image

# Output:
# ✓ Generated: app/core/hero/agenda_generator.py
# ✓ Generated: app/core/hero/agenda_with_image_generator.py
# ✓ Generated: tests/test_agenda_hero.py
#
# Manual steps required:
# 1. Add route to hero_routes.py
# 2. Update hero/__init__.py exports
```

### Example 3: Dry Run Preview

```bash
python cli.py integrate example_inputs/new_variant --type variant --dry-run

# Shows all files that would be generated without writing
```

---

## Best Practices

1. **Always validate first** before generating files
2. **Use meaningful names** for variant_id and hero_type
3. **Test constraints visually** to ensure content fits the design
4. **Use dry-run** to preview before committing to changes
5. **Run generated tests** to verify integration works
6. **Keep templates simple** with inline styles for portability
