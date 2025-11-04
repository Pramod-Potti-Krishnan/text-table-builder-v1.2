# Text Service v1.2 - Architecture Documentation

**Version:** 1.2.0
**Architecture:** Element-Based Deterministic Assembly
**Primary Model:** Gemini via Vertex AI (Application Default Credentials)
**Purpose:** Generate rich HTML content for presentation slides using template-driven assembly

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Philosophy](#architecture-philosophy)
3. [Content Generation Flow](#content-generation-flow)
4. [Hero vs Content Slides](#hero-vs-content-slides)
5. [Element-Based Assembly System](#element-based-assembly-system)
6. [Component Architecture](#component-architecture)
7. [Single-Call Architecture](#single-call-architecture)
8. [Character Requirement System](#character-requirement-system)
9. [Template Structure](#template-structure)
10. [Variant Specifications](#variant-specifications)
11. [API Endpoints](#api-endpoints)
12. [LLM Integration](#llm-integration)

---

## Overview

Text Service v1.2 is a **deterministic template assembly service** that generates rich HTML content for presentation slides. Unlike traditional content generation systems, v1.2 uses a **JSON-driven, element-based approach** where:

1. **Slides are decomposed into elements** (boxes, columns, sections, metrics)
2. **Each element has strict character requirements** defined in JSON specs
3. **Templates are pure HTML** with `{placeholder}` syntax
4. **ONE LLM call generates ALL elements** to ensure content coherence
5. **Assembly is deterministic** - template + content map → final HTML

### Key Capabilities

- **34 Platinum Approved Templates** across 10 slide types
- **Single-call content generation** for element coherence
- **Character count precision** (baseline ± 5% tolerance)
- **Parallel-ready architecture** (though currently using single-call)
- **Vertex AI integration** with Application Default Credentials
- **Zero layout logic** in Text Service (Layout Builder v7.5 handles structure)

### Service Boundaries

```
┌─────────────────────────────────────────────────────────────────┐
│                     Text Service v1.2                            │
│  • Generate HTML content for individual slide elements           │
│  • Assemble elements into templates                             │
│  • Validate character counts                                     │
│  • NO layout positioning (done by Layout Builder v7.5)          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Architecture Philosophy

### Deterministic Assembly

v1.2 follows a **deterministic assembly philosophy**:

```
Requirements → JSON Spec → Element Prompts → LLM → Content Map → Template → HTML
```

**No AI in assembly**:
- Templates are static HTML files
- Assembly is string replacement: `{placeholder}` → `generated_content`
- Character counts guide LLM, but assembly never modifies content

### Separation of Concerns

```
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│   Director v3.4      │  │   Text Service v1.2   │  │  Layout Builder v7.5 │
│                      │  │                       │  │                      │
│ • Content strategy   │  │ • HTML generation     │  │ • L25 layout         │
│ • Slide purposes     │  │ • Element assembly    │  │ • Positioning        │
│ • Key messages       │  │ • Character limits    │  │ • Deck composition   │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘
```

**Text Service v1.2 responsibilities**:
1. Accept `variant_id` from Director
2. Load JSON spec + HTML template
3. Generate element content via LLM
4. Assemble content into template
5. Return HTML (Layout Builder handles rest)

---

## Content Generation Flow

### Complete Request-to-HTML Pipeline

```
1. Director Request
   ↓
2. POST /v1.2/generate
   {
     "variant_id": "matrix_2x2",
     "slide_spec": {
       "slide_title": "Digital Transformation",
       "slide_purpose": "Present 4 pillars",
       "key_message": "Transform across all areas"
     }
   }
   ↓
3. Load Variant Spec
   • app/variant_specs/matrix/matrix_2x2.json
   • Contains elements, character requirements, template path
   ↓
4. Build Context
   • Slide context (title, purpose, message)
   • Presentation context (optional)
   ↓
5. Build Single Complete Prompt
   • ElementPromptBuilder.build_complete_slide_prompt()
   • ALL elements in ONE prompt
   ↓
6. Generate Content (ONE LLM CALL)
   • Vertex AI: gemini-2.0-flash-exp
   • Returns JSON with all elements
   ↓
7. Parse Response
   • Extract element contents
   • Validate required fields
   ↓
8. Build Content Map
   • {placeholder: content} mapping
   ↓
9. Assemble Template
   • Load app/templates/matrix/matrix_2x2.html
   • Replace {box_1_title} → "Innovation"
   • Replace {box_1_description} → "Adopt cutting-edge..."
   ↓
10. Validate Character Counts
    • Check min/max ranges
    • Report violations if any
    ↓
11. Return Response
    {
      "html": "<div style='...'>...</div>",
      "elements": [...],
      "metadata": {...},
      "validation": {...}
    }
```

### Timing Breakdown

Typical generation timeline for a single slide:

```
Component              Time
─────────────────────  ──────
Load variant spec      ~2ms   (cached after first load)
Build context          ~1ms
Build prompt           ~5ms
LLM generation         ~2-4s  (Vertex AI roundtrip)
Parse response         ~10ms
Assemble template      ~5ms   (cached after first load)
Validate counts        ~2ms
─────────────────────  ──────
Total                  ~2-4s  (dominated by LLM)
```

---

## Hero vs Content Slides

Text Service v1.2 handles two types of slides differently:

### Hero Slides (v1.0/v1.1 Legacy)

**Characteristics**:
- Simple structure: title, subtitle, optional rich_content
- Uses `StructuredTextGenerator` from `generators.py`
- Format ownership architecture (text_service vs layout_builder)
- Field-by-field generation with separate LLM calls

**Generator**: `StructuredTextGenerator` (lines 449-831, `app/core/generators.py`)

**Example Request**:
```python
{
  "layout_id": "L01",
  "field_specifications": {
    "slide_title": {
      "type": "title",
      "format_type": "plain_text",
      "format_owner": "layout_builder",
      "max_chars": 60
    },
    "subtitle": {
      "type": "subtitle",
      "format_type": "plain_text",
      "format_owner": "layout_builder",
      "max_chars": 100
    }
  }
}
```

**Flow**:
```
Field-by-Field Generation:
  For each field:
    1. Check format_owner
    2. Generate plain_text or html
    3. Validate against max_chars/max_lines
    4. Return content
```

### Content Slides (v1.2 Element-Based)

**Characteristics**:
- Complex multi-element structure (boxes, columns, metrics, sections)
- Uses `ElementBasedContentGenerator` from `element_based_generator.py`
- Single-call architecture (ALL elements in ONE LLM call)
- Template-driven assembly with strict character requirements

**Generator**: `ElementBasedContentGenerator` (lines 30-432, `app/core/element_based_generator.py`)

**Example Request**:
```python
{
  "variant_id": "matrix_2x2",
  "slide_spec": {
    "slide_title": "Digital Transformation Framework",
    "slide_purpose": "Present 4 strategic pillars",
    "key_message": "Transform business across all dimensions"
  }
}
```

**Flow**:
```
Single-Call Generation:
  1. Load variant spec (4 elements: box_1, box_2, box_3, box_4)
  2. Build ONE complete prompt for ALL elements
  3. LLM generates JSON with all 4 boxes
  4. Parse and validate
  5. Assemble into template
  6. Return complete HTML
```

### Key Differences

| Aspect | Hero Slides (v1.0/v1.1) | Content Slides (v1.2) |
|--------|-------------------------|------------------------|
| **Generator** | `StructuredTextGenerator` | `ElementBasedContentGenerator` |
| **Input** | Field specifications | Variant ID + slide spec |
| **LLM Calls** | One per field | **ONE for all elements** |
| **Structure** | Simple (title/subtitle) | Complex (multi-element) |
| **Templates** | Layout Builder handles | Text Service assembles |
| **Character Limits** | Max only | **Baseline ± 5% range** |
| **Format Ownership** | Split (text vs layout) | Text Service owns all |
| **Assembly** | Layout Builder | **Deterministic template assembly** |

---

## Element-Based Assembly System

### Core Concept

v1.2 treats every slide as a **collection of elements**:

```
Slide = Element₁ + Element₂ + ... + Elementₙ

Where each element:
  • Has a type (text_box, metric_card, comparison_column, etc.)
  • Has required fields (title, description, bullets, etc.)
  • Has strict character requirements (baseline ± 5%)
  • Maps to placeholders in HTML template
```

### Element Types

**1. Text Box** (matrix, grid layouts)
```json
{
  "element_id": "box_1",
  "element_type": "text_box",
  "required_fields": ["title", "description"],
  "placeholders": {
    "title": "box_1_title",
    "description": "box_1_description"
  }
}
```

**2. Comparison Column** (comparison layouts)
```json
{
  "element_id": "column_1",
  "element_type": "comparison_column",
  "required_fields": ["heading", "items"],
  "placeholders": {
    "heading": "column_1_heading",
    "items": "column_1_items"  // HTML <ul><li>...</li></ul>
  }
}
```

**3. Sequential Step** (sequential layouts)
```json
{
  "element_id": "step_1",
  "element_type": "sequential_step",
  "required_fields": ["title", "paragraph_1", "paragraph_2", "paragraph_3"],
  "placeholders": {
    "title": "step_1_title",
    "paragraph_1": "step_1_paragraph_1",
    "paragraph_2": "step_1_paragraph_2",
    "paragraph_3": "step_1_paragraph_3"
  }
}
```

**4. Metric Card** (metrics layouts)
```json
{
  "element_id": "metric_1",
  "element_type": "metric_card",
  "required_fields": ["number", "label", "description"],
  "placeholders": {
    "number": "metric_1_number",
    "label": "metric_1_label",
    "description": "metric_1_description"
  }
}
```

**5. Section with Bullets** (single_column, asymmetric layouts)
```json
{
  "element_id": "section_1",
  "element_type": "section_with_bullets",
  "required_fields": ["heading", "bullet_1", "bullet_2", "bullet_3"],
  "placeholders": {
    "heading": "section_1_heading",
    "bullet_1": "section_1_bullet_1",
    "bullet_2": "section_1_bullet_2",
    "bullet_3": "section_1_bullet_3"
  }
}
```

### Assembly Process

```python
# Step 1: Load variant spec
spec = load_variant_spec("matrix_2x2")
# spec = {
#   "elements": [
#     {"element_id": "box_1", ...},
#     {"element_id": "box_2", ...},
#     {"element_id": "box_3", ...},
#     {"element_id": "box_4", ...}
#   ],
#   "template_path": "app/templates/matrix/matrix_2x2.html"
# }

# Step 2: Generate content (ONE LLM call)
llm_response = llm_service(complete_prompt)
# Returns:
# {
#   "box_1": {"title": "Innovation", "description": "Adopt cutting-edge..."},
#   "box_2": {"title": "Customer Focus", "description": "Put customers..."},
#   "box_3": {"title": "Data-Driven", "description": "Leverage analytics..."},
#   "box_4": {"title": "Agility", "description": "Respond quickly..."}
# }

# Step 3: Build content map
content_map = {
  "box_1_title": "Innovation",
  "box_1_description": "Adopt cutting-edge technologies...",
  "box_2_title": "Customer Focus",
  "box_2_description": "Put customers at the center...",
  ...
}

# Step 4: Assemble template
html = template_assembler.assemble_template(
  template_path="app/templates/matrix/matrix_2x2.html",
  content_map=content_map
)
# Result: HTML with all {placeholders} replaced
```

---

## Component Architecture

### 1. ElementBasedContentGenerator

**File**: `app/core/element_based_generator.py` (lines 30-432)

**Role**: Main orchestrator for v1.2 content generation

**Key Methods**:

```python
class ElementBasedContentGenerator:
    def __init__(self, llm_service, variant_specs_dir, templates_dir):
        self.llm_service = llm_service
        self.prompt_builder = ElementPromptBuilder(variant_specs_dir)
        self.context_builder = ContextBuilder()
        self.template_assembler = TemplateAssembler(templates_dir)

    def generate_slide_content(self, variant_id, slide_spec,
                                presentation_spec=None) -> Dict:
        """
        Main entry point for v1.2 content generation.

        Flow:
        1. Build contexts (slide + presentation)
        2. Get variant metadata
        3. Build complete slide prompt (all elements)
        4. Generate with ONE LLM call
        5. Parse response into element contents
        6. Build content map
        7. Assemble template
        8. Return result
        """
```

**Architecture**:
```
ElementBasedContentGenerator
├── llm_service (Callable)
├── prompt_builder (ElementPromptBuilder)
├── context_builder (ContextBuilder)
└── template_assembler (TemplateAssembler)
```

**Single-Call Architecture** (NEW in v1.2):
```python
# Build ONE prompt for ALL elements
complete_prompt = self.prompt_builder.build_complete_slide_prompt(
    variant_id=variant_id,
    slide_context=contexts["slide_context"],
    presentation_context=contexts.get("presentation_context")
)

# Generate content with ONE LLM call (not per-element)
llm_response = self.llm_service(complete_prompt)

# Parse response into element contents
element_contents = self._parse_complete_response(
    llm_response=llm_response,
    variant_id=variant_id
)
```

### 2. ElementPromptBuilder

**File**: `app/core/element_prompt_builder.py` (lines 18-422)

**Role**: Build targeted prompts for element generation

**Key Methods**:

```python
class ElementPromptBuilder:
    def __init__(self, variant_specs_dir):
        self.variant_specs_dir = Path(variant_specs_dir)
        self.variant_index = self._load_variant_index()
        self._spec_cache = {}  # Cache loaded specs

    def load_variant_spec(self, variant_id: str) -> Dict:
        """Load variant JSON spec from file."""
        # Cache check
        if variant_id in self._spec_cache:
            return self._spec_cache[variant_id]

        # Load from app/variant_specs/{slide_type}/{variant_id}.json
        spec_path = self.variant_specs_dir / slide_type / f"{variant_id}.json"
        with open(spec_path, 'r') as f:
            spec = json.load(f)

        # Cache for performance
        self._spec_cache[variant_id] = spec
        return spec

    def build_complete_slide_prompt(self, variant_id, slide_context,
                                      presentation_context=None) -> str:
        """
        Build ONE prompt for generating ALL elements at once.

        This is the v1.2 single-call architecture.
        """
        spec = self.load_variant_spec(variant_id)

        prompt = f"""Generate complete content for a presentation slide.

VARIANT: {variant_id} ({spec['description']})
SLIDE TYPE: {spec['slide_type']}
TOTAL ELEMENTS: {len(spec['elements'])}

SLIDE CONTEXT:
{slide_context}

IMPORTANT: Generate ALL elements together to ensure content coherence.
Each element should cover a DIFFERENT aspect - avoid repetition.

ELEMENTS TO GENERATE:

1. box_1 (text_box):
   Required fields: title, description
   Character count requirements:
     - title: 27-32 characters (target: 30)
     - description: 228-252 characters (target: 240)

2. box_2 (text_box):
   ...

RESPONSE FORMAT:
Return a single JSON object with all elements:

{
  "box_1": {
    "title": "content here",
    "description": "content here"
  },
  "box_2": {
    "title": "content here",
    "description": "content here"
  }
}

CRITICAL INSTRUCTIONS:
1. Generate ALL elements in ONE response
2. Ensure each element has DIFFERENT content (no repetition)
3. All content should be coherent and work together
4. Follow character count requirements strictly
5. Return ONLY valid JSON with no additional text
"""
        return prompt
```

**Element-Specific Instructions**:

The prompt builder adds type-specific instructions for each element type (lines 153-251):

```python
def _get_element_type_instructions(self, element_type: str) -> str:
    instructions = {
        "text_box": (
            "- Title should be concise and descriptive\n"
            "- Description should explain the concept clearly\n"
            "- Use professional, business-appropriate language"
        ),
        "comparison_column": (
            "- Heading should clearly identify what's being compared\n"
            "- Items should be returned as HTML <ul> list with <li> tags\n"
            "- IMPORTANT: Start each list item with a bold subheading\n"
            "- Format: <li><strong>Subheading:</strong> Description</li>\n"
            "- Use parallel structure for easy comparison"
        ),
        "metric_card": (
            "- Number should be the key metric value\n"
            "- Label should identify what the metric represents\n"
            "- Description should provide context or insight\n"
            "- Use impactful, data-driven language"
        ),
        ...
    }
    return instructions.get(element_type, "")
```

### 3. ContextBuilder

**File**: `app/core/context_builder.py` (lines 15-226)

**Role**: Build comprehensive context for LLM generation

**Key Methods**:

```python
class ContextBuilder:
    def build_slide_context(self, slide_title, slide_purpose,
                             key_message, target_points=None,
                             tone="professional",
                             audience="business stakeholders") -> str:
        """Build context specific to current slide."""
        context = f"""Slide Title: {slide_title}

Slide Purpose: {slide_purpose}

Key Message: {key_message}

Target Audience: {audience}
Tone: {tone}
"""
        if target_points:
            context += "\nTarget Points to Include:\n"
            for i, point in enumerate(target_points, 1):
                context += f"{i}. {point}\n"

        return context

    def build_presentation_context(self, presentation_title,
                                    presentation_type,
                                    prior_slides_summary=None,
                                    current_slide_number=None,
                                    total_slides=None) -> str:
        """Build context about overall presentation."""
        context = f"""Presentation: {presentation_title}
Presentation Type: {presentation_type}
"""
        if current_slide_number and total_slides:
            context += f"\nSlide Position: {current_slide_number} of {total_slides}\n"

        if prior_slides_summary:
            context += f"""
Prior Slides Context:
{prior_slides_summary}

NOTE: Build upon the narrative. Do not repeat information already covered.
"""
        return context

    def build_complete_context(self, slide_spec, presentation_spec=None) -> Dict:
        """Build all context layers."""
        slide_context = self.build_slide_context(
            slide_title=slide_spec["slide_title"],
            slide_purpose=slide_spec["slide_purpose"],
            key_message=slide_spec["key_message"],
            target_points=slide_spec.get("target_points"),
            tone=slide_spec.get("tone", "professional"),
            audience=slide_spec.get("audience", "business stakeholders")
        )

        result = {"slide_context": slide_context}

        if presentation_spec:
            presentation_context = self.build_presentation_context(...)
            result["presentation_context"] = presentation_context

        return result
```

**Context Layers**:

```
┌─────────────────────────────────────────────────────────────┐
│ SLIDE CONTEXT (Required)                                     │
│ • Slide title, purpose, key message                          │
│ • Target points (optional)                                   │
│ • Tone, audience                                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ PRESENTATION CONTEXT (Optional)                              │
│ • Presentation title, type                                   │
│ • Prior slides summary                                       │
│ • Slide position (e.g., "Slide 5 of 20")                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ VARIANT CONTEXT (Automatic)                                  │
│ • Variant ID, description                                    │
│ • Element structure                                          │
│ • Character requirements                                     │
└─────────────────────────────────────────────────────────────┘
```

### 4. TemplateAssembler

**File**: `app/core/template_assembler.py` (lines 17-169)

**Role**: Load templates and assemble with content

**Key Methods**:

```python
class TemplateAssembler:
    def __init__(self, templates_dir):
        self.templates_dir = Path(templates_dir)
        self._template_cache = {}  # Cache loaded templates

    def load_template(self, template_path: str) -> str:
        """Load HTML template from file."""
        # Check cache
        if template_path in self._template_cache:
            return self._template_cache[template_path]

        # Normalize path (remove "app/templates/" if present)
        if template_path.startswith("app/templates/"):
            template_path = template_path[len("app/templates/"):]

        # Load from file
        full_path = self.templates_dir / template_path
        with open(full_path, 'r', encoding='utf-8') as f:
            template_html = f.read()

        # Cache for performance
        self._template_cache[template_path] = template_html
        return template_html

    def assemble_template(self, template_path: str,
                          content_map: Dict[str, str]) -> str:
        """
        Assemble template by replacing placeholders with content.

        Args:
            template_path: Path to template (e.g., "matrix/matrix_2x2.html")
            content_map: {placeholder: content} mapping
                        e.g., {"box_1_title": "Innovation", ...}

        Returns:
            Assembled HTML with all placeholders replaced
        """
        # Load template
        template_html = self.load_template(template_path)

        # Find all placeholders (valid names: letters, numbers, underscores)
        placeholder_pattern = r'\{([a-z_][a-z0-9_]*)\}'
        placeholders = set(re.findall(placeholder_pattern, template_html, re.IGNORECASE))

        # Check for missing placeholders
        missing = placeholders - set(content_map.keys())
        if missing:
            raise ValueError(f"Missing content for placeholders: {', '.join(sorted(missing))}")

        # Replace placeholders
        assembled_html = template_html
        for placeholder, content in content_map.items():
            placeholder_pattern = '{' + placeholder + '}'
            assembled_html = assembled_html.replace(placeholder_pattern, content)

        return assembled_html

    def get_template_placeholders(self, template_path: str) -> set:
        """Extract all placeholders from a template."""
        template_html = self.load_template(template_path)
        placeholder_pattern = r'\{([a-z_][a-z0-9_]*)\}'
        return set(re.findall(placeholder_pattern, template_html, re.IGNORECASE))

    def validate_content_map(self, template_path, content_map) -> Dict:
        """Validate that content map matches template requirements."""
        template_placeholders = self.get_template_placeholders(template_path)
        content_keys = set(content_map.keys())

        return {
            "missing": sorted(template_placeholders - content_keys),
            "extra": sorted(content_keys - template_placeholders)
        }
```

**Template Caching**:

Templates are cached in memory after first load for performance:

```python
# First call: loads from disk
html = assembler.load_template("matrix/matrix_2x2.html")  # ~50ms

# Subsequent calls: returns from cache
html = assembler.load_template("matrix/matrix_2x2.html")  # ~0.1ms
```

**Placeholder Pattern**:

Only matches valid placeholder names (prevents matching CSS):

```regex
Pattern: \{([a-z_][a-z0-9_]*)\}

Matches:
  {box_1_title}          ✅
  {section_2_bullet_3}   ✅
  {metric_card_number}   ✅

Does NOT match:
  { color: #fff; }       ❌ (CSS)
  {123invalid}           ❌ (starts with number)
  {Box-Title}            ❌ (contains hyphen)
```

---

## Single-Call Architecture

### Why Single-Call?

**Problem with Per-Element Generation** (v1.2 initial approach):
```
Generate box_1 → "Innovation: Adopt cutting-edge technologies..."
Generate box_2 → "Innovation and Technology: Leverage modern tools..."
Generate box_3 → "Digital Innovation: Implement new systems..."
Generate box_4 → "Technological Advancement: Embrace digital..."

❌ PROBLEM: Repetitive content, all boxes about similar themes
```

**Solution: Single-Call Generation** (v1.2 refactored):
```
Generate ALL boxes at once:
{
  "box_1": {"title": "Innovation", "description": "Adopt cutting-edge..."},
  "box_2": {"title": "Customer Focus", "description": "Put customers first..."},
  "box_3": {"title": "Data-Driven", "description": "Leverage analytics..."},
  "box_4": {"title": "Agility", "description": "Respond quickly..."}
}

✅ SOLUTION: Coherent, diverse content - each box covers DIFFERENT aspect
```

### Implementation

**Old Approach (DEPRECATED)**:
```python
# Generate each element separately
for element in spec["elements"]:
    element_prompt = build_element_prompt(element)
    content = llm_service(element_prompt)  # Separate LLM call
    element_contents.append(content)
```

**New Approach (v1.2 Current)**:
```python
# Generate ALL elements in ONE call
complete_prompt = build_complete_slide_prompt(
    variant_id=variant_id,
    all_elements=spec["elements"]
)

llm_response = llm_service(complete_prompt)  # ONE LLM call

all_elements_data = json.loads(llm_response)
# {
#   "box_1": {...},
#   "box_2": {...},
#   "box_3": {...},
#   "box_4": {...}
# }
```

### Prompt Structure

**Single-Call Prompt Format**:

```
Generate complete content for a presentation slide.

VARIANT: matrix_2x2 (2×2 matrix layout with 4 equal boxes)
SLIDE TYPE: matrix
TOTAL ELEMENTS: 4

SLIDE CONTEXT:
Slide Title: Digital Transformation Framework
Slide Purpose: Present 4 strategic pillars
Key Message: Transform business across all dimensions

IMPORTANT: Generate ALL elements together to ensure content coherence.
Each element should cover a DIFFERENT aspect - avoid repetition.

ELEMENTS TO GENERATE:

1. box_1 (text_box):
   Required fields: title, description
   Character count requirements:
     - title: 27-32 characters (target: 30)
     - description: 228-252 characters (target: 240)
   Instructions:
     - Title should be concise and descriptive
     - Description should explain the concept clearly

2. box_2 (text_box):
   Required fields: title, description
   Character count requirements:
     - title: 27-32 characters (target: 30)
     - description: 228-252 characters (target: 240)

3. box_3 (text_box):
   Required fields: title, description
   Character count requirements:
     - title: 27-32 characters (target: 30)
     - description: 228-252 characters (target: 240)

4. box_4 (text_box):
   Required fields: title, description
   Character count requirements:
     - title: 27-32 characters (target: 30)
     - description: 228-252 characters (target: 240)

RESPONSE FORMAT:
Return a single JSON object with all elements:

{
  "box_1": {
    "title": "content here",
    "description": "content here"
  },
  "box_2": {
    "title": "content here",
    "description": "content here"
  },
  "box_3": {
    "title": "content here",
    "description": "content here"
  },
  "box_4": {
    "title": "content here",
    "description": "content here"
  }
}

CRITICAL INSTRUCTIONS:
1. Generate ALL elements in ONE response
2. Ensure each element has DIFFERENT content (no repetition)
3. All content should be coherent and work together as one slide
4. Follow character count requirements strictly
5. Return ONLY valid JSON with no additional text
```

### Response Parsing

```python
def _parse_complete_response(self, llm_response: str, variant_id: str):
    """Parse LLM response containing ALL elements."""

    # Parse JSON response
    try:
        all_elements_data = json.loads(llm_response)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        all_elements_data = self._extract_json_from_response(llm_response)

    # Load variant spec to get element structure
    spec = self.prompt_builder.load_variant_spec(variant_id)

    # Convert to element contents format
    element_contents = []

    for element in spec["elements"]:
        element_id = element["element_id"]
        required_fields = element["required_fields"]

        # Get this element's data from response
        if element_id not in all_elements_data:
            raise ValueError(f"LLM response missing element: {element_id}")

        element_data = all_elements_data[element_id]

        # Validate required fields
        missing_fields = set(required_fields) - set(element_data.keys())
        if missing_fields:
            raise ValueError(f"Element {element_id} missing fields: {missing_fields}")

        # Build element content dictionary
        element_content = {
            "element_id": element_id,
            "element_type": element["element_type"],
            "placeholders": element["placeholders"],
            "generated_content": element_data,
            "character_counts": {
                field: len(str(value))
                for field, value in element_data.items()
            }
        }

        element_contents.append(element_content)

    return element_contents
```

---

## Character Requirement System

### Baseline ± 5% Tolerance

v1.2 uses a **baseline ± 5% tolerance model** for character counts:

```
Character Requirement:
  baseline: 120 characters
  min: baseline - 5% = 114 characters
  max: baseline + 5% = 126 characters

Valid Range: [114, 126]
```

**Why ± 5%?**
- Gives LLM flexibility while maintaining consistency
- Prevents overly rigid prompts
- Ensures visual balance across elements
- Validated against actual platinum templates

### JSON Specification

```json
{
  "element_id": "section_1",
  "element_type": "section_with_bullets",
  "required_fields": ["heading", "bullet_1", "bullet_2", "bullet_3"],
  "character_requirements": {
    "heading": {
      "baseline": 20,
      "min": 19,
      "max": 21
    },
    "bullet_1": {
      "baseline": 120,
      "min": 113,
      "max": 128
    },
    "bullet_2": {
      "baseline": 120,
      "min": 113,
      "max": 128
    },
    "bullet_3": {
      "baseline": 120,
      "min": 113,
      "max": 128
    }
  }
}
```

### Calculation Examples

**Matrix 2×2 Title**:
```
baseline: 30
min: 30 - 5% = 30 - 1.5 = 28.5 → 27 (round down)
max: 30 + 5% = 30 + 1.5 = 31.5 → 32 (round up)
Range: [27, 32]
```

**Matrix 2×2 Description**:
```
baseline: 240
min: 240 - 5% = 240 - 12 = 228
max: 240 + 5% = 240 + 12 = 252
Range: [228, 252]
```

**Single Column Bullet**:
```
baseline: 120
min: 120 - 5% = 120 - 6 = 114 → 113 (adjusted)
max: 120 + 5% = 120 + 6 = 126 → 128 (adjusted)
Range: [113, 128]
```

### Validation

```python
def validate_character_counts(self, element_contents, variant_id):
    """Validate generated content meets character requirements."""
    spec = self.prompt_builder.load_variant_spec(variant_id)
    violations = []

    for i, element in enumerate(spec["elements"]):
        elem_content = element_contents[i]
        char_reqs = element["character_requirements"]
        char_counts = elem_content["character_counts"]

        for field, count in char_counts.items():
            req = char_reqs.get(field, {})
            min_chars = req.get("min", 0)
            max_chars = req.get("max", float('inf'))

            if not (min_chars <= count <= max_chars):
                violations.append({
                    "element_id": elem_content["element_id"],
                    "field": field,
                    "actual_count": count,
                    "required_min": min_chars,
                    "required_max": max_chars
                })

    return {
        "valid": len(violations) == 0,
        "violations": violations
    }
```

**Example Violation**:
```json
{
  "valid": false,
  "violations": [
    {
      "element_id": "box_1",
      "field": "title",
      "actual_count": 45,
      "required_min": 27,
      "required_max": 32
    }
  ]
}
```

---

## Template Structure

### HTML Template Format

Templates are **pure HTML with inline CSS** using `{placeholder}` syntax:

**Example: Matrix 2×2** (`app/templates/matrix/matrix_2x2.html`)

```html
<div style="display: grid;
            grid-template-columns: repeat(2, 1fr);
            grid-template-rows: repeat(2, 1fr);
            gap: 24px;
            padding: 40px;
            height: 100%;
            box-sizing: border-box;">

  <!-- Box 1 (Purple) -->
  <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              border-radius: 16px;
              padding: 32px;
              display: flex;
              flex-direction: column;
              justify-content: center;
              box-shadow: 0 8px 16px rgba(0,0,0,0.1);">

    <h2 style="font-size: 35px;
               font-weight: 700;
               color: white;
               margin: 0 0 16px 0;
               line-height: 1.2;
               text-transform: uppercase;
               letter-spacing: 0.5px;">
      {box_1_title}
    </h2>

    <p style="font-size: 20px;
              line-height: 1.5;
              color: white;
              margin: 0;
              opacity: 0.95;">
      {box_1_description}
    </p>
  </div>

  <!-- Box 2 (Blue) -->
  <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              ...">
    <h2 style="...">{box_2_title}</h2>
    <p style="...">{box_2_description}</p>
  </div>

  <!-- Box 3 (Pink) -->
  <div style="...">
    <h2 style="...">{box_3_title}</h2>
    <p style="...">{box_3_description}</p>
  </div>

  <!-- Box 4 (Orange) -->
  <div style="...">
    <h2 style="...">{box_4_title}</h2>
    <p style="...">{box_4_description}</p>
  </div>

</div>
```

### Template Patterns

**1. Grid Layouts** (Matrix, Grid)
```html
<div style="display: grid; grid-template-columns: ...; gap: ...;">
  <div style="...">
    <h2>{box_1_title}</h2>
    <p>{box_1_description}</p>
  </div>
  ...
</div>
```

**2. Comparison Layouts** (Columns)
```html
<div style="display: flex; gap: ...;">
  <div style="flex: 1;">
    <h3>{column_1_heading}</h3>
    <ul>{column_1_items}</ul>
  </div>
  ...
</div>
```

**3. Sequential Layouts** (Steps)
```html
<div style="display: flex; gap: ...;">
  <div style="...">
    <div class="badge">1</div>
    <h3>{step_1_title}</h3>
    <p>{step_1_paragraph_1}</p>
    <p>{step_1_paragraph_2}</p>
    <p>{step_1_paragraph_3}</p>
  </div>
  ...
</div>
```

**4. Single Column Layouts** (Sections)
```html
<div style="padding: 0; margin: 0;">
  <div style="margin-bottom: 19px;">
    <h3 style="color: #2563eb;">{section_1_heading}</h3>
    <hr style="background: linear-gradient(90deg, #2563eb 0%, transparent 100%);">
    <ul>
      <li>{section_1_bullet_1}</li>
      <li>{section_1_bullet_2}</li>
      <li>{section_1_bullet_3}</li>
    </ul>
  </div>
  ...
</div>
```

### Placeholder Naming Convention

```
Pattern: {element_id}_{field_name}

Examples:
  {box_1_title}              - Element: box_1, Field: title
  {column_2_heading}         - Element: column_2, Field: heading
  {section_3_bullet_4}       - Element: section_3, Field: bullet_4
  {metric_card_number}       - Element: metric_card, Field: number
  {step_1_paragraph_2}       - Element: step_1, Field: paragraph_2

Rules:
  • Must start with letter or underscore
  • Can contain letters, numbers, underscores
  • Case-insensitive matching
  • No hyphens or special characters
```

---

## Variant Specifications

### JSON Structure

**Location**: `app/variant_specs/{slide_type}/{variant_id}.json`

**Example: Matrix 2×2** (`app/variant_specs/matrix/matrix_2x2.json`)

```json
{
  "variant_id": "matrix_2x2",
  "slide_type": "matrix",
  "template_path": "app/templates/matrix/matrix_2x2.html",
  "description": "2×2 matrix layout with 4 equal boxes",
  "elements": [
    {
      "element_id": "box_1",
      "element_type": "text_box",
      "required_fields": ["title", "description"],
      "placeholders": {
        "title": "box_1_title",
        "description": "box_1_description"
      },
      "character_requirements": {
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
    },
    {
      "element_id": "box_2",
      "element_type": "text_box",
      "required_fields": ["title", "description"],
      "placeholders": {
        "title": "box_2_title",
        "description": "box_2_description"
      },
      "character_requirements": {
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
    },
    {
      "element_id": "box_3",
      "element_type": "text_box",
      "required_fields": ["title", "description"],
      "placeholders": {
        "title": "box_3_title",
        "description": "box_3_description"
      },
      "character_requirements": {
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
    },
    {
      "element_id": "box_4",
      "element_type": "text_box",
      "required_fields": ["title", "description"],
      "placeholders": {
        "title": "box_4_title",
        "description": "box_4_description"
      },
      "character_requirements": {
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
  ],
  "layout": {
    "layout_type": "matrix",
    "rows": 2,
    "columns": 2,
    "total_boxes": 4
  }
}
```

### Variant Index

**Location**: `app/variant_specs/variant_index.json`

```json
{
  "total_variants": 34,
  "last_updated": "2025-11-03",
  "slide_types": {
    "matrix": {
      "description": "Matrix layouts with colored boxes",
      "variants": [
        {
          "variant_id": "matrix_2x2",
          "layout": "2×2 matrix with 4 boxes"
        },
        {
          "variant_id": "matrix_2x3",
          "layout": "2×3 matrix with 6 boxes"
        }
      ]
    },
    "grid": {
      "description": "Grid layouts with icons or numbers",
      "variants": [
        {
          "variant_id": "grid_2x3",
          "layout": "2×3 centered grid with icons"
        },
        ...
      ]
    },
    ...
  },
  "variant_lookup": {
    "matrix_2x2": "matrix",
    "matrix_2x3": "matrix",
    "grid_2x3": "grid",
    ...
  }
}
```

---

## API Endpoints

### POST /v1.2/generate

Generate slide content using element-based approach.

**Request**:
```json
{
  "variant_id": "matrix_2x2",
  "slide_spec": {
    "slide_title": "Digital Transformation Framework",
    "slide_purpose": "Present 4 strategic pillars for transformation",
    "key_message": "Transform business across all dimensions",
    "target_points": [
      "Innovation and technology",
      "Customer-centric approach",
      "Data-driven decisions",
      "Agile operations"
    ],
    "tone": "professional",
    "audience": "business stakeholders"
  },
  "presentation_spec": {
    "presentation_title": "2025 Strategic Plan",
    "presentation_type": "Business Strategy",
    "industry": "Technology",
    "company": "TechCorp",
    "current_slide_number": 5,
    "total_slides": 20,
    "prior_slides_summary": "Previous slides covered market analysis and competitive landscape."
  },
  "validate_character_counts": true
}
```

**Response**:
```json
{
  "success": true,
  "html": "<div style='...'><div style='...'>...</div></div>",
  "elements": [
    {
      "element_id": "box_1",
      "element_type": "text_box",
      "placeholders": {
        "title": "box_1_title",
        "description": "box_1_description"
      },
      "generated_content": {
        "title": "Innovation",
        "description": "Adopt cutting-edge technologies to stay ahead of market trends and deliver exceptional value to customers through continuous innovation and improvement."
      },
      "character_counts": {
        "title": 10,
        "description": 148
      }
    },
    ...
  ],
  "metadata": {
    "variant_id": "matrix_2x2",
    "template_path": "app/templates/matrix/matrix_2x2.html",
    "element_count": 4,
    "generation_mode": "single_call"
  },
  "validation": {
    "valid": true,
    "violations": []
  },
  "variant_id": "matrix_2x2",
  "template_path": "app/templates/matrix/matrix_2x2.html"
}
```

### GET /v1.2/variants

List all available variants organized by slide type.

**Response**:
```json
{
  "total_variants": 34,
  "slide_types": {
    "matrix": [
      {
        "variant_id": "matrix_2x2",
        "slide_type": "matrix",
        "description": "2×2 matrix layout with 4 equal boxes",
        "layout": "2×2 matrix with 4 boxes"
      },
      ...
    ],
    "grid": [...],
    ...
  }
}
```

### GET /v1.2/variant/{variant_id}

Get detailed information about a specific variant.

**Example**: `GET /v1.2/variant/matrix_2x2`

**Response**:
```json
{
  "variant_id": "matrix_2x2",
  "slide_type": "matrix",
  "description": "2×2 matrix layout with 4 equal boxes",
  "template_path": "app/templates/matrix/matrix_2x2.html",
  "layout": {
    "layout_type": "matrix",
    "rows": 2,
    "columns": 2,
    "total_boxes": 4
  },
  "element_count": 4,
  "elements": [
    {
      "element_id": "box_1",
      "element_type": "text_box",
      "required_fields": ["title", "description"],
      "placeholders": {...},
      "character_requirements": {...}
    },
    ...
  ]
}
```

---

## LLM Integration

### Vertex AI with Application Default Credentials

**File**: `app/services/llm_client.py`

**Provider**: Google Vertex AI (v3.3 security update)

**Authentication**:
- **Local Development**: Application Default Credentials (ADC)
  - Run: `gcloud auth application-default login`
  - Credentials stored at: `~/.config/gcloud/application_default_credentials.json`

- **Railway/Production**: Service Account JSON
  - Environment variable: `GCP_SERVICE_ACCOUNT_JSON`
  - Contains service account credentials as JSON string

**Configuration**:
```python
# Environment Variables
GCP_PROJECT_ID=deckster-xyz
GCP_LOCATION=us-central1
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash-exp
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=60000
```

**Initialization**:
```python
class GeminiClient(BaseLLMClient):
    def __init__(self, model="gemini-2.0-flash-exp", **kwargs):
        super().__init__(model, **kwargs)

        # Import Vertex AI dependencies
        import vertexai
        from google.oauth2 import service_account
        from vertexai.preview.generative_models import GenerativeModel

        # Get configuration
        service_account_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
        project_id = os.getenv("GCP_PROJECT_ID")
        location = os.getenv("GCP_LOCATION", "us-central1")

        if not project_id:
            raise ValueError("GCP_PROJECT_ID environment variable required")

        # Initialize Vertex AI
        if service_account_json:
            # Railway/Production: Use service account JSON
            credentials_dict = json.loads(service_account_json)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            vertexai.init(project=project_id, location=location, credentials=credentials)
        else:
            # Local: Use Application Default Credentials
            vertexai.init(project=project_id, location=location)

        # Create Gemini model instance
        self.client = GenerativeModel(self.model)

    async def generate(self, prompt: str) -> LLMResponse:
        """Generate content using Gemini via Vertex AI."""
        from vertexai.preview.generative_models import GenerationConfig

        generation_config = GenerationConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_tokens
        )

        response = self.client.generate_content(
            prompt,
            generation_config=generation_config
        )

        # Extract content and token usage
        content = response.text
        prompt_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
        completion_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)

        return LLMResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            model=self.model,
            provider="gemini-vertex",
            latency_ms=latency_ms
        )
```

**LLM Service Wrapper**:
```python
# app/services/__init__.py

def create_llm_callable() -> Callable[[str], str]:
    """
    Create a callable LLM service for ElementBasedContentGenerator.

    This wraps the async LLM client in a synchronous callable that
    returns just the content string (not full LLMResponse).
    """
    llm_client = get_llm_client()

    def llm_callable(prompt: str) -> str:
        """Synchronous wrapper for async LLM generation."""
        import asyncio

        # Run async generation in sync context
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(llm_client.generate(prompt))

        return response.content

    return llm_callable
```

**Usage in Generator**:
```python
# app/api/v1_2_routes.py

def get_generator() -> ElementBasedContentGenerator:
    """Dependency to get generator with LLM service."""
    llm_callable = create_llm_callable()

    return ElementBasedContentGenerator(
        llm_service=llm_callable,
        variant_specs_dir="app/variant_specs",
        templates_dir="app/templates"
    )

@router.post("/generate")
async def generate_slide_content(
    request: V1_2_GenerationRequest,
    generator: ElementBasedContentGenerator = Depends(get_generator)
):
    """Generate slide content using v1.2 element-based approach."""
    result = generator.generate_slide_content(
        variant_id=request.variant_id,
        slide_spec=request.slide_spec.model_dump(),
        presentation_spec=request.presentation_spec.model_dump() if request.presentation_spec else None
    )
    return V1_2_GenerationResponse(**result)
```

---

## Summary

Text Service v1.2 is a **deterministic template assembly service** that:

1. **Decomposes slides into elements** with strict character requirements
2. **Uses ONE LLM call** to generate all elements coherently
3. **Assembles content into HTML templates** via placeholder replacement
4. **Validates character counts** against baseline ± 5% ranges
5. **Integrates with Vertex AI** using Application Default Credentials
6. **Serves 34 platinum-approved templates** across 10 slide types

**Key Innovation**: Single-call architecture ensures content coherence across elements while maintaining deterministic assembly through JSON-driven specifications and pure HTML templates.

**Service Boundaries**: Text Service v1.2 generates rich HTML content only. Layout Builder v7.5 handles positioning, deck composition, and final presentation assembly using the L25 layout format.

---

**End of Architecture Documentation**
