# Theme Service Enhancement Request

**From**: Text & Table Builder Service v1.2 (Elementor)
**To**: Layout Service v7.5 (Theme Service)
**Date**: December 2024
**Priority**: High

---

## Executive Summary

The Text Service requires enhanced typography and styling tokens from the Theme Service to enable precise, theme-aware text generation within the 32×18 grid system. This document specifies the required API endpoints and data structures.

---

## Background

### Current Limitation

The existing Theme Service provides:
- Color tokens (14 colors)
- Basic typography (font family, sizes)
- Hero slide-specific styling

**What's Missing**:
- Granular typography tokens per heading level (h1-h4, body, subtitle, caption)
- List/bullet styling tokens
- Text box styling defaults
- Color tokens for text elements

### Why This Matters

The Text Service calculates character constraints based on:
- Font size (affects chars per line)
- Line height (affects max lines)
- Font family (affects character width ratio)

Without theme-aware typography tokens, the Text Service cannot:
1. Generate text that fits precisely within grid-based elements
2. Apply consistent styling across themes
3. Support theme switching without content overflow

---

## Required Enhancements

### 1. New API Endpoint

```
GET /api/themes/{theme_id}/typography
```

**Purpose**: Return complete typography tokens for a theme, enabling Text Service to calculate accurate character constraints.

**Response Structure**:

```json
{
  "theme_id": "corporate-blue",
  "font_family": "Poppins, sans-serif",
  "font_family_heading": "Poppins, sans-serif",
  "tokens": {
    "h1": {
      "size": 72,
      "size_px": "72px",
      "weight": 700,
      "line_height": 1.2,
      "letter_spacing": "-0.02em",
      "color": "#1f2937",
      "text_transform": "none"
    },
    "h2": {
      "size": 48,
      "size_px": "48px",
      "weight": 600,
      "line_height": 1.3,
      "letter_spacing": "-0.01em",
      "color": "#1f2937",
      "text_transform": "none"
    },
    "h3": {
      "size": 32,
      "size_px": "32px",
      "weight": 600,
      "line_height": 1.4,
      "letter_spacing": "0",
      "color": "#1f2937",
      "text_transform": "none"
    },
    "h4": {
      "size": 24,
      "size_px": "24px",
      "weight": 600,
      "line_height": 1.4,
      "letter_spacing": "0",
      "color": "#374151",
      "text_transform": "none"
    },
    "body": {
      "size": 20,
      "size_px": "20px",
      "weight": 400,
      "line_height": 1.6,
      "letter_spacing": "0",
      "color": "#374151"
    },
    "subtitle": {
      "size": 28,
      "size_px": "28px",
      "weight": 400,
      "line_height": 1.5,
      "letter_spacing": "0",
      "color": "#6b7280"
    },
    "caption": {
      "size": 16,
      "size_px": "16px",
      "weight": 400,
      "line_height": 1.4,
      "letter_spacing": "0.01em",
      "color": "#9ca3af"
    },
    "emphasis": {
      "weight": 600,
      "color": "#1f2937",
      "style": "normal"
    }
  },
  "list_styles": {
    "bullet_type": "disc",
    "bullet_color": "#1e40af",
    "bullet_size": "0.4em",
    "list_indent": "1.5em",
    "item_spacing": "0.5em",
    "numbered_style": "decimal",
    "nested_indent": "1.5em"
  },
  "textbox_defaults": {
    "background": "transparent",
    "background_gradient": null,
    "border_width": "0px",
    "border_color": "transparent",
    "border_radius": "8px",
    "padding": "16px",
    "box_shadow": "none"
  },
  "char_width_ratio": 0.5
}
```

---

### 2. Typography Tokens Specification

#### Heading Tokens (h1-h4)

| Token | Description | Unit | Corporate Blue | Dark Mode |
|-------|-------------|------|----------------|-----------|
| `h1.size` | Title slide title | px | 72 | 72 |
| `h1.weight` | Font weight | int | 700 | 700 |
| `h1.line_height` | Line height multiplier | float | 1.2 | 1.2 |
| `h1.color` | Text color | hex | #1f2937 | #f9fafb |
| `h2.size` | Slide title / Section | px | 48 | 48 |
| `h2.weight` | Font weight | int | 600 | 600 |
| `h2.line_height` | Line height multiplier | float | 1.3 | 1.3 |
| `h2.color` | Text color | hex | #1f2937 | #f3f4f6 |
| `h3.size` | Subsection heading | px | 32 | 32 |
| `h3.weight` | Font weight | int | 600 | 600 |
| `h3.line_height` | Line height multiplier | float | 1.4 | 1.4 |
| `h3.color` | Text color | hex | #1f2937 | #e5e7eb |
| `h4.size` | Card/box title | px | 24 | 24 |
| `h4.weight` | Font weight | int | 600 | 600 |
| `h4.line_height` | Line height multiplier | float | 1.4 | 1.4 |
| `h4.color` | Text color | hex | #374151 | #d1d5db |

