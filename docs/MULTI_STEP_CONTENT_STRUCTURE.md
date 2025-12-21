# Multi-Step Content Structure

## 3-Phase Architecture for Intelligent Content Generation

**Version:** 1.1 (Theme System Integration)
**Status:** Design Document for Review
**Scope:** C1 content slides and element-based generation
**Related:** THEME_SYSTEM_DESIGN.md (Four Dimensions model)

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [3-Phase Architecture Overview](#2-3-phase-architecture-overview)
   - 2.1 Relationship to Theme System
   - 2.2 Phase Summary
   - 2.3 Visual Flow (Four Dimensions)
3. [Phase 1: Structure Analysis](#3-phase-1-structure-analysis)
   - 3.4 ContentContext Impact on Structure
   - 3.5 Decision Logic (Space + ContentContext)
   - 3.6 LLM Prompt Template (with Audience/Purpose/Time)
   - 3.7 Structure Analyzer Implementation
4. [Phase 2: Space Calculation](#4-phase-2-space-calculation)
   - 4.2 Theme Impact on Character Budgets
   - 4.5 Typography Hierarchy System (3 Groups)
   - 4.6 Content Hierarchy (t1-t4) Deep Dive
   - 4.7 Hierarchy Level Usage Patterns
   - 4.8 Variants (34) Alignment to t1-t4
   - 4.9 Typography Specifications (from Theme)
   - 4.10 Single-Line Generation (Titles/Subtitles)
   - 4.11 SpaceCalculator Implementation (theme-aware)
5. [Phase 3: Content Generation](#5-phase-3-content-generation)
   - 5.2 What Theme vs ContentContext Contributes
   - 5.4 LLM Prompt Template (Theme + ContentContext)
   - 5.5 Multi-Step Generator Implementation
6. [Universal Application](#6-universal-application)
7. [API Contract Changes](#7-api-contract-changes)
   - 7.1 Enhanced Request (theme_config + content_context)
   - 7.3 Example Request/Response
   - 7.4 Backward Compatibility
8. [Trade-offs](#8-trade-offs)
9. [Implementation Considerations](#9-implementation-considerations)
10. [Summary](#summary)
    - Comparison Table
    - How Four Dimensions Flow Through Multi-Step
    - What Each Dimension Controls
    - Cross-Reference to Theme System

---

## 1. Problem Statement

### 1.1 Space Underutilization

**Current behavior:** C1 content slides generate 3-5 bullet points regardless of available space.

**Example - C1 Main Content (30x14 grids = 1800x840 pixels):**
- Available: ~35 lines of body text
- Generated: 3 bullets with 1-2 lines each
- **Utilization: ~15-20%**

The LLM has no visibility into the physical space. It generates "appropriate" content by text-generation standards, not visual standards.

### 1.2 No Structure Intelligence

**Current behavior:** Always single-column layout.

**Problem:** A 30x14 grid could elegantly hold:
- 2 columns with 6 points each
- 3 columns for comparison
- Heading + 2-column body

But the LLM isn't asked to decide structure - it just generates bullets.

### 1.3 Theme Ignored for Text

**Current behavior:** Theme colors exist but are never applied to generated text.

**Problem:** Generated HTML has hardcoded colors:
```html
<h2 style="color: #1e3a5f;">...</h2>  <!-- Always navy -->
```

Even when theme is "children" with purple headings.

### 1.4 Single-Step Limitations

**Current approach:**
```
Input → [LLM: "Generate content"] → Output
```

The LLM is asked to do everything at once:
- Decide structure (implicitly)
- Fit within space (unknown to it)
- Apply styling (unknown to it)
- Generate good content

**Result:** Content quality is fine, but layout optimization is impossible.

---

## 2. 3-Phase Architecture Overview

### 2.1 Relationship to Theme System

Multi-step generation works **within** the Theme System (see THEME_SYSTEM_DESIGN.md). The four dimensions affect generation:

| Dimension | Affects Phase | How |
|-----------|--------------|-----|
| **Theme** | Phase 2 & 3 | Font sizes → character budgets; Colors → HTML output |
| **Audience** | Phase 1 & 3 | Complexity → structure; Vocabulary → word choice |
| **Purpose** | Phase 1 & 3 | Structure pattern; CTAs; Emotional tone |
| **Time** | Phase 1 | Max bullets; Content depth |

### 2.2 Phase Summary

| Phase | Type | Input | Output | Duration |
|-------|------|-------|--------|----------|
| **Phase 1: Structure Analysis** | LLM Call | narrative, topics, space, **content_context** | StructurePlan | ~2s |
| **Phase 2: Space Calculation** | Deterministic | StructurePlan, **theme** | SpaceBudget | <1ms |
| **Phase 3: Content Generation** | LLM Call | StructurePlan, SpaceBudget, **theme**, **content_context** | Styled HTML | ~2-3s |

### 2.3 Visual Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                          REQUEST                                     │
│                                                                       │
│  narrative: "Benefits of cloud migration"                           │
│  topics: ["Cost savings", "Scalability", "Security"]                │
│  available_space: {width: 30, height: 14, unit: "grids"}            │
│                                                                       │
│  theme_config: {                        content_context: {           │
│    theme_id: "executive",                 audience: "executive",     │
│    fonts: {...},                          purpose: "persuade",       │
│    emphasis: {...}                        time: {duration: 15}       │
│  }                                      }                            │
└─────────────────────────────────────────────────────────────────────┘
                                  │
        ┌─────────────────────────┴─────────────────────────┐
        │                                                   │
        ▼                                                   ▼
┌─────────────────────────────┐               ┌─────────────────────────────┐
│  CONTENT CONTEXT ANALYSIS   │               │  THEME EXTRACTION           │
│                             │               │                             │
│  audience: executive        │               │  heading: 48px, #111827     │
│  → max 4 bullets            │               │  body: 20px, #374151        │
│  → concise language         │               │  emphasis: #dc2626          │
│  → jargon OK                │               │  bullet: square             │
│                             │               │                             │
│  purpose: persuade          │               │  (Used in Phase 2 & 3)      │
│  → include CTA              │               │                             │
│  → problem→solution         │               │                             │
│                             │               │                             │
│  time: 15 min               │               │                             │
│  → 3-4 bullets/section      │               │                             │
└─────────────────────────────┘               └─────────────────────────────┘
        │                                                   │
        └─────────────────────────┬─────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 1: Structure Analysis (LLM)                                   │
│                                                                       │
│  Input: narrative, topics, space, audience, purpose, time           │
│                                                                       │
│  Decision: "3 topics, executive audience, 15 min                    │
│             = 3-column layout, 3-4 points each, persuasive"         │
│                                                                       │
│  Output: StructurePlan                                               │
│    - layout_type: "three_column"                                     │
│    - has_heading: true                                               │
│    - sections: [{title: "Cost Savings", points: 3}, ...]            │
│    - total_points: 9 (constrained by audience+time)                 │
│    - structure_pattern: "problem_solution" (from purpose)           │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 2: Space Calculation (Deterministic)                          │
│                                                                       │
│  Input: StructurePlan + THEME (font sizes)                          │
│                                                                       │
│  Executive theme has larger fonts:                                   │
│    heading: 48px → fewer chars than 42px                            │
│    body: 20px → fewer chars than 18px                               │
│                                                                       │
│  width_px = 30 * 60 = 1800px                                        │
│  usable_width = 1800 * 0.90 = 1620px                                │
│  column_width = (1620 - 2*20) / 3 = 527px                           │
│                                                                       │
│  heading: 48px font → max 34 chars (vs 38 with 42px)                │
│  body: 20px font → max 45 chars/line (vs 50 with 18px)              │
│                                                                       │
│  Output: SpaceBudget (theme-adjusted)                                │
│    - heading_chars: 34                                               │
│    - per_column: {title_chars: 35, body_lines: 24, chars_per_line: 45}│
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 3: Content Generation (LLM)                                   │
│                                                                       │
│  Input: StructurePlan + SpaceBudget + THEME + CONTENT_CONTEXT       │
│                                                                       │
│  Prompt includes:                                                    │
│    - Character limits (from budget)                                 │
│    - Colors & fonts (from theme): heading=#111827, emphasis=#dc2626 │
│    - Language style (from audience): "concise, executive-level"     │
│    - Tone (from purpose): "persuasive with clear benefits"          │
│    - Include CTA (from purpose): "yes, action-oriented"             │
│                                                                       │
│  Output: Themed HTML                                                 │
│    - Executive colors (black/red)                                   │
│    - Concise bullets (audience)                                     │
│    - Persuasive language (purpose)                                  │
│    - ~80% space utilization                                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Phase 1: Structure Analysis

### 3.1 Purpose

Decide the optimal layout structure before generating any content. This is a **planning** step, not a content step.

**ContentContext affects structure decisions:**
- **Audience** → Maximum bullets, complexity level
- **Purpose** → Structure pattern (compare, process, problem-solution)
- **Time** → Content depth, point count

### 3.2 Input Model

```python
class StructureAnalysisInput(BaseModel):
    """Input for structure analysis phase."""

    narrative: str = Field(
        description="Main topic or message for the slide"
    )
    topics: List[str] = Field(
        default_factory=list,
        description="Key points or topics to cover"
    )
    available_space: AvailableSpace = Field(
        description="Grid dimensions available for content"
    )
    content_type: str = Field(
        default="body",
        description="Type: heading_only, body, comparison, process"
    )
    # NEW: ContentContext from Theme System
    content_context: Optional[ContentContext] = Field(
        default=None,
        description="Audience, purpose, time constraints"
    )
```

### 3.3 Output Model

```python
class StructureSection(BaseModel):
    """A section within the structure plan."""

    title: str = Field(
        description="Section title (for columns/groups)"
    )
    point_count: int = Field(
        ge=1, le=10,
        description="Number of bullet points in this section"
    )
    emphasis_index: Optional[int] = Field(
        default=None,
        description="Which point to emphasize (0-indexed), if any"
    )


class StructurePlan(BaseModel):
    """Output of structure analysis phase."""

    layout_type: str = Field(
        description="single_column, two_column, three_column"
    )
    has_heading: bool = Field(
        default=True,
        description="Whether to include a main heading"
    )
    has_subheading: bool = Field(
        default=False,
        description="Whether to include a subheading"
    )
    sections: List[StructureSection] = Field(
        description="Content sections (1 for single column, 2-3 for multi)"
    )
    total_points: int = Field(
        description="Total bullet points across all sections"
    )
    rationale: str = Field(
        description="Brief explanation of structure choice"
    )
    # NEW: ContentContext-derived fields
    structure_pattern: str = Field(
        default="standard",
        description="From purpose: standard, comparison, problem_solution, process, narrative"
    )
    include_cta: bool = Field(
        default=False,
        description="From purpose: whether to include call-to-action"
    )
    vocabulary_level: str = Field(
        default="professional",
        description="From audience: kids_simple, general, technical, executive"
    )
```

### 3.4 ContentContext Impact on Structure

| Dimension | Value | Impact on Structure |
|-----------|-------|---------------------|
| **Audience: kids_young** | 6-8 years | max 3 bullets, simple structure, large fonts |
| **Audience: kids_teen** | 9-14 years | max 4 bullets, moderate structure |
| **Audience: general** | Mixed | max 5 bullets, standard structure |
| **Audience: technical** | Engineers | max 6 bullets, can use tables/code |
| **Audience: executive** | C-level | max 4 bullets, key insights only |
| **Audience: academic** | Research | max 7 bullets, can have subpoints |
| **Purpose: inform** | Neutral | standard layout, factual |
| **Purpose: persuade** | Action | problem_solution pattern, include CTA |
| **Purpose: educate** | Learn | process/step pattern, examples |
| **Purpose: compare** | Options | two/three column comparison |
| **Time: 5 min** | Lightning | 3 points max, headlines only |
| **Time: 15 min** | Standard | 4-5 points, moderate depth |
| **Time: 30+ min** | Deep | 6+ points, detailed |

### 3.5 Decision Logic (Space + ContentContext)

| Space (grids) | Topics | Audience | Recommended Layout |
|---------------|--------|----------|-------------------|
| < 15×10 | Any | Any | single_column (constrained) |
| 15-25 wide | 1-2 | Any | single_column |
| 15-25 wide | 3+ | executive | two_column (3 max/col) |
| 15-25 wide | 3+ | general | two_column (4-5/col) |
| 25+ wide | 2 | purpose=compare | two_column comparison |
| 25+ wide | 3 | purpose=compare | three_column comparison |
| 25+ wide | 1-2 | Any | single_column with depth |
| 25+ wide | 4-6 | kids | two_column (3 each max) |
| 25+ wide | 4-6 | executive | two_column (3 each max) |
| 25+ wide | 4-6 | technical | two_column (4-5 each) |

### 3.6 LLM Prompt Template

```python
STRUCTURE_ANALYSIS_PROMPT = """
You are a presentation structure expert. Analyze the content requirements, available space, and audience context to recommend the optimal layout structure.

AVAILABLE SPACE:
- Width: {width_grids} grids ({width_px} pixels)
- Height: {height_grids} grids ({height_px} pixels)
- This is a {size_category} content area

CONTENT TO ORGANIZE:
- Topic: {narrative}
- Key points: {topics_list}
- Number of topics: {topic_count}

AUDIENCE & CONTEXT:
- Audience: {audience_type} ({audience_description})
- Purpose: {purpose_type} ({purpose_description})
- Time: {time_minutes} minutes ({time_description})
- Max bullets for this audience/time: {max_bullets}

STRUCTURE OPTIONS:
1. single_column: Best for narratives, detailed explanations, or 1-2 topics
2. two_column: Best for comparisons, 4-6 topics, or before/after content
3. three_column: Best for exactly 3 categories, or 6-9 related points

STRUCTURE PATTERNS (based on purpose):
- standard: Heading + bullets (default)
- comparison: Side-by-side evaluation (purpose=compare/persuade)
- problem_solution: Problem statement → Solution points (purpose=persuade)
- process: Numbered steps (purpose=educate)
- narrative: Flowing paragraphs (purpose=inform/entertain)

CONSTRAINTS:
- Each column needs minimum 150px width to be readable
- {audience_type} audience: maximum {max_bullets_per_section} points per section
- Total points across all sections: {min_points}-{max_points}
- {cta_instruction}

Respond with JSON:
{{
  "layout_type": "single_column|two_column|three_column",
  "has_heading": true,
  "has_subheading": false,
  "sections": [
    {{"title": "Section Title", "point_count": 3, "emphasis_index": null}}
  ],
  "total_points": 6,
  "rationale": "Brief explanation",
  "structure_pattern": "standard|comparison|problem_solution|process|narrative",
  "include_cta": false,
  "vocabulary_level": "{vocabulary_level}"
}}

Choose the structure that best serves the {audience_type} audience for a {purpose_type} presentation.
"""
```

### 3.7 Structure Analyzer Implementation

```python
class StructureAnalyzer:
    """Analyzes content requirements and recommends structure."""

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def analyze(
        self,
        narrative: str,
        topics: List[str],
        available_space: AvailableSpace,
        content_context: Optional[ContentContext] = None
    ) -> StructurePlan:
        """
        Analyze content and space to determine optimal structure.

        Args:
            narrative: Main topic for the slide
            topics: Key points to cover
            available_space: Grid dimensions
            content_context: Audience, purpose, time context

        Returns:
            StructurePlan with layout recommendation
        """
        width_px, height_px = available_space.to_pixels()

        # Use defaults if no context provided
        ctx = content_context or ContentContext()

        # Categorize space
        if width_px < 900:
            size_category = "small"
            max_cols = 1
        elif width_px < 1500:
            size_category = "medium"
            max_cols = 2
        else:
            size_category = "large"
            max_cols = 3

        # Get audience constraints
        audience_constraints = self._get_audience_constraints(ctx.audience)
        purpose_pattern = self._get_purpose_pattern(ctx.purpose)
        time_constraints = self._get_time_constraints(ctx.time)

        # Adjust max points based on audience + time
        max_bullets = min(
            audience_constraints["max_bullets"],
            time_constraints["max_bullets"]
        )

        # Calculate point range
        body_height = height_px - 80  # Reserve for heading
        space_max_points = int(body_height / 40)  # ~40px per point
        max_points = min(space_max_points, max_bullets)
        min_points = max(3, len(topics))

        prompt = STRUCTURE_ANALYSIS_PROMPT.format(
            width_grids=available_space.width,
            width_px=width_px,
            height_grids=available_space.height,
            height_px=height_px,
            size_category=size_category,
            narrative=narrative,
            topics_list=", ".join(topics) if topics else "(none specified)",
            topic_count=len(topics),
            # Audience context
            audience_type=ctx.audience.audience_type,
            audience_description=audience_constraints["description"],
            max_bullets_per_section=audience_constraints["max_per_section"],
            vocabulary_level=audience_constraints["vocabulary"],
            # Purpose context
            purpose_type=ctx.purpose.purpose_type,
            purpose_description=purpose_pattern["description"],
            cta_instruction=purpose_pattern["cta_instruction"],
            # Time context
            time_minutes=ctx.time.duration_minutes,
            time_description=time_constraints["description"],
            max_bullets=max_bullets,
            min_points=min_points,
            max_points=max_points
        )

        response = await self.llm_service.generate(
            prompt=prompt,
            system="You are a presentation layout expert. Output valid JSON only.",
            temperature=0.3  # Low temperature for consistent decisions
        )

        return StructurePlan.model_validate_json(response)

    def _get_audience_constraints(self, audience: AudienceConfig) -> dict:
        """Get structure constraints for audience type."""
        AUDIENCE_CONSTRAINTS = {
            "kids_young": {"max_bullets": 6, "max_per_section": 3, "vocabulary": "kids_simple", "description": "Children 6-8: simple words, short sentences"},
            "kids_teen": {"max_bullets": 8, "max_per_section": 4, "vocabulary": "general", "description": "Teens 9-14: moderate complexity"},
            "general": {"max_bullets": 10, "max_per_section": 5, "vocabulary": "general", "description": "Mixed audience: accessible language"},
            "technical": {"max_bullets": 12, "max_per_section": 6, "vocabulary": "technical", "description": "Technical: precise terminology OK"},
            "executive": {"max_bullets": 8, "max_per_section": 4, "vocabulary": "executive", "description": "Executives: concise, insight-focused"},
            "academic": {"max_bullets": 14, "max_per_section": 7, "vocabulary": "academic", "description": "Academic: detailed, citations OK"},
        }
        return AUDIENCE_CONSTRAINTS.get(audience.audience_type, AUDIENCE_CONSTRAINTS["general"])

    def _get_purpose_pattern(self, purpose: PurposeConfig) -> dict:
        """Get structure pattern for purpose type."""
        PURPOSE_PATTERNS = {
            "inform": {"pattern": "standard", "cta_instruction": "No call-to-action needed", "description": "Neutral, factual delivery"},
            "persuade": {"pattern": "problem_solution", "cta_instruction": "Include a clear call-to-action as final point", "description": "Build case for action"},
            "educate": {"pattern": "process", "cta_instruction": "Include 'try it' or 'practice' suggestion", "description": "Step-by-step learning"},
            "entertain": {"pattern": "narrative", "cta_instruction": "No call-to-action needed", "description": "Engaging storytelling"},
            "inspire": {"pattern": "narrative", "cta_instruction": "End with aspirational message", "description": "Motivational delivery"},
            "report": {"pattern": "standard", "cta_instruction": "Include 'next steps' if applicable", "description": "Data-driven summary"},
        }
        return PURPOSE_PATTERNS.get(purpose.purpose_type, PURPOSE_PATTERNS["inform"])

    def _get_time_constraints(self, time: TimeConfig) -> dict:
        """Get constraints based on presentation duration."""
        if time.duration_minutes <= 5:
            return {"max_bullets": 6, "description": "Lightning talk: headlines only, no detail"}
        elif time.duration_minutes <= 15:
            return {"max_bullets": 10, "description": "Standard: moderate depth"}
        elif time.duration_minutes <= 30:
            return {"max_bullets": 15, "description": "Extended: detailed with examples"}
        else:
            return {"max_bullets": 20, "description": "Workshop: comprehensive coverage"}
```

---

## 4. Phase 2: Space Calculation

### 4.1 Purpose

Convert the structure plan into exact character budgets using deterministic math. **No LLM needed.**

**Theme is the primary input** - font sizes from ThemeConfig determine character capacity:
- Larger fonts (executive, children) → fewer characters per line
- Smaller fonts (technical, professional) → more characters per line

### 4.2 Theme Impact on Character Budgets

| Theme | Heading Font | Body Font | Heading Chars (30 grids) | Body Chars/Line |
|-------|--------------|-----------|--------------------------|-----------------|
| **professional** | 42px | 18px | 70 | 50 |
| **executive** | 48px | 20px | 61 | 45 |
| **children** | 56px | 24px | 52 | 37 |
| **educational** | 40px | 18px | 73 | 50 |
| **technical** | 38px | 16px | 77 | 56 |
| **creative** | 44px | 18px | 66 | 50 |

The formula: `chars = width_px / (font_size * char_width_ratio)`

### 4.3 Output Model

```python
class SectionBudget(BaseModel):
    """Character budget for one section/column."""

    title_chars: int = Field(
        ge=0,
        description="Max characters for section title"
    )
    body_lines: int = Field(
        ge=1,
        description="Number of lines available for body"
    )
    chars_per_line: int = Field(
        ge=10,
        description="Characters per line based on column width"
    )
    point_char_limit: int = Field(
        ge=20,
        description="Max characters per bullet point"
    )


class SpaceBudget(BaseModel):
    """Complete character budget for content generation."""

    heading_chars: int = Field(
        ge=0,
        description="Max characters for main heading (0 if no heading)"
    )
    subheading_chars: int = Field(
        ge=0,
        description="Max characters for subheading (0 if none)"
    )
    sections: List[SectionBudget] = Field(
        description="Budget per section/column"
    )
    total_body_chars: int = Field(
        description="Total characters available across all sections"
    )
    utilization_target: float = Field(
        default=0.85,
        ge=0.5, le=1.0,
        description="Target fill percentage"
    )
```

### 4.3 Grid System Constants

```python
# Base grid system (from layout_builder)
GRID_COLUMNS = 32
GRID_ROWS = 18
CELL_SIZE = 60  # pixels

# Slide dimensions
SLIDE_WIDTH = 1920  # pixels
SLIDE_HEIGHT = 1080  # pixels

# Margins
OUTER_PADDING = 10  # pixels
INNER_PADDING = 16  # pixels
FILL_FACTOR = 0.90  # Use 90% of available space

# Column gaps
COLUMN_GAP = 20  # pixels between columns
```

### 4.5 Typography Hierarchy System

Typography is organized into **three distinct groups** that apply consistently across the entire presentation:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PRESENTATION TYPOGRAPHY GROUPS                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  GROUP 1: HERO SLIDES (H1, H2, H3)                                  │
│  ─────────────────────────────────                                   │
│  Ultra-large impact fonts for full-slide messaging                  │
│  - hero_title:    72-96px (dominates the slide)                     │
│  - hero_subtitle: 36-48px (supporting message)                      │
│  - hero_accent:   24-32px (author, date, section number)            │
│                                                                       │
│  GROUP 2: SLIDE-LEVEL (Title bar area)                              │
│  ─────────────────────────────────────                               │
│  Consistent across all content slides (C1, I-series)                │
│  - slide_title:   42-48px (main slide title)                        │
│  - slide_subtitle: 28-32px (slide subtitle)                         │
│                                                                       │
│  GROUP 3: CONTENT HIERARCHY (t1, t2, t3, t4)                        │
│  ────────────────────────────────────────────                        │
│  For main content area in C1 and element-based generation           │
│  - t1 (heading):      28-32px  ← MUST be < slide_subtitle           │
│  - t2 (subheading):   22-26px                                        │
│  - t3 (sub-subhead):  18-22px  ← Optional level                     │
│  - t4 (body text):    16-18px  ← Actual content                     │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.6 Content Hierarchy (t1-t4) Deep Dive

**Critical constraint:** Content heading (t1) must be SMALLER than slide_subtitle to maintain visual hierarchy.

```
┌─────────────────────────────────────────────────────────────────────┐
│  SLIDE                                                               │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ slide_title (48px): "Quarterly Results"                        │  │
│  │ slide_subtitle (32px): "Financial Performance Overview"        │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ CONTENT AREA (C1 main content)                                 │  │
│  │                                                                 │  │
│  │  t1 (28px): "Revenue Growth"    ← Smaller than subtitle!      │  │
│  │                                                                 │  │
│  │    t2 (24px): "North America"                                  │  │
│  │      • t4 (18px): Revenue increased 23% YoY                    │  │
│  │      • t4 (18px): Market share grew to 34%                     │  │
│  │                                                                 │  │
│  │    t2 (24px): "Europe"                                         │  │
│  │      t3 (20px): "Western Europe"  ← Optional sub-subheading   │  │
│  │        • t4 (18px): Strong performance in UK and Germany       │  │
│  │                                                                 │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.7 Hierarchy Level Usage Patterns

Not all levels are always used. The typography adapts:

| Pattern | Levels Used | When to Use |
|---------|-------------|-------------|
| **t1 + t4** | Heading + body only | Simple content, few points |
| **t1 + t2 + t4** | Heading + subheading + body | Grouped content (most common) |
| **t1 + t2 + t3 + t4** | All levels | Complex hierarchical content |
| **t2 + t4** | No main heading | When slide title serves as heading |

**Relative sizing when levels are skipped:**

```python
# If t2 (subheading) is skipped, t3 takes its visual weight
HIERARCHY_FALLBACK = {
    "t1_only": {
        "t1": 28,  # Normal
        "t4": 18   # Normal body
    },
    "t1_t2_t4": {
        "t1": 28,
        "t2": 24,
        "t4": 18
    },
    "t1_t4_no_t2": {
        "t1": 28,
        "t4": 20   # Body slightly larger when no subheadings
    }
}
```

### 4.8 Variants (34) Alignment to t1-t4

The 34 content variants MUST use the t1-t4 hierarchy, not arbitrary sizes:

| Variant Category | Element | Maps To |
|------------------|---------|---------|
| **matrix_2x2** | Cell title | t2 |
| **matrix_2x2** | Cell content | t4 |
| **bullets** | Bullet text | t4 |
| **bullets** | Section heading | t1 |
| **comparison** | Column header | t2 |
| **comparison** | Row content | t4 |
| **process_4** | Step title | t2 |
| **process_4** | Step description | t4 |
| **timeline** | Event title | t2 |
| **timeline** | Event description | t4 |

**Principle:** Every text element in a variant maps to exactly one of t1, t2, t3, or t4. No arbitrary font sizes.

### 4.9 Typography Specifications (from Theme)

Each theme defines the concrete values for all three groups:

```python
# Complete typography hierarchy per theme
THEME_TYPOGRAPHY_HIERARCHY = {
    "professional": {
        # Group 1: Hero slides
        "hero_title": {"size": 72, "weight": 700, "color": "#ffffff"},
        "hero_subtitle": {"size": 36, "weight": 400, "color": "#e5e7eb"},
        "hero_accent": {"size": 24, "weight": 400, "color": "#9ca3af"},

        # Group 2: Slide-level
        "slide_title": {"size": 42, "weight": 700, "color": "#1e3a5f"},
        "slide_subtitle": {"size": 28, "weight": 400, "color": "#4b5563"},

        # Group 3: Content hierarchy (t1-t4)
        "t1": {"size": 28, "weight": 600, "color": "#1e3a5f"},
        "t2": {"size": 22, "weight": 600, "color": "#374151"},
        "t3": {"size": 18, "weight": 600, "color": "#4b5563"},
        "t4": {"size": 16, "weight": 400, "color": "#4b5563", "line_height": 1.6}
    },
    "executive": {
        # Group 1: Hero slides (larger, bolder)
        "hero_title": {"size": 84, "weight": 700, "color": "#ffffff"},
        "hero_subtitle": {"size": 42, "weight": 400, "color": "#f3f4f6"},
        "hero_accent": {"size": 28, "weight": 400, "color": "#d1d5db"},

        # Group 2: Slide-level
        "slide_title": {"size": 48, "weight": 700, "color": "#111827"},
        "slide_subtitle": {"size": 32, "weight": 400, "color": "#374151"},

        # Group 3: Content hierarchy (t1-t4) - larger for executives
        "t1": {"size": 32, "weight": 600, "color": "#111827"},
        "t2": {"size": 26, "weight": 600, "color": "#374151"},
        "t3": {"size": 22, "weight": 500, "color": "#4b5563"},
        "t4": {"size": 20, "weight": 400, "color": "#4b5563", "line_height": 1.5}
    },
    "children": {
        # Group 1: Hero slides (playful, very large)
        "hero_title": {"size": 96, "weight": 700, "color": "#ffffff"},
        "hero_subtitle": {"size": 48, "weight": 400, "color": "#fef3c7"},
        "hero_accent": {"size": 32, "weight": 400, "color": "#fde68a"},

        # Group 2: Slide-level
        "slide_title": {"size": 56, "weight": 700, "color": "#7c3aed"},
        "slide_subtitle": {"size": 36, "weight": 400, "color": "#a78bfa"},

        # Group 3: Content hierarchy (t1-t4) - larger, more spacing for kids
        "t1": {"size": 36, "weight": 700, "color": "#7c3aed"},
        "t2": {"size": 28, "weight": 600, "color": "#8b5cf6"},
        "t3": {"size": 24, "weight": 500, "color": "#a78bfa"},
        "t4": {"size": 22, "weight": 400, "color": "#4b5563", "line_height": 1.8}
    }
}
```

### 4.10 Single-Line Generation (Titles/Subtitles)

For generating single lines (e.g., element titles), the parameters are simpler:

```python
class SingleLineGenerationParams:
    """Parameters for single-line text generation."""

    # From theme
    font_type: str       # e.g., "Inter", "Playfair Display"
    font_size: int       # From t1, t2, etc. based on element role
    font_color: str      # From theme

    # From audience (content context)
    max_words: int       # Kids: 3-5, Executive: 4-8, General: 5-10
    max_characters: int  # Calculated from font_size and container width

    # Calculated
    def calculate_max_chars(self, container_width_px: int) -> int:
        char_width = self.font_size * 0.55  # Average char width ratio
        return int(container_width_px / char_width)
```

| Audience | Max Words (Title) | Max Words (Subtitle) | Vocabulary |
|----------|-------------------|----------------------|------------|
| kids_young | 3-4 | 4-6 | Simple |
| kids_teen | 4-6 | 5-8 | Clear |
| general | 5-8 | 6-10 | Accessible |
| technical | 4-7 | 5-10 | Precise |
| executive | 3-5 | 4-7 | Concise |

### 4.11 SpaceCalculator Implementation

```python
class SpaceCalculator:
    """Calculates character budgets from structure plan, space, and THEME (t1-t4 hierarchy)."""

    def __init__(self, theme: Optional[ThemeConfig] = None):
        self.theme = theme or ThemeConfig()
        # Load typography specs from theme (or defaults)
        self.typography = self._load_typography()

    def _load_typography(self) -> Dict[str, Dict]:
        """Load typography specifications from theme."""
        base = TYPOGRAPHY_DEFAULTS.copy()

        # Apply theme overrides if theme has specific typography
        if self.theme.theme_id in THEME_TYPOGRAPHY:
            for level, overrides in THEME_TYPOGRAPHY[self.theme.theme_id].items():
                if level in base:
                    base[level].update(overrides)

        # Also check if theme has explicit fonts dict
        if hasattr(self.theme, 'fonts') and self.theme.fonts:
            for level, font_spec in self.theme.fonts.items():
                if level in base:
                    base[level]["size"] = font_spec.size
                    base[level]["line_height"] = font_spec.line_height
                    if font_spec.family:
                        base[level]["family"] = font_spec.family
                    if font_spec.weight:
                        base[level]["weight"] = font_spec.weight

        return base

    def calculate(
        self,
        structure: StructurePlan,
        available_space: AvailableSpace
    ) -> SpaceBudget:
        """
        Calculate exact character budgets for the structure.

        Args:
            structure: Layout plan from Phase 1
            available_space: Grid dimensions

        Returns:
            SpaceBudget with character limits
        """
        width_px, height_px = available_space.to_pixels()

        # Apply margins (5% each side = 10% total)
        usable_width = int(width_px * FILL_FACTOR)
        usable_height = int(height_px * FILL_FACTOR)

        # Calculate heading budget (using THEME typography)
        heading_chars = 0
        heading_height = 0
        if structure.has_heading:
            heading_spec = self.typography["heading"]  # From theme
            heading_height = int(heading_spec["size"] * heading_spec["line_height"]) + 16
            heading_chars = self._chars_for_width(usable_width, heading_spec)

        # Calculate subheading budget (using THEME typography)
        subheading_chars = 0
        subheading_height = 0
        if structure.has_subheading:
            sub_spec = self.typography["subheading"]  # From theme
            subheading_height = int(sub_spec["size"] * sub_spec["line_height"]) + 12
            subheading_chars = self._chars_for_width(usable_width, sub_spec)

        # Remaining height for body
        body_height = usable_height - heading_height - subheading_height - 20

        # Calculate column widths
        num_columns = self._column_count(structure.layout_type)
        total_gaps = (num_columns - 1) * COLUMN_GAP
        column_width = (usable_width - total_gaps) // num_columns

        # Calculate section budgets (using THEME typography)
        section_budgets = []
        body_spec = self.typography["body"]  # From theme
        title_spec = self.typography["section_title"]  # From theme

        for section in structure.sections:
            # Section title (if multi-column)
            title_chars = 0
            title_height = 0
            if num_columns > 1:
                title_chars = self._chars_for_width(column_width, title_spec)
                title_height = int(title_spec["size"] * title_spec["line_height"]) + 8

            # Body lines
            available_body_height = body_height - title_height
            line_height_px = int(body_spec["size"] * body_spec["line_height"])
            body_lines = available_body_height // line_height_px

            # Characters per line
            chars_per_line = self._chars_for_width(column_width, body_spec)

            # Per-point limit (assume 2 lines per point average)
            point_char_limit = chars_per_line * 2

            section_budgets.append(SectionBudget(
                title_chars=title_chars,
                body_lines=body_lines,
                chars_per_line=chars_per_line,
                point_char_limit=point_char_limit
            ))

        # Total body characters
        total_body = sum(
            s.body_lines * s.chars_per_line
            for s in section_budgets
        )

        return SpaceBudget(
            heading_chars=heading_chars,
            subheading_chars=subheading_chars,
            sections=section_budgets,
            total_body_chars=total_body
        )

    def _chars_for_width(self, width_px: int, spec: dict) -> int:
        """Calculate how many characters fit in given width."""
        avg_char_width = spec["size"] * spec["char_width_ratio"]
        return int(width_px / avg_char_width)

    def _column_count(self, layout_type: str) -> int:
        """Get column count from layout type."""
        return {
            "single_column": 1,
            "two_column": 2,
            "three_column": 3
        }.get(layout_type, 1)
```

### 4.6 Calculation Examples

#### Example 1: C1 Main Content (30x14 grids)

```python
available_space = AvailableSpace(width=30, height=14, unit="grids")
# width_px = 30 * 60 = 1800px
# height_px = 14 * 60 = 840px

# With structure: two_column, has_heading=True

# Usable dimensions (90%)
usable_width = 1620px
usable_height = 756px

# Heading (42px font)
heading_height = 42 * 1.2 + 16 = 66px
heading_chars = 1620 / (42 * 0.55) = 70 chars

# Body height
body_height = 756 - 66 - 20 = 670px

# Two columns
column_width = (1620 - 20) / 2 = 800px

# Per column (24px section title, 18px body)
title_height = 24 * 1.3 + 8 = 39px
body_area = 670 - 39 = 631px
body_lines = 631 / (18 * 1.6) = 21 lines
chars_per_line = 800 / (18 * 0.5) = 88 chars

# Result: 2 columns, each with 21 lines of 88 chars = 3696 chars per column
# Total body: 7392 chars (vs current ~500 chars generated)
```

#### Example 2: Small Element (10x10 grids)

```python
available_space = AvailableSpace(width=10, height=10, unit="grids")
# width_px = 600px, height_px = 600px

# Forced single_column due to small width

# Usable: 540x540

# Heading (smaller, 32px for small elements)
heading_chars = 540 / (32 * 0.55) = 30 chars
heading_height = 32 * 1.2 + 12 = 50px

# Body (16px for small elements)
body_height = 540 - 50 - 16 = 474px
body_lines = 474 / (16 * 1.6) = 18 lines
chars_per_line = 540 / (16 * 0.5) = 67 chars

# Result: Single column with 18 lines of 67 chars = 1206 chars
```

---

## 5. Phase 3: Content Generation

### 5.1 Purpose

Generate content that **exactly fits** the calculated budget while applying:
- **Theme styling** - colors, fonts, bullet styles (visual presentation)
- **ContentContext language** - vocabulary, tone, structure pattern (content substance)

### 5.2 What Theme vs ContentContext Contributes

| Aspect | From Theme | From ContentContext |
|--------|------------|---------------------|
| **Colors** | ✅ Full palette (see below) | - |
| **Fonts** | ✅ font sizes (already in budget), families | - |
| **Bullet style** | ✅ disc, square, number, none | - |
| **Vocabulary** | - | ✅ kids_simple, general, technical, executive |
| **Tone** | - | ✅ neutral, persuasive, pedagogical, inspirational |
| **Structure pattern** | - | ✅ standard, problem_solution, process |
| **CTA inclusion** | - | ✅ from purpose (persuade=yes, inform=no) |
| **Content depth** | - | ✅ from time (5min=headlines, 30min=detailed) |

### 5.2.1 Color Palette Usage in Content Generation

Phase 3 uses colors from the theme's color palette (see THEME_SYSTEM_DESIGN.md §1.4-1.7):

| HTML Element | Color Key | Example (professional) |
|--------------|-----------|------------------------|
| Heading (t1) | `text_primary` | #1e3a5f |
| Subheading (t2) | `text_primary` or `primary` | #1e3a5f |
| Body text (t4) | `text_secondary` | #4b5563 |
| Emphasis/bold | `accent` | #3b82f6 |
| CTA button | `accent` + white | #3b82f6 |
| Box backgrounds | `surface` | #f8fafc |
| Box borders | `border` | #e2e8f0 |
| Section dividers | `tertiary_3` | #cbd5e1 |
| Matrix headers | `primary_light` | #e8eef4 |
| Chart colors | `chart_1` through `chart_6` | Sequential |

```python
# In Phase 3 content generation, colors come from palette
colors = theme.get_color_palette()

html = f"""
<h2 style="color: {colors['text_primary']};">Heading</h2>
<p style="color: {colors['text_secondary']};">Body text with
  <span style="color: {colors['accent']}; font-weight: 600;">emphasis</span>
</p>
<div style="background: {colors['surface']}; border: 1px solid {colors['border']};">
  Card content
</div>
"""
```

### 5.3 Input Combination

```python
class ContentGenerationInput(BaseModel):
    """Combined input for content generation phase."""

    structure: StructurePlan  # From Phase 1 (includes vocabulary_level, structure_pattern)
    budget: SpaceBudget       # From Phase 2 (theme-adjusted character limits)
    theme: ThemeConfig        # For visual styling (colors, fonts)
    content_context: ContentContext  # For content substance (audience, purpose, time)
    narrative: str
    topics: List[str]
```

### 5.4 LLM Prompt Template

```python
CONTENT_GENERATION_PROMPT = """
You are an expert content writer for business presentations.

TASK: Generate content that EXACTLY fills the allocated space with appropriate language for the audience.

STRUCTURE: {layout_type} ({structure_pattern} pattern)
- Has heading: {has_heading}
- Sections: {section_count}

SPACE BUDGET:
{budget_details}

TOPIC: {narrative}
KEY POINTS: {topics}

═══════════════════════════════════════════════════════════════════════════════
CONTENT CONTEXT (affects WHAT you write):
═══════════════════════════════════════════════════════════════════════════════

AUDIENCE: {audience_type}
- Vocabulary: {vocabulary_level}
- {audience_instructions}

PURPOSE: {purpose_type}
- Tone: {tone}
- {purpose_instructions}
- {cta_instruction}

TIME: {time_minutes} minutes
- Content depth: {depth_level}
- {time_instructions}

═══════════════════════════════════════════════════════════════════════════════
THEME STYLING (affects HOW it looks):
═══════════════════════════════════════════════════════════════════════════════

- Heading: font-size: {heading_size}px; color: {heading_color}; font-weight: 700;
- Section title: font-size: {section_size}px; color: {section_color}; font-weight: 600;
- Body: font-size: {body_size}px; color: {body_color};
- Emphasis: color: {emphasis_color}; font-weight: 600;
- Bullet style: {bullet_style}

═══════════════════════════════════════════════════════════════════════════════
CONSTRAINTS:
═══════════════════════════════════════════════════════════════════════════════

1. Heading must be EXACTLY {heading_chars} characters or fewer
2. Each section title: EXACTLY {section_title_chars} characters or fewer
3. Each bullet point: EXACTLY {point_char_limit} characters or fewer
4. Generate EXACTLY {total_points} bullet points total

═══════════════════════════════════════════════════════════════════════════════
OUTPUT:
═══════════════════════════════════════════════════════════════════════════════

Generate HTML with inline styles matching the theme. Fill approximately 85% of the available space.

Use vocabulary appropriate for {audience_type} audience.
Use {tone} tone appropriate for {purpose_type} purpose.
{structure_pattern_instruction}

Output format:
```html
<div class="content-wrapper" style="font-family: {font_family};">
  <h2 style="font-size: {heading_size}px; color: {heading_color}; font-weight: 700;">
    Heading here
  </h2>
  <div class="columns" style="display: flex; gap: 20px;">
    <div class="column">
      <h3 style="font-size: {section_size}px; color: {section_color}; font-weight: 600;">
        Section Title
      </h3>
      <ul style="font-size: {body_size}px; color: {body_color}; list-style-type: {bullet_style};">
        <li>Point 1</li>
        <li>Point 2</li>
      </ul>
    </div>
    <!-- more columns -->
  </div>
</div>
```
"""

# ContentContext instruction builders
AUDIENCE_INSTRUCTIONS = {
    "kids_young": "Use simple words (1-2 syllables). Short sentences. Fun, engaging.",
    "kids_teen": "Clear language. Some complexity OK. Relatable examples.",
    "general": "Accessible language. Avoid jargon. Clear explanations.",
    "technical": "Technical terms OK. Precise language. Can reference APIs, code, specs.",
    "executive": "Concise. Business impact focus. Key insights only. No fluff.",
    "academic": "Formal. Citations OK. Detailed reasoning. Technical depth."
}

PURPOSE_INSTRUCTIONS = {
    "inform": "Present facts neutrally. No persuasion. Objective.",
    "persuade": "Build case for action. Benefits first. Clear value proposition.",
    "educate": "Step-by-step explanation. Examples. Check understanding.",
    "entertain": "Engaging language. Stories. Humor OK if appropriate.",
    "inspire": "Aspirational. Vision-focused. Emotional connection.",
    "report": "Data-driven. Findings + implications. Neutral analysis."
}

STRUCTURE_PATTERN_INSTRUCTIONS = {
    "standard": "Use heading + bullets format.",
    "comparison": "Structure as side-by-side comparison with clear differentiators.",
    "problem_solution": "Lead with problem/challenge, then present solutions.",
    "process": "Number the steps. Use action verbs. Sequential flow.",
    "narrative": "Flow as story. Beginning, middle, conclusion."
}
```

### 5.5 Multi-Step Generator Implementation

```python
class MultiStepGenerator:
    """Orchestrates 3-phase content generation with Theme and ContentContext."""

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.structure_analyzer = StructureAnalyzer(llm_service)
        self.space_calculator = SpaceCalculator()

    async def generate(
        self,
        narrative: str,
        topics: List[str],
        available_space: AvailableSpace,
        theme: Optional[ThemeConfig] = None,
        content_context: Optional[ContentContext] = None
    ) -> Dict[str, Any]:
        """
        Generate content using 3-phase approach.

        Args:
            narrative: Main topic
            topics: Key points
            available_space: Grid dimensions
            theme: Theme for visual styling (Phase 2 & 3)
            content_context: Audience/Purpose/Time for content (Phase 1 & 3)

        Returns:
            Dict with content, metadata, and phase outputs
        """
        theme = theme or ThemeConfig()
        content_context = content_context or ContentContext()

        # Space calculator uses THEME for font-based calculations
        self.space_calculator = SpaceCalculator(theme)

        # Phase 1: Structure Analysis (uses ContentContext)
        structure = await self.structure_analyzer.analyze(
            narrative=narrative,
            topics=topics,
            available_space=available_space,
            content_context=content_context  # Audience, Purpose, Time
        )

        # Phase 2: Space Calculation (uses Theme for font sizes)
        budget = self.space_calculator.calculate(
            structure=structure,
            available_space=available_space
        )

        # Phase 3: Content Generation (uses BOTH Theme and ContentContext)
        content = await self._generate_content(
            structure=structure,
            budget=budget,
            theme=theme,
            content_context=content_context,
            narrative=narrative,
            topics=topics
        )

        return {
            "content": content,
            "metadata": {
                "llm_calls": 2,
                "generation_mode": "multi_step",
                "layout_type": structure.layout_type,
                "structure_pattern": structure.structure_pattern,
                "vocabulary_level": structure.vocabulary_level,
                "space_utilization": self._estimate_utilization(content, budget),
                "theme_id": theme.theme_id,
                "audience": content_context.audience.audience_type,
                "purpose": content_context.purpose.purpose_type,
                "time_minutes": content_context.time.duration_minutes,
                "phases": {
                    "structure": structure.model_dump(),
                    "budget": budget.model_dump()
                }
            }
        }

    async def _generate_content(
        self,
        structure: StructurePlan,
        budget: SpaceBudget,
        theme: ThemeConfig,
        content_context: ContentContext,
        narrative: str,
        topics: List[str]
    ) -> str:
        """Phase 3: Generate HTML content styled by Theme, worded by ContentContext."""

        # Build budget details string
        budget_details = self._format_budget(budget)

        # Get THEME values (visual styling)
        heading_font = theme.get_font("heading")
        body_font = theme.get_font("body")

        # Get CONTENT CONTEXT values (content substance)
        audience = content_context.audience
        purpose = content_context.purpose
        time = content_context.time

        audience_instructions = AUDIENCE_INSTRUCTIONS.get(
            audience.audience_type, AUDIENCE_INSTRUCTIONS["general"]
        )
        purpose_instructions = PURPOSE_INSTRUCTIONS.get(
            purpose.purpose_type, PURPOSE_INSTRUCTIONS["inform"]
        )
        structure_pattern_instruction = STRUCTURE_PATTERN_INSTRUCTIONS.get(
            structure.structure_pattern, STRUCTURE_PATTERN_INSTRUCTIONS["standard"]
        )

        # Time-based depth
        if time.duration_minutes <= 5:
            depth_level = "headlines"
            time_instructions = "Keep points very brief - one idea per bullet"
        elif time.duration_minutes <= 15:
            depth_level = "moderate"
            time_instructions = "Moderate detail - main point with brief explanation"
        else:
            depth_level = "detailed"
            time_instructions = "Full detail - include examples and context"

        # CTA instruction from purpose
        if purpose.include_cta:
            cta_instruction = "Include a clear call-to-action as the final point"
        else:
            cta_instruction = "No call-to-action needed"

        prompt = CONTENT_GENERATION_PROMPT.format(
            # Structure
            layout_type=structure.layout_type,
            structure_pattern=structure.structure_pattern,
            has_heading=structure.has_heading,
            section_count=len(structure.sections),
            budget_details=budget_details,
            narrative=narrative,
            topics=", ".join(topics) if topics else "expand on main topic",

            # Budget constraints
            heading_chars=budget.heading_chars,
            section_title_chars=budget.sections[0].title_chars if budget.sections else 0,
            point_char_limit=budget.sections[0].point_char_limit if budget.sections else 100,
            total_points=structure.total_points,

            # THEME: Visual styling
            font_family=heading_font.family or "Inter",
            heading_size=heading_font.size,
            heading_color=heading_font.color,
            section_size=theme.get_font("subheading").size,
            section_color=theme.get_font("subheading").color,
            body_size=body_font.size,
            body_color=body_font.color,
            emphasis_color=theme.emphasis.color,
            bullet_style=theme.bullet_style,

            # CONTENT CONTEXT: Content substance
            audience_type=audience.audience_type,
            vocabulary_level=structure.vocabulary_level,
            audience_instructions=audience_instructions,
            purpose_type=purpose.purpose_type,
            tone=purpose.emotional_tone,
            purpose_instructions=purpose_instructions,
            cta_instruction=cta_instruction,
            time_minutes=time.duration_minutes,
            depth_level=depth_level,
            time_instructions=time_instructions,
            structure_pattern_instruction=structure_pattern_instruction
        )

        return await self.llm_service.generate(
            prompt=prompt,
            system="You are a presentation content expert. Output clean HTML only. "
                   f"Write for a {audience.audience_type} audience with {purpose.purpose_type} purpose.",
            temperature=0.7
        )

    def _format_budget(self, budget: SpaceBudget) -> str:
        """Format budget as readable string for prompt."""
        lines = []
        if budget.heading_chars > 0:
            lines.append(f"- Heading: max {budget.heading_chars} characters")
        for i, section in enumerate(budget.sections):
            lines.append(f"- Section {i+1}:")
            if section.title_chars > 0:
                lines.append(f"  - Title: max {section.title_chars} characters")
            lines.append(f"  - Body: {section.body_lines} lines, {section.chars_per_line} chars/line")
        lines.append(f"- Total body capacity: {budget.total_body_chars} characters")
        return "\n".join(lines)

    def _estimate_utilization(self, content: str, budget: SpaceBudget) -> float:
        """Estimate how much of the budget was used."""
        # Rough estimate: count non-HTML characters
        import re
        text_only = re.sub(r'<[^>]+>', '', content)
        text_chars = len(text_only.replace('\n', '').replace(' ', ''))
        return min(1.0, text_chars / budget.total_body_chars)
```

### 5.5 Example Generated Output

**Input:**
- narrative: "Benefits of Cloud Migration"
- topics: ["Cost Savings", "Scalability", "Security"]
- available_space: 30x14 grids
- theme: professional

**Structure (Phase 1):**
```json
{
  "layout_type": "three_column",
  "has_heading": true,
  "sections": [
    {"title": "Cost Savings", "point_count": 4},
    {"title": "Scalability", "point_count": 4},
    {"title": "Security", "point_count": 4}
  ],
  "total_points": 12
}
```

**Budget (Phase 2):**
```json
{
  "heading_chars": 70,
  "sections": [
    {"title_chars": 40, "body_lines": 20, "chars_per_line": 55, "point_char_limit": 110}
  ],
  "total_body_chars": 3300
}
```

**Generated HTML (Phase 3):**

```html
<div class="content-wrapper" style="font-family: Inter, sans-serif;">

  <h2 style="
    font-size: 42px;
    font-weight: 700;
    color: #1e3a5f;
    line-height: 1.2;
    margin-bottom: 24px;
    text-align: center;
  ">
    Transform Your Business with Cloud Migration
  </h2>

  <div class="columns" style="display: flex; gap: 20px;">

    <!-- Cost Savings Column -->
    <div class="column" style="flex: 1;">
      <h3 style="
        font-size: 24px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 16px;
      ">
        Cost Savings
      </h3>
      <ul style="
        font-size: 18px;
        color: #4b5563;
        line-height: 1.6;
        list-style-type: disc;
        padding-left: 20px;
      ">
        <li style="margin-bottom: 8px;">
          Reduce capital expenditure by 40-60% by eliminating on-premise hardware
        </li>
        <li style="margin-bottom: 8px;">
          Pay only for resources you use with flexible consumption-based pricing
        </li>
        <li style="margin-bottom: 8px;">
          Lower IT maintenance costs through managed infrastructure services
        </li>
        <li style="margin-bottom: 8px;">
          Achieve faster ROI with reduced deployment and provisioning time
        </li>
      </ul>
    </div>

    <!-- Scalability Column -->
    <div class="column" style="flex: 1;">
      <h3 style="
        font-size: 24px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 16px;
      ">
        Scalability
      </h3>
      <ul style="
        font-size: 18px;
        color: #4b5563;
        line-height: 1.6;
        list-style-type: disc;
        padding-left: 20px;
      ">
        <li style="margin-bottom: 8px;">
          Scale resources instantly to meet demand spikes without planning delays
        </li>
        <li style="margin-bottom: 8px;">
          Support global expansion with multi-region deployment capabilities
        </li>
        <li style="margin-bottom: 8px;">
          Handle 10x traffic growth without infrastructure redesign
        </li>
        <li style="margin-bottom: 8px;">
          Enable auto-scaling policies that respond to real-time metrics
        </li>
      </ul>
    </div>

    <!-- Security Column -->
    <div class="column" style="flex: 1;">
      <h3 style="
        font-size: 24px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 16px;
      ">
        Security
      </h3>
      <ul style="
        font-size: 18px;
        color: #4b5563;
        line-height: 1.6;
        list-style-type: disc;
        padding-left: 20px;
      ">
        <li style="margin-bottom: 8px;">
          Leverage enterprise-grade encryption for data at rest and in transit
        </li>
        <li style="margin-bottom: 8px;">
          Benefit from continuous security monitoring and threat detection
        </li>
        <li style="margin-bottom: 8px;">
          Meet compliance requirements with SOC2, HIPAA, and GDPR certifications
        </li>
        <li style="margin-bottom: 8px;">
          <span style="color: #3b82f6; font-weight: 600;">
            Reduce breach risk by 35% with automated security patches
          </span>
        </li>
      </ul>
    </div>

  </div>
</div>
```

**Space Utilization: ~82%** (vs ~20% with current single-step approach)

---

## 6. Universal Application

### 6.1 Works for Any Grid Size

The 3-phase system is **grid-agnostic**. The same code handles:
- C1 main content (30x14 grids)
- Small sidebar element (10x8 grids)
- Wide banner (28x4 grids)
- Tall narrow panel (8x14 grids)

### 6.2 C1 Main Content Integration

**Location:** `app/core/slides/c1_text_generator.py`

```python
class C1TextGenerator:
    """C1 content generation with multi-step support."""

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.multi_step = MultiStepGenerator(llm_service)

    async def generate(self, request: UnifiedSlideRequest) -> ContentSlideResponse:
        """Generate C1 content using multi-step when space is provided."""

        # Determine generation mode
        if request.available_space:
            # Multi-step generation
            result = await self.multi_step.generate(
                narrative=request.narrative,
                topics=request.topics or [],
                available_space=request.available_space,
                theme=request.theme_config
            )
            return ContentSlideResponse(
                body=result["content"],
                slide_title=self._extract_title(result["content"]),
                metadata=result["metadata"]
            )
        else:
            # Fallback to current single-step (backward compatible)
            return await self._generate_single_step(request)
```

### 6.3 Element-Based Generation Integration

**Location:** `app/core/element_based_generator.py`

```python
class ElementBasedGenerator:
    """Generate content for arbitrary element sizes."""

    async def generate_element(
        self,
        element_type: str,
        narrative: str,
        grid_width: int,
        grid_height: int,
        theme: Optional[ThemeConfig] = None
    ) -> Dict[str, Any]:
        """
        Generate content for a specific element size.

        Args:
            element_type: text, list, paragraph, comparison
            narrative: Content topic
            grid_width: Element width in grids
            grid_height: Element height in grids
            theme: Optional theme config

        Returns:
            Generated HTML with metadata
        """
        available_space = AvailableSpace(
            width=grid_width,
            height=grid_height,
            unit="grids"
        )

        result = await self.multi_step.generate(
            narrative=narrative,
            topics=[],  # Element content doesn't have explicit topics
            available_space=available_space,
            theme=theme
        )

        return result
```

### 6.4 Grid Size to Structure Mapping

| Grid Size | Recommended | Notes |
|-----------|-------------|-------|
| 6x6 or smaller | single_column, 2-3 bullets | Very constrained |
| 10x10 | single_column, 4-6 bullets | Small widget |
| 15x10 | single_column, 6-8 bullets | Sidebar |
| 20x12 | single or two_column | Medium content |
| 30x14 (C1) | two or three_column | Main content |
| 30x16 | three_column optimal | Large content |

The StructureAnalyzer makes these decisions automatically based on the space and topic count.

---

## 7. API Contract Changes

### 7.1 Enhanced Request

```python
class UnifiedSlideRequest(BaseModel):
    # Existing fields...
    slide_number: int
    narrative: str
    topics: Optional[List[str]] = None

    # NEW: Grid dimensions for multi-step generation
    available_space: Optional[AvailableSpace] = Field(
        default=None,
        description="Grid dimensions (triggers multi-step when provided)"
    )

    # NEW: Theme for visual styling (Phase 2 & 3)
    theme_config: Optional[ThemeConfig] = Field(
        default=None,
        description="Theme configuration - affects fonts/colors"
    )

    # NEW: ContentContext for content substance (Phase 1 & 3)
    content_context: Optional[ContentContext] = Field(
        default=None,
        description="Audience, purpose, time - affects vocabulary/tone/structure"
    )
```

### 7.2 Enhanced Response

```python
class ContentSlideResponse(BaseModel):
    # Existing fields...
    slide_title: str
    subtitle: Optional[str]
    body: str
    background_color: str

    # Enhanced metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Includes generation_mode, llm_calls, space_utilization, layout_type"
    )
```

### 7.3 Example Request/Response

**Request:**
```json
{
  "slide_number": 3,
  "narrative": "Key benefits of our AI platform",
  "topics": ["Speed", "Accuracy", "Cost"],
  "available_space": {
    "width": 30,
    "height": 14,
    "unit": "grids"
  },
  "theme_config": {
    "theme_id": "executive"
  },
  "content_context": {
    "audience": {
      "audience_type": "executive"
    },
    "purpose": {
      "purpose_type": "persuade",
      "include_cta": true,
      "emotional_tone": "confident"
    },
    "time": {
      "duration_minutes": 15
    }
  }
}
```

**Response:**
```json
{
  "slide_title": "Key Benefits of Our AI Platform",
  "subtitle": null,
  "body": "<div class='content-wrapper' style='font-family: Inter;'>...</div>",
  "background_color": "#ffffff",
  "metadata": {
    "llm_calls": 2,
    "generation_mode": "multi_step",
    "layout_type": "three_column",
    "structure_pattern": "problem_solution",
    "vocabulary_level": "executive",
    "space_utilization": 0.82,
    "theme_id": "executive",
    "audience": "executive",
    "purpose": "persuade",
    "time_minutes": 15,
    "phases": {
      "structure": {
        "layout_type": "three_column",
        "has_heading": true,
        "structure_pattern": "problem_solution",
        "include_cta": true,
        "vocabulary_level": "executive",
        "sections": [...]
      },
      "budget": {
        "heading_chars": 61,
        "total_body_chars": 2700
      }
    }
  }
}
```

### 7.4 Backward Compatibility

| Scenario | Behavior |
|----------|----------|
| `available_space` NOT provided | Falls back to single-step generation |
| `theme_config` NOT provided | Uses default professional theme |
| `content_context` NOT provided | Uses default (general audience, inform, 15 min) |
| Old Director version | Works unchanged (no breaking changes) |

---

## 8. Trade-offs

### 8.1 Comparison Table

| Aspect | Single-Step (Current) | Multi-Step (Proposed) |
|--------|----------------------|----------------------|
| **LLM Calls** | 1 | 2 |
| **Latency** | ~2-3s | ~4-5s |
| **Space Utilization** | ~20-30% | ~80-90% |
| **Structure Intelligence** | None (always single column) | High (adapts to content) |
| **Theme Application** | None | Full |
| **Content Quality** | Good | Better (fits space) |
| **Complexity** | Low | Medium |

### 8.2 When to Use Each

**Use Single-Step When:**
- Speed is critical (real-time generation)
- Space is unknown/irrelevant
- Simple content with no structure needs
- Backward compatibility required

**Use Multi-Step When:**
- Quality and space utilization matter
- Content will be displayed in defined areas
- Theme styling is important
- User is willing to wait 2s longer

### 8.3 Cost Analysis

| Scenario | Single-Step | Multi-Step | Impact |
|----------|-------------|------------|--------|
| 10-slide deck, 6 content slides | 6 LLM calls | 12 LLM calls | +$0.02 (at $0.01/call) |
| With combined C1 generation | 6 calls | 12 calls | +$0.02 |
| 50 presentations/day | 300 calls | 600 calls | +$3/day |

**The cost is negligible** compared to the quality improvement.

### 8.4 Latency Mitigation

Options to reduce perceived latency:
1. **Streaming:** Start rendering after Phase 1, update after Phase 3
2. **Caching:** Cache structure decisions for similar topic/space combinations
3. **Parallel:** If multiple elements needed, run Phase 1s in parallel

---

## 9. Implementation Considerations

### 9.1 Files to Create

| File | Purpose |
|------|---------|
| `app/models/theme_models.py` | FontSpec, ThemeConfig, AvailableSpace, SpaceBudget |
| `app/core/content/__init__.py` | Module exports |
| `app/core/content/structure_analyzer.py` | Phase 1 LLM logic |
| `app/core/content/space_calculator.py` | Phase 2 math |
| `app/core/content/multi_step_generator.py` | Orchestrator |

### 9.2 Files to Modify

| File | Changes |
|------|---------|
| `app/core/slides/c1_text_generator.py` | Add multi-step path |
| `app/core/element_based_generator.py` | Add multi-step path |
| `app/models/requests.py` | Import extended ThemeConfig |
| `app/api/slides_routes.py` | Accept available_space, theme_config |

### 9.3 Rollout Strategy

1. **Phase A (Safe):** Add new models and modules, no route changes
2. **Phase B (Opt-in):** Enable multi-step only when `available_space` is provided
3. **Phase C (Default):** Make multi-step default for C1, single-step for backward compat

### 9.4 Testing Strategy

```python
# Test structure analysis
async def test_structure_analysis():
    analyzer = StructureAnalyzer(mock_llm)
    result = await analyzer.analyze(
        narrative="Benefits of AI",
        topics=["Speed", "Accuracy", "Cost"],
        available_space=AvailableSpace(width=30, height=14)
    )
    assert result.layout_type in ["two_column", "three_column"]
    assert len(result.sections) >= 2

# Test space calculation
def test_space_calculation():
    calculator = SpaceCalculator()
    budget = calculator.calculate(
        structure=StructurePlan(layout_type="two_column", ...),
        available_space=AvailableSpace(width=30, height=14)
    )
    assert budget.heading_chars > 50
    assert budget.total_body_chars > 3000

# Test full generation
async def test_multi_step_generation():
    generator = MultiStepGenerator(llm_service)
    result = await generator.generate(
        narrative="Cloud benefits",
        topics=["Cost", "Scale"],
        available_space=AvailableSpace(width=30, height=14)
    )
    assert "content" in result
    assert result["metadata"]["llm_calls"] == 2
    assert result["metadata"]["space_utilization"] > 0.7
```

---

## Summary

### Comparison: Current vs Multi-Step

| Aspect | Current (Single-Step) | Multi-Step |
|--------|----------------------|------------|
| **Generation approach** | Single LLM call | 3-phase (2 LLM + 1 math) |
| **Space awareness** | None (character count only) | Full (grid-based calculation) |
| **Structure decisions** | None (always single column) | Intelligent (1-3 columns based on space/topics) |
| **Theme application** | None (hardcoded colors) | Full (inline CSS from theme) |
| **Audience/Purpose/Time** | None | Full ContentContext integration |
| **Space utilization** | ~20-30% | ~80-90% |
| **Latency** | ~2-3s | ~4-5s |
| **Backward compatible** | N/A | Yes (falls back when space not provided) |

### How Four Dimensions Flow Through Multi-Step

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FOUR DIMENSIONS INPUT                             │
│                                                                       │
│  Theme: executive          ContentContext:                           │
│  (visual styling)          - audience: executive                     │
│                            - purpose: persuade                       │
│                            - time: 15 min                            │
└─────────────────────────────────────────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│    PHASE 1        │   │    PHASE 2        │   │    PHASE 3        │
│ Structure Analysis│   │ Space Calculation │   │ Content Generation│
├───────────────────┤   ├───────────────────┤   ├───────────────────┤
│                   │   │                   │   │                   │
│ ContentContext    │   │ Theme →           │   │ Theme →           │
│ affects:          │   │ affects:          │   │ affects:          │
│ - max bullets     │   │ - font sizes      │   │ - colors          │
│ - structure       │   │ - char budgets    │   │ - fonts           │
│ - pattern         │   │ - line counts     │   │ - bullet style    │
│ - vocabulary lvl  │   │                   │   │                   │
│                   │   │                   │   │ ContentContext →  │
│                   │   │                   │   │ affects:          │
│                   │   │                   │   │ - vocabulary      │
│                   │   │                   │   │ - tone            │
│                   │   │                   │   │ - CTA             │
│                   │   │                   │   │ - depth           │
└───────────────────┘   └───────────────────┘   └───────────────────┘
```

### What Each Dimension Controls

| Dimension | Phase 1 | Phase 2 | Phase 3 |
|-----------|---------|---------|---------|
| **Theme** | - | ✅ Font sizes → char budgets | ✅ Colors, fonts in HTML |
| **Audience** | ✅ Max bullets, complexity | - | ✅ Vocabulary level |
| **Purpose** | ✅ Structure pattern | - | ✅ Tone, CTA inclusion |
| **Time** | ✅ Content depth | - | ✅ Detail level |

### Key Insights

1. **Theme vs ContentContext are separate concerns:**
   - Theme = HOW it looks (can change after generation via CSS)
   - ContentContext = WHAT it says (requires regeneration to change)

2. **Theme affects BOTH phases 2 and 3:**
   - Phase 2: Font sizes determine character budgets
   - Phase 3: Colors and fonts go into HTML

3. **ContentContext affects BOTH phases 1 and 3:**
   - Phase 1: Audience+Time → max bullets; Purpose → structure pattern
   - Phase 3: Audience → vocabulary; Purpose → tone; Time → depth

4. **Separation enables intelligence:**
   - By separating "what structure" (Phase 1) from "what content" (Phase 3)
   - And by separating "how much fits" (Phase 2) from "how it looks" (Phase 3)
   - We enable layout decisions that were impossible with single-step generation

5. **Backward compatibility preserved:**
   - All new fields are optional
   - When not provided, sensible defaults used
   - Old Director versions work unchanged

### Cross-Reference to Theme System

See **THEME_SYSTEM_DESIGN.md** for complete details on:
- Four Dimensions model (Theme, Audience, Purpose, Time)
- Theme presets (professional, executive, children, etc.)
- ContentContext presets (AUDIENCE_PRESETS, PURPOSE_PRESETS, TIME_PRESETS)
- Frontend theme switching
- Service contracts
