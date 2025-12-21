# Theme System Design

## Comprehensive Theme Architecture for All Slide Types

**Version:** 2.1 (Cross-Service Contract + Frontend Capabilities)
**Status:** Design Document for Review
**Scope:** Theme integration across Hero slides, Content slides, I-Series, and all Elements
**Parties:** Frontend, Layout Service, Director, Text Service

---

## Table of Contents

1. [Overview: Theme Across All Slide Types](#1-overview-theme-across-all-slide-types)
   - 1.2 Where Theme Applies
   - 1.3 Typography Hierarchy System (3 Groups: Hero, Slide-Level, Content t1-t4)
   - 1.4 Color Palette System (Primary, Accent, Tertiary, Neutrals, Charts)
   - 1.5 Color Usage by Element Type
   - 1.6 Theme Color Palettes (Examples)
   - 1.7 Cross-Service Color Agreement
   - 1.8 Human-Readable Summary
2. [The Four Dimensions: Theme, Audience, Purpose, Time](#2-the-four-dimensions-theme-audience-purpose-time)
   - 2.1 Overview of All Dimensions
   - 2.2 Theme vs Audience vs Purpose vs Time
   - 2.3 Audience Types and Content Density
   - 2.4 Purpose Types and Content Focus
   - 2.5 Time Available and Content Depth
   - 2.6 How All Four Dimensions Work Together
   - 2.7 Content Context Models (AudienceConfig, PurposeConfig, TimeConfig)
   - 2.8-2.10 Presets (Audience, Purpose, Time)
3. [Theme Application by Slide Type](#3-theme-application-by-slide-type)
   - 3.1 Hero Slides (H1, H2, H3)
   - 3.2 Content Slides (C1)
   - 3.3 I-Series Slides (I1, I2, I3, I4)
   - 3.4 Individual Elements
4. [Cross-Service Contract Summary](#4-cross-service-contract-summary) ⭐ **EXPANDED**
   - 4.1 The Four Parties (Frontend, Layout, Director, Text)
   - 4.2 Party Responsibilities Matrix
   - 4.3 What Each Service MUST Do
     - 4.3.1 Director - Required Actions
     - 4.3.2 Layout Service - Required Actions
     - 4.3.3 Text Service - Required Actions
     - 4.3.4 Frontend - Required Actions
   - 4.4 What User Can Change From Frontend
   - 4.5 Data Flow Examples
   - 4.6 Contract Summary Table
   - 4.7 Who Controls What
   - 4.8 Theme Registry Synchronization
   - 4.9 Implementation Checklist
5. [Frontend Theme Switching](#5-frontend-theme-switching)
   - 5.1 The Requirement
   - 5.2 Two Approaches (Inline vs CSS Classes)
   - 5.3 CSS Class Naming Convention
   - 5.4 Theme Switching Flow
   - 5.5 What Changes vs What Stays
6. [Theme Models](#6-theme-models)
7. [Theme Presets](#7-theme-presets)
8. [Process Workflow](#8-process-workflow)
9. [Current State Analysis](#9-current-state-analysis)
10. [Implementation Considerations](#10-implementation-considerations)
11. [Summary](#11-summary)
12. [Cross-Service Coordination Log](#12-cross-service-coordination-log) ⭐ **ACTIVE**
    - 12.1 Layout Service Response (Confirmed)
    - 12.2 Text Service Response to Layout Service
    - 12.3 Director Response & Text Service Answers
    - 12.4 Frontend Response & Text Service Answers ⭐ **NEW**

---

## 1. Overview: Theme Across All Slide Types

### 1.1 What is Theme?

**Theme = Visual Styling** - How content LOOKS, independent of what the content says.

Theme controls:
- Font family (Inter, Georgia, Comic Sans)
- Font sizes (heading 42px, body 18px)
- Font colors (navy headings, gray body)
- Background colors (solid or gradients)
- Accent/emphasis colors
- Bullet styles (disc, circle, square)

Theme does NOT control:
- How much content to generate (that's Audience)
- What to say (that's narrative/topics)
- Layout structure (that's determined by space + content needs)

### 1.2 Where Theme Applies

| Slide/Element Type | Theme Affects | Notes |
|-------------------|---------------|-------|
| **H1-generated (Title)** | Text colors, font sizes, background gradient | Image has its own visual_style |
| **H1-structured** | All text fields, background color | Author info, date styling |
| **H2-section** | Section number, title styling, background | Section divider aesthetic |
| **H3-closing** | Contact info, CTA styling, background | Call-to-action emphasis |
| **C1 Content** | Heading, subheading, body, bullets | Main content area |
| **I1 (Image Left)** | Title, body, background; image style | Wide image (660×1080) |
| **I2 (Image Right)** | Title, body, background; image style | Wide image (660×1080) |
| **I3 (Narrow Image Left)** | Title, body, background; image style | Narrow image (360×1080), more text space |
| **I4 (Narrow Image Right)** | Title, body, background; image style | Narrow image (360×1080), more text space |
| **Element: Title** | Font family, size, weight, color | Single element |
| **Element: Subtitle** | Font family, size, weight, color | Single element |
| **Element: Body Text** | Font, bullets, line spacing, color | Multi-line content |
| **Element: Table/Matrix** | Header colors, cell colors, borders | Structured data |

### 1.3 Typography Hierarchy System

Theme defines typography at **three distinct levels** that must be consistent across the entire presentation:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TYPOGRAPHY HIERARCHY GROUPS                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  GROUP 1: HERO SLIDES (H1, H2, H3)                                  │
│  Ultra-large impact fonts for full-slide messaging                  │
│  - hero_title:    72-96px (dominates the slide)                     │
│  - hero_subtitle: 36-48px (supporting message)                      │
│  - hero_accent:   24-32px (author, date, section number)            │
│                                                                       │
│  GROUP 2: SLIDE-LEVEL (Title bar area of C1, I-series)              │
│  - slide_title:   42-48px (main slide title)                        │
│  - slide_subtitle: 28-32px (slide subtitle)                         │
│                                                                       │
│  GROUP 3: CONTENT HIERARCHY (t1, t2, t3, t4)                        │
│  For main content area and elements                                 │
│  - t1 (heading):      28-32px  ← MUST be < slide_subtitle           │
│  - t2 (subheading):   22-26px                                        │
│  - t3 (sub-subhead):  18-22px  ← Optional level                     │
│  - t4 (body text):    16-18px  ← Actual content                     │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

**Critical constraint:** Content heading (t1) must be SMALLER than slide_subtitle to maintain visual hierarchy.

**All 34 variants** use t1-t4 hierarchy (no arbitrary font sizes):
| Variant Element | Maps To |
|-----------------|---------|
| Matrix cell title | t2 |
| Bullet text | t4 |
| Process step title | t2 |
| Comparison header | t2 |
| Timeline event | t2 |

See **MULTI_STEP_CONTENT_STRUCTURE.md §4.5-4.10** for detailed typography specifications per theme.

### 1.4 Color Palette System

Theme defines a **structured color palette** that all services (Director, Layout, Text) must agree on:

```
┌─────────────────────────────────────────────────────────────────────┐
│                      THEME COLOR PALETTE                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  PRIMARY COLORS (Brand Identity)                                     │
│  ───────────────────────────────                                     │
│  - primary:        Main brand color (buttons, links, emphasis)      │
│  - primary_dark:   Darker variant (hover states, headers)           │
│  - primary_light:  Lighter variant (backgrounds, highlights)        │
│                                                                       │
│  ACCENT COLORS (Highlights & CTAs)                                  │
│  ─────────────────────────────────                                   │
│  - accent:         Call-to-action, important highlights             │
│  - accent_dark:    Darker variant for emphasis                      │
│  - accent_light:   Subtle accent backgrounds                        │
│                                                                       │
│  TERTIARY COLORS (Supporting Elements)                              │
│  ─────────────────────────────────────                               │
│  - tertiary_1:     Secondary groupings, borders                     │
│  - tertiary_2:     Alternate backgrounds                            │
│  - tertiary_3:     Subtle dividers, shadows                         │
│                                                                       │
│  NEUTRAL COLORS (Backgrounds & Text)                                │
│  ────────────────────────────────────                                │
│  - background:     Slide background (usually white/light)           │
│  - surface:        Card/box backgrounds                             │
│  - border:         Default border color                             │
│  - text_primary:   Main text (headings)                             │
│  - text_secondary: Body text                                        │
│  - text_muted:     Captions, secondary info                         │
│                                                                       │
│  DATA VISUALIZATION (Charts, Graphs)                                │
│  ────────────────────────────────────                                │
│  - chart_1 through chart_6: Sequential chart colors                 │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.5 Color Usage by Element Type

| Element Type | Colors Used | Notes |
|--------------|-------------|-------|
| **Slide background** | background | Usually white or very light |
| **Hero slide background** | primary_dark or gradient | High impact |
| **Content box/card** | surface, border | Subtle differentiation |
| **Heading text** | text_primary or primary | Depends on theme |
| **Body text** | text_secondary | Readable, not too dark |
| **Emphasis/bold** | accent or primary | Draws attention |
| **CTA button** | accent + white text | High contrast |
| **Matrix/table headers** | primary_light + text_primary | Distinct from cells |
| **Matrix/table cells** | surface or background | Clean |
| **Process step icons** | primary, tertiary_1, tertiary_2 | Sequence |
| **Comparison columns** | alternating tertiary | Visual separation |
| **Timeline markers** | accent | Highlight events |
| **Chart bars/slices** | chart_1 through chart_6 | Data series |

### 1.6 Theme Color Palettes (Examples)

```python
THEME_COLOR_PALETTES = {
    "professional": {
        # Primary (Navy blue)
        "primary": "#1e3a5f",
        "primary_dark": "#152a45",
        "primary_light": "#e8eef4",

        # Accent (Blue)
        "accent": "#3b82f6",
        "accent_dark": "#2563eb",
        "accent_light": "#dbeafe",

        # Tertiary (Grays with blue tint)
        "tertiary_1": "#64748b",
        "tertiary_2": "#94a3b8",
        "tertiary_3": "#cbd5e1",

        # Neutrals
        "background": "#ffffff",
        "surface": "#f8fafc",
        "border": "#e2e8f0",
        "text_primary": "#1e3a5f",
        "text_secondary": "#4b5563",
        "text_muted": "#9ca3af",

        # Charts
        "chart_1": "#3b82f6",
        "chart_2": "#10b981",
        "chart_3": "#f59e0b",
        "chart_4": "#ef4444",
        "chart_5": "#8b5cf6",
        "chart_6": "#ec4899"
    },
    "executive": {
        # Primary (Black/Charcoal)
        "primary": "#111827",
        "primary_dark": "#030712",
        "primary_light": "#f3f4f6",

        # Accent (Red)
        "accent": "#dc2626",
        "accent_dark": "#b91c1c",
        "accent_light": "#fee2e2",

        # Tertiary (Warm grays)
        "tertiary_1": "#4b5563",
        "tertiary_2": "#6b7280",
        "tertiary_3": "#9ca3af",

        # Neutrals
        "background": "#ffffff",
        "surface": "#f9fafb",
        "border": "#e5e7eb",
        "text_primary": "#111827",
        "text_secondary": "#374151",
        "text_muted": "#6b7280",

        # Charts (Bold, high contrast)
        "chart_1": "#111827",
        "chart_2": "#dc2626",
        "chart_3": "#f59e0b",
        "chart_4": "#10b981",
        "chart_5": "#6366f1",
        "chart_6": "#8b5cf6"
    },
    "children": {
        # Primary (Purple)
        "primary": "#7c3aed",
        "primary_dark": "#5b21b6",
        "primary_light": "#ede9fe",

        # Accent (Yellow/Orange)
        "accent": "#f59e0b",
        "accent_dark": "#d97706",
        "accent_light": "#fef3c7",

        # Tertiary (Playful colors)
        "tertiary_1": "#ec4899",
        "tertiary_2": "#06b6d4",
        "tertiary_3": "#10b981",

        # Neutrals (Warmer)
        "background": "#fffbeb",
        "surface": "#fef3c7",
        "border": "#fde68a",
        "text_primary": "#7c3aed",
        "text_secondary": "#4b5563",
        "text_muted": "#9ca3af",

        # Charts (Bright, fun)
        "chart_1": "#7c3aed",
        "chart_2": "#ec4899",
        "chart_3": "#f59e0b",
        "chart_4": "#10b981",
        "chart_5": "#06b6d4",
        "chart_6": "#ef4444"
    },
    "educational": {
        # Primary (Teal/Blue)
        "primary": "#0d9488",
        "primary_dark": "#0f766e",
        "primary_light": "#ccfbf1",

        # Accent (Orange)
        "accent": "#ea580c",
        "accent_dark": "#c2410c",
        "accent_light": "#ffedd5",

        # Tertiary
        "tertiary_1": "#0284c7",
        "tertiary_2": "#7c3aed",
        "tertiary_3": "#64748b",

        # Neutrals
        "background": "#ffffff",
        "surface": "#f0fdfa",
        "border": "#99f6e4",
        "text_primary": "#0f766e",
        "text_secondary": "#374151",
        "text_muted": "#6b7280",

        # Charts
        "chart_1": "#0d9488",
        "chart_2": "#ea580c",
        "chart_3": "#0284c7",
        "chart_4": "#7c3aed",
        "chart_5": "#84cc16",
        "chart_6": "#f43f5e"
    }
}
```

### 1.7 Cross-Service Color Agreement

**Critical:** All three services must use the same color palette:

| Service | What It Uses Colors For | Must Match |
|---------|------------------------|------------|
| **Director** | Passes theme_config to other services | Defines the theme_id |
| **Layout Service** | Box fills, borders, backgrounds | Uses palette from theme_id |
| **Text Service** | Generated HTML (text colors, emphasis) | Uses palette from theme_id |

```
┌─────────────────────────────────────────────────────────────────────┐
│                     COLOR AGREEMENT FLOW                             │
│                                                                       │
│  Director                                                            │
│     │                                                                │
│     │ theme_id: "professional"                                       │
│     │ (color palette is IMPLICIT - all services know it)            │
│     │                                                                │
│     ├──────────────────────────────┐                                │
│     │                              │                                │
│     ▼                              ▼                                │
│  Layout Service               Text Service                          │
│  ───────────────              ────────────                          │
│  Box fill: #e8eef4           Heading: #1e3a5f                       │
│  (primary_light)             (text_primary)                         │
│                                                                       │
│  Border: #e2e8f0             Emphasis: #3b82f6                      │
│  (border)                    (accent)                               │
│                                                                       │
│  Card bg: #f8fafc            Body: #4b5563                          │
│  (surface)                   (text_secondary)                       │
│                                                                       │
│         SAME PALETTE ─────────────────── SAME PALETTE               │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

**Option A: Implicit Agreement**
- All services have THEME_COLOR_PALETTES built-in
- Director sends only `theme_id`
- Services look up colors locally

**Option B: Explicit Passing**
- Director sends full `color_palette` object
- Services use exactly what's provided
- More flexible but more data to pass

**Recommendation:** Option A with fallback. Services have built-in palettes, Director can optionally override specific colors.

### 1.8 Human-Readable Summary

> **Think of Theme like clothing for your presentation:**
> - **Professional theme** = Business suit (navy, clean, structured)
> - **Executive theme** = Power suit (black, bold, impactful)
> - **Educational theme** = Smart casual (blue, readable, clear)
> - **Children theme** = Playful outfit (colorful, fun, large text)
>
> **The same words can be "dressed" differently** - a slide about "Cloud Computing" looks corporate in Professional theme, but friendly and approachable in Educational theme.

---

## 2. The Four Dimensions: Theme, Audience, Purpose, Time

### 2.1 Overview of All Dimensions

| Dimension | What It Controls | Example | Can Change After Generation? |
|-----------|-----------------|---------|------------------------------|
| **Theme** | Visual appearance | Navy vs Purple headings | Yes (CSS swap) |
| **Audience** | Content complexity | Simple words vs Industry jargon | No |
| **Purpose** | Content focus | Inform vs Persuade vs Entertain | No |
| **Time** | Content depth | 5-min overview vs 1-hour deep dive | No |

### 2.2 Theme vs Audience vs Purpose vs Time

| Aspect | Theme | Audience | Purpose | Time |
|--------|-------|----------|---------|------|
| **What it controls** | Visual appearance | Complexity & vocabulary | Focus & structure | Depth & detail |
| **Affects** | Colors, fonts, styling | Amount of text, word choice | Persuasion elements, CTAs | How much to cover |
| **Same content?** | Yes - just looks different | No - different complexity | No - different structure | No - different depth |
| **User can change?** | Yes - via frontend | No - set at generation | No - set at generation | No - set at generation |
| **Example** | Navy vs Purple | Kids words vs Technical terms | "Buy now" vs "Learn about" | 3 bullets vs 8 bullets |

### 2.3 Audience Types and Content Density

| Audience | Content Characteristics | Bullet Points | Complexity |
|----------|------------------------|---------------|------------|
| **Young Kids (5-8)** | Very simple, short sentences | 2-3 per slide | Simple words |
| **Children (9-12)** | Simple but more content | 3-4 per slide | Basic concepts |
| **High Schoolers** | Moderate detail | 4-6 per slide | Some jargon OK |
| **College Students** | Detailed content | 5-7 per slide | Technical terms OK |
| **Professionals** | Dense, comprehensive | 5-8 per slide | Industry jargon |
| **Executives** | Concise, high-impact | 3-5 per slide | Key metrics only |

### 2.4 Purpose Types and Content Focus

| Purpose | Content Focus | Slide Structure | Language Style |
|---------|--------------|-----------------|----------------|
| **Inform** | Facts, data, explanations | Topic → Details → Summary | Neutral, objective |
| **Educate** | Concepts, learning | Build-up → Examples → Exercises | Clear, pedagogical |
| **Persuade** | Benefits, proof points | Problem → Solution → CTA | Compelling, emotional |
| **Entertain** | Stories, engagement | Hook → Journey → Payoff | Casual, fun |
| **Inspire** | Vision, motivation | Challenge → Path → Vision | Aspirational, powerful |
| **Report** | Results, analysis | Data → Insights → Recommendations | Factual, concise |

**How Purpose Affects Content:**

```
Same Topic: "Cloud Computing"

PURPOSE: Inform
→ "Cloud computing is a model for delivering computing services over the internet.
   It includes servers, storage, databases, and software."

PURPOSE: Persuade
→ "Stop wasting money on outdated infrastructure. Cloud computing can cut your
   IT costs by 40% while doubling your team's productivity. Here's how..."

PURPOSE: Educate
→ "Let's understand cloud computing step by step. First, imagine your computer,
   but instead of being on your desk, it's in a data center..."

PURPOSE: Entertain
→ "Remember when we used to carry floppy disks? Now your entire business
   lives in 'the cloud' - which sounds way cooler than 'someone else's computer'..."
```

### 2.5 Time Available and Content Depth

| Time Slot | Slides | Content Per Slide | Presenter Guidance |
|-----------|--------|-------------------|-------------------|
| **5 min (Lightning)** | 3-5 | Headlines only, no details | 1 key point per slide |
| **10 min (Quick)** | 5-8 | Brief bullets, 2-3 each | Hit the highlights |
| **20 min (Standard)** | 8-12 | Full bullets, 4-5 each | Moderate depth |
| **30 min (Extended)** | 10-15 | Detailed content | Include examples |
| **45 min (Deep)** | 12-18 | Comprehensive | Include case studies |
| **60+ min (Workshop)** | 15-25+ | Full depth + exercises | Interactive elements |

**How Time Affects Content:**

```
Same Topic: "Benefits of AI in Healthcare"

TIME: 5 minutes (Lightning Talk)
→ 4 slides:
  1. Title: "AI is Transforming Healthcare"
  2. "3 Key Benefits" (just headlines)
  3. "Real Results: 40% faster diagnosis"
  4. "Start your AI journey today"

TIME: 30 minutes (Standard Presentation)
→ 12 slides:
  1. Title
  2. Problem: Current healthcare challenges
  3. What is AI in healthcare?
  4. Benefit 1: Faster diagnostics (with examples)
  5. Benefit 2: Reduced costs (with data)
  6. Benefit 3: Better outcomes (with case study)
  7. Implementation approach
  8. Common concerns addressed
  9. Success story: Hospital X
  10. ROI analysis
  11. Getting started roadmap
  12. Call to action + Q&A
```

### 2.6 How All Four Dimensions Work Together

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER REQUEST                                │
│  "Create a 15-minute sales pitch about renewable energy              │
│   for executives"                                                    │
└─────────────────────────────────────────────────────────────────────┘
                                  │
        ┌─────────────┬───────────┼───────────┬─────────────┐
        ▼             ▼           ▼           ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   THEME     │ │  AUDIENCE   │ │   PURPOSE   │ │    TIME     │
│ "executive" │ │ "executives"│ │  "persuade" │ │  "15 min"   │
│             │ │             │ │             │ │             │
│ - Black/red │ │ - Concise   │ │ - Benefits  │ │ - 8 slides  │
│ - Bold text │ │ - Jargon OK │ │ - Proof pts │ │ - 3-4 bullets│
│ - Square    │ │ - Key only  │ │ - Strong CTA│ │ - Examples  │
│   bullets   │ │             │ │             │ │             │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
        │             │               │               │
        │             │               │               │
        │    ┌────────┴───────────────┴───────────────┘
        │    │
        ▼    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    GENERATED PRESENTATION                            │
│                                                                       │
│  8 slides, each with:                                                │
│  - 3-4 high-impact bullets (TIME + AUDIENCE)                        │
│  - Persuasive language with proof points (PURPOSE)                  │
│  - Bold black headings with red emphasis (THEME)                    │
│  - Strong call-to-action on closing slide (PURPOSE)                 │
│  - Key ROI metrics highlighted (AUDIENCE)                           │
│  - Square bullets on gray background (THEME)                        │
└─────────────────────────────────────────────────────────────────────┘
```

**Example: Same Topic, Different Configurations**

| Configuration | Theme | Audience | Purpose | Time | Result |
|--------------|-------|----------|---------|------|--------|
| Investor Pitch | Executive | Investors | Persuade | 10 min | 6 slides, ROI-focused, bold styling, strong CTA |
| Team Training | Educational | Employees | Educate | 45 min | 15 slides, step-by-step, clear visuals, exercises |
| Kids Workshop | Children | Young kids | Entertain | 20 min | 8 slides, simple words, colorful, interactive |
| Board Report | Professional | Executives | Report | 30 min | 12 slides, data-heavy, neutral, recommendations |

### 2.7 Content Context Models

These three models control WHAT is generated (vs Theme which controls HOW it looks).

#### AudienceConfig

```python
class AudienceConfig(BaseModel):
    """Audience configuration affecting content complexity."""

    audience_type: str = Field(
        default="professional",
        description="Target audience: kids_young, kids_older, high_school, college, professional, executive"
    )

    # Complexity controls
    complexity_level: str = Field(
        default="moderate",
        description="simple, moderate, advanced - affects vocabulary"
    )
    max_sentence_words: int = Field(
        default=20,
        ge=5, le=40,
        description="Max words per sentence (kids=10, professional=25)"
    )
    avoid_jargon: bool = Field(
        default=False,
        description="True for kids/general audience"
    )
```

#### PurposeConfig

```python
class PurposeConfig(BaseModel):
    """Purpose configuration affecting content focus and structure."""

    purpose_type: str = Field(
        default="inform",
        description="inform, educate, persuade, entertain, inspire, report"
    )

    # Content focus
    include_cta: bool = Field(
        default=False,
        description="Include call-to-action (True for persuade/inspire)"
    )
    include_data: bool = Field(
        default=True,
        description="Include statistics/data points"
    )
    include_examples: bool = Field(
        default=True,
        description="Include real-world examples"
    )
    emotional_tone: str = Field(
        default="neutral",
        description="neutral, enthusiastic, urgent, empathetic, authoritative"
    )

    # Structure guidance
    structure_pattern: str = Field(
        default="topic_details",
        description="topic_details, problem_solution, story_arc, comparison"
    )
```

#### TimeConfig

```python
class TimeConfig(BaseModel):
    """Time configuration affecting content depth and slide count."""

    duration_minutes: int = Field(
        default=20,
        ge=1, le=120,
        description="Presentation duration in minutes"
    )

    # Derived from duration
    @property
    def slide_count_range(self) -> tuple:
        """Recommended slide count based on duration."""
        if self.duration_minutes <= 5:
            return (3, 5)
        elif self.duration_minutes <= 10:
            return (5, 8)
        elif self.duration_minutes <= 20:
            return (8, 12)
        elif self.duration_minutes <= 30:
            return (10, 15)
        elif self.duration_minutes <= 45:
            return (12, 18)
        else:
            return (15, 25)

    @property
    def bullets_per_slide(self) -> int:
        """Recommended bullets based on duration."""
        if self.duration_minutes <= 5:
            return 2  # Headlines only
        elif self.duration_minutes <= 10:
            return 3
        elif self.duration_minutes <= 30:
            return 4
        else:
            return 5

    @property
    def include_deep_content(self) -> bool:
        """Include case studies, detailed examples."""
        return self.duration_minutes >= 30
```

#### Combined ContentContext

```python
class ContentContext(BaseModel):
    """Combined context for content generation (excluding Theme)."""

    audience: AudienceConfig = Field(default_factory=AudienceConfig)
    purpose: PurposeConfig = Field(default_factory=PurposeConfig)
    time: TimeConfig = Field(default_factory=TimeConfig)

    def get_max_bullets(self) -> int:
        """Get max bullets considering both audience and time."""
        audience_bullets = {
            "kids_young": 3,
            "kids_older": 4,
            "executive": 4,
            "professional": 6,
        }.get(self.audience.audience_type, 5)

        # Take the minimum of audience and time constraints
        return min(audience_bullets, self.time.bullets_per_slide)

    def get_content_density(self) -> float:
        """Get content density multiplier."""
        # Shorter presentations = less content per slide
        time_factor = min(1.0, self.time.duration_minutes / 20)

        # Kids = less content
        audience_factor = {
            "kids_young": 0.4,
            "kids_older": 0.6,
            "executive": 0.7,
            "professional": 1.0,
        }.get(self.audience.audience_type, 0.8)

        return time_factor * audience_factor
```

### 2.8 Audience Presets

```python
AUDIENCE_PRESETS = {
    "kids_young": AudienceConfig(
        audience_type="kids_young",
        complexity_level="simple",
        max_sentence_words=8,
        avoid_jargon=True
    ),
    "kids_older": AudienceConfig(
        audience_type="kids_older",
        complexity_level="simple",
        max_sentence_words=12,
        avoid_jargon=True
    ),
    "high_school": AudienceConfig(
        audience_type="high_school",
        complexity_level="moderate",
        max_sentence_words=18,
        avoid_jargon=False
    ),
    "college": AudienceConfig(
        audience_type="college",
        complexity_level="advanced",
        max_sentence_words=22,
        avoid_jargon=False
    ),
    "professional": AudienceConfig(
        audience_type="professional",
        complexity_level="advanced",
        max_sentence_words=25,
        avoid_jargon=False
    ),
    "executive": AudienceConfig(
        audience_type="executive",
        complexity_level="advanced",
        max_sentence_words=20,
        avoid_jargon=False  # Executives know jargon
    ),
}
```

### 2.9 Purpose Presets

```python
PURPOSE_PRESETS = {
    "inform": PurposeConfig(
        purpose_type="inform",
        include_cta=False,
        include_data=True,
        include_examples=True,
        emotional_tone="neutral",
        structure_pattern="topic_details"
    ),
    "educate": PurposeConfig(
        purpose_type="educate",
        include_cta=False,
        include_data=True,
        include_examples=True,
        emotional_tone="neutral",
        structure_pattern="topic_details"
    ),
    "persuade": PurposeConfig(
        purpose_type="persuade",
        include_cta=True,
        include_data=True,
        include_examples=True,
        emotional_tone="enthusiastic",
        structure_pattern="problem_solution"
    ),
    "entertain": PurposeConfig(
        purpose_type="entertain",
        include_cta=False,
        include_data=False,
        include_examples=True,
        emotional_tone="enthusiastic",
        structure_pattern="story_arc"
    ),
    "inspire": PurposeConfig(
        purpose_type="inspire",
        include_cta=True,
        include_data=False,
        include_examples=True,
        emotional_tone="empathetic",
        structure_pattern="story_arc"
    ),
    "report": PurposeConfig(
        purpose_type="report",
        include_cta=False,
        include_data=True,
        include_examples=False,
        emotional_tone="neutral",
        structure_pattern="topic_details"
    ),
}
```

### 2.10 Time Presets

```python
TIME_PRESETS = {
    "lightning": TimeConfig(duration_minutes=5),    # 3-5 slides
    "quick": TimeConfig(duration_minutes=10),       # 5-8 slides
    "standard": TimeConfig(duration_minutes=20),    # 8-12 slides
    "extended": TimeConfig(duration_minutes=30),    # 10-15 slides
    "deep": TimeConfig(duration_minutes=45),        # 12-18 slides
    "workshop": TimeConfig(duration_minutes=60),    # 15-25 slides
}
```

---

## 3. Theme Application by Slide Type

### 3.1 Hero Slides (H1, H2, H3)

#### H1-generated (Title Slide with AI Image)

| Element | Theme Control | Notes |
|---------|--------------|-------|
| Title text | Font, size, color, weight | Overlaid on image |
| Subtitle | Font, size, color | Secondary text |
| Background | Gradient colors | Fallback if image fails |
| Image style | `visual_style` parameter | Affects image generation prompt |

**Theme Application:**
```html
<!-- H1-generated with "executive" theme -->
<div class="hero-slide" style="background-image: url('...')">
  <h1 style="
    font-family: Inter, sans-serif;
    font-size: 64px;
    font-weight: 800;
    color: #ffffff;
    text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
  ">
    Strategic Vision 2025
  </h1>
  <p style="
    font-size: 28px;
    color: rgba(255,255,255,0.9);
  ">
    Transforming the Future
  </p>
</div>
```

#### H1-structured (Title Slide without Image)

| Element | Theme Control | Notes |
|---------|--------------|-------|
| Title | Font, size, color | Main title |
| Subtitle | Font, size, color | Tagline |
| Author info | Font, size, color | Presenter name |
| Date info | Font, size, color | Presentation date |
| Background | Solid color or gradient | `background_color` field |

**Theme Application:**
```html
<!-- H1-structured with "professional" theme -->
<div class="hero-slide" style="background-color: #1e3a5f;">
  <h1 style="color: #ffffff; font-size: 56px; font-weight: 700;">
    Q4 Business Review
  </h1>
  <p style="color: rgba(255,255,255,0.8); font-size: 24px;">
    Performance Analysis and Outlook
  </p>
  <div style="color: rgba(255,255,255,0.7); font-size: 18px;">
    <span>John Smith, CEO</span>
    <span style="margin-left: 24px;">December 2024</span>
  </div>
</div>
```

#### H2-section (Section Divider)

| Element | Theme Control | Notes |
|---------|--------------|-------|
| Section number | Font, size, color, style | "01", "02", etc. |
| Section title | Font, size, color | Section name |
| Background | Solid color | Often darker than content |

#### H3-closing (Closing Slide)

| Element | Theme Control | Notes |
|---------|--------------|-------|
| Closing message | Font, size, color | "Thank You" etc. |
| Contact info | Font, size, color | Email, links |
| CTA button | Background, text color | Call-to-action styling |
| Background | Solid color or gradient | Often matches H1 |

### 3.2 Content Slides (C1)

| Element | Theme Control | Notes |
|---------|--------------|-------|
| Slide title | `fonts.heading` | Main title at top |
| Subtitle | `fonts.subheading` | Optional subtitle |
| Body text | `fonts.body` | Bullet points, paragraphs |
| Emphasis | `emphasis.color`, `emphasis.weight` | Highlighted text |
| Bullets | `bullet_style` | disc, circle, square |
| Background | `background_color` | Usually white/light |

**Theme Application Example:**

```html
<!-- C1 Content with "educational" theme -->
<div class="content-slide" style="background-color: #ffffff;">
  <h2 style="
    font-family: Inter, sans-serif;
    font-size: 38px;
    font-weight: 600;
    color: #1e40af;
    margin-bottom: 16px;
  ">
    How Photosynthesis Works
  </h2>

  <ul style="
    font-size: 18px;
    color: #1f2937;
    line-height: 1.7;
    list-style-type: disc;
  ">
    <li>Plants absorb sunlight through chlorophyll</li>
    <li>Carbon dioxide enters through leaf stomata</li>
    <li>Water travels up from roots</li>
    <li style="color: #059669; font-weight: 600;">
      Glucose is produced as food for the plant
    </li>
  </ul>
</div>
```

### 3.3 I-Series Slides (I1, I2, I3, I4)

I-series are image+text combination slides with different layouts:

| Layout | Image Position | Image Size | Content Area |
|--------|---------------|------------|--------------|
| **I1** | Left | Wide (660×1080) | Right side |
| **I2** | Right | Wide (660×1080) | Left side |
| **I3** | Left | Narrow (360×1080) | Larger right side |
| **I4** | Right | Narrow (360×1080) | Larger left side |

#### Theme Elements in I-Series

| Element | Theme Control | Notes |
|---------|--------------|-------|
| Title | `fonts.heading` | Above or beside image |
| Subtitle | `fonts.subheading` | Optional secondary text |
| Body/Content | `fonts.body` | Bullet points, paragraphs |
| Emphasis | `emphasis.color`, `emphasis.weight` | Highlighted text |
| Background | `background_color` | Usually white (#ffffff) |
| Image style | `visual_style` | Affects AI image generation |

#### I-Series Specific Considerations

1. **Text must contrast with image** - If image is dark, text overlay needs light colors or text shadow
2. **Compact content** - Less space than C1, theme should account for this
3. **Image visual_style alignment** - Theme should inform image generation style:
   - Professional theme → "professional, clean, corporate photography"
   - Children theme → "playful, colorful, illustrated style"
   - Educational theme → "clear, informative, diagram-style"

**Theme Application Example:**

```html
<!-- I1 (Image Left) with "executive" theme -->
<div class="iseries-slide" style="display: flex; background-color: #f9fafb;">

  <!-- Image area (left) -->
  <div class="image-container" style="width: 660px; height: 1080px;">
    <img src="..." alt="Business growth chart"
         style="width: 100%; height: 100%; object-fit: cover;">
  </div>

  <!-- Content area (right) -->
  <div class="content-container" style="flex: 1; padding: 60px;">

    <h2 style="
      font-family: Inter, sans-serif;
      font-size: 48px;
      font-weight: 800;
      color: #111827;
      line-height: 1.1;
      margin-bottom: 24px;
    ">
      Revenue Growth
    </h2>

    <p style="
      font-size: 24px;
      color: #1f2937;
      margin-bottom: 32px;
    ">
      Q4 exceeded all projections
    </p>

    <ul style="
      font-size: 20px;
      color: #374151;
      line-height: 1.5;
      list-style-type: square;
    ">
      <li style="margin-bottom: 16px;">
        <span style="color: #dc2626; font-weight: 700;">+47%</span> year-over-year growth
      </li>
      <li style="margin-bottom: 16px;">
        Market share expanded to 23%
      </li>
      <li style="margin-bottom: 16px;">
        Customer retention at 94%
      </li>
    </ul>

  </div>
</div>
```

#### I-Series Theme Mapping

| Theme | Image Style | Text Colors | Background |
|-------|------------|-------------|------------|
| Professional | Corporate photography, clean | Navy heading, gray body | White |
| Executive | Bold imagery, charts | Black heading, red accents | Light gray |
| Educational | Diagrams, illustrations | Blue heading, dark body | White |
| Children | Colorful, playful | Purple heading, pink accents | Light yellow |

### 3.4 Individual Elements

When generating individual elements (not full slides), theme applies directly:

| Element Type | Theme Fields Used | Frontend Can Override? |
|--------------|-------------------|----------------------|
| Title | `fonts.heading.family`, `fonts.heading.size`, `fonts.heading.color`, `fonts.heading.weight` | Yes |
| Subtitle | `fonts.subheading.*` | Yes |
| Body/Paragraph | `fonts.body.*` | Yes |
| Caption | `fonts.caption.*` | Yes |
| Table Header | `fonts.subheading.*` + `matrix_colors[0]` | Yes |
| Table Cells | `fonts.body.*` + `matrix_colors[1:]` | Yes |

#### Element Generation Modes

**Mode A: Theme from Director (Content Generation Time)**
```json
{
  "element_type": "title",
  "content": "Benefits of Cloud Computing",
  "theme_config": {
    "fonts": {
      "heading": {"family": "Georgia", "size": 48, "color": "#1a365d"}
    }
  }
}
```
→ Text Service generates HTML with these exact styles.

**Mode B: No Theme (Frontend Controls)**
```json
{
  "element_type": "title",
  "content": "Benefits of Cloud Computing"
}
```
→ Text Service generates semantic HTML without inline styles.
→ Frontend applies styles from Layout Service theme.

**Mode C: Theme ID Only**
```json
{
  "element_type": "title",
  "content": "Benefits of Cloud Computing",
  "theme_id": "professional"
}
```
→ Text Service looks up preset and applies those styles.

---

## 4. Cross-Service Contract Summary

### 4.1 The Four Parties

The theme system involves **four distinct parties**, each with specific responsibilities:

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                           ┌──────────────┐                           │
│                           │   FRONTEND   │                           │
│                           │    (User)    │                           │
│                           └──────┬───────┘                           │
│                                  │                                   │
│                    User selects theme, audience, purpose, time       │
│                    User can CHANGE THEME after generation (CSS)      │
│                                  │                                   │
│                                  ▼                                   │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                      LAYOUT SERVICE                          │    │
│  │                                                               │    │
│  │  • Manages theme presets and custom themes                   │    │
│  │  • Defines slide layouts and grid positions                  │    │
│  │  • Provides box fills, borders, backgrounds (using palette)  │    │
│  │  • Stores generated content from Text Service                │    │
│  │  • Enables theme switching via CSS class swap                │    │
│  └────────────────────────────┬────────────────────────────────┘    │
│                               │                                      │
│       Sends: theme_id, content_context, available_space, narrative   │
│                               │                                      │
│                               ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                         DIRECTOR                              │    │
│  │                      (Orchestrator)                           │    │
│  │                                                               │    │
│  │  • Receives full presentation context                        │    │
│  │  • Resolves theme_id → full theme config (typography+colors) │    │
│  │  • Resolves audience/purpose/time → content_context          │    │
│  │  • Passes styling_mode to Text Service                       │    │
│  │  • Coordinates multi-slide generation                        │    │
│  └────────────────────────────┬────────────────────────────────┘    │
│                               │                                      │
│       Sends: theme_config, content_context, available_space,         │
│              narrative, topics, styling_mode                         │
│                               │                                      │
│                               ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                       TEXT SERVICE                            │    │
│  │                    (Content Generator)                        │    │
│  │                                                               │    │
│  │  • Generates content using 3-phase multi-step approach       │    │
│  │  • Phase 1: Structure (uses content_context)                 │    │
│  │  • Phase 2: Space calculation (uses theme typography)        │    │
│  │  • Phase 3: Content generation (uses theme + context)        │    │
│  │  • Returns HTML with CSS classes OR inline styles            │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Party Responsibilities Matrix

| Responsibility | Frontend | Layout Service | Director | Text Service |
|---------------|----------|----------------|----------|--------------|
| **Define theme presets** | - | ✅ MUST | - | Has fallbacks |
| **Store color palettes** | - | ✅ MUST | ✅ MUST | ✅ MUST |
| **Store typography specs** | - | ✅ MUST | ✅ MUST | ✅ MUST |
| **User theme selection** | ✅ | - | - | - |
| **Theme switching (post-gen)** | ✅ CSS swap | Provides CSS | - | - |
| **Resolve theme_id → config** | - | Can do | ✅ SHOULD | Fallback |
| **Determine audience/purpose/time** | ✅ Input | Passes through | ✅ Interprets | Uses |
| **Pass available_space** | - | ✅ MUST | ✅ MUST | Uses |
| **Generate content** | - | - | Orchestrates | ✅ Does |
| **Apply box fills/borders** | - | ✅ MUST | - | - |
| **Apply text styling** | CSS classes | - | - | HTML output |

### 4.3 What Each Service MUST Do

#### 4.3.1 DIRECTOR - Required Actions

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DIRECTOR MUST DO                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  1. RESOLVE THEME                                                    │
│     ─────────────────                                                │
│     • Maintain THEME_REGISTRY with all theme presets                │
│     • When receiving theme_id, expand to full config:               │
│       - Typography: hero, slide_level, t1-t4 (font, size, color)   │
│       - Colors: primary, accent, tertiary, neutrals, charts         │
│     • Send FULL theme_config to Text Service (not just theme_id)   │
│                                                                       │
│  2. PASS CONTENT CONTEXT                                            │
│     ──────────────────────                                           │
│     • Convert user inputs to structured content_context:            │
│       - audience_type → AudienceConfig                              │
│       - purpose_type → PurposeConfig (with include_cta, etc.)      │
│       - duration → TimeConfig                                        │
│     • Always include content_context in Text Service requests       │
│                                                                       │
│  3. SPECIFY STYLING MODE                                            │
│     ───────────────────────                                          │
│     • Include styling_mode in request:                              │
│       - "css_classes": For theme-switchable output                  │
│       - "inline_styles": For fixed styling (exports, PDFs)          │
│     • Default to "css_classes" for editor use                       │
│                                                                       │
│  4. PASS AVAILABLE SPACE                                            │
│     ──────────────────────                                           │
│     • Always include available_space from Layout Service            │
│     • {width: X, height: Y, unit: "grids"}                          │
│     • This triggers multi-step generation in Text Service          │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

**Director Request Example:**
```json
{
  "slide_number": 3,
  "narrative": "Key benefits of our platform",
  "topics": ["Speed", "Reliability", "Cost"],

  "available_space": {
    "width": 30,
    "height": 14,
    "unit": "grids"
  },

  "styling_mode": "css_classes",

  "theme_config": {
    "theme_id": "executive",
    "typography": {
      "hero_title": {"size": 84, "weight": 700, "color": "#ffffff"},
      "slide_title": {"size": 48, "weight": 700, "color": "#111827"},
      "slide_subtitle": {"size": 32, "weight": 400, "color": "#374151"},
      "t1": {"size": 32, "weight": 600, "color": "#111827"},
      "t2": {"size": 26, "weight": 600, "color": "#374151"},
      "t3": {"size": 22, "weight": 500, "color": "#4b5563"},
      "t4": {"size": 20, "weight": 400, "color": "#4b5563"}
    },
    "colors": {
      "primary": "#111827",
      "primary_light": "#f3f4f6",
      "accent": "#dc2626",
      "surface": "#f9fafb",
      "border": "#e5e7eb",
      "text_primary": "#111827",
      "text_secondary": "#374151"
    }
  },

  "content_context": {
    "audience": {"audience_type": "executive"},
    "purpose": {"purpose_type": "persuade", "include_cta": true},
    "time": {"duration_minutes": 15}
  }
}
```

#### 4.3.2 LAYOUT SERVICE - Required Actions

```
┌─────────────────────────────────────────────────────────────────────┐
│                   LAYOUT SERVICE MUST DO                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  1. MAINTAIN THEME REGISTRY                                          │
│     ──────────────────────────                                       │
│     • Store all theme presets (professional, executive, etc.)       │
│     • Each preset includes:                                          │
│       - Full typography hierarchy (hero, slide, t1-t4)              │
│       - Full color palette (20+ color keys)                         │
│     • Sync theme registry with Director and Text Service            │
│                                                                       │
│  2. PROVIDE AVAILABLE SPACE                                          │
│     ─────────────────────────                                        │
│     • For each content area, calculate grid dimensions              │
│     • Pass to Director: {width, height, unit: "grids"}              │
│     • Example: C1 main content = 30x14 grids                        │
│                                                                       │
│  3. APPLY BOX STYLING FROM PALETTE                                  │
│     ──────────────────────────────                                   │
│     • Box fills: Use surface, primary_light, tertiary colors       │
│     • Borders: Use border color from palette                        │
│     • Backgrounds: Use background, surface colors                   │
│     • MUST match the same palette Text Service uses                 │
│                                                                       │
│  4. GENERATE THEME CSS                                              │
│     ────────────────────────                                         │
│     • Create CSS for each theme:                                     │
│       .theme-professional .deckster-t1 { color: #1e3a5f; ... }     │
│       .theme-executive .deckster-t1 { color: #111827; ... }        │
│     • Include CSS classes for: t1, t2, t3, t4, emphasis, etc.      │
│     • Load appropriate CSS when user selects theme                  │
│                                                                       │
│  5. ENABLE THEME SWITCHING                                          │
│     ────────────────────────                                         │
│     • When user changes theme:                                       │
│       - Swap CSS class on presentation container                    │
│       - Update box fills/borders from new palette                   │
│       - NO content regeneration needed                              │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

**Layout Service Theme CSS Example:**
```css
/* Theme: Professional */
.theme-professional {
  --color-primary: #1e3a5f;
  --color-accent: #3b82f6;
  --color-surface: #f8fafc;
  --color-border: #e2e8f0;
  --color-text-primary: #1e3a5f;
  --color-text-secondary: #4b5563;
}

.theme-professional .deckster-t1 {
  font-size: 28px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.theme-professional .deckster-t4 {
  font-size: 16px;
  font-weight: 400;
  color: var(--color-text-secondary);
}

/* Theme: Executive */
.theme-executive {
  --color-primary: #111827;
  --color-accent: #dc2626;
  --color-surface: #f9fafb;
  /* ... */
}

.theme-executive .deckster-t1 {
  font-size: 32px;
  font-weight: 600;
  color: var(--color-text-primary);
}
```

#### 4.3.3 TEXT SERVICE - Required Actions

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TEXT SERVICE MUST DO                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  1. SUPPORT BOTH STYLING MODES                                       │
│     ────────────────────────────                                     │
│     • styling_mode: "css_classes" →                                 │
│         Output: <h3 class="deckster-t1">Heading</h3>               │
│     • styling_mode: "inline_styles" →                               │
│         Output: <h3 style="font-size:32px;color:#111827">...</h3>  │
│     • Default to css_classes if not specified                       │
│                                                                       │
│  2. USE TYPOGRAPHY HIERARCHY                                         │
│     ──────────────────────────                                       │
│     • Map content to t1, t2, t3, t4 levels                          │
│     • Content heading → t1                                          │
│     • Subheading → t2                                               │
│     • Sub-subheading → t3                                           │
│     • Body text, bullets → t4                                       │
│                                                                       │
│  3. USE COLOR PALETTE                                               │
│     ───────────────────                                              │
│     • heading color → text_primary or primary                       │
│     • body color → text_secondary                                   │
│     • emphasis → accent                                             │
│     • boxes → surface, border                                       │
│                                                                       │
│  4. RESPECT CONTENT CONTEXT                                         │
│     ─────────────────────────                                        │
│     • audience → vocabulary, max_bullets, complexity                │
│     • purpose → tone, structure_pattern, include_cta                │
│     • time → content_depth, bullets_per_slide                       │
│                                                                       │
│  5. RETURN METADATA                                                  │
│     ───────────────────                                              │
│     • Include theme_applied, styling_mode in response               │
│     • Include theme_id so Layout Service knows what CSS to use      │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

**Text Service Response Example (css_classes mode):**
```json
{
  "content": "<div class=\"deckster-content\"><h3 class=\"deckster-t1\">Key Benefits</h3><ul class=\"deckster-bullets\"><li class=\"deckster-t4\">50% faster processing</li></ul></div>",
  "metadata": {
    "styling_mode": "css_classes",
    "theme_id": "executive",
    "css_classes_used": ["deckster-t1", "deckster-t4", "deckster-bullets", "deckster-emphasis"]
  }
}
```

#### 4.3.4 FRONTEND - Required Actions

```
┌─────────────────────────────────────────────────────────────────────┐
│                     FRONTEND MUST DO                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  1. PROVIDE THEME SELECTION UI                                       │
│     ────────────────────────────                                     │
│     • Theme picker with preset options                              │
│     • Custom theme editor (optional)                                 │
│     • Preview before applying                                        │
│                                                                       │
│  2. COLLECT FOUR DIMENSIONS                                         │
│     ─────────────────────────                                        │
│     • Theme selector (visual)                                        │
│     • Audience dropdown (kids → executive)                          │
│     • Purpose dropdown (inform, persuade, educate, etc.)            │
│     • Time/Duration input (5 min → 60+ min)                         │
│     • These affect generation and CANNOT change after               │
│                                                                       │
│  3. ENABLE THEME SWITCHING (POST-GENERATION)                        │
│     ─────────────────────────────────────────                        │
│     • "Change Theme" button always available                        │
│     • Switching swaps CSS class, not content:                       │
│         <div class="presentation theme-professional">               │
│                          ↓                                          │
│         <div class="presentation theme-executive">                  │
│     • Instant visual update, no API calls                           │
│                                                                       │
│  4. COMMUNICATE WHAT NEEDS REGENERATION                             │
│     ─────────────────────────────────────                            │
│     • If user changes AUDIENCE/PURPOSE/TIME:                        │
│         Show warning: "This will regenerate all content"            │
│     • If user changes THEME:                                        │
│         No warning needed - instant CSS swap                        │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.4 What User Can Change From Frontend

```
┌─────────────────────────────────────────────────────────────────────┐
│              FRONTEND THEME SWITCHING CAPABILITIES                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ✅ CAN CHANGE INSTANTLY (CSS swap, no regeneration):               │
│  ─────────────────────────────────────────────────────               │
│  • Theme preset (Professional → Executive)                          │
│  • All colors (primary, accent, text colors)                        │
│  • Font families (Inter → Georgia)                                  │
│  • Font sizes (within t1-t4 hierarchy)                              │
│  • Font weights                                                      │
│  • Background colors                                                 │
│  • Box fills and borders                                            │
│  • Bullet styles                                                    │
│  • Line heights                                                      │
│                                                                       │
│  ❌ CANNOT CHANGE (requires content regeneration):                  │
│  ─────────────────────────────────────────────────                   │
│  • Audience type (kids → executive)                                 │
│  • Purpose type (inform → persuade)                                 │
│  • Time allocation (5 min → 30 min)                                 │
│  • Number of bullets                                                │
│  • Content text/words                                               │
│  • Layout structure (2-col → 3-col)                                 │
│  • Image content                                                    │
│                                                                       │
│  WHY?                                                                │
│  ─────                                                               │
│  Theme = Visual styling (HOW it looks) → CSS can handle             │
│  Content Context = What to say (WHAT is written) → needs LLM        │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.5 Data Flow Examples

#### Layout Service → Director

```json
{
  "presentation_id": "abc-123",
  "slides": [...],
  "theme": {
    "theme_id": "custom-corporate",
    "fonts": {
      "heading": {"family": "Montserrat", "size": 44, "weight": 700, "color": "#2c3e50"},
      "body": {"family": "Open Sans", "size": 16, "weight": 400, "color": "#34495e"}
    },
    "colors": {
      "background": "#ffffff",
      "accent": "#3498db",
      "emphasis": "#e74c3c"
    }
  }
}
```

#### Director → Text Service

**For Content Generation (Full Context):**
```json
{
  "slide_number": 3,
  "narrative": "Key benefits of our platform",
  "topics": ["Speed", "Reliability", "Cost"],
  "available_space": {"width": 30, "height": 14, "unit": "grids"},

  "theme_config": {
    "theme_id": "executive",
    "fonts": {
      "heading": {"family": "Inter", "size": 48, "weight": 800, "color": "#111827"},
      "body": {"family": "Inter", "size": 20, "weight": 400, "color": "#374151"}
    },
    "emphasis": {"color": "#dc2626", "weight": 700},
    "styling_mode": "css_classes"
  },

  "content_context": {
    "audience": {
      "audience_type": "executive",
      "complexity_level": "advanced",
      "max_sentence_words": 20,
      "avoid_jargon": false
    },
    "purpose": {
      "purpose_type": "persuade",
      "include_cta": true,
      "include_data": true,
      "emotional_tone": "enthusiastic",
      "structure_pattern": "problem_solution"
    },
    "time": {
      "duration_minutes": 15
    }
  }
}
```

**For Simple Element:**
```json
{
  "element_type": "title",
  "content": "Transform Your Business",
  "theme_config": {
    "fonts": {
      "heading": {"family": "Montserrat", "size": 44, "color": "#2c3e50"}
    }
  }
}
```
**Or (when frontend controls styling):**
```json
{
  "element_type": "title",
  "content": "Transform Your Business"
}
```
→ Text Service returns plain text or minimal HTML, frontend applies theme.

#### Text Service → Director (Response)

```json
{
  "content": "<h2 style='font-family: Montserrat...'>...</h2>",
  "metadata": {
    "theme_applied": true,
    "theme_id": "custom-corporate",
    "audience_type": "professional",
    "content_density": 1.0
  }
}
```

### 4.6 Contract Summary Table

| Source | Destination | Data | Required? |
|--------|-------------|------|-----------|
| Frontend | Layout Service | User selections (theme, audience, purpose, time) | Required |
| Layout Service | Director | `theme_id`, `content_context`, `available_space` | Required |
| Director | Text Service | `theme_config` (full), `content_context`, `styling_mode` | Required |
| Text Service | Director | Styled HTML + metadata | Required |
| Layout Service | Frontend | Theme CSS, box styling | Required |
| Frontend | (direct) | Theme class swap on presentation container | N/A |

### 4.7 Who Controls What

| Aspect | Controlled By | Can Override After Generation? |
|--------|--------------|--------------------------------|
| **THEME (Visual)** | | |
| Theme presets | Layout Service | Yes - instant CSS swap |
| Custom themes | Layout Service + Frontend | Yes - CSS swap |
| Theme selection | User via Frontend | Yes - anytime, instant |
| CSS class definitions | Layout Service | Yes - update CSS |
| Applying classes to HTML | Text Service | N/A (at generation time) |
| Overriding styles | Frontend | Yes - CSS swap |
| **CONTENT CONTEXT** | | |
| Audience type | User → Frontend → Director | No - requires regeneration |
| Purpose type | User → Frontend → Director | No - requires regeneration |
| Time/duration | User → Frontend → Director | No - requires regeneration |
| Content density | Derived from above | No - requires regeneration |
| Content text | Text Service | No - requires regeneration |

### 4.8 Theme Registry Synchronization

**CRITICAL**: All three services (Layout, Director, Text) MUST have identical theme registries.

```
┌─────────────────────────────────────────────────────────────────────┐
│                  THEME REGISTRY SYNC STRATEGY                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Option 1: Canonical Source (RECOMMENDED)                            │
│  ────────────────────────────────────────                            │
│  Layout Service hosts the canonical theme registry.                  │
│  Director and Text Service sync from Layout Service on startup.      │
│                                                                       │
│  Option 2: Config File                                               │
│  ───────────────────────                                             │
│  All services read from a shared config file or environment.        │
│  Deployments update all services simultaneously.                     │
│                                                                       │
│  Option 3: Embedded with Validation                                  │
│  ─────────────────────────────────                                   │
│  Each service has embedded presets.                                  │
│  A health check endpoint validates sync across services.            │
│                                                                       │
│  THEME REGISTRY CONTENTS:                                            │
│  ─────────────────────────                                           │
│  theme_id: "professional"                                            │
│    ├── typography: {hero_title, slide_title, slide_subtitle,        │
│    │                t1, t2, t3, t4}                                  │
│    └── colors: {primary, primary_dark, primary_light,               │
│                 accent, accent_dark, accent_light,                   │
│                 tertiary_1, tertiary_2, tertiary_3,                 │
│                 background, surface, border,                        │
│                 text_primary, text_secondary, text_muted,           │
│                 chart_1...chart_6}                                  │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.9 Implementation Checklist

**For Director Team:**
- [ ] Implement `THEME_REGISTRY` with all presets
- [ ] Expand `theme_id` → full `theme_config` before calling Text Service
- [ ] Include `styling_mode` in all Text Service requests
- [ ] Include `available_space` from Layout Service
- [ ] Build `content_context` from user inputs
- [ ] Add health check for theme registry sync

**For Layout Service Team:**
- [ ] Host canonical `THEME_REGISTRY`
- [ ] Generate CSS for each theme preset
- [ ] Apply box fills/borders using palette colors
- [ ] Provide `available_space` for each content area
- [ ] Enable theme class swap on presentation container
- [ ] Create sync endpoint for Director/Text Service

**For Text Service Team:**
- [ ] Support `styling_mode` parameter
- [ ] Output CSS classes when `styling_mode: "css_classes"`
- [ ] Use t1-t4 hierarchy for content elements
- [ ] Respect `content_context` for vocabulary/tone
- [ ] Include `theme_id` and `css_classes_used` in metadata
- [ ] Fallback to `"professional"` if no theme specified

**For Frontend Team:**
- [ ] Provide theme selector UI
- [ ] Collect audience/purpose/time before generation
- [ ] Implement theme class swap mechanism
- [ ] Show regeneration warning for audience/purpose/time changes
- [ ] Load theme CSS based on selected preset

---

## 5. Frontend Theme Switching

### 5.1 The Requirement

**User Story:** "I want to change my presentation's theme from Professional to Executive without regenerating all content."

This means:
- Content (words, bullets, structure) stays the same
- Visual styling (colors, fonts, sizes) changes
- Background colors change
- Must be fast (no LLM calls needed)

### 5.2 Two Approaches

#### Approach A: Inline Styles (Current Direction)

Text Service embeds styles in HTML:
```html
<h2 style="font-family: Inter; font-size: 42px; color: #1e3a5f;">
  Key Benefits
</h2>
```

**To change theme:**
1. Frontend must regex/parse HTML
2. Replace inline styles with new theme values
3. Complex and error-prone

**Pros:** Self-contained HTML, works anywhere
**Cons:** Hard to change theme after generation

#### Approach B: CSS Classes (More Flexible)

Text Service outputs semantic HTML:
```html
<h2 class="slide-heading">
  Key Benefits
</h2>
```

Frontend applies theme via CSS:
```css
/* Professional theme */
.slide-heading {
  font-family: Inter;
  font-size: 42px;
  color: #1e3a5f;
}

/* Switch to Executive theme - just swap CSS */
.slide-heading {
  font-family: Inter;
  font-size: 48px;
  color: #111827;
}
```

**To change theme:**
1. Swap CSS stylesheet
2. Instant, no HTML changes needed

**Pros:** Easy theme switching, clean separation
**Cons:** Requires CSS coordination, frontend must load styles

#### Approach C: Hybrid (Recommended)

Text Service supports BOTH modes:

**When `theme_config` is provided:**
→ Return HTML with inline styles (for specific styling needs)

**When `theme_config` is NOT provided or `use_css_classes: true`:**
→ Return HTML with CSS classes (for theme switching)

```python
# In request
{
  "narrative": "...",
  "styling_mode": "css_classes"  # or "inline_styles"
}
```

### 5.3 CSS Class Naming Convention

```css
/* Element classes */
.deckster-heading { }
.deckster-subheading { }
.deckster-body { }
.deckster-caption { }
.deckster-emphasis { }
.deckster-bullet-list { }

/* Slide type classes */
.deckster-hero-title { }
.deckster-section-number { }
.deckster-closing-message { }
.deckster-contact-info { }

/* Theme modifiers (frontend applies) */
.theme-professional .deckster-heading { color: #1e3a5f; }
.theme-executive .deckster-heading { color: #111827; }
.theme-children .deckster-heading { color: #7c3aed; }
```

### 5.4 Theme Switching Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  1. INITIAL GENERATION                                               │
│                                                                       │
│  User creates presentation with "professional" theme                 │
│  Director passes theme_config to Text Service                        │
│  Text Service returns HTML with CSS classes (styling_mode=css)       │
│  Layout Service applies "professional" CSS                           │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  2. USER CHANGES THEME TO "EXECUTIVE"                                │
│                                                                       │
│  User clicks "Change Theme" in Layout Service UI                     │
│  Frontend swaps CSS class on container:                              │
│    <div class="presentation theme-professional">                     │
│                      ↓                                               │
│    <div class="presentation theme-executive">                        │
│                                                                       │
│  All slides instantly update styling                                 │
│  NO regeneration needed                                              │
│  NO API calls needed                                                 │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.5 What Changes vs What Stays

| Aspect | Theme Change | Needs Regeneration? |
|--------|--------------|---------------------|
| Font family | ✅ Changes | No |
| Font size | ✅ Changes | No |
| Font color | ✅ Changes | No |
| Background color | ✅ Changes | No |
| Accent/emphasis color | ✅ Changes | No |
| Bullet style | ✅ Changes | No |
| Content text | ❌ Stays same | N/A |
| Number of bullets | ❌ Stays same | Would need regen |
| Layout structure | ❌ Stays same | Would need regen |
| Image content | ❌ Stays same | Would need regen |

---

## 6. Theme Models

### 6.1 FontSpec Model

```python
class FontSpec(BaseModel):
    """Typography specification for a text element type."""

    family: str = Field(
        default="Inter",
        description="Font family name (must be web-safe or loaded by frontend)"
    )
    size: int = Field(
        default=18,
        ge=10, le=120,
        description="Font size in pixels"
    )
    weight: int = Field(
        default=400,
        ge=100, le=900,
        description="Font weight (100=thin, 400=normal, 700=bold, 900=black)"
    )
    color: str = Field(
        default="#374151",
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Hex color code"
    )
    line_height: float = Field(
        default=1.5,
        ge=1.0, le=3.0,
        description="Line height as multiplier of font size"
    )

    def to_css(self) -> str:
        """Generate inline CSS style string."""
        return (
            f"font-family: {self.family}, sans-serif; "
            f"font-size: {self.size}px; "
            f"font-weight: {self.weight}; "
            f"color: {self.color}; "
            f"line-height: {self.line_height};"
        )
```

### 6.2 ThemeConfig Model (Extended)

```python
class ThemeConfig(BaseModel):
    """Complete theme configuration for visual styling."""

    theme_id: str = Field(
        default="professional",
        description="Theme identifier"
    )

    # Typography by element type
    fonts: Dict[str, FontSpec] = Field(
        default_factory=lambda: {
            "heading": FontSpec(size=42, weight=700, color="#1e3a5f", line_height=1.2),
            "subheading": FontSpec(size=28, weight=500, color="#374151", line_height=1.4),
            "body": FontSpec(size=18, weight=400, color="#4b5563", line_height=1.6),
            "caption": FontSpec(size=14, weight=400, color="#6b7280", line_height=1.4),
        }
    )

    # Colors
    background_color: str = Field(
        default="#ffffff",
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Default slide background"
    )
    hero_background_color: str = Field(
        default="#1e3a5f",
        description="Background for hero slides (H1, H2, H3)"
    )
    accent_color: str = Field(
        default="#3b82f6",
        description="Primary accent color"
    )

    # Emphasis
    emphasis: EmphasisConfig = Field(
        default_factory=lambda: EmphasisConfig(color="#3b82f6", weight=600)
    )

    # Bullets
    bullet_style: str = Field(
        default="disc",
        description="disc, circle, square, none"
    )

    # Matrix/Table styling
    matrix_header_color: str = Field(
        default="#1e3a5f",
        description="Header row background"
    )
    matrix_cell_colors: List[str] = Field(
        default_factory=lambda: ["#f3f4f6", "#e5e7eb"],
        description="Alternating cell colors"
    )

    # Styling mode
    styling_mode: str = Field(
        default="inline_styles",
        description="inline_styles or css_classes"
    )

    def get_font(self, element_type: str) -> FontSpec:
        """Get font spec for element type with fallback."""
        return self.fonts.get(element_type, self.fonts.get("body", FontSpec()))
```

### 6.3 EmphasisConfig Model

```python
class EmphasisConfig(BaseModel):
    """Configuration for emphasized/highlighted text."""

    color: str = Field(default="#3b82f6", pattern=r"^#[0-9A-Fa-f]{6}$")
    weight: int = Field(default=600, ge=100, le=900)
    style: Optional[str] = Field(default=None)  # underline, italic, or None

    def to_css(self) -> str:
        css = f"color: {self.color}; font-weight: {self.weight};"
        if self.style == "underline":
            css += " text-decoration: underline;"
        elif self.style == "italic":
            css += " font-style: italic;"
        return css
```

---

## 7. Theme Presets

### 7.1 Professional Theme

```python
PROFESSIONAL_THEME = ThemeConfig(
    theme_id="professional",
    fonts={
        "heading": FontSpec(family="Inter", size=42, weight=700, color="#1e3a5f", line_height=1.2),
        "subheading": FontSpec(family="Inter", size=28, weight=500, color="#374151", line_height=1.4),
        "body": FontSpec(family="Inter", size=18, weight=400, color="#4b5563", line_height=1.6),
        "caption": FontSpec(family="Inter", size=14, weight=400, color="#6b7280", line_height=1.4),
    },
    background_color="#ffffff",
    hero_background_color="#1e3a5f",
    accent_color="#3b82f6",
    emphasis=EmphasisConfig(color="#3b82f6", weight=600),
    bullet_style="disc"
)
```

### 7.2 Executive Theme

```python
EXECUTIVE_THEME = ThemeConfig(
    theme_id="executive",
    fonts={
        "heading": FontSpec(family="Inter", size=48, weight=800, color="#111827", line_height=1.1),
        "subheading": FontSpec(family="Inter", size=32, weight=500, color="#1f2937", line_height=1.3),
        "body": FontSpec(family="Inter", size=20, weight=400, color="#374151", line_height=1.5),
        "caption": FontSpec(family="Inter", size=16, weight=400, color="#4b5563", line_height=1.4),
    },
    background_color="#f9fafb",
    hero_background_color="#111827",
    accent_color="#dc2626",
    emphasis=EmphasisConfig(color="#dc2626", weight=700),
    bullet_style="square"
)
```

### 7.3 Educational Theme

```python
EDUCATIONAL_THEME = ThemeConfig(
    theme_id="educational",
    fonts={
        "heading": FontSpec(family="Inter", size=38, weight=600, color="#1e40af", line_height=1.3),
        "subheading": FontSpec(family="Inter", size=24, weight=500, color="#3b82f6", line_height=1.4),
        "body": FontSpec(family="Inter", size=18, weight=400, color="#1f2937", line_height=1.7),
        "caption": FontSpec(family="Inter", size=14, weight=400, color="#6b7280", line_height=1.4),
    },
    background_color="#ffffff",
    hero_background_color="#1e40af",
    accent_color="#059669",
    emphasis=EmphasisConfig(color="#059669", weight=600),
    bullet_style="disc"
)
```

### 7.4 Children Theme

```python
CHILDREN_THEME = ThemeConfig(
    theme_id="children",
    fonts={
        "heading": FontSpec(family="Comic Sans MS", size=44, weight=700, color="#7c3aed", line_height=1.3),
        "subheading": FontSpec(family="Comic Sans MS", size=28, weight=600, color="#ec4899", line_height=1.4),
        "body": FontSpec(family="Comic Sans MS", size=22, weight=400, color="#374151", line_height=1.8),
        "caption": FontSpec(family="Comic Sans MS", size=16, weight=400, color="#6b7280", line_height=1.5),
    },
    background_color="#fef3c7",  # Light yellow
    hero_background_color="#7c3aed",  # Purple
    accent_color="#f59e0b",  # Amber
    emphasis=EmphasisConfig(color="#f59e0b", weight=700),
    bullet_style="circle"
)
```

### 7.5 Preset Registry

```python
THEME_PRESETS: Dict[str, ThemeConfig] = {
    "professional": PROFESSIONAL_THEME,
    "executive": EXECUTIVE_THEME,
    "educational": EDUCATIONAL_THEME,
    "children": CHILDREN_THEME,
}

def get_theme(theme_id: str) -> ThemeConfig:
    """Get theme preset by ID with fallback to professional."""
    return THEME_PRESETS.get(theme_id, THEME_PRESETS["professional"])
```

---

## 8. Process Workflow

### 8.1 End-to-End Flow: New Presentation

```
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 1: User Creates Presentation in Layout Service                │
│                                                                       │
│  - User enters topic: "Quarterly Business Review"                   │
│  - User selects theme: "Executive"                                  │
│  - User indicates audience: "Leadership team" → executive           │
│  - Layout Service stores theme_id + audience_type                   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 2: Layout Service Sends to Director                           │
│                                                                       │
│  {                                                                   │
│    "topic": "Quarterly Business Review",                            │
│    "slide_count": 10,                                               │
│    "theme_id": "executive",                                         │
│    "audience": "executive",                                         │
│    "styling_mode": "css_classes"  // for easy theme switching       │
│  }                                                                   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 3: Director Orchestrates Generation                           │
│                                                                       │
│  For each slide:                                                     │
│  - Looks up theme preset (executive → ThemeConfig)                  │
│  - Looks up audience preset (executive → AudienceConfig)            │
│  - Calls Text Service with both configs                             │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 4: Text Service Generates Content                             │
│                                                                       │
│  - Uses audience_config for content density (4 bullets, concise)    │
│  - Uses styling_mode=css_classes (returns semantic HTML)            │
│  - Returns: <h2 class="deckster-heading">Q4 Results</h2>            │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 5: Layout Service Applies Theme Styles                        │
│                                                                       │
│  - Loads executive theme CSS                                         │
│  - Wraps presentation in <div class="theme-executive">              │
│  - CSS styles applied to all .deckster-* classes                    │
│  - User sees styled presentation                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 8.2 End-to-End Flow: Theme Change

```
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 1: User Clicks "Change Theme" in Layout Service               │
│                                                                       │
│  - Presentation already has content                                  │
│  - User selects new theme: "Professional"                           │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 2: Layout Service Updates Theme (NO API CALLS)                │
│                                                                       │
│  - Changes container class:                                          │
│      <div class="presentation theme-executive">                      │
│                        ↓                                             │
│      <div class="presentation theme-professional">                   │
│                                                                       │
│  - Loads professional theme CSS                                      │
│  - All slides instantly restyle                                      │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 3: Done!                                                       │
│                                                                       │
│  - No Director call                                                  │
│  - No Text Service call                                              │
│  - Instant update                                                    │
│  - Content unchanged, only styling changed                           │
└─────────────────────────────────────────────────────────────────────┘
```

### 8.3 When Regeneration IS Needed

| User Action | Needs Regeneration? | Why |
|-------------|---------------------|-----|
| Change theme | No | CSS swap only |
| Change font size | No | CSS update only |
| Change colors | No | CSS update only |
| Change audience | **YES** | Content density changes |
| Edit narrative | **YES** | Content changes |
| Add/remove slides | Partial | Only new slides |
| Change layout structure | **YES** | Multi-step structure changes |

---

## 9. Current State Analysis

### 9.1 Existing ThemeConfig (What We Have)

**Location:** `app/models/requests.py`

```python
class ThemeConfig(BaseModel):
    theme_id: str = Field(default="professional")
    text_primary: str = Field(default="#1f2937")
    text_secondary: str = Field(default="#374151")
    text_muted: str = Field(default="#6b7280")
    border_light: str = Field(default="#e5e7eb")
    box_gradients: List[Dict[str, str]] = Field(default_factory=list)
    matrix_colors: List[str] = Field(default_factory=list)
    char_multiplier: float = Field(default=1.0)
    max_bullets: int = Field(default=5)
    font_scale: float = Field(default=1.0)
```

### 9.2 What's Used vs Ignored

| Field | Used? | Where | Gap |
|-------|-------|-------|-----|
| `theme_id` | Partially | Image prompts only | Not used for text |
| `text_primary` | **NO** | - | Should apply to headings |
| `text_secondary` | **NO** | - | Should apply to body |
| `text_muted` | **NO** | - | Should apply to captions |
| `box_gradients` | Yes | Matrix layouts | OK |
| `matrix_colors` | Yes | Matrix layouts | OK |
| `char_multiplier` | **NO** | - | Should affect density |
| `max_bullets` | **NO** | - | Should limit bullets |
| `font_scale` | **NO** | - | Should scale fonts |

### 9.3 The Gap Summary

1. **Text colors are hardcoded** - `#1e3a5f` for headings everywhere
2. **Font sizes are hardcoded** - `42px` headings, `18px` body
3. **No audience consideration** - Same density for kids and executives
4. **No CSS class mode** - All inline styles, hard to change
5. **No frontend coordination** - Theme switching requires regeneration

---

## 10. Implementation Considerations

### 10.1 Files to Create

| File | Purpose |
|------|---------|
| `app/models/theme_models.py` | FontSpec, EmphasisConfig, ThemeConfig, AudienceConfig |
| `app/core/theme/__init__.py` | Module exports |
| `app/core/theme/presets.py` | Theme presets registry |
| `app/core/theme/audience_presets.py` | Audience presets registry |
| `app/core/theme/styler.py` | HTML styling logic (inline vs CSS classes) |

### 10.2 Files to Modify

| File | Changes |
|------|---------|
| `app/models/requests.py` | Import new ThemeConfig |
| `app/core/slides/*.py` | Use theme for styling |
| `app/core/hero/*.py` | Use theme for hero slides |
| `app/api/slides_routes.py` | Accept theme_config, audience_config |

### 10.3 Backward Compatibility

| Scenario | Behavior |
|----------|----------|
| No theme_config | Use professional preset |
| No audience_config | Use professional audience |
| Old Director version | Works unchanged |
| Old theme_config format | Extend, don't break |

### 10.4 Rollout Strategy

1. **Phase A:** Add new models alongside existing (no breaking changes)
2. **Phase B:** Add `styling_mode` support (opt-in CSS classes)
3. **Phase C:** Update generators to use theme
4. **Phase D:** Coordinate with Layout Service for CSS class support
5. **Phase E:** Add audience support for content density

---

## 11. Summary

### 11.1 The Four Dimensions

| Dimension | What It Controls | Who Controls | Can Change After Generation? |
|-----------|-----------------|--------------|------------------------------|
| **Theme** | Visual styling (fonts, colors, backgrounds) | Layout Service → Director → Text Service | **Yes** - CSS swap, instant |
| **Audience** | Content complexity, vocabulary | User → Director → Text Service | No - needs regeneration |
| **Purpose** | Content focus, structure, CTAs | User → Director → Text Service | No - needs regeneration |
| **Time** | Content depth, slide count, bullets | User → Director → Text Service | No - needs regeneration |

### 11.2 The Four Parties

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FOUR-PARTY ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   ┌──────────────┐        ┌──────────────────┐                      │
│   │   FRONTEND   │◄──────►│  LAYOUT SERVICE  │                      │
│   │              │        │                  │                      │
│   │ • User UI    │        │ • Theme registry │                      │
│   │ • Theme pick │        │ • Theme CSS      │                      │
│   │ • CSS swap   │        │ • Box styling    │                      │
│   └──────────────┘        │ • Grid layouts   │                      │
│                           └────────┬─────────┘                      │
│                                    │                                │
│                           theme_id, content_context, available_space│
│                                    │                                │
│                                    ▼                                │
│                           ┌──────────────────┐                      │
│                           │     DIRECTOR     │                      │
│                           │                  │                      │
│                           │ • Orchestrator   │                      │
│                           │ • Expand theme   │                      │
│                           │ • Build context  │                      │
│                           └────────┬─────────┘                      │
│                                    │                                │
│                           theme_config (full), content_context,     │
│                           available_space, styling_mode             │
│                                    │                                │
│                                    ▼                                │
│                           ┌──────────────────┐                      │
│                           │   TEXT SERVICE   │                      │
│                           │                  │                      │
│                           │ • Content gen    │                      │
│                           │ • Space calc     │                      │
│                           │ • CSS classes    │                      │
│                           └──────────────────┘                      │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 11.3 Frontend Theme Switching Capabilities

```
┌─────────────────────────────────────────────────────────────────────┐
│              WHAT FRONTEND CAN CHANGE AFTER GENERATION               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ✅ INSTANT CHANGE (CSS swap, no regeneration, no API call):        │
│  ───────────────────────────────────────────────────────────         │
│  • Theme preset        Professional → Executive → Children           │
│  • Font families       Inter → Georgia → Comic Sans                  │
│  • Font sizes          (within t1-t4 hierarchy)                      │
│  • All colors          Primary, accent, text, background             │
│  • Font weights        400 → 700                                     │
│  • Line heights        1.4 → 1.6                                     │
│  • Box fills           Surface colors, tertiary colors               │
│  • Box borders         Border colors, widths                         │
│  • Bullet styles       Disc → Square → Custom                        │
│  • Background colors   Slide backgrounds                             │
│                                                                       │
│  HOW IT WORKS:                                                       │
│  ─────────────                                                       │
│  <div class="presentation theme-professional">                       │
│                     ↓  (user clicks "Executive")                    │
│  <div class="presentation theme-executive">                          │
│                                                                       │
│  ❌ REQUIRES REGENERATION (API call needed):                        │
│  ─────────────────────────────────────────────                       │
│  • Audience type       kids_young → executive                        │
│  • Purpose type        inform → persuade                             │
│  • Time/duration       5 min → 30 min                                │
│  • Content text        (the actual words)                            │
│  • Number of bullets   3 bullets → 6 bullets                         │
│  • Layout structure    2-column → 3-column                           │
│  • Image content       (AI-generated images)                         │
│                                                                       │
│  WHY THE DIFFERENCE?                                                 │
│  ───────────────────                                                 │
│  Theme = HOW content looks → CSS handles visuals                     │
│  Content Context = WHAT is said → LLM must regenerate                │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 11.4 What Each Dimension Affects

| Aspect | Theme | Audience | Purpose | Time |
|--------|-------|----------|---------|------|
| Font family | ✅ | | | |
| Font size | ✅ | | | |
| Colors | ✅ | | | |
| Background | ✅ | | | |
| Bullet style | ✅ | | | |
| Box fills/borders | ✅ | | | |
| Vocabulary level | | ✅ | | |
| Jargon usage | | ✅ | | |
| Sentence length | | ✅ | | |
| Max bullets | | ✅ | | ✅ |
| CTA inclusion | | | ✅ | |
| Emotional tone | | | ✅ | |
| Content structure | | | ✅ | |
| Total slides | | | | ✅ |
| Include examples | | | | ✅ |

### 11.5 Key Architectural Decisions

1. **Theme is the ONLY dimension that can change after generation** - CSS class mode enables instant theme switching without API calls
2. **Audience, Purpose, and Time affect CONTENT** - changing these requires full regeneration (LLM calls)
3. **Theme applies to ALL slide types** - Hero (H1, H2, H3), Content (C1), I-Series (I1-I4), and all Elements
4. **CSS classes over inline styles** - For editor use, generate with `styling_mode: "css_classes"` to enable theme switching
5. **Inline styles for exports** - For PDF/PPTX exports, use `styling_mode: "inline_styles"` for self-contained output
6. **Three services need same theme registry** - Layout, Director, Text Service must have synchronized theme presets
7. **ContentContext combines non-visual dimensions** - AudienceConfig + PurposeConfig + TimeConfig
8. **Backward compatible** - old requests without these fields work unchanged with defaults

### 11.6 Quick Reference: Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    GENERATION TIME FLOW                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  User → Frontend:                                                    │
│    • Select theme (or customize colors/fonts)                       │
│    • Indicate audience (kids, professionals, executives)            │
│    • Specify purpose (inform, persuade, educate)                    │
│    • Set duration (5 min, 20 min, 45 min)                           │
│                                                                       │
│  Frontend → Layout Service:                                          │
│    • theme_id (or custom theme object)                              │
│    • audience_type, purpose_type, duration_minutes                  │
│    • layout choices (slides, grids)                                 │
│                                                                       │
│  Layout Service → Director:                                          │
│    • theme_id (Layout has the registry)                             │
│    • content_context (audience + purpose + time)                    │
│    • available_space (grid dimensions for each content area)        │
│                                                                       │
│  Director → Text Service:                                            │
│    • theme_config (FULL - typography + colors)                      │
│    • content_context (audience + purpose + time)                    │
│    • available_space (for multi-step generation)                    │
│    • styling_mode: "css_classes" | "inline_styles"                  │
│                                                                       │
│  Text Service → Director:                                            │
│    • content (HTML with CSS classes or inline styles)               │
│    • metadata {theme_id, styling_mode, css_classes_used}            │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    POST-GENERATION THEME SWITCH                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  User clicks "Change Theme" in Frontend:                            │
│                                                                       │
│    1. Frontend swaps CSS class on container:                        │
│       <div class="presentation theme-professional">                 │
│                          ↓                                          │
│       <div class="presentation theme-executive">                    │
│                                                                       │
│    2. Layout Service updates box fills/borders from new palette     │
│                                                                       │
│    3. DONE - instant, no API calls, no regeneration                 │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 12. Cross-Service Coordination Log

This section documents the cross-team alignment process for the theme system implementation.

---

### 12.1 Layout Service Response (December 2024)

**Status:** ✅ CONFIRMED ALIGNMENT

Layout Service team reviewed Section 4.3.2 and confirmed they can fulfill all responsibilities:

| Responsibility | Status | Notes |
|---------------|--------|-------|
| Host canonical `THEME_REGISTRY` | ✅ Ready | 4 themes with full palettes |
| Provide `available_space` | ✅ Ready | All 26 layouts have content area dimensions |
| Generate theme CSS | ✅ Ready | CSS custom properties ready |
| Enable instant theme switching | ✅ Ready | CSS class swap, no regeneration |
| Add chart colors (chart_1-6) | 🔄 Planned | Will add to complete 20+ key palette |
| Add tertiary colors (tertiary_1-3) | 🔄 Planned | Will add to complete 20+ key palette |

**Sync Endpoints Available:**
- `GET /api/themes/{theme_id}` - Per-theme lookup (exists now)
- `GET /api/themes/sync` - Bulk sync (can add if preferred)

**Questions Raised:**
1. Prefer per-theme or bulk sync endpoint?
2. Color key naming: camelCase or snake_case?
3. What's Text Service fallback if Layout Service is unreachable at startup?

**Reference:** `layout_builder_main/v7.5-main/docs/THEME_SYSTEM_RESPONSE.md`

---

### 12.2 Text Service Response & Guidance

**From:** Text Service Team
**Date:** December 2024
**Status:** ✅ APPROVED TO PROCEED

---

**Layout Service team: Thank you for confirming alignment. We're pleased the architecture works for your service. Below are our answers and guidance.**

---

#### Answers to Your Questions

**Q1: Prefer per-theme or bulk sync endpoint?**

> **A: Bulk sync preferred (`GET /api/themes/sync`)**
>
> Text Service will call this once at startup to cache all theme definitions. This is more efficient than multiple per-theme calls and ensures we have the complete registry available immediately.
>
> **Suggested response format:**
> ```json
> {
>   "themes": {
>     "professional": { "typography": {...}, "colors": {...} },
>     "executive": { "typography": {...}, "colors": {...} },
>     "educational": { "typography": {...}, "colors": {...} },
>     "children": { "typography": {...}, "colors": {...} }
>   },
>   "version": "1.0.0",
>   "last_updated": "2024-12-20T00:00:00Z"
> }
> ```

---

**Q2: Color key naming: camelCase or snake_case?**

> **A: `snake_case`**
>
> Text Service uses Python, where `snake_case` is the convention. This ensures clean Pydantic model mapping without field aliases.
>
> **Use these keys:**
> ```
> primary, primary_dark, primary_light
> accent, accent_dark, accent_light
> tertiary_1, tertiary_2, tertiary_3
> background, surface, border
> text_primary, text_secondary, text_muted
> chart_1, chart_2, chart_3, chart_4, chart_5, chart_6
> ```

---

**Q3: What's Text Service fallback if Layout Service is unreachable at startup?**

> **A: Embedded `THEME_PRESETS` fallback**
>
> Text Service maintains a built-in `THEME_PRESETS` dictionary as a fallback:
>
> ```python
> # app/core/theme/presets.py
> THEME_PRESETS = {
>     "professional": {
>         "typography": {...},
>         "colors": {
>             "primary": "#1e3a5f",
>             "accent": "#3b82f6",
>             # ... full palette
>         }
>     },
>     # ... other themes
> }
> ```
>
> **Behavior:**
> 1. On startup, Text Service attempts `GET /api/themes/sync`
> 2. If successful → cache Layout Service themes (canonical source)
> 3. If failed → use embedded `THEME_PRESETS` + log warning
> 4. Periodic refresh every 5 minutes (configurable)
>
> **Important:** The embedded presets should match Layout Service's registry. We recommend both services validate their registries match during CI/CD.

---

#### Additional Guidance

**1. Theme Version Tracking**

Include a `version` field in your sync response. Text Service will cache this and include it in response metadata so Director can verify theme consistency:

```json
{
  "metadata": {
    "theme_id": "professional",
    "theme_version": "1.0.0",
    "theme_source": "layout_service"  // or "fallback"
  }
}
```

**2. Adding Chart & Tertiary Colors**

When adding the missing color keys, please follow this structure:

```json
{
  "colors": {
    // ... existing colors ...

    // Tertiary (for groupings, borders, dividers)
    "tertiary_1": "#...",  // Lightest
    "tertiary_2": "#...",  // Medium
    "tertiary_3": "#...",  // Darkest

    // Charts (for data visualization)
    "chart_1": "#...",     // Primary chart color
    "chart_2": "#...",
    "chart_3": "#...",
    "chart_4": "#...",
    "chart_5": "#...",
    "chart_6": "#..."      // 6th color for max variety
  }
}
```

**3. CSS Class Naming Alignment**

Text Service will output these CSS classes when `styling_mode: "css_classes"`:

```html
<h3 class="deckster-t1">...</h3>
<p class="deckster-t4">...</p>
<span class="deckster-emphasis">...</span>
<ul class="deckster-bullets">...</ul>
```

Please ensure your theme CSS defines these classes:
- `.deckster-t1`, `.deckster-t2`, `.deckster-t3`, `.deckster-t4`
- `.deckster-emphasis`
- `.deckster-bullets`, `.deckster-bullet-item`

---

#### Confirmation

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TEXT SERVICE TEAM DECISION                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ✅ APPROVED: Layout Service may proceed with implementation         │
│                                                                       │
│  Action Items for Layout Service:                                    │
│  ─────────────────────────────────                                   │
│  1. Add `GET /api/themes/sync` endpoint (bulk)                      │
│  2. Use snake_case for all color keys                               │
│  3. Add chart_1-6 and tertiary_1-3 to palettes                      │
│  4. Include version field in sync response                          │
│  5. Define .deckster-* CSS classes per theme                        │
│                                                                       │
│  Action Items for Text Service:                                      │
│  ─────────────────────────────────                                   │
│  1. Implement theme sync on startup                                  │
│  2. Maintain embedded THEME_PRESETS as fallback                     │
│  3. Add theme_version to response metadata                          │
│  4. Support styling_mode parameter                                   │
│                                                                       │
│  Next Step: Layout Service implements sync endpoint                  │
│             Text Service integrates once endpoint is ready           │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 12.3 Director Response & Text Service Answers (December 2024)

**Director's Document:** `agents/director_agent/v4.0/docs/THEME_SYSTEM_DIRECTOR_RESPONSE.md`

**Status:** ✅ CONFIRMED ALIGNMENT

Director team reviewed THEME_SYSTEM_DESIGN.md v2.1 and confirmed:

| Aspect | Status | Notes |
|--------|--------|-------|
| Four-dimension approach | ✅ Aligned | Maps to existing strawman extraction |
| Phase 1 (Foundation) | 🚀 Starting | Ready in 1 week, no external dependencies |
| Phase 2 (Text Integration) | ⏳ Waiting | Depends on Text Service parameter support |
| Phase 3 (Layout Integration) | ⏳ Waiting | Depends on Layout Service endpoints |
| Backward compatibility | ✅ 100% | Existing presentations continue working |
| Graceful degradation | ✅ Confirmed | Will omit params if Text Service doesn't support |

**Director's 3-Phase Plan:**
- **Phase 1**: ThemeConfig, ContentContext models + embedded registry (1 week)
- **Phase 2**: Text Service client updates (3-5 days after Text ready)
- **Phase 3**: Layout Service sync + CSS mode (3-5 days after Layout ready)

---

#### Text Service Answers to Director's Questions

**Q1: Parameter Support Status (CRITICAL)**

> **Does Text Service v1.2.2 currently support `theme_config`, `content_context`, `styling_mode`, `available_space`?**

| Parameter | Supported in v1.2.2? | Implementation Status |
|-----------|---------------------|----------------------|
| `theme_config` | ❌ Not yet | Designed, ~2 weeks to implement |
| `content_context` | ❌ Not yet | Designed, ~2 weeks to implement |
| `styling_mode` | ❌ Not yet | Designed, ~1 week to implement |
| `available_space` | ❌ Not yet | Designed, ~2 weeks to implement (multi-step gen) |

**Text Service Implementation Timeline:**
```
┌─────────────────────────────────────────────────────────────────────┐
│                TEXT SERVICE IMPLEMENTATION PLAN                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Week 1: Foundation                                                  │
│  ─────────────────                                                   │
│  • Add theme_config to request models (Pydantic)                    │
│  • Add content_context to request models                            │
│  • Add styling_mode parameter support                                │
│  • Implement CSS class output mode                                   │
│                                                                       │
│  Week 2: Multi-Step Generation                                       │
│  ─────────────────────────────                                       │
│  • Add available_space parameter                                     │
│  • Implement Phase 1 (Structure Analysis)                           │
│  • Implement Phase 2 (Space Calculation)                            │
│  • Update Phase 3 (Content Generation) with theme/context           │
│                                                                       │
│  Week 3: Integration & Testing                                       │
│  ────────────────────────────                                        │
│  • Theme registry sync with Layout Service                          │
│  • End-to-end testing with Director                                 │
│  • Deploy v1.3.0                                                    │
│                                                                       │
│  Target: Text Service v1.3.0 ready in ~3 weeks                      │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

**Recommendation for Director:** Proceed with Phase 1 immediately. Phase 2 integration can begin in ~2 weeks when Text Service has basic parameter support.

---

**Q2: Parameter Handling Behavior**

> **If Director passes parameters that Text Service doesn't yet support, what happens?**

**Answer: Option A - Ignore unknown parameters (backward compatible)**

Text Service uses Pydantic with `extra = "ignore"` configuration. Unknown fields are silently ignored, allowing:
- Director can start sending new params immediately
- Text Service will use them once implemented
- No breaking changes during rollout

```python
# Current behavior in app/models/requests.py
class UnifiedSlideRequest(BaseModel):
    class Config:
        extra = "ignore"  # Unknown fields silently ignored
```

**Director can safely pass `theme_config`, `content_context`, etc. to v1.2.2** - they will be ignored until v1.3.0.

---

**Q3: Content Context Usage**

> **How will Text Service use `content_context` to adapt content generation?**

**Full mapping documented in:** `MULTI_STEP_CONTENT_STRUCTURE.md` Section 3.4

| Field | Text Service Behavior |
|-------|----------------------|
| `audience.audience_type` | Controls vocabulary level, max bullets, jargon usage |
| `audience.complexity_level` | Adjusts sentence complexity (simple → advanced) |
| `audience.max_sentence_words` | Enforces max words per sentence (kids: 8, executive: 15) |
| `audience.avoid_jargon` | Replaces technical terms with plain language |
| `purpose.purpose_type` | Sets structure pattern (inform→standard, persuade→problem_solution) |
| `purpose.include_cta` | Adds call-to-action on closing slides |
| `purpose.emotional_tone` | Adjusts language warmth (formal → enthusiastic) |
| `time.duration_minutes` | Controls content depth (5min: headlines, 30min: detailed) |

**Example Impact:**
```
audience_type: "kids_young" + purpose_type: "educate"
→ Max 3 bullets, simple words, no jargon, pedagogical structure

audience_type: "executive" + purpose_type: "persuade"
→ Max 4 bullets, data-driven, industry terms OK, problem→solution→CTA
```

---

**Q4: CSS Classes Output Format**

> **Confirm the CSS class naming convention Text Service will use.**

**CONFIRMED ✅** - Text Service will output exactly these classes when `styling_mode: "css_classes"`:

```html
<!-- Typography hierarchy -->
<h3 class="deckster-t1">Content Heading</h3>
<h4 class="deckster-t2">Section Subheading</h4>
<h5 class="deckster-t3">Sub-section</h5>
<p class="deckster-t4">Body text and bullets</p>

<!-- Emphasis and structure -->
<span class="deckster-emphasis">Highlighted text</span>
<strong class="deckster-bold">Bold text</strong>
<ul class="deckster-bullets">
  <li class="deckster-bullet-item">Bullet point</li>
</ul>

<!-- Container -->
<div class="deckster-content">
  <!-- All content wrapped -->
</div>
```

**Full CSS Class List:**
- `.deckster-t1`, `.deckster-t2`, `.deckster-t3`, `.deckster-t4` (typography)
- `.deckster-emphasis`, `.deckster-bold` (inline styling)
- `.deckster-bullets`, `.deckster-bullet-item` (lists)
- `.deckster-content` (container)
- `.deckster-heading`, `.deckster-subheading` (aliases)

---

**Q5: Theme Config Structure**

> **Does the typography + colors structure match what Text Service expects?**

**CONFIRMED ✅** - Structure matches. Minor addition requested:

**Director's proposed structure:** ✅ Correct
```json
{
  "theme_id": "executive",
  "typography": {
    "t1": {"size": 32, "weight": 600, "color": "#111827", "family": "Inter"},
    ...
  },
  "colors": {
    "primary": "#111827",
    "accent": "#dc2626",
    ...
  }
}
```

**Enhancement requested:** Add `line_height` to typography specs:
```json
{
  "t1": {
    "size": 32,
    "weight": 600,
    "color": "#111827",
    "family": "Inter",
    "line_height": 1.3  // ← ADD THIS
  }
}
```

**Default line_height values if not provided:**
- t1: 1.2 (headings, tighter)
- t2: 1.3
- t3: 1.4
- t4: 1.5 (body text, looser)

---

#### Confirmation

```
┌─────────────────────────────────────────────────────────────────────┐
│              TEXT SERVICE RESPONSE TO DIRECTOR                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ✅ APPROVED: Director may proceed with Phase 1 immediately          │
│                                                                       │
│  Timeline Alignment:                                                 │
│  ───────────────────                                                 │
│  • Director Phase 1: Now → 1 week (Foundation)                      │
│  • Text Service v1.3.0: Now → 3 weeks (Full parameter support)      │
│  • Director Phase 2: Week 2-3 (Integration with Text Service)       │
│  • Director Phase 3: Week 3-4 (Integration with Layout Service)     │
│                                                                       │
│  Answers Summary:                                                    │
│  ────────────────                                                    │
│  Q1: Parameters NOT supported in v1.2.2, ~3 weeks for v1.3.0       │
│  Q2: Option A - unknown params ignored (backward compatible)        │
│  Q3: Full content_context mapping in MULTI_STEP doc Section 3.4    │
│  Q4: CONFIRMED - .deckster-* classes as documented                  │
│  Q5: CONFIRMED - structure matches, add line_height to typography   │
│                                                                       │
│  Next Step: Director proceeds with Phase 1                          │
│             Text Service begins v1.3.0 implementation               │
│             Sync call in ~1 week to align Phase 2 timing            │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 12.4 Frontend Response & Text Service Answers (December 2024)

**Frontend's Document:** `/Users/pk1980/Documents/Software/deckster-frontend/docs/FRONTEND_THEME_RESPONSE.md`

**Status:** ✅ CONFIRMED ALIGNMENT (with clarifications provided)

Frontend team reviewed THEME_SYSTEM_DESIGN.md v2.1 and confirmed:

| Aspect | Status | Notes |
|--------|--------|-------|
| Visual theme switching | ✅ Implemented | Instant, no regeneration |
| Color customization | ✅ Ready to expand | 14 → 25 colors committed |
| CSS-based approach | ✅ Aligned | Via postMessage to viewer |
| Theme presets | ✅ 4 presets ready | With custom override support |
| Real-time preview | ✅ Implemented | Preview before apply |

**Needs Clarification:**
- Theme ID mapping (frontend vs backend naming)
- Audience/Purpose/Time collection (not in current UI)
- CSS class vs postMessage approach
- Typography controls scope

---

#### Text Service Answers to Frontend's Questions

**Q1: Theme ID Mapping Strategy**

> **Frontend themes: `corporate-blue`, `elegant-emerald`, `vibrant-orange`, `dark-mode`**
> **Backend themes: `professional`, `executive`, `educational`, `children`**
> **Is `theme_id` purely visual or does it imply audience/purpose settings?**

**Answer: Theme is VISUAL ONLY. Audience/Purpose/Time are SEPARATE dimensions.**

```
┌─────────────────────────────────────────────────────────────────────┐
│            THEME vs CONTENT CONTEXT: SEPARATE CONCEPTS               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  THEME (Visual) ─────────────────────────────────────────────────    │
│  • Controls: colors, fonts, backgrounds, visual styling              │
│  • CAN change after generation (CSS swap)                           │
│  • Frontend owns visual theme presets                               │
│  • User can pick any visual theme at any time                       │
│                                                                       │
│  CONTENT CONTEXT (Non-Visual) ───────────────────────────────────    │
│  • Controls: vocabulary, bullet count, tone, structure              │
│  • CANNOT change after generation (needs regeneration)              │
│  • Collected at presentation creation                               │
│  • Affects what content the LLM generates                           │
│                                                                       │
│  ───────────────────────────────────────────────────────────────     │
│  A user CAN have:                                                    │
│  • Visual theme: "corporate-blue" (frontend preset)                  │
│  • Audience: "executive"                                             │
│  • Purpose: "persuade"                                               │
│  • Time: 15 minutes                                                  │
│                                                                       │
│  These are ORTHOGONAL - any combination is valid.                   │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

**Recommendation: Option C - Keep frontend theme IDs independent**

- Frontend themes: `corporate-blue`, `elegant-emerald`, etc. (visual presets)
- Backend themes: Used for default color palettes if frontend doesn't customize
- User can apply ANY visual theme to content generated with ANY audience/purpose

**Theme ID Mapping Layer (optional, for defaults):**

| Frontend Theme | Suggested Content Context Default |
|----------------|-----------------------------------|
| `corporate-blue` | audience: professional |
| `elegant-emerald` | audience: professional |
| `vibrant-orange` | audience: general |
| `dark-mode` | (any - just visual preference) |

**Key Point:** Frontend should NOT infer audience/purpose from theme selection. These are separate user choices.

---

**Q2: Audience/Purpose/Time Collection**

> **When should these be collected? What UI components? Regeneration warning?**

**Answer: Collect at NEW PRESENTATION creation, with edit capability (+ warning)**

```
┌─────────────────────────────────────────────────────────────────────┐
│               AUDIENCE/PURPOSE/TIME COLLECTION UX                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  WHEN TO COLLECT:                                                    │
│  ────────────────                                                    │
│  • At NEW PRESENTATION creation (modal or wizard step)              │
│  • BEFORE first content generation                                   │
│  • Editable later via "Presentation Settings" (with warning)        │
│                                                                       │
│  RECOMMENDED UI COMPONENTS:                                          │
│  ───────────────────────────                                         │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  New Presentation                                            │    │
│  │                                                              │    │
│  │  Who is your audience?                                       │    │
│  │  ┌─────────────────────────────────────────────────┐        │    │
│  │  │ 👔 Professionals            ▼                    │        │    │
│  │  └─────────────────────────────────────────────────┘        │    │
│  │  Options: Kids (6-10), Kids (10-14), High School,           │    │
│  │           College, Professionals, Executives                 │    │
│  │                                                              │    │
│  │  What's the purpose?                                         │    │
│  │  ┌─────────────────────────────────────────────────┐        │    │
│  │  │ 💡 Inform                   ▼                    │        │    │
│  │  └─────────────────────────────────────────────────┘        │    │
│  │  Options: Inform, Educate, Persuade, Entertain,             │    │
│  │           Inspire, Report                                    │    │
│  │                                                              │    │
│  │  How long is your presentation?                              │    │
│  │  ┌───────────────────────────────────────┐                  │    │
│  │  │ ○───────●──────────────────────○      │   15 min        │    │
│  │  │ 5 min                        60 min   │                  │    │
│  │  └───────────────────────────────────────┘                  │    │
│  │                                                              │    │
│  │  Visual Theme: [Corporate Blue ▼]  (can change anytime)     │    │
│  │                                                              │    │
│  │              [Create Presentation]                          │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  EDIT AFTER CREATION (with warning):                                │
│  ─────────────────────────────────────                               │
│  User clicks "Edit Settings" on existing presentation:              │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  ⚠️ Changing these settings will regenerate all content     │    │
│  │                                                              │    │
│  │  Current: Professionals, Inform, 15 min                     │    │
│  │  New:     Executives, Persuade, 20 min                      │    │
│  │                                                              │    │
│  │  This cannot be undone. Continue?                           │    │
│  │                                                              │    │
│  │        [Cancel]    [Regenerate Content]                     │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  STORAGE:                                                            │
│  ────────                                                            │
│  Store in presentation metadata:                                     │
│  {                                                                   │
│    "content_context": {                                              │
│      "audience_type": "professional",                               │
│      "purpose_type": "inform",                                      │
│      "duration_minutes": 15                                         │
│    }                                                                 │
│  }                                                                   │
│  Pass to Director on each generation request.                       │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

**UI Placement:** Can be part of existing "New Presentation" flow or a dedicated "Presentation Setup" step.

**Defaults (if user skips):**
- Audience: `professional`
- Purpose: `inform`
- Time: `15` minutes

---

**Q3: CSS Class vs PostMessage Approach**

> **Frontend uses postMessage to viewer iframe. Backend suggests CSS class swap. Which approach?**

**Answer: Option B - PostMessage works, viewer uses CSS classes internally**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    HYBRID APPROACH (RECOMMENDED)                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Frontend (ThemePanel)                                               │
│        │                                                             │
│        │ postMessage({ action: 'setTheme', params: {                │
│        │   themeId: 'corporate-blue',                               │
│        │   colorOverrides: { primary: '#ff0000' }                   │
│        │ }})                                                        │
│        ▼                                                             │
│  Viewer Iframe                                                       │
│        │                                                             │
│        │ Internally applies:                                        │
│        │ 1. CSS class: <div class="presentation theme-corporate-blue">
│        │ 2. CSS variables: --color-primary: #ff0000;                │
│        │ 3. .deckster-* classes styled via theme CSS                │
│        ▼                                                             │
│  Content renders with theme colors                                   │
│                                                                       │
│  ───────────────────────────────────────────────────────────────     │
│                                                                       │
│  WHY THIS WORKS:                                                     │
│  • Frontend: No architecture change (keep postMessage)              │
│  • Viewer: Uses CSS classes internally (aligns with backend spec)   │
│  • Text Service: Outputs .deckster-* classes in HTML                │
│  • Viewer CSS: Maps .deckster-* classes to theme colors             │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

**No changes needed to frontend postMessage approach.** Viewer iframe should:
1. Receive theme via postMessage
2. Apply CSS class to presentation container
3. Use CSS custom properties (`--color-primary`, etc.)
4. Style `.deckster-*` classes using those properties

---

**Q4: Typography Controls**

> **Should frontend control typography (fonts, sizes) or just colors?**

**Answer: Option B for now - Colors only in frontend. Expand later if needed.**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TYPOGRAPHY RESPONSIBILITY                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  CURRENT (Phase 1):                                                  │
│  ─────────────────                                                   │
│  • Frontend: Controls colors only (ThemePanel)                      │
│  • Backend: Generates HTML with .deckster-t1, .deckster-t4 classes │
│  • Viewer CSS: Defines font sizes per class                         │
│                                                                       │
│  Example CSS in viewer:                                              │
│  .deckster-t1 { font-size: 32px; font-weight: 600; }               │
│  .deckster-t4 { font-size: 18px; font-weight: 400; }               │
│                                                                       │
│  Typography is "baked in" per theme - not user-customizable.        │
│                                                                       │
│  ───────────────────────────────────────────────────────────────     │
│                                                                       │
│  FUTURE (Phase 2, optional):                                         │
│  ─────────────────────────────                                       │
│  • Add "Typography" section to ThemePanel                           │
│  • Controls: Font family, size scale, line height                   │
│  • Override via CSS custom properties:                              │
│    --font-family-heading: "Georgia";                                │
│    --font-size-t1: 36px;                                            │
│                                                                       │
│  Only if user demand exists. Colors-only is sufficient for MVP.     │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

**For now:** Frontend focuses on color customization. Typography is handled by theme CSS in the viewer.

---

#### Additional Guidance for Frontend Team

**1. Color Palette Expansion (14 → 25)**

Your proposed expansion is correct. Ensure snake_case for all keys:

```typescript
// New colors to add
accent_light: string
accent_dark: string
tertiary_1: string
tertiary_2: string
tertiary_3: string
chart_1: string  // through chart_6
...
text_muted: string  // rename from footer_text
surface: string     // rename from background_alt
```

**2. Chart Colors Usage**

Chart colors are used by data visualization elements (charts, graphs). Frontend should:
- Include in theme presets (6 colors per theme)
- Pass to any charting library used in viewer
- Ensure good contrast and accessibility

**3. Theme Preset Updates**

When expanding presets, ensure each has all 25 colors defined:

```typescript
const THEME_PRESETS = {
  'corporate-blue': {
    // ... existing 14 colors ...
    // ADD:
    accent_light: '#fef3c7',
    accent_dark: '#b45309',
    tertiary_1: '#3b82f6',
    tertiary_2: '#60a5fa',
    tertiary_3: '#93c5fd',
    chart_1: '#3b82f6',
    chart_2: '#10b981',
    chart_3: '#f59e0b',
    chart_4: '#ef4444',
    chart_5: '#8b5cf6',
    chart_6: '#ec4899',
  }
}
```

---

#### Confirmation

```
┌─────────────────────────────────────────────────────────────────────┐
│              TEXT SERVICE RESPONSE TO FRONTEND                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ✅ APPROVED: Frontend may proceed with implementation              │
│                                                                       │
│  Answers Summary:                                                    │
│  ────────────────                                                    │
│  Q1: Theme is VISUAL ONLY - keep frontend IDs, separate from        │
│      Audience/Purpose/Time (which are content generation params)    │
│                                                                       │
│  Q2: Collect Audience/Purpose/Time at presentation creation.        │
│      Dropdowns + slider. Show regeneration warning if changed.      │
│      Store in presentation metadata, pass to Director.              │
│                                                                       │
│  Q3: Option B - Keep postMessage, viewer uses CSS classes           │
│      internally. No frontend architecture change needed.            │
│                                                                       │
│  Q4: Option B - Colors only for now. Typography via viewer CSS.     │
│      Can expand later if user demand exists.                        │
│                                                                       │
│  ───────────────────────────────────────────────────────────────     │
│                                                                       │
│  Action Items for Frontend:                                          │
│  ──────────────────────────                                          │
│  1. Expand color palette 14 → 25 (snake_case keys)                  │
│  2. Add Audience/Purpose/Time inputs to "New Presentation" flow    │
│  3. Add regeneration warning for post-creation context changes      │
│  4. Store content_context in presentation metadata                  │
│  5. Pass content_context to Director on generation requests         │
│                                                                       │
│  Action Items for Text Service:                                      │
│  ──────────────────────────────                                      │
│  1. Document exact content_context API field structure              │
│  2. Provide .deckster-* CSS class reference for viewer              │
│  3. Coordinate with Director on content_context passthrough         │
│                                                                       │
│  Next Step: Frontend proceeds with Phase 2 (color expansion)        │
│             Sync call to align on content_context API               │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

**Contact:** Text Service Team
**Document:** This file serves as the coordination record for all cross-service theme system alignment.

---

**Version:** 2.4 (Frontend Response Added)
**Date:** December 2024
**Lines:** ~3,150