#### Body Text Tokens

| Token | Description | Unit | Corporate Blue | Dark Mode |
|-------|-------------|------|----------------|-----------|
| `body.size` | Regular paragraph | px | 20 | 20 |
| `body.weight` | Font weight | int | 400 | 400 |
| `body.line_height` | Line height multiplier | float | 1.6 | 1.6 |
| `body.color` | Text color | hex | #374151 | #d1d5db |
| `subtitle.size` | Slide subtitle | px | 28 | 28 |
| `subtitle.weight` | Font weight | int | 400 | 400 |
| `subtitle.line_height` | Line height multiplier | float | 1.5 | 1.5 |
| `subtitle.color` | Text color | hex | #6b7280 | #9ca3af |
| `caption.size` | Small text, footnotes | px | 16 | 16 |
| `caption.weight` | Font weight | int | 400 | 400 |
| `caption.line_height` | Line height multiplier | float | 1.4 | 1.4 |
| `caption.color` | Text color | hex | #9ca3af | #6b7280 |

#### Emphasis Token

| Token | Description | Corporate Blue | Dark Mode |
|-------|-------------|----------------|-----------|
| `emphasis.weight` | Bold text weight | 600 | 600 |
| `emphasis.color` | Bold text color | #1f2937 | #f9fafb |
| `emphasis.style` | Font style (normal/italic) | normal | normal |

---

### 3. List/Bullet Styling Tokens

| Token | Description | Default | Options |
|-------|-------------|---------|---------|
| `bullet_type` | Default bullet character | disc | disc, circle, square, dash, arrow, check, none |
| `bullet_color` | Bullet color | theme.primary | Any hex color |
| `bullet_size` | Bullet size relative to text | 0.4em | 0.3em - 0.6em |
| `list_indent` | List indentation from left | 1.5em | 1em - 2.5em |
| `item_spacing` | Space between list items | 0.5em | 0.25em - 1em |
| `numbered_style` | Numbered list format | decimal | decimal, lower-alpha, upper-alpha, lower-roman, upper-roman |
| `nested_indent` | Additional indent for nested lists | 1.5em | 1em - 2em |

**Bullet Type CSS Values**:
```css
disc     → list-style-type: disc
circle   → list-style-type: circle
square   → list-style-type: square
dash     → list-style-type: "– " (custom marker)
arrow    → list-style-type: "→ " (custom marker)
check    → list-style-type: "✓ " (custom marker)
none     → list-style-type: none
```

---

### 4. Text Box Styling Defaults

| Token | Description | Default | Type |
|-------|-------------|---------|------|
| `background` | Background color | transparent | CSS color |
| `background_gradient` | CSS gradient | null | CSS gradient string or null |
| `border_width` | Border width | 0px | CSS length |
| `border_color` | Border color | transparent | CSS color |
| `border_radius` | Corner radius | 8px | CSS length |
| `padding` | Inner padding | 16px | CSS length |
| `box_shadow` | Shadow effect | none | CSS shadow |

**Example Values**:
```css
/* Transparent (default) */
background: transparent;
border: 0px solid transparent;

/* Subtle background */
background: rgba(30, 64, 175, 0.05);
border: 1px solid rgba(30, 64, 175, 0.1);
border-radius: 8px;

/* Gradient background */
background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
border: 1px solid #0ea5e9;
border-radius: 12px;
box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
```

---

### 5. Character Width Ratio

For accurate character constraint calculations, each theme should provide:

| Token | Description | Default | Notes |
|-------|-------------|---------|-------|
| `char_width_ratio` | Average character width / font size | 0.5 | Varies by font family |

**Common Font Ratios**:
| Font Family | Char Width Ratio |
|-------------|------------------|
| Poppins | 0.50 |
| Inter | 0.48 |
| Roboto | 0.47 |
| Open Sans | 0.49 |
| Montserrat | 0.52 |
| Lato | 0.47 |

This ratio is used to calculate: `avg_char_width = font_size * char_width_ratio`

---

## Theme Variations Required

### Minimum Themes to Support

