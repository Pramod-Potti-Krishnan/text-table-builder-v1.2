# Text Service Theming System Requirements

**Version**: 1.0
**Date**: December 2024
**Service**: Text/Table Builder (v1.2)
**Scope**: 34 template variants across C1 and L25 categories

---

## Overview

This document defines the theming system architecture for the Text Service. The system comprises **four independent constructs** that can be combined in any configuration:

1. **Theme** - Visual identity (fonts, colors, element styles)
2. **Dark/Light Mode** - Color scheme toggle
3. **Audience (Age Group)** - Content density and readability adjustments
4. **Purpose** - Tone and presentation style

Each construct operates independently, allowing combinations like:
- "Corporate Blue Theme + Dark Mode + Adults + Sales"
- "Warm Pastel Theme + Light Mode + Kids + Educational"

---

## 1. Theme

A **Theme** is a cohesive visual identity applied consistently across all slides in a presentation.

### 1.1 Typography System

#### Font Families (1-2 types)

| Font Type | Usage |
|-----------|-------|
| **Primary Font** | Body text, descriptions, bullet lists, table content |
| **Secondary Font** (optional) | Headings, titles, emphasis elements |

#### Font Size Tiers

The service uses **6 standardized font size tiers** for the main content area:

| Tier | Name | Size Range | Purpose | Examples |
|------|------|------------|---------|----------|
| **T1** | Metrics/Display | 72-104px | Big numbers, KPIs, statistics | "42%", "$1.2M" |
| **T2** | Section Headings | 28-35px | Column headers, section titles | "Key Benefits", "Phase 1" |
| **T3** | Subheadings | 24-26px | Box titles, card headings | "Cost Savings", "Efficiency" |
| **T4** | Body Text | 19-22px | Descriptions, paragraphs | Explanatory content |
| **T5** | Small Text | 16-19px | Lists, table cells, bullets | Supporting details |
| **T6** | Special/Quote | Variable | Quote text, attribution, decorative | Testimonials, citations |

> **Note**: Title and Subtitle sizes are controlled by the Layout Service, not this theming system.

#### Font Weights

| Weight | Value | Usage |
|--------|-------|-------|
| Regular | 400 | Body text, descriptions |
| Bold | 700 | Headings, subheadings |
| Extra Bold | 900 | Metrics, step numbers |

---

### 1.2 Color System

#### Font Colors

The system requires **font colors with both light and dark mode variants**:

| Color Role | Light Mode Value | Dark Mode Value | Usage |
|------------|------------------|-----------------|-------|
| **Text Primary** | `#1f2937` (dark) | `#f8fafc` (light) | Main headings, primary text |
| **Text Secondary** | `#374151` (dark) | `#e2e8f0` (light) | Body text, descriptions |
| **Text Body** | `#4b5563` (dark) | `#cbd5e1` (light) | Paragraph content |
| **Text Muted** | `#6b7280` (gray) | `#94a3b8` (light gray) | De-emphasized text, labels |
| **Text on Dark BG** | `#ffffff` | `#ffffff` | Text on gradients/colored backgrounds |
| **Text on Dark 95%** | `rgba(255,255,255,0.95)` | `rgba(255,255,255,0.95)` | Semi-transparent on colored |
| **Accent Blue** | `#2563eb` | `#60a5fa` | Blue-themed emphasis |
| **Accent Green** | `#10b981` | `#34d399` | Green-themed emphasis |
| **Accent Red** | `#dc2626` | `#f87171` | Red/negative indicators |

> **Key Principle**: In light mode, font colors are dark (for contrast on white backgrounds). In dark mode, font colors are light (for contrast on dark backgrounds). Text on colored/gradient backgrounds remains white in both modes.

#### Element Colors (Boxes, Borders, Backgrounds)

The system requires **two variants** per color family (Light Mode and Dark Mode):

| Color Family | Light Variant (Pastels) | Dark Variant (Saturated) | Usage |
|--------------|------------------------|-------------------------|-------|
| **Blue** | `#dbeafe`, `#f0f9ff` | `#2563eb`, `#1a73e8` | Box 1, Column 1, Primary accent |
| **Green** | `#d1fae5`, `#f0fdf4` | `#10b981`, `#059669` | Box 2, Column 2, Success states |
| **Yellow/Amber** | `#fef3c7`, `#fde68a` | `#f59e0b`, `#f7971e` | Box 3, Column 3, Warnings |
| **Pink/Rose** | `#fce7f3`, `#fbcfe8` | `#ec4899`, `#f5576c` | Box 4, Column 4 |
| **Purple** | `#ede9fe`, `#ddd6fe` | `#667eea`, `#8b5cf6` | Box 5, Accent elements |
| **Teal** | `#ccfbf1`, `#99f6e4` | `#14b8a6`, `#0d9488` | Additional accent |
| **Orange** | `#fed7aa`, `#fdba74` | `#f97316`, `#ea580c` | Additional accent |

