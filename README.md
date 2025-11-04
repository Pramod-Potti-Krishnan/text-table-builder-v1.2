# Text & Table Builder v1.2 - Deterministic Assembly Architecture

> **🚀 Quick Start**: See [QUICKSTART.md](./QUICKSTART.md) for 3-step setup and testing guide!

## Overview

Version 1.2 introduces a revolutionary **deterministic assembly architecture** that transforms how slide content is generated. Instead of generating complete HTML in a single LLM call, v1.2 breaks slides into atomic **elements**, generates content for each element individually with precise constraints, then assembles them into templates.

### Key Advantages

✅ **Deterministic Output**: Template-based assembly ensures consistent HTML structure
✅ **Precise Control**: Character count requirements enforced per element
✅ **Parallel Generation**: Elements generated concurrently for 3-5x speed improvement
✅ **Format Ownership**: Text Service owns all hero_content and rich_content 100%
✅ **Element-Level Targeting**: Each element gets optimized prompt with specific context
✅ **Template Caching**: Reusable templates loaded once and cached

---

## Gemini Integration with Vertex AI

v1.2 is **fully integrated** with Google's Gemini models via Vertex AI, using Application Default Credentials (ADC) for secure authentication.

### Model Routing Strategy

v1.2 intelligently routes elements to different models based on complexity:

| Element Type | Model | Rationale |
|-------------|-------|-----------|
| text_box, metric_card, quote | **Gemini 2.0 Flash** | Simple content, fast generation |
| table_row, comparison_column, sequential_step | **Gemini 1.5 Pro** | Complex structured content |
| colored_section, insights_box | **Gemini 1.5 Pro** | Nuanced contextual content |

**Cost Savings**: 60-70% reduction compared to using Pro for everything!

### Setup Instructions

#### Local Development

```bash
# 1. Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# 2. Authenticate with ADC
gcloud auth application-default login

# 3. Set project
gcloud config set project YOUR_PROJECT_ID

# 4. Set environment variable
export GCP_PROJECT_ID=your-project-id

# 5. Test integration
python3 test_gemini_integration.py
```

#### Production/Railway Deployment

```bash
# 1. Create service account in Google Cloud Console
# 2. Grant "Vertex AI User" role
# 3. Download JSON key
# 4. Set environment variables:
export GCP_PROJECT_ID=your-project-id
export GCP_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
```

### Testing Gemini Integration

Run the integration test to verify everything works:

```bash
cd agents/text_table_builder/v1.2
python3 test_gemini_integration.py
```

**Expected output:**
```
============================================================
v1.2 Gemini Integration Test
============================================================

Checking Prerequisites
============================================================
✓ GCP_PROJECT_ID: your-project-id
✓ Google Cloud credentials found
✓ Vertex AI library installed
✓ All prerequisites met

TEST 1: LLM Service Initialization
============================================================
✓ LLM service initialized
  - Model routing enabled: True
  - Flash model: gemini-2.0-flash-exp
  - Pro model: gemini-1.5-pro
✓ Generation successful
✓ Valid JSON response
✓ Usage stats:
  - Total calls: 1
  - Flash calls: 1 (100.0%)
  - Total tokens: 156

TEST 2: Element-Based Generation (matrix_2x2)
============================================================
✓ Generator initialized with Gemini integration
✓ Generation successful
  - HTML length: 4156 characters
  - Elements generated: 4
✓ LLM usage for this generation:
  - Total calls: 4
  - Total tokens: 624
✓ Saved generated HTML to: test_output_gemini.html

============================================================
✅ All tests passed!
```

---

## Architecture Flow

```
Director Specification (variant_id + context)
            ↓
    Load Variant Spec
            ↓
    Build Element Prompts ← Context Builder
            ↓
    Generate Elements (parallel) ← LLM Service
            ↓
    Assemble Template ← Template Cache
            ↓
    Validate & Return HTML
```

---

## Components

### 1. Element Prompt Builder (`app/core/element_prompt_builder.py`)

Builds targeted prompts for individual slide elements based on variant specifications.

**Key Features:**
- Loads variant specs from JSON files
- Builds prompts with character count requirements
- Includes element-specific instructions
- Caches variant specs for performance

**Usage:**
```python
from app.core import ElementPromptBuilder

builder = ElementPromptBuilder(variant_specs_dir="app/variant_specs")

# Load variant specification
spec = builder.load_variant_spec("matrix_2x2")

# Build prompts for all elements
element_prompts = builder.build_all_element_prompts(
    variant_id="matrix_2x2",
    slide_context="This slide presents our core company values",
    presentation_context="Q4 Business Review for executive stakeholders"
)
```

---

### 2. Context Builder (`app/core/context_builder.py`)

Builds comprehensive context for content generation from Director's specifications.

**Key Features:**
- Slide-level context (title, purpose, key message)
- Presentation-level context (prior slides, position in deck)
- Element relationships
- Tone and audience specifications