The Theme Service should provide typography tokens for at least these themes:

| Theme ID | Primary Font | Char Ratio | Description |
|----------|--------------|------------|-------------|
| `corporate-blue` | Poppins | 0.50 | Professional business (default) |
| `elegant-emerald` | Poppins | 0.50 | Sophisticated nature-inspired |
| `vibrant-orange` | Poppins | 0.50 | Energetic creative |
| `dark-mode` | Poppins | 0.50 | Modern dark theme |

### Custom Theme Support

When users create custom themes, they should be able to override:
1. Font family (heading and body separately)
2. All typography tokens
3. List/bullet styles
4. Text box defaults

---

## Integration Flow

```
┌─────────────────────┐         ┌─────────────────────┐
│    Text Service     │         │   Theme Service     │
│    (Elementor)      │         │   (Layout v7.5)     │
└─────────────────────┘         └─────────────────────┘
           │                              │
           │ GET /api/themes/{id}/typography
           │──────────────────────────────▶
           │                              │
           │◀──────────────────────────────│
           │  Typography tokens response   │
           │                              │
           ▼                              │
    ┌──────────────┐                      │
    │ Calculate    │                      │
    │ constraints  │                      │
    │ using tokens │                      │
    └──────────────┘                      │
           │                              │
           ▼                              │
    ┌──────────────┐                      │
    │ Generate     │                      │
    │ text content │                      │
    │ with styling │                      │
    └──────────────┘                      │
```

---

## Fallback Behavior

If Theme Service is unavailable, Text Service will use built-in defaults:

```python
DEFAULT_TYPOGRAPHY = {
    "font_family": "Poppins, sans-serif",
    "tokens": {
        "h1": {"size": 72, "weight": 700, "line_height": 1.2, "color": "#1f2937"},
        "h2": {"size": 48, "weight": 600, "line_height": 1.3, "color": "#1f2937"},
        "h3": {"size": 32, "weight": 600, "line_height": 1.4, "color": "#1f2937"},
        "h4": {"size": 24, "weight": 600, "line_height": 1.4, "color": "#374151"},
        "body": {"size": 20, "weight": 400, "line_height": 1.6, "color": "#374151"},
        "subtitle": {"size": 28, "weight": 400, "line_height": 1.5, "color": "#6b7280"},
        "caption": {"size": 16, "weight": 400, "line_height": 1.4, "color": "#9ca3af"},
        "emphasis": {"weight": 600, "color": "#1f2937"}
    },
    "char_width_ratio": 0.5
}
```

---

## Timeline Request

| Milestone | Target |
|-----------|--------|
| API endpoint specification review | 1 week |
| Implementation of `/typography` endpoint | 2 weeks |
| Token population for 4 base themes | 1 week |
| Integration testing with Text Service | 1 week |

---

## Contact

For questions about this request, contact the Text Service team.

---

## Appendix: Text Service Usage

### How Typography Tokens Are Used

```python
# Text Service calculates constraints using theme tokens
def calculate_text_constraints(grid_width, grid_height, typography):
    # Get font metrics from theme
    font_size = typography["body"]["size"]  # e.g., 20
    line_height = typography["body"]["line_height"]  # e.g., 1.6
    char_ratio = typography.get("char_width_ratio", 0.5)

    # Calculate pixel dimensions
    content_width = (grid_width * 60) - 20 - 32  # grid - outer - inner padding
    content_height = (grid_height * 60) - 20 - 32

    # Calculate character constraints
    avg_char_width = font_size * char_ratio  # 20 * 0.5 = 10px
    line_height_px = font_size * line_height  # 20 * 1.6 = 32px

    chars_per_line = content_width / avg_char_width
    max_lines = content_height / line_height_px
    max_characters = chars_per_line * max_lines * 0.9  # 90% fill factor

    return {
        "chars_per_line": int(chars_per_line),
        "max_lines": int(max_lines),
        "max_characters": int(max_characters)
    }
```

### Generated HTML Uses Theme Tokens

```html
<!-- Text Service generates HTML with theme-applied styling -->
<div style="
  font-family: Poppins, sans-serif;
  font-size: 20px;
  font-weight: 400;
  line-height: 1.6;
  color: #374151;
  background: transparent;
  padding: 16px;
  border-radius: 8px;
">
  <ul style="
    list-style-type: disc;
    padding-left: 1.5em;
    color: #374151;
  ">
    <li style="margin-bottom: 0.5em;">
      <span style="color: #1e40af;">●</span> First bullet point
    </li>
  </ul>
</div>
```