#### Gradient Definitions

For high-impact elements (Metrics cards, Sequential steps):

| Gradient Name | CSS Value | Usage |
|---------------|-----------|-------|
| **Purple** | `linear-gradient(135deg, #667eea 0%, #764ba2 100%)` | Metric card 1 |
| **Pink** | `linear-gradient(135deg, #f5576c 0%, #f093fb 100%)` | Metric card 2 |
| **Cyan** | `linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)` | Metric card 3 |
| **Green** | `linear-gradient(135deg, #11998e 0%, #38ef7d 100%)` | Metric card 4 |
| **Gold** | `linear-gradient(135deg, #f7971e 0%, #ffd200 100%)` | Metric card 5 |

#### Border Colors

| Name | Value | Usage |
|------|-------|-------|
| **Default Border** | `#d1d5db` | Standard box borders |
| **Accent Border** | `#667eea` | Highlight borders (impact quote) |
| **Light Border** | `#e5e7eb` | Divider lines, separators |

---

### 1.3 Theme Requirements Summary

A complete theme definition must include **both light and dark variants** for colors:

```
Theme = {
  id: string,                    // e.g., "corporate-blue"
  name: string,
  has_dark_mode: boolean,        // true if theme supports dark mode

  fonts: {
    primary: string,
    secondary: string (optional)
  },

  fontSizes: {
    t1: string,  // e.g., "88px" - Metrics
    t2: string,  // e.g., "29px" - Headings
    t3: string,  // e.g., "26px" - Subheadings
    t4: string,  // e.g., "20px" - Body
    t5: string,  // e.g., "18px" - Small
    t6: string   // e.g., "32px" - Special
  },

  // CRITICAL: Font colors need BOTH light and dark variants
  fontColors: {
    light: {                     // For light mode (dark text on light bg)
      primary: string,           // e.g., "#1f2937"
      secondary: string,         // e.g., "#374151"
      body: string,              // e.g., "#4b5563"
      muted: string,             // e.g., "#6b7280"
      onColoredBg: string,       // e.g., "#ffffff"
      accentBlue: string,
      accentGreen: string,
      accentRed: string
    },
    dark: {                      // For dark mode (light text on dark bg)
      primary: string,           // e.g., "#f8fafc"
      secondary: string,         // e.g., "#e2e8f0"
      body: string,              // e.g., "#cbd5e1"
      muted: string,             // e.g., "#94a3b8"
      onColoredBg: string,       // e.g., "#ffffff" (same)
      accentBlue: string,        // e.g., "#60a5fa" (lighter)
      accentGreen: string,       // e.g., "#34d399" (lighter)
      accentRed: string          // e.g., "#f87171" (lighter)
    }
  },

  // Element colors also need light/dark variants
  elementColors: {
    box1: { light: string, dark: string },
    box2: { light: string, dark: string },
    box3: { light: string, dark: string },
    box4: { light: string, dark: string },
    box5: { light: string, dark: string },
    background: { light: string, dark: string },
    backgroundAlt: { light: string, dark: string }
  },

  gradients: {
    gradient1-5: string          // Same for both modes (high contrast)
  },

  borders: {
    light: {
      default: string,           // e.g., "#d1d5db"
      accent: string,
      subtle: string
    },
    dark: {
      default: string,           // e.g., "#4b5563"
      accent: string,
      subtle: string
    }
  }
}
```

---

## 2. Dark/Light Mode

**Dark/Light Mode** is an independent toggle that operates on top of any theme.

### 2.1 Mode Behaviors

| Element | Light Mode (Default) | Dark Mode |
|---------|---------------------|-----------|
| **Slide Background** | White/Light (controlled by Layout Service) | Dark (controlled by Layout Service) |
| **Primary Text** | Dark (`#1f2937`) | White (`#ffffff`) |
| **Secondary Text** | Gray (`#374151`) | Light Gray (`#e5e7eb`) |
| **Box Backgrounds** | Light pastels | Darker variants or semi-transparent |
| **Borders** | Gray (`#d1d5db`) | Lighter for visibility (`#4b5563`) |
| **Metrics Cards** | **No change** (already high contrast) | **No change** |

