# Text Service v1.2: Deterministic Assembly Architecture
## Streamlined Implementation Plan

**Version**: 1.2.0
**Date**: January 2025
**Status**: Planning Complete - Ready for Implementation

---

## Executive Summary

Transform content slide generation (L25) from **"LLM generates full HTML"** to **"Extract elements → Generate content → Deterministic assembly"**. Hero slides (L29) remain unchanged as they work well with the current approach.

### Core Philosophy

**Current v1.1 Approach:**
```
Request → Build full prompt with golden example → LLM generates complete HTML → Return
```

**New v1.2 Approach:**
```
Request (slide_type + variant) → Load golden template → Extract element specs →
Generate each element → Assemble → Return
```

### Key Benefits

✅ **Deterministic HTML**: Guaranteed consistency (golden templates preserved exactly)
✅ **Precise Control**: Character counts within ±5% of baseline
✅ **Better Quality**: LLM focuses on content, not structure
✅ **Maintainable**: Templates separate from generation logic
✅ **Debuggable**: Inspect individual elements independently

---

## Architecture Overview

### Request Flow

1. **Director requests**: `slide_type='matrix'` + `variant='2x2'`
2. **System loads**: Golden template + element specifications
3. **System generates**: Content for each element (parallel)
4. **System assembles**: Elements into template
5. **System returns**: Complete HTML

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Director Agent v3.4                       │
│            (requests: slide_type + variant)                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Text Service v1.2 API Endpoint                  │
│              POST /api/v1/generate/content/v2                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           ElementBasedContentGenerator                       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Load Variant│  │Build Prompts │  │   Assemble   │     │
│  │     Spec     │→ │  & Generate  │→ │   Template   │     │
│  │   (JSON)     │  │   Elements   │  │    (HTML)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Golden Template Extraction & Storage

**Duration**: Day 1-2
**Objective**: Extract golden HTML templates from v1.1 prompts and store as standalone files with placeholders.

### 1.1 Directory Structure

Create template directory:

```
agents/text_table_builder/v1.2/app/templates/
├── matrix/
│   ├── matrix_2x2.html
│   └── matrix_2x3.html
├── grid/
│   ├── grid_2x3.html
│   └── grid_3x3.html
├── multilateral_comparison/
│   ├── comparison_2col.html
│   ├── comparison_3col.html
│   └── comparison_4col.html
├── sequential/
│   ├── sequential_3col.html
│   ├── sequential_4col.html
│   └── sequential_5col.html
├── asymmetric/
│   ├── asymmetric_8_4.html
│   └── asymmetric_4_8.html
├── hybrid/
│   ├── hybrid_top_2x2.html
│   └── hybrid_left_2x2.html
├── metrics/
│   ├── metrics_3col.html
│   └── metrics_4col.html
├── single_column/
│   └── single_column.html
├── impact_quote/
│   └── impact_quote.html
└── table/
    └── table_multi_col.html
```

### 1.2 Template Extraction Process

**Manual extraction** (not automated) ensures golden templates are preserved exactly:

For each content slide type in v1.1:

1. **Open v1.1 prompt file**
   - Example: `/agents/text_table_builder/v1.1/app/prompts/content/matrix.md`

2. **Locate "Golden Example" section**
   - Find the HTML code block under `## ✨ Golden Example`

3. **Copy HTML exactly**
   - Preserve ALL inline styles
   - Keep exact structure
   - Maintain all formatting

4. **Replace content with placeholders**
   - **Titles**: Replace with `{box_1_title}`, `{box_2_title}`, etc.
   - **Descriptions**: Replace with `{box_1_description}`, `{box_2_description}`, etc.
   - **Lists**: Replace with `{section_1_items}`, etc.
   - **Numbers**: Replace with `{metric_1_value}`, etc.

5. **Save as template HTML file**
   - Example: `app/templates/matrix/matrix_2x2.html`

### 1.3 Placeholder Naming Conventions

**Standard conventions** for consistency:

```html
<!-- Matrices and Grids -->
{box_1_title}           → Box/quadrant heading
{box_1_description}     → Box/quadrant content
{box_2_title}
{box_2_description}
...

<!-- Sequential/Steps -->
{step_1_title}          → Step heading
{step_1_description}    → Step content
{step_2_title}
{step_2_description}
...

<!-- Columns -->
{column_1_heading}      → Column header
{column_1_items}        → Column content (may be bullets)
{column_2_heading}
{column_2_items}
...

<!-- Metrics -->
{metric_1_value}        → Large number/percentage
{metric_1_label}        → Metric description
{metric_2_value}
{metric_2_label}
...

<!-- Single Column -->
{main_content}          → Primary content area

<!-- Impact Quote -->
{quote_text}            → Main quote
{attribution}           → Author/source
```

### 1.4 Example: Matrix 2x2 Template

**Source**: v1.1 matrix.md golden example
**Output**: `app/templates/matrix/matrix_2x2.html`

```html
<div style="display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 16px;
            padding: 0 40px 40px 0;
            height: 100%;
            background: white;">

  <!-- Top Left: Purple -->
  <div style="padding: 40px;
              border-radius: 12px;
              background: #6366f1;
              display: flex;
              flex-direction: column;
              justify-content: flex-start;
              align-items: flex-start;
              text-align: left;
              box-shadow: 0 8px 24px rgba(99, 102, 241, 0.2);">

    <h3 style="font-size: 35px;
               font-weight: 700;
               color: white;
               margin: 0 0 20px 0;
               text-transform: uppercase;
               letter-spacing: 1px;
               text-shadow: 0 2px 8px rgba(0,0,0,0.2);">
      {box_1_title}
    </h3>

    <p style="font-size: 21px;
              font-weight: 400;
              color: rgba(255,255,255,0.95);
              line-height: 1.36;
              margin: 0;">
      {box_1_description}
    </p>

  </div>

  <!-- Repeat for boxes 2, 3, 4 with different colors -->
  ...

</div>
```

### 1.5 Validation Checklist

For each template:

- [ ] All inline styles preserved exactly from golden example
- [ ] Placeholders use consistent naming convention
- [ ] No duplicate placeholder names
- [ ] HTML structure identical to v1.1 golden example
- [ ] File saved in correct directory
- [ ] Template renders correctly (visual check)

**Deliverable**: 20-25 template HTML files ready for assembly

---

## Phase 2: Element Specification & Analysis

**Duration**: Day 2-3
**Objective**: Manually analyze each template variant and document required elements with character counts.

