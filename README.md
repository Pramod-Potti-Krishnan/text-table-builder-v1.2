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
  - Flash model: gemini-2.5-flash
  - Pro model: gemini-2.5-pro
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

## Hero Slides (L29 Layout)

v1.2 includes **3 specialized hero slide endpoints** for generating full-bleed impact slides using the L29 layout. These complement the content slide variants for a complete presentation solution.

### Architecture Philosophy

Hero slides use a **different architecture** than content slides:

| Aspect | Content Slides (L25) | Hero Slides (L29) |
|--------|---------------------|-------------------|
| Generation | Element-based assembly | Single LLM call |
| Prompt Style | Targeted element prompts | Rich v1.1-style prompts |
| HTML Structure | Template placeholders | Complete inline-styled HTML |
| Complexity | High (4-8 elements) | Low (1-3 elements) |
| Model | Flash + Pro routing | Flash only |

**Why Single-Call?** Hero slides have simple structure (title + subtitle + CTA), making element-based assembly unnecessary overhead.

### Hero Slide Types

#### 1. Title Slide (`/v1.2/hero/title`)

Opening slide with maximum visual impact.

**HTML Structure:**
```html
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); ...">
  <h1 style="font-size: 96px; color: white; font-weight: 900; ...">
    AI in Healthcare: Transforming Diagnostics
  </h1>
  <p style="font-size: 42px; color: rgba(255,255,255,0.95); ...">
    Revolutionizing diagnostic accuracy through advanced machine learning
  </p>
  <div style="font-size: 32px; color: rgba(255,255,255,0.9); ...">
    Dr. Sarah Chen | HealthTech Innovations | December 2025
  </div>
</div>
```

**Visual Features:**
- ✅ Gradient background (4 theme options)
- ✅ 96px title font (ultra-large, bold)
- ✅ 42px subtitle font
- ✅ 32px attribution font
- ✅ Text shadows for depth
- ✅ Center-aligned, flexbox centered

**Character Limits:**
- Title: 40-80 chars (max 100)
- Subtitle: 80-120 chars (max 150)
- Attribution: 60-100 chars (max 120)

---

#### 2. Section Divider (`/v1.2/hero/section`)

Transition slide marking major section changes.

**HTML Structure:**
```html
<div style="background: #1f2937; ...">
  <div style="border-left: 12px solid #667eea; padding-left: 48px;">
    <h2 style="font-size: 84px; color: white; font-weight: 700; ...">
      Implementation Roadmap
    </h2>
    <p style="font-size: 42px; color: #9ca3af; ...">
      From Planning to Full Deployment
    </p>
  </div>
</div>
```