### 2.2 Color Inversions

| Light Mode Value | Dark Mode Value |
|------------------|-----------------|
| `#1f2937` | `#ffffff` |
| `#374151` | `#e5e7eb` |
| `#6b7280` | `#9ca3af` |
| `#dbeafe` (light blue bg) | `#1e3a8a` (dark blue bg) |
| `#d1fae5` (light green bg) | `#065f46` (dark green bg) |
| `#fef3c7` (light yellow bg) | `#78350f` (dark brown bg) |
| `#fce7f3` (light pink bg) | `#831843` (dark pink bg) |
| `#d1d5db` (border) | `#4b5563` (lighter border) |

### 2.3 Elements That Do NOT Change

- **Metric gradient cards** - Already use white text on dark gradients
- **Matrix boxes** - Already use white text on saturated colors
- **White text on colored backgrounds** - Remains white

### 2.4 Mode Toggle Requirement

```
darkMode: boolean  // true = dark mode, false = light mode
```

The parent service should apply this as a class or attribute that triggers CSS variable swaps.

---

## 3. Audience (Age Group)

**Audience** adjusts content density, font sizing, and vocabulary based on the target age group.

### 3.1 Audience Definitions

| Audience | Age Range | Words/Sentence | Font Modifier | Vocabulary Level |
|----------|-----------|----------------|---------------|------------------|
| **Kids** | 6-12 years | 8-12 words | +20% larger | Simple |
| **Teens** | 13-17 years | 12-18 words | +10% larger | Moderate |
| **Adults** | 18-60 years | 15-25 words | Base (1.0x) | Full |
| **Seniors** | 60+ years | 12-18 words | +15% larger | Full |

### 3.2 Visual Adjustments

| Adjustment | Kids | Teens | Adults | Seniors |
|------------|------|-------|--------|---------|
| Font Size Multiplier | 1.2x | 1.1x | 1.0x | 1.15x |
| Line Height | 1.8 | 1.7 | 1.5-1.6 | 1.7 |
| Spacing | +20% | +10% | Base | +15% |
| Paragraph Length | Short | Medium | Standard | Medium |

### 3.3 Content Generation Adjustments

These affect the **LLM prompts** used to generate slide content:

| Aspect | Kids | Teens | Adults | Seniors |
|--------|------|-------|--------|---------|
| Max words per bullet | 10 | 15 | 20 | 15 |
| Sentence complexity | Simple | Moderate | Any | Clear |
| Technical jargon | None | Minimal | Allowed | Minimal |
| Examples style | Relatable, fun | Current, relevant | Professional | Familiar |

### 3.4 Audience Configuration

```
audience: {
  type: "kids" | "teens" | "adults" | "seniors",
  visual: {
    fontSizeMultiplier: number,  // 1.0, 1.1, 1.15, 1.2
    lineHeightMultiplier: number,
    spacingMultiplier: number
  },
  content: {
    maxWordsPerSentence: number,
    maxWordsPerBullet: number,
    vocabularyLevel: "simple" | "moderate" | "full",
    useTechnicalJargon: boolean
  }
}
```

---

## 4. Purpose

**Purpose** defines the tone, style, and presentation approach for the content.

### 4.1 Purpose Definitions

| Purpose | Tone | Primary Goal | Content Style |
|---------|------|--------------|---------------|
| **Educational** | Explanatory, supportive | Teach and inform | Step-by-step, clear explanations |
| **Sales** | Persuasive, confident | Convert and convince | Benefits-focused, call-to-action |
| **Marketing** | Engaging, aspirational | Attract and interest | Broad appeal, catchy phrases |
| **Informational** | Neutral, factual | Report and present | Balanced, data-driven |
| **Entertainment** | Fun, casual | Engage and amuse | Humorous, conversational |

### 4.2 System Prompt Roles

Each purpose maps to a different **LLM persona**:

| Purpose | System Prompt Role |
|---------|-------------------|
| **Educational** | "You are a patient teacher who explains concepts clearly, breaks down complex ideas into digestible parts, and ensures understanding before moving forward." |
| **Sales** | "You are a confident sales professional who highlights benefits, addresses objections proactively, and guides the audience toward a clear call-to-action." |
| **Marketing** | "You are a creative marketing specialist who crafts compelling narratives, uses engaging language, and appeals to emotions while maintaining authenticity." |
| **Informational** | "You are an objective analyst who presents facts clearly, maintains neutrality, and lets the data speak for itself without bias or embellishment." |
| **Entertainment** | "You are an engaging entertainer who keeps the audience amused, uses humor appropriately, and makes even mundane topics interesting and memorable." |