### 2.1 Variant Specification Structure

Create JSON specification for each variant:

**Directory**: `config/variants/`

**Files**: One JSON per variant (e.g., `matrix_2x2.json`)

### 2.2 Specification Schema

```json
{
  "variant_id": "matrix_2x2",
  "slide_type": "matrix",
  "variant_name": "2x2",
  "description": "2x2 matrix for strategic frameworks (SWOT, priority matrix, BCG matrix)",
  "layout_id": "L25",
  "template_file": "matrix/matrix_2x2.html",

  "elements": [
    {
      "element_id": "box_1_title",
      "element_type": "heading",
      "purpose": "Top-left quadrant heading (e.g., 'Do First', 'Strengths', 'Stars')",
      "placeholder": "{box_1_title}",
      "char_count": {
        "golden": 12,
        "baseline": 11,
        "min": 10,
        "max": 12
      },
      "style_guidance": "Concise label, 1-3 words, uppercase appropriate for matrix context"
    },
    {
      "element_id": "box_1_description",
      "element_type": "paragraph",
      "purpose": "Top-left quadrant detailed description explaining the concept",
      "placeholder": "{box_1_description}",
      "char_count": {
        "golden": 389,
        "baseline": 370,
        "min": 351,
        "max": 389
      },
      "style_guidance": "Professional explanation with multiple sentences, specific examples"
    }
    // ... 6 more elements (4 titles + 4 descriptions total)
  ],

  "total_elements": 8,
  "total_word_count_target": "357-408 words"
}
```

### 2.3 Character Count Calculation

**Formula**:
```
golden = actual character count from v1.1 golden example
baseline = golden × 0.95  (5% reduction)
min = baseline × 0.95      (5% below baseline)
max = baseline × 1.05      (5% above baseline)
```

**Example**:
```
Golden example title: "Do First" = 8 characters
baseline = 8 × 0.95 = 7.6 → 8 (rounded)
min = 8 × 0.95 = 7.6 → 7
max = 8 × 1.05 = 8.4 → 9

Result: min=7, baseline=8, max=9, golden=8
```

### 2.4 Element Analysis Process

For each golden template:

1. **Count placeholders**
   - Identify all `{placeholder}` instances in template
   - List unique placeholders

2. **Extract original content**
   - Go back to v1.1 golden example
   - Copy the actual content that was in each placeholder position

3. **Count characters**
   - Use `len(content.strip())` for each element
   - Apply formula to calculate baseline, min, max

4. **Document purpose**
   - What is this element for?
   - What type of content should it contain?
   - Any specific constraints or requirements?

5. **Add style guidance**
   - Tone (professional, concise, technical, etc.)
   - Format (sentences, bullet points, single word, etc.)
   - Any special instructions

### 2.5 Example: Matrix 2x2 Specification

**File**: `config/variants/matrix_2x2.json`

```json
{
  "variant_id": "matrix_2x2",
  "slide_type": "matrix",
  "variant_name": "2x2",
  "description": "Classic 2x2 strategic matrix framework (4 quadrants)",
  "layout_id": "L25",
  "template_file": "matrix/matrix_2x2.html",

  "elements": [
    {
      "element_id": "box_1_title",
      "element_type": "heading",
      "purpose": "Top-left quadrant heading",
      "placeholder": "{box_1_title}",
      "char_count": {"golden": 8, "baseline": 8, "min": 7, "max": 9},
      "style_guidance": "1-2 words, uppercase, action-oriented or category label"
    },
    {
      "element_id": "box_1_description",
      "element_type": "paragraph",
      "purpose": "Top-left quadrant detailed explanation",
      "placeholder": "{box_1_description}",
      "char_count": {"golden": 389, "baseline": 370, "min": 351, "max": 389},
      "style_guidance": "2-4 sentences explaining concept, include specific examples"
    },
    {
      "element_id": "box_2_title",
      "element_type": "heading",
      "purpose": "Top-right quadrant heading",
      "placeholder": "{box_2_title}",
      "char_count": {"golden": 8, "baseline": 8, "min": 7, "max": 9},
      "style_guidance": "1-2 words, uppercase, action-oriented or category label"
    },
    {
      "element_id": "box_2_description",
      "element_type": "paragraph",
      "purpose": "Top-right quadrant detailed explanation",
      "placeholder": "{box_2_description}",
      "char_count": {"golden": 387, "baseline": 368, "min": 349, "max": 387},
      "style_guidance": "2-4 sentences explaining concept, include specific examples"
    },
    {
      "element_id": "box_3_title",
      "element_type": "heading",
      "purpose": "Bottom-left quadrant heading",
      "placeholder": "{box_3_title}",
      "char_count": {"golden": 8, "baseline": 8, "min": 7, "max": 9},
      "style_guidance": "1-2 words, uppercase, action-oriented or category label"
    },
    {
      "element_id": "box_3_description",
      "element_type": "paragraph",
      "purpose": "Bottom-left quadrant detailed explanation",
      "placeholder": "{box_3_description}",
      "char_count": {"golden": 385, "baseline": 366, "min": 347, "max": 385},
      "style_guidance": "2-4 sentences explaining concept, include specific examples"
    },
    {
      "element_id": "box_4_title",
      "element_type": "heading",
      "purpose": "Bottom-right quadrant heading",
      "placeholder": "{box_4_title}",
      "char_count": {"golden": 9, "baseline": 9, "min": 8, "max": 10},
      "style_guidance": "1-2 words, uppercase, action-oriented or category label"
    },
    {
      "element_id": "box_4_description",
      "element_type": "paragraph",
      "purpose": "Bottom-right quadrant detailed explanation",
      "placeholder": "{box_4_description}",
      "char_count": {"golden": 391, "baseline": 371, "min": 352, "max": 390},
      "style_guidance": "2-4 sentences explaining concept, include specific examples"
    }
  ],

  "total_elements": 8,
  "total_word_count_target": "357-408 words",

  "metadata": {
    "common_use_cases": ["SWOT Analysis", "Priority Matrix (Eisenhower)", "BCG Matrix", "Risk Matrix"],
    "model": "gemini-1.5-pro",
    "complexity": "medium"
  }
}
```

### 2.6 Master Variant Index

**File**: `config/variants/index.json`

Maps slide types to available variants:

```json
{
  "version": "1.2.0",
  "content_slide_types": {
    "matrix": {
      "variants": ["2x2", "2x3"],
      "description": "Strategic framework matrices",
      "model": "gemini-1.5-pro"
    },
    "grid": {
      "variants": ["2x3", "3x3"],
      "description": "Feature grids and capability showcases",
      "model": "gemini-2.0-flash-exp"
    },
    "multilateral_comparison": {
      "variants": ["2col", "3col", "4col"],
      "description": "Side-by-side comparisons",
      "model": "gemini-2.0-flash-exp"
    },
    "sequential": {
      "variants": ["3col", "4col", "5col"],
      "description": "Step-by-step processes",
      "model": "gemini-2.0-flash-exp"
    },
    "asymmetric": {
      "variants": ["8_4", "4_8"],
      "description": "Asymmetric layouts with main and sidebar",
      "model": "gemini-2.0-flash-exp"
    },
    "hybrid": {
      "variants": ["top_2x2", "left_2x2"],
      "description": "Hybrid layouts combining grid and text",
      "model": "gemini-1.5-pro"
    },
    "metrics": {
      "variants": ["3col", "4col"],
      "description": "Metric cards with large numbers",
      "model": "gemini-2.0-flash-exp"
    },
    "single_column": {
      "variants": ["default"],
      "description": "Single column rich text",
      "model": "gemini-2.0-flash-exp"
    },
    "impact_quote": {
      "variants": ["default"],
      "description": "Large quotes or key messages",
      "model": "gemini-2.0-flash-exp"
    },
    "table": {
      "variants": ["multi_col"],
      "description": "Data tables",
      "model": "gemini-1.5-pro"
    }
  },
  "total_variants": 20
}
```

**Deliverable**: 20-25 variant JSON specifications + master index

---

## Phase 3: Dynamic Prompt Construction System

**Duration**: Day 3-4
**Objective**: Build a prompt builder that dynamically constructs focused prompts for each element.

### 3.1 Prompt Builder Architecture

**File**: `app/core/prompt_builder.py`

```python
"""
Element Prompt Builder
======================

Constructs focused prompts for individual element generation.
"""

from typing import Dict, Any, Optional
from app.models.variant_spec import ElementSpec


class ElementPromptBuilder:
    """
    Builds prompts for individual elements.

    Philosophy:
    - Focus on ONE element at a time
    - Provide slide context for coherence
    - Set clear character constraints
    - Give style guidance
    - Include previous slide context for flow
    """

    def build_element_prompt(
        self,
        element_spec: ElementSpec,
        slide_context: Dict[str, Any],
        previous_context: Optional[str] = None,
        attempt: int = 1,
        char_count_feedback: Optional[str] = None
    ) -> str:
        """
        Build focused prompt for single element.

        Args:
            element_spec: Element specification from variant JSON
            slide_context: Slide-level context (title, narrative, key_points)
            previous_context: Summary of previous slides
            attempt: Current attempt number (for retry guidance)
            char_count_feedback: Feedback if retrying due to char count

        Returns:
            Complete prompt string ready for LLM
        """
        prompt_parts = []

        # 1. Slide Overview
        prompt_parts.append(self._build_slide_overview(slide_context))

        # 2. Element Purpose
        prompt_parts.append(self._build_element_purpose(element_spec))

        # 3. Character Constraints
        prompt_parts.append(self._build_constraints(element_spec, char_count_feedback))

        # 4. Style Guidance
        prompt_parts.append(self._build_style_guidance(element_spec))

        # 5. Previous Context (if available)
        if previous_context:
            prompt_parts.append(self._build_previous_context(previous_context))

        # 6. Output Instructions
        prompt_parts.append(self._build_output_instructions(element_spec))

        return "\n\n".join(prompt_parts)

    def _build_slide_overview(self, context: Dict[str, Any]) -> str:
        """Build slide context section."""
        return f"""# SLIDE CONTEXT
You are generating content for a presentation slide.

**Slide Title**: {context.get('title', 'N/A')}
**Narrative**: {context.get('narrative', 'N/A')}
**Key Points**: {', '.join(context.get('key_points', []))}
**Audience**: {context.get('audience', 'General business audience')}"""

    def _build_element_purpose(self, spec: ElementSpec) -> str:
        """Build element purpose section."""
        return f"""# THIS ELEMENT
**Element**: {spec.element_id}
**Type**: {spec.element_type}
**Purpose**: {spec.purpose}

This element is part of a larger slide structure. Your content will be assembled with other elements to create a cohesive slide."""

    def _build_constraints(
        self,
        spec: ElementSpec,
        feedback: Optional[str] = None
    ) -> str:
        """Build constraints section."""
        base = f"""# REQUIREMENTS
**Character Count**: {spec.char_count.min}-{spec.char_count.max} characters (target: {spec.char_count.baseline})
**Format**: Plain text only (NO HTML tags, NO markdown formatting)"""

        if feedback:
            base += f"\n\n⚠️ **ADJUSTMENT NEEDED**: {feedback}"

        return base

    def _build_style_guidance(self, spec: ElementSpec) -> str:
        """Build style guidance section."""
        return f"""# STYLE GUIDANCE
{spec.style_guidance}

Write in a professional, clear, and engaging manner appropriate for business presentations."""

    def _build_previous_context(self, context: str) -> str:
        """Build previous slides context section."""
        return f"""# PREVIOUS SLIDES
To maintain narrative flow, here's what came before:

{context}

Ensure your content flows naturally from this context."""

    def _build_output_instructions(self, spec: ElementSpec) -> str:
        """Build output instructions section."""
        return f"""# OUTPUT
Generate ONLY the text content for this {spec.element_type}.

- Must be {spec.char_count.min}-{spec.char_count.max} characters
- Plain text only (NO HTML, NO markdown)
- Professional tone
- Directly relevant to slide context

Your content:"""
```

### 3.2 Context Builder

**File**: `app/core/context_builder.py`

