# Text Service CLI

A command-line tool for integrating new slide formats into Text Service v1.2. Supports both **content slide variants** (matrix, grid, comparison layouts) and **hero slide types** (title, section, agenda, closing slides).

## Features

- **Validate** input files before integration
- **Analyze** HTML templates for placeholders and structure
- **Generate** complete integration artifacts:
  - Variant spec JSON files
  - HTML templates
  - Python generator classes (for hero slides)
  - Test scripts
  - Route and index update snippets
- **Interactive mode** for choosing output destination
- **Image-enhanced variants** for hero slides with `--with-image` flag

## Installation

```bash
cd text-service-cli
pip install -r requirements.txt
```

## Quick Start

### Integrate a New Content Variant

```bash
# Validate inputs first
python cli.py validate example_inputs/new_variant --type variant

# Analyze template structure
python cli.py analyze example_inputs/new_variant/template.html

# Generate all integration files
python cli.py integrate example_inputs/new_variant --type variant
```

### Integrate a New Hero Slide Type

```bash
# Validate hero inputs
python cli.py validate example_inputs/new_hero --type hero

# Generate hero slide files (with image variant)
python cli.py integrate example_inputs/new_hero --type hero --with-image
```

## Commands

### `validate`

Validates input directory structure and files.

```bash
python cli.py validate <input_dir> --type <variant|hero>
```

**Required files for variant:**
- `metadata.json` - Variant metadata and element definitions
- `template.html` - HTML template with placeholders
- `constraints.json` (optional) - Character constraints

**Required files for hero:**
- `metadata.json` - Hero type metadata
- `prompt_template.md` - LLM prompt template
- `validation_rules.json` - Content validation rules

### `analyze`

Analyzes an HTML template for placeholders and structure.

```bash
python cli.py analyze <template_file>
```

Shows:
- Detected placeholders grouped by element
- Suggested character constraints
- Template structure analysis

### `integrate`

Generates all files needed to integrate a new format.

```bash
python cli.py integrate <input_dir> --type <variant|hero> [options]
```

**Options:**
- `--type` - Format type: `variant` or `hero` (required)
- `--with-image` - Also generate image-enhanced variant (hero only)
- `--dry-run` - Show what would be generated without writing
- `--skip-validation` - Skip input validation
- `-y, --yes` - Write directly to service directories without prompting

## Input File Formats

### Variant Metadata (`metadata.json`)

```json
{
  "variant_id": "matrix_3x3",
  "slide_type": "matrix",
  "display_name": "3x3 Matrix Layout",
  "description": "A 3x3 grid layout with 9 boxes",
  "elements": [
    {
      "element_id": "box_1",
      "element_type": "text_box",
      "required_fields": ["title", "description"]
    }
  ],
  "layout": {
    "columns": 3,
    "rows": 3,
    "total_boxes": 9
  }
}
```

### Hero Metadata (`metadata.json`)

```json
{
  "hero_type": "agenda",
  "display_name": "Agenda Slide",
  "description": "Shows presentation outline",
  "endpoint_path": "/v1.2/hero/agenda",
  "generator_class": "AgendaSlideGenerator",
  "html_structure": {
    "title": "Main title",
    "items": "List of agenda items"
  },
  "character_constraints": {
    "title": {"baseline": 40, "min": 30, "max": 50}
  }
}
```

### Template Placeholders

Use Text Service placeholder conventions:

| Pattern | Example | Element Type |
|---------|---------|--------------|
| `{box_N_field}` | `{box_1_title}` | Text box |
| `{column_N_field}` | `{column_2_heading}` | Comparison column |
| `{metric_N_field}` | `{metric_1_value}` | Metric card |
| `{section_N_field}` | `{section_1_bullet_1}` | Colored section |
| `{step_N_field}` | `{step_3_paragraph}` | Sequential step |

## Generated Files

### For Variants

| File | Path | Description |
|------|------|-------------|
| Variant Spec | `app/variant_specs/{type}/{id}.json` | Element definitions and constraints |
| HTML Template | `app/templates/{type}/{id}.html` | Slide HTML template |
| Test Script | `tests/test_{id}.py` | Integration test |
| Index Update | (snippet) | Additions for `variant_index.json` |

### For Hero Slides

| File | Path | Description |
|------|------|-------------|
| Generator Class | `app/core/hero/{type}_generator.py` | Python generator |
| Image Generator | `app/core/hero/{type}_with_image_generator.py` | With image support |
| Test Script | `tests/test_{type}_hero.py` | Integration test |
| Route Snippet | (snippet) | Additions for `hero_routes.py` |
| Init Snippet | (snippet) | Additions for `hero/__init__.py` |

## Directory Structure

```
text-service-cli/
├── cli.py                    # Main CLI entry point
├── requirements.txt          # Dependencies
├── README.md                 # This file
├── USAGE_GUIDE.md           # Detailed usage guide
├── core/
│   ├── __init__.py
│   ├── input_validator.py    # Input validation
│   ├── placeholder_detector.py # Placeholder analysis
│   └── spec_analyzer.py      # Spec generation
├── generators/
│   ├── __init__.py
│   ├── variant_gen.py        # Variant file generator
│   └── hero_gen.py           # Hero file generator
└── example_inputs/
    ├── new_variant/          # Example variant input
    │   ├── metadata.json
    │   ├── template.html
    │   └── constraints.json
    └── new_hero/             # Example hero input
        ├── metadata.json
        ├── prompt_template.md
        └── validation_rules.json
```

## Integration with Text Service

After generating files, the CLI provides instructions for completing integration:

1. **Copy generated files** to appropriate service directories
2. **Update `variant_index.json`** with the provided snippet
3. **Update routes** (for hero slides) with route snippets
4. **Update `__init__.py`** exports
5. **Run generated tests** to verify integration

## Development

### Running Tests

```bash
# From text-service-cli directory
python -m pytest tests/

# Test the example variant
python cli.py integrate example_inputs/new_variant --type variant --dry-run

# Test the example hero
python cli.py integrate example_inputs/new_hero --type hero --with-image --dry-run
```

### Adding New Placeholder Patterns

Edit `core/placeholder_detector.py` to add new patterns:

```python
PLACEHOLDER_PATTERNS = {
    'new_element': r'\{new_(\d+)_(\w+)\}',
    # ...
}
```

## License

Internal tool for Deckster development.