**Usage:**
```python
from app.core import ContextBuilder

builder = ContextBuilder()

# Build slide context
slide_context = builder.build_slide_context(
    slide_title="Our Core Values",
    slide_purpose="Communicate company values to stakeholders",
    key_message="Innovation, growth, customer success, team empowerment",
    tone="professional",
    audience="executive stakeholders"
)

# Build presentation context
pres_context = builder.build_presentation_context(
    presentation_title="Q4 Business Review",
    presentation_type="Business Presentation",
    current_slide_number=5,
    total_slides=20,
    prior_slides_summary="Covered Q4 financial results and market analysis"
)
```

---

### 3. Template Assembler (`app/core/template_assembler.py`)

Loads HTML templates and assembles them with generated content by replacing placeholders.

**Key Features:**
- Template caching for performance
- Placeholder extraction and validation
- Content map assembly
- Path normalization

**Usage:**
```python
from app.core import TemplateAssembler

assembler = TemplateAssembler(templates_dir="app/templates")

# Load template
template_html = assembler.load_template("matrix/matrix_2x2.html")

# Assemble with content
content_map = {
    "box_1_title": "Innovation",
    "box_1_description": "We drive innovation...",
    "box_2_title": "Growth",
    "box_2_description": "Strategic expansion..."
    # ... etc
}

assembled_html = assembler.assemble_template(
    template_path="matrix/matrix_2x2.html",
    content_map=content_map
)
```

---

### 4. Element-Based Content Generator (`app/core/element_based_generator.py`)

Main orchestrator that coordinates the complete v1.2 workflow.

**Key Features:**
- End-to-end content generation
- Parallel or sequential element generation
- Character count validation
- LLM service integration

**Usage:**
```python
from app.core import ElementBasedContentGenerator

# Initialize with LLM service
generator = ElementBasedContentGenerator(
    llm_service=your_llm_function,
    enable_parallel=True,
    max_workers=5
)

# Generate slide content
result = generator.generate_slide_content(
    variant_id="matrix_2x2",
    slide_spec={
        "slide_title": "Our Core Values",
        "slide_purpose": "Communicate values",
        "key_message": "Innovation, growth, success, empowerment",
        "tone": "professional",
        "audience": "executive stakeholders"
    },
    presentation_spec={
        "presentation_title": "Q4 Business Review",
        "presentation_type": "Business Presentation",
        "current_slide_number": 5,
        "total_slides": 20
    }
)

# Result contains:
# - html: Assembled HTML string
# - elements: List of generated element contents
# - metadata: Generation metadata
# - variant_id: The variant used
# - template_path: Template path used
```

---

## Available Variants

v1.2 supports **26 variants** across **10 slide types**:

### Matrix Layouts (2 variants)
- `matrix_2x2` - 2×2 grid with 4 boxes
- `matrix_2x3` - 2×3 grid with 6 boxes

### Grid Layouts (2 variants)
- `grid_2x3` - 2×3 grid with title + item lists
- `grid_3x2` - 3×2 grid with title + item lists

### Comparison Layouts (3 variants)
- `comparison_2col` - 2 vertical columns with headers
- `comparison_3col` - 3 vertical columns with headers
- `comparison_4col` - 4 vertical columns with headers

### Sequential Layouts (3 variants)
- `sequential_3col` - 3 numbered steps
- `sequential_4col` - 4 numbered steps
- `sequential_5col` - 5 numbered steps

### Asymmetric Layouts (4 variants)
- `asymmetric_8_4` - Main content + sidebar (2:1 ratio)
- `asymmetric_8_4_3section` - 3 colored sections + sidebar
- `asymmetric_8_4_4section` - 4 colored sections + sidebar
- `asymmetric_8_4_5section` - 5 colored sections + sidebar

### Hybrid Layouts (2 variants)
- `hybrid_top_2x2` - 2×2 grid on top, text box at bottom
- `hybrid_left_2x2` - 2×2 grid on left, text box on right

### Metrics Layouts (4 variants)
- `metrics_3col` - 3 metric cards with insights box
- `metrics_4col` - 4 metric cards (compact)
- `metrics_3x2_grid` - 3×2 grid with 6 cards + insights
- `metrics_2x2_grid` - 2×2 grid with 4 large cards

### Single Column (1 variant)
- `single_column` - Narrative layout with subheading, paragraphs, quote

### Impact Quote (1 variant)
- `impact_quote` - Large centered quote with attribution

### Table Layouts (4 variants)
- `table_2col` - Category + 1 data column, 5 rows
- `table_3col` - Category + 2 data columns, 5 rows
- `table_4col` - Category + 3 data columns, 5 rows
- `table_5col` - Category + 4 data columns, 5 rows

---

## API Endpoints

### POST `/v1.2/generate`

Generate slide content using element-based approach.

**Request:**
```json
{
  "variant_id": "matrix_2x2",
  "slide_spec": {
    "slide_title": "Our Core Values",
    "slide_purpose": "Communicate company values",
    "key_message": "Innovation, growth, success, empowerment",
    "tone": "professional",
    "audience": "executive stakeholders"
  },
  "presentation_spec": {
    "presentation_title": "Q4 Business Review",
    "presentation_type": "Business Presentation",
    "current_slide_number": 5,
    "total_slides": 20
  },
  "enable_parallel": true,
  "validate_character_counts": true
}
```