```python
"""
Context Builder
===============

Builds slide-level context for element generation.
"""

from typing import Dict, Any, List, Optional


class ContextBuilder:
    """
    Builds context for element generation.

    Responsibilities:
    - Extract relevant slide context
    - Format previous slide summaries
    - Provide audience/theme context
    """

    def build_slide_context(
        self,
        slide_title: str,
        narrative: str,
        key_points: List[str],
        audience: Optional[str] = None,
        theme: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build slide context dictionary.

        Args:
            slide_title: Main slide title
            narrative: Slide narrative/description
            key_points: List of key points to cover
            audience: Target audience
            theme: Presentation theme

        Returns:
            Formatted context dictionary
        """
        return {
            "title": slide_title,
            "narrative": narrative,
            "key_points": key_points,
            "audience": audience or "General business audience",
            "theme": theme or "professional"
        }

    def format_previous_context(
        self,
        previous_slides: List[Dict[str, Any]],
        max_slides: int = 3
    ) -> str:
        """
        Format previous slides context for prompt.

        Args:
            previous_slides: List of previous slide summaries
            max_slides: Maximum number of slides to include

        Returns:
            Formatted context string
        """
        if not previous_slides:
            return "This is the first slide in the presentation."

        # Take last N slides
        recent_slides = previous_slides[-max_slides:]

        context_lines = []
        for slide in recent_slides:
            context_lines.append(
                f"Slide {slide.get('slide_number')}: {slide.get('title')} - {slide.get('summary', 'N/A')}"
            )

        return "\n".join(context_lines)
```

### 3.3 Retry Logic with Feedback

When character count validation fails, provide specific feedback:

```python
def _get_char_count_feedback(
    current_count: int,
    min_count: int,
    max_count: int,
    baseline: int
) -> str:
    """Generate feedback for character count adjustment."""

    if current_count < min_count:
        shortage = min_count - current_count
        return (
            f"Content is too short by {shortage} characters. "
            f"Add more specific details, examples, or expand key concepts."
        )
    elif current_count > max_count:
        excess = current_count - max_count
        return (
            f"Content is too long by {excess} characters. "
            f"Be more concise, remove redundancy, focus on essential points only."
        )
    else:
        return ""
```

**Deliverable**: Prompt construction system with clear, focused prompts

---

## Phase 4: Template Assembly Service

**Duration**: Day 4-5
**Objective**: Create simple, reliable HTML assembly service.

### 4.1 Template Assembler

**File**: `app/core/template_assembler.py`

```python
"""
Template Assembler
==================

Loads HTML templates and assembles them with generated content.
"""

import re
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class TemplateAssembler:
    """
    Assembles HTML templates with generated element content.

    Philosophy:
    - Simple string replacement (fast, reliable)
    - Template caching (avoid repeated file I/O)
    - Clear validation (catch missing elements early)
    """

    def __init__(self, templates_dir: Path):
        """
        Initialize assembler.

        Args:
            templates_dir: Path to templates directory
        """
        self.templates_dir = Path(templates_dir)
        self._cache: Dict[str, str] = {}

        if not self.templates_dir.exists():
            raise FileNotFoundError(f"Templates directory not found: {self.templates_dir}")

    def assemble(
        self,
        template_file: str,
        elements: Dict[str, str]
    ) -> str:
        """
        Assemble template with element content.

        Args:
            template_file: Template filename (e.g., 'matrix/matrix_2x2.html')
            elements: Dict mapping element_id → generated_content

        Returns:
            Complete HTML with all elements inserted

        Raises:
            FileNotFoundError: Template doesn't exist
            ValueError: Missing element content or placeholders remain
        """
        # Load template
        template = self._load_template(template_file)

        # Replace all placeholders
        assembled = template
        replaced_count = 0

        for element_id, content in elements.items():
            placeholder = f"{{{element_id}}}"

            if placeholder in assembled:
                assembled = assembled.replace(placeholder, content)
                replaced_count += 1
            else:
                logger.warning(f"Placeholder not found in template: {placeholder}")

        logger.info(f"Replaced {replaced_count}/{len(elements)} placeholders")

        # Validate no placeholders remain
        remaining = re.findall(r'\{([^}]+)\}', assembled)
        if remaining:
            logger.error(f"Unfilled placeholders: {remaining}")
            raise ValueError(
                f"Template assembly incomplete. "
                f"Missing content for: {', '.join(remaining)}"
            )

        return assembled

    def _load_template(self, template_file: str) -> str:
        """
        Load template from file with caching.

        Args:
            template_file: Template filename relative to templates_dir

        Returns:
            Template HTML content

        Raises:
            FileNotFoundError: Template file doesn't exist
        """
        # Check cache
        if template_file in self._cache:
            logger.debug(f"Template cache hit: {template_file}")
            return self._cache[template_file]

        # Load from file
        template_path = self.templates_dir / template_file

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # Cache it
        self._cache[template_file] = template_content

        logger.info(f"Loaded template: {template_file} ({len(template_content)} chars)")

        return template_content

    def validate_template(self, template_file: str) -> Dict[str, Any]:
        """
        Validate template structure.

        Checks:
        - Template file exists
        - Placeholders follow naming convention
        - No duplicate placeholders

        Args:
            template_file: Template filename

        Returns:
            Validation result dictionary
        """
        try:
            template = self._load_template(template_file)
        except FileNotFoundError as e:
            return {
                "valid": False,
                "error": str(e),
                "placeholders": []
            }

        # Extract all placeholders
        placeholders = re.findall(r'\{([^}]+)\}', template)

        # Check for duplicates
        unique_placeholders = set(placeholders)
        duplicates = [p for p in unique_placeholders if placeholders.count(p) > 1]

        validation = {
            "valid": len(duplicates) == 0,
            "template_file": template_file,
            "placeholders": list(unique_placeholders),
            "placeholder_count": len(unique_placeholders),
            "total_occurrences": len(placeholders),
            "duplicates": duplicates if duplicates else None
        }

        if duplicates:
            validation["error"] = f"Duplicate placeholders found: {duplicates}"

        return validation

    def clear_cache(self):
        """Clear template cache (useful for development/testing)."""
        self._cache.clear()
        logger.info("Template cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cached_templates": len(self._cache),
            "templates": list(self._cache.keys())
        }
```

### 4.2 Assembly Validation

Ensure assembled HTML is correct:

1. **All placeholders replaced**: No `{...}` patterns remain
2. **HTML structure intact**: Original structure preserved
3. **Inline styles preserved**: All styles from golden template present
4. **No truncation**: Full content assembled

**Deliverable**: Reliable assembly service with caching and validation

---

## Phase 5: Element-Based Content Generator

**Duration**: Day 5-6
**Objective**: Create orchestrator that generates elements and assembles templates.

### 5.1 Generator Architecture

**File**: `app/core/generators_v2.py`