**Visual Features:**
- ✅ Dark background (#1f2937) for contrast
- ✅ 12px colored left border accent
- ✅ 84px section title (large, bold)
- ✅ 42px context text (muted gray)
- ✅ Left-aligned (not centered)
- ✅ Minimal, dramatic aesthetic

**Character Limits:**
- Section title: 40-60 chars (max 80)
- Context text: 80-120 chars (max 150)

---

#### 3. Closing Slide (`/v1.2/hero/closing`)

Final slide with call-to-action and contact information.

**HTML Structure:**
```html
<div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); ...">
  <h2 style="font-size: 72px; color: white; ...">
    Ready to Transform Your Operations?
  </h2>
  <p style="font-size: 36px; color: rgba(255,255,255,0.95); ...">
    Join 500+ organizations using AI to reduce costs and deliver superior experiences
  </p>
  <div style="padding: 32px 72px; background: white; color: #667eea; font-size: 32px; border-radius: 12px; ...">
    Schedule Your Demo Today
  </div>
  <div style="font-size: 28px; color: rgba(255,255,255,0.9); ...">
    contact@company.com | www.company.com | 1-800-COMPANY
  </div>
</div>
```

**Visual Features:**
- ✅ Gradient background
- ✅ 72px closing message
- ✅ 36px supporting text
- ✅ 32px white CTA button (prominent)
- ✅ 28px contact info
- ✅ Button shadow for depth

**Character Limits:**
- Closing message: 50-80 chars (max 120)
- Supporting text: Variable (based on value prop)
- CTA button: 3-5 words
- Contact: 3-5 items

---

### Inline-Styled HTML

Hero slides generate **complete inline-styled HTML** inspired by v1.1's world-class prompts:

**Key Features:**
- 🎨 Gradient backgrounds (`linear-gradient(135deg, ...)`)
- 📏 Large typography (96px/84px/72px fonts)
- 🌈 RGBA colors for transparency
- ✨ Text shadows for readability (`0 4px 12px rgba(0,0,0,0.3)`)
- 📐 Flexbox centering
- 💫 Full inline styles (no external CSS)

**Validation Approach:**

Unlike content slides, hero slide validation checks for **inline style patterns** rather than CSS classes:

```python
# Check for gradient background
has_gradient = bool(re.search(r'<div[^>]*style=.*linear-gradient', content, re.DOTALL))

# Check for large typography
has_96px_font = bool(re.search(r'<h1[^>]*style=.*font-size:\s*96px', content, re.DOTALL))

# Check for white text
has_white_text = bool(re.search(r'color:\s*white', content))
```

This ensures generated HTML matches the v1.1-style rich styling requirements.

---

### Hero Slide Request Format

**Common Fields:**
```json
{
  "slide_number": 1,
  "slide_type": "title_slide",
  "narrative": "Core message or purpose of this slide",
  "topics": ["Key", "Topics", "To", "Cover"],
  "context": {
    "theme": "professional",
    "audience": "executive stakeholders",
    "presentation_title": "Q4 Business Review",
    "contact_info": "email@company.com"
  }
}
```

**Response Format:**
```json
{
  "content": "<div style='width: 100%; height: 100%; background: linear-gradient(...); ...'>...</div>",
  "metadata": {
    "slide_type": "title_slide",
    "slide_number": 1,
    "validation": {
      "valid": true,
      "violations": [],
      "warnings": [],
      "metrics": {
        "title_length": 47,
        "subtitle_length": 69
      }
    },
    "generation_mode": "hero_slide_async"
  }
}
```

---

### Total v1.2 Capabilities

**Content Slides:** 10 slide types with 26 variants
**Hero Slides:** 3 specialized endpoints
**Total Endpoints:** 13 (10 content `/v1.2/generate` + 3 hero `/v1.2/hero/*`)

This makes v1.2 a **complete presentation generation service** handling both rich content and impactful hero slides.

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

### POST `/v1.2/hero/title`

Generate title/opening slide (L29 hero layout).

**Request:**
```json
{
  "slide_number": 1,
  "slide_type": "title_slide",
  "narrative": "AI transforming healthcare diagnostics",
  "topics": ["Machine Learning", "Patient Outcomes", "Diagnostic Accuracy"],
  "context": {
    "theme": "professional",
    "audience": "healthcare professionals",
    "presentation_title": "AI in Healthcare: Transforming Diagnostics"
  }
}
```

**Response:**
```json
{
  "content": "<div style=\"width: 100%; height: 100%; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px;\"><h1 style=\"font-size: 96px; color: white; font-weight: 900; text-align: center; margin: 0 0 40px 0; text-shadow: 0 4px 12px rgba(0,0,0,0.3); line-height: 1.1; letter-spacing: -2px;\">AI in Healthcare: Transforming Diagnostics</h1>...</div>",
  "metadata": {
    "slide_type": "title_slide",
    "slide_number": 1,
    "validation": {
      "valid": true,
      "violations": [],
      "warnings": [],
      "metrics": {
        "title_length": 47,
        "subtitle_length": 69
      }
    },
    "generation_mode": "hero_slide_async"
  }
}
```

---

### POST `/v1.2/hero/section`

Generate section divider slide (L29 hero layout).

**Request:**
```json
{
  "slide_number": 5,
  "slide_type": "section_divider",
  "narrative": "Transitioning to implementation phase",
  "topics": ["Planning", "Deployment", "Timeline"],
  "context": {
    "theme": "professional"
  }
}
```

---

### POST `/v1.2/hero/closing`

Generate closing/conclusion slide (L29 hero layout).

**Request:**
```json
{
  "slide_number": 15,
  "slide_type": "closing_slide",
  "narrative": "Call to action for adopting AI diagnostics",
  "topics": ["Implementation", "ROI", "Next Steps"],
  "context": {
    "theme": "professional",
    "contact_info": "contact@healthtech.com | www.healthtech.com"
  }
}
```

---

## Directory Structure

```
v1.2/
├── app/
│   ├── core/                      # Core v1.2 architecture
│   │   ├── element_prompt_builder.py
│   │   ├── context_builder.py
│   │   ├── template_assembler.py
│   │   ├── element_based_generator.py
│   │   └── hero/                  # Hero slide generators (L29 layout)
│   │       ├── __init__.py
│   │       ├── base_hero_generator.py      # Base class for hero slides
│   │       ├── title_slide_generator.py    # Opening/title slides
│   │       ├── section_divider_generator.py # Section transitions
│   │       └── closing_slide_generator.py   # Closing/CTA slides
│   ├── api/                       # API routes
│   │   ├── v1_2_routes.py         # Content slide endpoints
│   │   └── hero_routes.py         # Hero slide endpoints
│   ├── models/                    # Pydantic models
│   │   └── v1_2_models.py
│   ├── templates/                 # HTML templates (26 files)
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