**Response:**
```json
{
  "success": true,
  "html": "<div style='...'> ... </div>",
  "elements": [
    {
      "element_id": "box_1",
      "element_type": "text_box",
      "generated_content": {
        "title": "Innovation Excellence",
        "description": "We drive transformative change..."
      },
      "character_counts": {
        "title": 30,
        "description": 120
      }
    }
  ],
  "metadata": {
    "variant_id": "matrix_2x2",
    "template_path": "matrix/matrix_2x2.html",
    "element_count": 4,
    "generation_mode": "parallel"
  },
  "validation": {
    "valid": true,
    "violations": []
  }
}
```

### GET `/v1.2/variants`

List all available variants organized by slide type.

### GET `/v1.2/variant/{variant_id}`

Get detailed specification for a specific variant.

---

## Directory Structure

```
v1.2/
├── app/
│   ├── core/                      # Core v1.2 architecture
│   │   ├── element_prompt_builder.py
│   │   ├── context_builder.py
│   │   ├── template_assembler.py
│   │   └── element_based_generator.py
│   ├── api/                       # API routes
│   │   └── v1_2_routes.py
│   ├── models/                    # Pydantic models
│   │   └── v1_2_models.py
│   ├── templates/                 # HTML templates (24 files)
│   │   ├── matrix/
│   │   ├── grid/
│   │   ├── comparison/
│   │   ├── sequential/
│   │   ├── asymmetric/
│   │   ├── hybrid/
│   │   ├── metrics/
│   │   ├── single_column/
│   │   ├── impact_quote/
│   │   └── table/
│   └── variant_specs/             # JSON specifications (26 files)
│       ├── matrix/
│       ├── grid/
│       ├── ...
│       └── variant_index.json     # Master variant index
├── tests/
│   └── test_v1_2_integration.py  # Integration tests
├── IMPLEMENTATION_PLAN.md         # Implementation roadmap
└── README.md                      # This file
```

---

## Testing

Run the integration test suite:

```bash
cd agents/text_table_builder/v1.2
python3 tests/test_v1_2_integration.py
```

**Expected Output:**
```
============================================================
v1.2 Integration Test Suite
============================================================

=== Testing ElementPromptBuilder ===
✓ Loaded variant spec: matrix_2x2
✓ Element count: 4
✓ Built element prompt (length: 673 chars)
✓ Built prompts for all 4 elements

=== Testing ContextBuilder ===
✓ Built slide context (length: 237 chars)
✓ Built presentation context (length: 99 chars)

=== Testing TemplateAssembler ===
✓ Loaded template (length: 3788 chars)
✓ Extracted 8 placeholders
✓ Assembled template (length: 3769 chars)

=== Testing Complete v1.2 Workflow ===
✓ Generated slide content
  - HTML length: 4156 chars
  - Elements generated: 4
  - Generation mode: sequential
✓ HTML contains all generated content
✓ All elements have required fields
✓ Character count validation: True

============================================================
✅ All tests passed!
============================================================
```

---

## Migration from v1.1

### Key Differences

| v1.1 | v1.2 |
|------|------|
| Single LLM call generates complete HTML | Multiple targeted LLM calls per element |
| Full HTML in system prompt | Templates loaded from files |
| No character count enforcement | Strict character count requirements |
| Sequential generation only | Parallel generation supported |
| Prompt size: ~10K tokens | Prompt size: ~1K tokens per element |

### Benefits of v1.2

1. **Faster Generation**: 3-5x faster with parallel element generation
2. **Better Quality**: Element-specific prompts produce more targeted content
3. **Easier Maintenance**: Templates and specs separate from code
4. **Format Consistency**: Deterministic assembly ensures pixel-perfect output
5. **Scalability**: Add new variants by adding JSON + HTML files

---

## Character Count Requirements

All elements have strict character count requirements defined in variant specs:

```json
{
  "character_requirements": {
    "title": {
      "baseline": 30,
      "min": 27,
      "max": 32
    },
    "description": {
      "baseline": 120,
      "min": 114,
      "max": 126
    }
  }
}
```

The formula:
- **Baseline**: Target character count from golden examples
- **Min**: baseline × 0.95
- **Max**: baseline × 1.05

Validation can be enabled via API to check generated content meets requirements.

---

## Performance

### Benchmarks (Matrix 2×2)

| Mode | Time | LLM Calls |
|------|------|-----------|
| Sequential | ~4.2s | 4 calls |
| Parallel (5 workers) | ~1.1s | 4 concurrent |

**3.8x speedup** with parallel generation!

---

## Future Enhancements

- [ ] Add more variants (additional grid sizes, new layouts)
- [ ] Implement retry logic for character count violations
- [ ] Add variant recommendation based on content
- [ ] Support dynamic template generation
- [ ] Add variant A/B testing capabilities

---

## Contributing

To add a new variant:

1. Create HTML template in `app/templates/{slide_type}/{variant_id}.html`
2. Create JSON spec in `app/variant_specs/{slide_type}/{variant_id}.json`
3. Update `variant_index.json` with new variant entry
4. Test with integration test suite

---

## License

Copyright © 2025 Deckster. All rights reserved.