```python
"""
Element-Based Content Generator (v1.2)
=======================================

Orchestrates element generation and template assembly.
"""

import time
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Tuple

from app.models.variant_spec import VariantElementSpec, ElementSpec
from app.models.requests import ContentGenerationRequest
from app.models.responses import ContentGenerationResponse
from app.core.llm_client import get_llm_client, BaseLLMClient
from app.core.template_assembler import TemplateAssembler
from app.core.prompt_builder import ElementPromptBuilder
from app.core.context_builder import ContextBuilder
from app.core.session_manager import get_session_manager, SessionManager

logger = logging.getLogger(__name__)


class ElementBasedContentGenerator:
    """
    v1.2 Generator: Element extraction → generation → assembly.

    Process:
    1. Load variant specification (from JSON)
    2. Build slide context
    3. Generate all elements in parallel
    4. Validate character counts (with retry)
    5. Assemble into template
    6. Return complete HTML
    """

    def __init__(
        self,
        llm_client: BaseLLMClient = None,
        session_manager: SessionManager = None,
        variants_dir: Path = None,
        templates_dir: Path = None
    ):
        """
        Initialize generator.

        Args:
            llm_client: LLM client for generation
            session_manager: Session manager for context
            variants_dir: Directory with variant JSON specs
            templates_dir: Directory with HTML templates
        """
        self.llm_client = llm_client or get_llm_client()
        self.session_manager = session_manager or get_session_manager()

        # Default paths
        if variants_dir is None:
            base_dir = Path(__file__).parent.parent.parent
            variants_dir = base_dir / "config" / "variants"
        if templates_dir is None:
            base_dir = Path(__file__).parent.parent.parent
            templates_dir = base_dir / "app" / "templates"

        self.variants_dir = Path(variants_dir)
        self.templates_dir = Path(templates_dir)

        # Initialize components
        self.assembler = TemplateAssembler(self.templates_dir)
        self.prompt_builder = ElementPromptBuilder()
        self.context_builder = ContextBuilder()

        # Cache for variant specs
        self._variant_cache: Dict[str, VariantElementSpec] = {}

    async def generate(
        self,
        request: ContentGenerationRequest
    ) -> ContentGenerationResponse:
        """
        Generate content using element-based approach.

        Args:
            request: Content generation request

        Returns:
            ContentGenerationResponse with assembled HTML
        """
        start_time = time.time()

        try:
            # 1. Load variant specification
            variant_id = self._get_variant_id(request.slide_type, request.variant)
            variant_spec = self._load_variant_spec(variant_id)

            logger.info(
                f"Generating {variant_id} for slide {request.slide_id} "
                f"({len(variant_spec.elements)} elements)"
            )

            # 2. Build slide context
            slide_context = self.context_builder.build_slide_context(
                slide_title=request.slide_context.get('title'),
                narrative=request.slide_context.get('narrative'),
                key_points=request.slide_context.get('key_points', []),
                audience=request.slide_context.get('audience'),
                theme=request.slide_context.get('theme')
            )

            # 3. Get previous slides context
            previous_context = None
            if request.presentation_id:
                previous_slides = await self._get_previous_slides(request.presentation_id)
                previous_context = self.context_builder.format_previous_context(previous_slides)

            # 4. Generate all elements (in parallel)
            generated_elements, element_metadata = await self._generate_all_elements(
                variant_spec=variant_spec,
                slide_context=slide_context,
                previous_context=previous_context
            )

            # 5. Assemble template
            html_content = self.assembler.assemble(
                template_file=variant_spec.template_file,
                elements=generated_elements
            )

            # 6. Calculate metrics
            generation_time = time.time() - start_time

            # 7. Build response
            response = ContentGenerationResponse(
                slide_id=request.slide_id,
                variant_id=variant_id,
                html_content=html_content,
                elements=generated_elements,
                metadata={
                    "generation_time_ms": round(generation_time * 1000, 2),
                    "elements_generated": len(generated_elements),
                    "element_metadata": element_metadata,
                    "variant_spec": variant_spec.variant_name,
                    "template_file": variant_spec.template_file,
                    "total_word_count": self._count_words(html_content),
                    "model_used": self.llm_client.model
                }
            )

            logger.info(
                f"✓ Generated {variant_id} in {generation_time:.2f}s "
                f"({len(generated_elements)} elements)"
            )

            return response

        except Exception as e:
            logger.error(f"✗ Error generating content for {request.slide_id}: {e}")
            raise

    async def _generate_all_elements(
        self,
        variant_spec: VariantElementSpec,
        slide_context: Dict[str, Any],
        previous_context: str
    ) -> Tuple[Dict[str, str], Dict[str, Any]]:
        """
        Generate content for all elements in parallel.

        Args:
            variant_spec: Variant specification
            slide_context: Slide context
            previous_context: Previous slides summary

        Returns:
            Tuple of (generated_elements, element_metadata)
        """
        # Generate all elements in parallel
        tasks = [
            self._generate_element(
                element_spec=element_spec,
                slide_context=slide_context,
                previous_context=previous_context
            )
            for element_spec in variant_spec.elements
        ]

        results = await asyncio.gather(*tasks)

        # Unpack results
        generated_elements = {}
        element_metadata = {}

        for element_spec, (content, metadata) in zip(variant_spec.elements, results):
            generated_elements[element_spec.element_id] = content
            element_metadata[element_spec.element_id] = metadata

        return generated_elements, element_metadata

    async def _generate_element(
        self,
        element_spec: ElementSpec,
        slide_context: Dict[str, Any],
        previous_context: str,
        max_retries: int = 2
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate content for a single element with retry logic.

        Args:
            element_spec: Element specification
            slide_context: Slide context
            previous_context: Previous slides
            max_retries: Max retry attempts

        Returns:
            Tuple of (content, metadata)
        """
        attempt = 0
        char_count_feedback = None

        while attempt <= max_retries:
            # Build prompt
            prompt = self.prompt_builder.build_element_prompt(
                element_spec=element_spec,
                slide_context=slide_context,
                previous_context=previous_context,
                attempt=attempt + 1,
                char_count_feedback=char_count_feedback
            )

            # Generate content
            content = await self.llm_client.generate(prompt)
            content = content.strip()

            # Validate character count
            char_count = len(content)

            if element_spec.char_count.min <= char_count <= element_spec.char_count.max:
                # Success!
                metadata = {
                    "char_count": char_count,
                    "baseline": element_spec.char_count.baseline,
                    "min": element_spec.char_count.min,
                    "max": element_spec.char_count.max,
                    "valid": True,
                    "attempts": attempt + 1
                }
                return content, metadata

            # Failed validation - prepare for retry
            attempt += 1
            if attempt <= max_retries:
                if char_count < element_spec.char_count.min:
                    shortage = element_spec.char_count.min - char_count
                    char_count_feedback = (
                        f"Content is too short by {shortage} characters. "
                        f"Add more specific details or examples."
                    )
                else:
                    excess = char_count - element_spec.char_count.max
                    char_count_feedback = (
                        f"Content is too long by {excess} characters. "
                        f"Be more concise, focus on key points only."
                    )

                logger.warning(
                    f"Element {element_spec.element_id}: char count {char_count} "
                    f"out of range [{element_spec.char_count.min}-{element_spec.char_count.max}]. "
                    f"Retrying ({attempt}/{max_retries})..."
                )

        # Max retries exceeded - return with warning
        logger.warning(
            f"Element {element_spec.element_id} failed validation after {max_retries} retries. "
            f"Using content anyway (char_count: {char_count})"
        )

        metadata = {
            "char_count": char_count,
            "baseline": element_spec.char_count.baseline,
            "min": element_spec.char_count.min,
            "max": element_spec.char_count.max,
            "valid": False,
            "attempts": max_retries + 1,
            "warning": f"Character count out of range: {char_count}"
        }

        return content, metadata

    def _load_variant_spec(self, variant_id: str) -> VariantElementSpec:
        """Load variant specification from JSON with caching."""
        # Check cache
        if variant_id in self._variant_cache:
            return self._variant_cache[variant_id]

        # Load from file
        spec_file = self.variants_dir / f"{variant_id}.json"

        if not spec_file.exists():
            raise FileNotFoundError(f"Variant spec not found: {spec_file}")

        with open(spec_file, 'r', encoding='utf-8') as f:
            spec_data = json.load(f)

        variant_spec = VariantElementSpec(**spec_data)

        # Cache it
        self._variant_cache[variant_id] = variant_spec

        logger.info(f"Loaded variant spec: {variant_id}")

        return variant_spec

    def _get_variant_id(self, slide_type: str, variant: str) -> str:
        """Generate variant ID from slide_type and variant."""
        # Example: slide_type='matrix', variant='2x2' → 'matrix_2x2'
        variant_clean = variant.replace('x', '_').replace('-', '_')
        return f"{slide_type}_{variant_clean}"

    async def _get_previous_slides(self, presentation_id: str) -> List[Dict[str, Any]]:
        """Get previous slides from session manager."""
        # Implementation depends on session manager
        return []

    def _count_words(self, html: str) -> int:
        """Count words in HTML (strip tags)."""
        import re
        text = re.sub(r'<[^>]+>', '', html)
        return len(text.split())
```