### 4.3 Content Style Guidelines

| Aspect | Educational | Sales | Marketing | Informational | Entertainment |
|--------|-------------|-------|-----------|---------------|---------------|
| **Opening** | "Let's explore..." | "Discover how..." | "Imagine..." | "Research shows..." | "Here's something fun..." |
| **Structure** | Logical progression | Problem → Solution | Story arc | Facts first | Surprise/delight |
| **Evidence** | Examples, analogies | Testimonials, ROI | Social proof | Data, citations | Anecdotes |
| **Closing** | Summary, next steps | Clear CTA | Emotional hook | Key takeaways | Memorable punchline |
| **Language** | Instructive | Action-oriented | Evocative | Precise | Playful |

### 4.4 Purpose Configuration

```
purpose: {
  type: "educational" | "sales" | "marketing" | "informational" | "entertainment",
  prompt: {
    systemRole: string,      // LLM system prompt
    toneKeywords: string[],  // e.g., ["persuasive", "confident"]
    avoidKeywords: string[]  // e.g., ["maybe", "perhaps"]
  },
  style: {
    openingPattern: string,
    closingPattern: string,
    evidenceType: string,
    ctaRequired: boolean
  }
}
```

---

## Template Coverage

This theming system applies to the following **34 template variants** (in both C1 and L25 categories):

| Category | Templates | Count |
|----------|-----------|-------|
| **Metrics** | metrics_2x2_grid, metrics_3col, metrics_3x2_grid, metrics_4col | 4 |
| **Table** | table_2col, table_3col, table_4col, table_5col | 4 |
| **Grid** | grid_2x2_centered, grid_2x2_left, grid_2x2_numbered, grid_2x3, grid_2x3_left, grid_2x3_numbered, grid_3x2, grid_3x2_left, grid_3x2_numbered | 9 |
| **Sequential** | sequential_3col, sequential_4col, sequential_5col | 3 |
| **Single Column** | single_column_3section, single_column_4section, single_column_5section | 3 |
| **Comparison** | comparison_2col, comparison_3col, comparison_4col | 3 |
| **Matrix** | matrix_2x2, matrix_2x3 | 2 |
| **Hybrid** | hybrid_left_2x2, hybrid_top_2x2 | 2 |
| **Asymmetric** | asymmetric_8_4_3section, asymmetric_8_4_4section, asymmetric_8_4_5section | 3 |
| **Impact Quote** | impact_quote | 1 |
| **Total** | | **34** |

---

## Integration Requirements

### For Frontend/Parent Service

1. **Theme Application**: Pass theme CSS variables to content area
2. **Mode Toggle**: Apply dark/light mode class that triggers variable swaps
3. **Audience Multipliers**: Apply font-size and spacing multipliers via CSS
4. **Purpose**: Primarily affects content generation (LLM prompts), minimal visual impact

### For Text Service

1. **Template Updates**: Convert hardcoded styles to CSS variable references
2. **LLM Prompts**: Parameterize system prompts based on Audience and Purpose
3. **Content Length**: Adjust word counts based on Audience settings
4. **Configuration**: Accept theme/mode/audience/purpose parameters in API requests

### API Contract (Proposed)

```json
{
  "template": "grid_2x2_centered",
  "content": { ... },
  "theming": {
    "theme": "corporate-blue",      // or custom theme object
    "darkMode": false,
    "audience": "adults",
    "purpose": "sales"
  }
}
```

---

## Open Questions for Cross-Service Alignment

1. **CSS Variable Naming**: What prefix should we use? (`--deck-`, `--theme-`, `--text-`?)
2. **Theme Loading**: Should themes be loaded via CSS file, inline styles, or CSS-in-JS?
3. **Dark Mode Toggle**: Should this be template-side or slide-container-side?
4. **Predefined Themes**: How many should we offer initially? What names?
5. **Audience/Purpose Storage**: Should these be presentation-level or slide-level settings?
6. **Font Loading**: How are custom fonts loaded by the parent service?

---

## Next Steps

1. Review this document across services
2. Agree on CSS variable naming convention
3. Define 3-5 predefined themes
4. Align on API contract for theming parameters
5. Implement CSS variable structure in Text Service templates
6. Test integration with parent React.js service

---

*Document prepared for cross-service alignment meeting*