**Deliverable**: Complete generator with parallel element generation and assembly

---

## Phase 6: API Integration

**Duration**: Day 6-7
**Objective**: Add v1.2 endpoint while keeping v1.1 endpoints active.

### 6.1 Request/Response Models

**File**: `app/models/requests.py` (extend existing)

```python
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ContentGenerationRequest(BaseModel):
    """Request model for v1.2 element-based generation."""

    slide_id: str = Field(..., description="Unique slide identifier")
    presentation_id: str = Field(..., description="Presentation identifier")
    slide_number: int = Field(..., description="Slide number in presentation")

    # Variant specification
    slide_type: str = Field(
        ...,
        description="Slide type: matrix, grid, multilateral_comparison, sequential, etc."
    )
    variant: str = Field(
        ...,
        description="Variant name: 2x2, 3col, etc."
    )

    # Content context
    slide_context: Dict[str, Any] = Field(
        ...,
        description="Slide context including title, narrative, key_points, audience, theme"
    )

    # Optional previous context
    previous_slides: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Previous slides context for narrative flow"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "slide_id": "slide_001",
                "presentation_id": "pres_123",
                "slide_number": 2,
                "slide_type": "matrix",
                "variant": "2x2",
                "slide_context": {
                    "title": "Priority Matrix",
                    "narrative": "Organize tasks by urgency and importance",
                    "key_points": ["Do First", "Schedule", "Delegate", "Eliminate"],
                    "audience": "Project managers",
                    "theme": "professional"
                }
            }
        }
```

**File**: `app/models/responses.py` (extend existing)

```python
from typing import Dict, Any
from pydantic import BaseModel, Field


class ContentGenerationResponse(BaseModel):
    """Response model for v1.2 element-based generation."""

    slide_id: str = Field(..., description="Slide identifier from request")
    variant_id: str = Field(..., description="Variant identifier (e.g., 'matrix_2x2')")

    # Generated content
    html_content: str = Field(..., description="Complete assembled HTML")
    elements: Dict[str, str] = Field(
        ...,
        description="Generated element content (element_id → content)"
    )

    # Metadata
    metadata: Dict[str, Any] = Field(
        ...,
        description="Generation metadata (timing, validation, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "slide_id": "slide_001",
                "variant_id": "matrix_2x2",
                "html_content": "<div>...assembled HTML...</div>",
                "elements": {
                    "box_1_title": "Do First",
                    "box_1_description": "Critical tasks requiring...",
                    "box_2_title": "Schedule",
                    "box_2_description": "Important but not urgent..."
                },
                "metadata": {
                    "generation_time_ms": 1234.5,
                    "elements_generated": 8,
                    "element_metadata": {},
                    "model_used": "gemini-1.5-pro"
                }
            }
        }
```

**File**: `app/models/variant_spec.py` (new)

```python
"""Variant specification models."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class CharCountConstraint(BaseModel):
    """Character count constraints for an element."""

    golden: int = Field(..., description="Original golden example character count")
    baseline: int = Field(..., description="Baseline count (golden - 5%)")
    min: int = Field(..., description="Minimum characters (baseline - 5%)")
    max: int = Field(..., description="Maximum characters (baseline + 5%)")


class ElementSpec(BaseModel):
    """Specification for a single element."""

    element_id: str = Field(..., description="Element identifier (e.g., 'box_1_title')")
    element_type: str = Field(..., description="Type: heading, paragraph, list, etc.")
    purpose: str = Field(..., description="Element purpose/context")
    placeholder: str = Field(..., description="Template placeholder (e.g., '{box_1_title}')")
    char_count: CharCountConstraint = Field(..., description="Character count constraints")
    style_guidance: str = Field(..., description="Style/tone guidance for generation")


class VariantElementSpec(BaseModel):
    """Complete specification for a slide variant."""

    variant_id: str = Field(..., description="Unique variant ID (e.g., 'matrix_2x2')")
    slide_type: str = Field(..., description="Slide type")
    variant_name: str = Field(..., description="Human-readable variant name")
    description: str = Field(..., description="Variant description")
    layout_id: str = Field(..., description="Layout ID (L25, L29)")
    template_file: str = Field(..., description="HTML template filename")

    elements: List[ElementSpec] = Field(..., description="List of elements")

    total_elements: int = Field(..., description="Total number of elements")
    total_word_count_target: Optional[str] = Field(None, description="Word count target range")

    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
```

### 6.2 API Endpoint

**File**: `app/api/routes.py` (add to existing)

```python
from fastapi import APIRouter, HTTPException, status
from app.models.requests import ContentGenerationRequest
from app.models.responses import ContentGenerationResponse
from app.core.generators_v2 import ElementBasedContentGenerator

router = APIRouter()


@router.post(
    "/api/v1/generate/content/v2",
    response_model=ContentGenerationResponse,
    tags=["Generation v1.2"],
    summary="Generate content with deterministic assembly (v1.2)",
    description="""
    **v1.2 Deterministic Assembly Endpoint**

    Element-based generation with template assembly for content slides.

    Process:
    1. Loads variant specification (from JSON)
    2. Generates content for each element with character constraints
    3. Assembles into pre-validated HTML template
    4. Returns complete HTML

    **Supported slide types**:
    - matrix (2x2, 2x3)
    - grid (2x3, 3x3)
    - multilateral_comparison (2col, 3col, 4col)
    - sequential (3col, 4col, 5col)
    - asymmetric (8_4, 4_8)
    - hybrid (top_2x2, left_2x2)
    - metrics (3col, 4col)
    - single_column (default)
    - impact_quote (default)
    - table (multi_col)
    """
)
async def generate_content_v2(request: ContentGenerationRequest):
    """
    Generate content using v1.2 element-based approach.

    Returns assembled HTML with element metadata.
    """
    try:
        logger.info(
            f"v1.2 content generation: {request.slide_type}/{request.variant} "
            f"for slide {request.slide_id}"
        )

        generator = ElementBasedContentGenerator()
        result = await generator.generate(request)

        logger.info(
            f"✓ Generated {result.variant_id}: "
            f"{result.metadata['elements_generated']} elements in "
            f"{result.metadata['generation_time_ms']:.0f}ms"
        )

        return result

    except FileNotFoundError as e:
        logger.error(f"Variant not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant specification not found: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Content generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )


@router.get(
    "/api/v1/variants",
    tags=["Generation v1.2"],
    summary="List available variants",
    description="Get list of available slide types and variants"
)
async def list_variants():
    """List all available variants."""
    # Load from config/variants/index.json
    pass


@router.get(
    "/api/v1/variants/{slide_type}",
    tags=["Generation v1.2"],
    summary="Get variants for slide type",
    description="Get available variants for a specific slide type"
)
async def get_variants_for_type(slide_type: str):
    """Get variants for specific slide type."""
    # Load from config/variants/index.json
    pass
```

### 6.3 Existing Endpoints (Keep Active)

```python
# Legacy endpoints (v1.1) - keep for hero slides
@router.post("/api/v1/generate/text", tags=["Generation v1.1"])
async def generate_text(request: TextGenerationRequest):
    """Legacy text generation (for hero slides)."""
    # Existing v1.1 implementation
    pass

@router.post("/api/v1/generate/batch", tags=["Generation v1.1"])
async def generate_batch(request: BatchTextGenerationRequest):
    """Batch generation (v1.1)."""
    # Existing v1.1 implementation
    pass
```

**Deliverable**: v1.2 API endpoint integrated, v1.1 endpoints preserved

---

## Phase 7: Testing & Validation

**Duration**: Day 7-8
**Objective**: Comprehensive testing of v1.2 system.

### 7.1 Unit Tests

**File**: `tests/test_template_assembler.py`

```python
"""Tests for Template Assembler."""

import pytest
from pathlib import Path
from app.core.template_assembler import TemplateAssembler


class TestTemplateAssembler:
    @pytest.fixture
    def assembler(self, tmp_path):
        """Create assembler with temp directory."""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        return TemplateAssembler(templates_dir)

    def test_assemble_simple(self, assembler, tmp_path):
        """Test simple template assembly."""
        # Create test template
        template_file = tmp_path / "templates" / "test.html"
        template_file.write_text("<div>{title}</div><p>{description}</p>")

        result = assembler.assemble(
            template_file="test.html",
            elements={
                "title": "Test Title",
                "description": "Test Description"
            }
        )

        assert result == "<div>Test Title</div><p>Test Description</p>"
        assert "{" not in result

    def test_assemble_missing_element(self, assembler, tmp_path):
        """Test assembly with missing element."""
        template_file = tmp_path / "templates" / "test.html"
        template_file.write_text("<div>{title}</div><p>{description}</p>")

        with pytest.raises(ValueError, match="Missing content"):
            assembler.assemble(
                template_file="test.html",
                elements={"title": "Test"}  # Missing 'description'
            )

    def test_cache_works(self, assembler, tmp_path):
        """Test template caching."""
        template_file = tmp_path / "templates" / "test.html"
        template_file.write_text("<div>{title}</div>")

        # First load
        assembler.assemble("test.html", {"title": "Test"})

        # Second load should use cache
        stats = assembler.get_cache_stats()
        assert stats["cached_templates"] == 1
```

**File**: `tests/test_prompt_builder.py`

```python
"""Tests for Prompt Builder."""

import pytest
from app.core.prompt_builder import ElementPromptBuilder
from app.models.variant_spec import ElementSpec, CharCountConstraint


class TestElementPromptBuilder:
    @pytest.fixture
    def builder(self):
        return ElementPromptBuilder()

    @pytest.fixture
    def element_spec(self):
        return ElementSpec(
            element_id="box_1_title",
            element_type="heading",
            purpose="Top-left quadrant heading",
            placeholder="{box_1_title}",
            char_count=CharCountConstraint(
                golden=12, baseline=11, min=10, max=12
            ),
            style_guidance="1-2 words, concise"
        )

    def test_build_prompt(self, builder, element_spec):
        """Test prompt construction."""
        slide_context = {
            "title": "Test Slide",
            "narrative": "Test narrative",
            "key_points": ["Point 1", "Point 2"]
        }

        prompt = builder.build_element_prompt(
            element_spec, slide_context
        )

        assert "SLIDE CONTEXT" in prompt
        assert "THIS ELEMENT" in prompt
        assert "REQUIREMENTS" in prompt
        assert "10-12 characters" in prompt
        assert "OUTPUT" in prompt
```

### 7.2 Integration Tests

**File**: `tests/test_generators_v2.py`

```python
"""Integration tests for v1.2 generator."""

import pytest
from app.core.generators_v2 import ElementBasedContentGenerator
from app.models.requests import ContentGenerationRequest


class TestElementBasedContentGenerator:
    @pytest.fixture
    def generator(self):
        return ElementBasedContentGenerator()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_generate_matrix_2x2(self, generator):
        """Test generating matrix 2x2 content (requires LLM)."""
        request = ContentGenerationRequest(
            slide_id="test_001",
            presentation_id="test_pres",
            slide_number=1,
            slide_type="matrix",
            variant="2x2",
            slide_context={
                "title": "Priority Matrix",
                "narrative": "Organize tasks",
                "key_points": ["Do First", "Schedule", "Delegate", "Eliminate"]
            }
        )

        response = await generator.generate(request)

        assert response.slide_id == "test_001"
        assert response.variant_id == "matrix_2x2"
        assert len(response.elements) == 8  # 4 titles + 4 descriptions
        assert "<div" in response.html_content
        assert "{" not in response.html_content  # No placeholders remain
```

### 7.3 Comparison Tests

```python
"""Compare v1.1 and v1.2 outputs."""

@pytest.mark.comparison
@pytest.mark.asyncio
async def test_compare_v1_v2_matrix():
    """Compare v1.1 and v1.2 generation for matrix slide."""
    # Generate with v1.1
    v1_generator = LegacyGenerator()
    v1_result = await v1_generator.generate(...)

    # Generate with v1.2
    v2_generator = ElementBasedContentGenerator()
    v2_result = await v2_generator.generate(...)

    # Compare structure (should be identical)
    assert_html_structure_identical(v1_result.html, v2_result.html_content)

    # Compare character counts (v1.2 should be more precise)
    v1_variance = calculate_char_variance(v1_result)
    v2_variance = calculate_char_variance(v2_result)
    assert v2_variance < v1_variance
```

**Deliverable**: Comprehensive test suite with >90% coverage

---

## Success Criteria

### Quality Metrics
✅ **95%+ character count compliance** (within ±5% of baseline)
✅ **100% HTML structure consistency** (matches golden templates exactly)
✅ **90%+ test coverage** (all components tested)
✅ **Zero placeholder errors** in production

### Performance Metrics
✅ **<2s average generation time** per slide
✅ **Element generation parallelized** (all elements generated concurrently)
✅ **Template caching working** (no repeated file loads)

### Integration Metrics
✅ **Director integration successful** (can call v1.2 endpoint)
✅ **All 10 content slide types supported**
✅ **Graceful fallback** if variant not found
✅ **Clear error messages** for debugging

---

## Implementation Timeline

### Week 1: Core Development
- **Days 1-2**: Template extraction & element analysis
- **Days 3-4**: Prompt builder & assembly service
- **Days 5-6**: Element generator & API integration
- **Day 7**: Initial testing

### Week 2: Testing & Refinement
- **Day 8**: Comprehensive test suite
- **Days 9-10**: Performance optimization
- **Days 11-12**: Bug fixes & edge cases
- **Days 13-14**: Documentation & deployment prep

---

## Migration Strategy

### Parallel Deployment
1. **v1.1 endpoints remain active** (hero slides, legacy)
2. **v1.2 endpoint added** (`/api/v1/generate/content/v2`)
3. **Director decides** which to use based on slide_type

### Gradual Rollout
- **Week 1**: Test with matrix slides only
- **Week 2**: Add grid, comparison, sequential
- **Week 3**: Complete rollout to all content types
- **Week 4**: Monitor and optimize

### Fallback Strategy
- If v1.2 generation fails, fallback to v1.1
- Log errors for investigation
- Gradual confidence building

---

## Key Simplifications vs Original Plan

1. **Manual template extraction** (not automated BeautifulSoup)
   - ✅ Faster, more reliable
   - ✅ Preserves exact golden HTML
   - ✅ Easier to maintain

2. **Manual element analysis** (not automated)
   - ✅ More accurate element identification
   - ✅ Better context documentation
   - ✅ Clearer specifications

3. **Focused prompt structure**
   - ✅ Element-specific prompts (not full slide context)
   - ✅ Clear character constraints
   - ✅ Retry logic with guidance

4. **Simple assembly service**
   - ✅ String replacement (not complex parsing)
   - ✅ Cached templates
   - ✅ Clear validation

5. **Focus on content slides only**
   - ✅ 10 content slide types
   - ✅ Hero slides use v1.1 approach
   - ✅ Clearer scope

---

## Directory Structure (Final)

```
agents/text_table_builder/v1.2/
├── app/
│   ├── core/
│   │   ├── generators_v2.py         # Element-based generator
│   │   ├── template_assembler.py    # Template assembly
│   │   ├── prompt_builder.py        # Prompt construction
│   │   ├── context_builder.py       # Context management
│   │   ├── llm_client.py           # LLM integration (from v1.1)
│   │   └── session_manager.py       # Session management (from v1.1)
│   ├── models/
│   │   ├── variant_spec.py         # Variant specifications
│   │   ├── requests.py             # API request models
│   │   └── responses.py            # API response models
│   ├── api/
│   │   └── routes.py               # API endpoints
│   ├── templates/
│   │   ├── matrix/
│   │   │   ├── matrix_2x2.html
│   │   │   └── matrix_2x3.html
│   │   ├── grid/
│   │   ├── multilateral_comparison/
│   │   ├── sequential/
│   │   ├── asymmetric/
│   │   ├── hybrid/
│   │   ├── metrics/
│   │   ├── single_column/
│   │   ├── impact_quote/
│   │   └── table/
│   └── utils/
├── config/
│   └── variants/
│       ├── matrix_2x2.json
│       ├── matrix_2x3.json
│       ├── ...
│       └── index.json
├── tests/
│   ├── test_template_assembler.py
│   ├── test_prompt_builder.py
│   ├── test_generators_v2.py
│   └── test_integration.py
├── main.py
├── requirements.txt
├── README.md
└── IMPLEMENTATION_PLAN.md (THIS FILE)
```

---

## Next Steps

1. **Review this plan** with team
2. **Approve approach** and timeline
3. **Begin Phase 1**: Template extraction
4. **Track progress** in project management system

---

**End of Implementation Plan**
