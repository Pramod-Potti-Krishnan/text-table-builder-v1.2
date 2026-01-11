# Illustrator Color System

A comprehensive color system with Primary, Secondary, and 10 Accent color families. Each accent has dark, pastel, and light pastel variants for use across hexagon shapes, text boxes, and dark/light mode theming.

---

## Table of Contents

1. [Color System Overview](#color-system-overview)
2. [Primary & Secondary Colors](#primary--secondary-colors)
3. [Accent Color Families (1-10)](#accent-color-families-1-10)
4. [Usage Guidelines](#usage-guidelines)
5. [Dark/Light Mode Behavior](#darklight-mode-behavior)
6. [CSS Variable Definitions](#css-variable-definitions)
7. [Quick Reference](#quick-reference)

---

## Color System Overview

### Color Types

| Type | Purpose | Opacity |
|------|---------|---------|
| **Primary** | Main brand/theme color | 100% (solid) |
| **Secondary** | Supporting brand color | 100% (solid) |
| **Accent Dark** | Hexagon shapes, solid elements | 100% (solid) |
| **Accent Pastel** | Text box backgrounds | 60% transparent |
| **Accent Light Pastel** | Heading text (dark mode) | 100% (solid font) |

### Transparency Rules

| Element | Transparency |
|---------|--------------|
| Hexagon shapes (dark colors) | NOT transparent (solid) |
| Text box backgrounds (pastel) | 60% transparent |
| All fonts/text | NOT transparent (solid) |

---

## Primary & Secondary Colors

| Color | Hex | Usage |
|-------|-----|-------|
| **Primary** | `#0066CC` | Main theme color, CTAs, primary shapes |
| **Primary Dark** | `#004C99` | Hover states, emphasis |
| **Primary Light** | `#3399FF` | Highlights, secondary elements |
| **Secondary** | `#FF6B35` | Accent, complementary elements |
| **Secondary Dark** | `#CC4400` | Hover states |
| **Secondary Light** | `#FF9966` | Highlights |

---

## Accent Color Families (1-10)

Each accent family has three variants:

- **Dark**: For hexagon shapes and solid elements (100% solid)
- **Pastel**: For text box backgrounds (60% transparent)
- **Light Pastel**: For heading text in dark mode (solid font color)

### Accent 1: Purple

| Variant | Hex | RGBA (for backgrounds) | Usage |
|---------|-----|------------------------|-------|
| **Dark** | `#805AA0` | `rgba(128, 90, 160, 1.0)` | Hexagon shape |
| **Pastel** | `#E8D7F1` | `rgba(232, 215, 241, 0.6)` | Text box background |
| **Light Pastel** | `#E6D2F5` | — | Heading text (dark mode) |

### Accent 2: Blue

| Variant | Hex | RGBA (for backgrounds) | Usage |
|---------|-----|------------------------|-------|
| **Dark** | `#2980B9` | `rgba(41, 128, 185, 1.0)` | Hexagon shape |
| **Pastel** | `#BDE0F9` | `rgba(189, 224, 249, 0.6)` | Text box background |
| **Light Pastel** | `#B4DCFF` | — | Heading text (dark mode) |

### Accent 3: Red

| Variant | Hex | RGBA (for backgrounds) | Usage |
|---------|-----|------------------------|-------|
| **Dark** | `#C0392B` | `rgba(192, 57, 43, 1.0)` | Hexagon shape |
| **Pastel** | `#FEE2E2` | `rgba(254, 226, 226, 0.6)` | Text box background |
| **Light Pastel** | `#FFC8C3` | — | Heading text (dark mode) |

### Accent 4: Green

| Variant | Hex | RGBA (for backgrounds) | Usage |
|---------|-----|------------------------|-------|
| **Dark** | `#27AE60` | `rgba(39, 174, 96, 1.0)` | Hexagon shape |
| **Pastel** | `#D4EDDA` | `rgba(212, 237, 218, 0.6)` | Text box background |
| **Light Pastel** | `#B4F5D2` | — | Heading text (dark mode) |

### Accent 5: Yellow/Gold

| Variant | Hex | RGBA (for backgrounds) | Usage |
|---------|-----|------------------------|-------|
| **Dark** | `#D39E1E` | `rgba(211, 158, 30, 1.0)` | Hexagon shape |
| **Pastel** | `#FDE68A` | `rgba(253, 230, 138, 0.6)` | Text box background |
| **Light Pastel** | `#FFF0BE` | — | Heading text (dark mode) |

### Accent 6: Cyan

| Variant | Hex | RGBA (for backgrounds) | Usage |
|---------|-----|------------------------|-------|
| **Dark** | `#0097A7` | `rgba(0, 151, 167, 1.0)` | Hexagon shape |
| **Pastel** | `#C3F1F7` | `rgba(195, 241, 247, 0.6)` | Text box background |
| **Light Pastel** | `#B2EBF2` | — | Heading text (dark mode) |

### Accent 7: Orange

| Variant | Hex | RGBA (for backgrounds) | Usage |
|---------|-----|------------------------|-------|
| **Dark** | `#E65100` | `rgba(230, 81, 0, 1.0)` | Hexagon shape |
| **Pastel** | `#FFE0B2` | `rgba(255, 224, 178, 0.6)` | Text box background |
| **Light Pastel** | `#FFCCBC` | — | Heading text (dark mode) |

### Accent 8: Teal

| Variant | Hex | RGBA (for backgrounds) | Usage |
|---------|-----|------------------------|-------|
| **Dark** | `#00796B` | `rgba(0, 121, 107, 1.0)` | Hexagon shape |
| **Pastel** | `#B2DFDB` | `rgba(178, 223, 219, 0.6)` | Text box background |
| **Light Pastel** | `#B2DFDB` | — | Heading text (dark mode) |

### Accent 9: Pink/Magenta

| Variant | Hex | RGBA (for backgrounds) | Usage |
|---------|-----|------------------------|-------|
| **Dark** | `#C2185B` | `rgba(194, 24, 91, 1.0)` | Hexagon shape |
| **Pastel** | `#E1D5F6` | `rgba(225, 213, 246, 0.6)` | Text box background |
| **Light Pastel** | `#F8BBD9` | — | Heading text (dark mode) |

### Accent 10: Indigo

| Variant | Hex | RGBA (for backgrounds) | Usage |
|---------|-----|------------------------|-------|
| **Dark** | `#3949AB` | `rgba(57, 73, 171, 1.0)` | Hexagon shape |
| **Pastel** | `#C5CAE9` | `rgba(197, 202, 233, 0.6)` | Text box background |
| **Light Pastel** | `#D1D9FF` | — | Heading text (dark mode) |

---

## Complete Accent Color Reference Table

| # | Name | Dark (Shape) | Pastel (Box BG) | Light Pastel (DM Text) |
|---|------|--------------|-----------------|------------------------|
| 1 | Purple | `#805AA0` | `rgba(232, 215, 241, 0.6)` | `#E6D2F5` |
| 2 | Blue | `#2980B9` | `rgba(189, 224, 249, 0.6)` | `#B4DCFF` |
| 3 | Red | `#C0392B` | `rgba(254, 226, 226, 0.6)` | `#FFC8C3` |
| 4 | Green | `#27AE60` | `rgba(212, 237, 218, 0.6)` | `#B4F5D2` |
| 5 | Yellow | `#D39E1E` | `rgba(253, 230, 138, 0.6)` | `#FFF0BE` |
| 6 | Cyan | `#0097A7` | `rgba(195, 241, 247, 0.6)` | `#B2EBF2` |
| 7 | Orange | `#E65100` | `rgba(255, 224, 178, 0.6)` | `#FFCCBC` |
| 8 | Teal | `#00796B` | `rgba(178, 223, 219, 0.6)` | `#B2DFDB` |
| 9 | Pink | `#C2185B` | `rgba(225, 213, 246, 0.6)` | `#F8BBD9` |
| 10 | Indigo | `#3949AB` | `rgba(197, 202, 233, 0.6)` | `#D1D9FF` |

---

## Usage Guidelines

### Hexagon Shapes (Solid Dark Colors)

- Use **Accent Dark** colors
- 100% opacity (solid, NOT transparent)
- Text on shapes: Always **white** (`#FFFFFF`)
- Does NOT change between light/dark mode

```html
<!-- Hexagon with Accent 1 (Purple) -->
<div style="background: #805AA0;">
  <span style="color: #FFFFFF;">Shape Label</span>
</div>
```

### Text Boxes (Pastel Backgrounds)

- Use **Accent Pastel** colors at 60% opacity
- Contains two text types (both solid, not transparent):
  - **Heading**: Changes color based on mode
  - **Body text**: Changes color based on mode

```html
<!-- Text box with Accent 1 (Purple) -->
<div style="background: rgba(232, 215, 241, 0.6); border-radius: 8px;">
  <!-- Heading: Dark color in light mode, light pastel in dark mode -->
  <h3 style="color: var(--accent-1-text, #805AA0);">Heading</h3>

  <!-- Body: Dark gray in light mode, white in dark mode -->
  <p style="color: var(--text-primary, #374151);">Body text here</p>
</div>
```

### Pairing: Shape to Text Box

Each hexagon shape pairs with its corresponding text box:

| Shape (Dark) | Text Box (Pastel) | Heading Text |
|--------------|-------------------|--------------|
| Accent 1 Dark | Accent 1 Pastel | Accent 1 Dark/Light Pastel |
| Accent 2 Dark | Accent 2 Pastel | Accent 2 Dark/Light Pastel |
| ... | ... | ... |

---

## TEXT_BOX Title Styling Options

TEXT_BOX components support three distinct title styling options, each with specific color behavior.

### Background Options

| Option | Value | Description |
|--------|-------|-------------|
| **Transparent** | `transparent` | No background color |
| **Colored** | Accent Pastel (60%) | Uses one of 10 accent pastel colors at 60% opacity |

**Important**: Accent Dark colors are NEVER used for text box backgrounds - only for shapes (hexagons) and title badges.

### Option A: Colored Title (`title_style: "plain"` or `"highlighted"`)

The title text uses accent colors that change between light and dark mode.

| Mode | Title Color | Example |
|------|-------------|---------|
| Light Mode | **Accent Dark** | `#805AA0` (purple) |
| Dark Mode | **Accent Light Pastel** | `#E6D2F5` (light purple) |

```
┌─────────────────────────────────────┐
│  Title Text (Accent Dark/#805AA0)   │  ← Changes color by mode
│                                     │
│  • Body text (#374151)              │
│  • Body text (#374151)              │
│  Background: rgba(232,215,241,0.6)  │
└─────────────────────────────────────┘
```

### Option B: Non-Colored Title (neutral/monochrome)

The title uses the same color as body text - no accent color.

| Mode | Title Color | Example |
|------|-------------|---------|
| Light Mode | **Dark Gray** | `#374151` |
| Dark Mode | **White** | `#FFFFFF` |

```
┌─────────────────────────────────────┐
│  Title Text (#374151 or #FFFFFF)    │  ← Same as body text color
│                                     │
│  • Body text (#374151)              │
│  • Body text (#374151)              │
│  Background: rgba(232,215,241,0.6)  │
└─────────────────────────────────────┘
```

### Option C: Badged Title (`title_style: "colored-bg"`)

The title appears inside a colored badge/pill with the accent dark color as background.

| Element | Color | Mode Behavior |
|---------|-------|---------------|
| Badge Background | **Accent Dark** | Does NOT change |
| Badge Text | **White (#FFFFFF)** | **ALWAYS white, NEVER changes** |

```
┌─────────────────────────────────────┐
│ ┌─────────────────────┐             │
│ │ TITLE (WHITE)       │  ← Badge: Accent Dark bg, WHITE text
│ └─────────────────────┘             │  (never changes in dark mode)
│                                     │
│  • Body text (#374151)              │  ← Changes: #374151 → #FFFFFF
│  • Body text (#374151)              │
│  Background: rgba(232,215,241,0.6)  │
└─────────────────────────────────────┘
```

**Critical**: The badged title text is ALWAYS white (`#FFFFFF`) regardless of light/dark mode. This ensures readability against the dark accent background.

### TEXT_BOX Color Summary

| Element | Light Mode | Dark Mode | Changes? |
|---------|------------|-----------|----------|
| **Text Box Background (colored)** | Accent Pastel 60% | Accent Pastel 60% | No |
| **Text Box Background (transparent)** | transparent | transparent | No |
| **Colored Title (plain/highlighted)** | Accent Dark | Accent Light Pastel | Yes |
| **Non-Colored Title** | `#374151` | `#FFFFFF` | Yes |
| **Badged Title Background** | Accent Dark | Accent Dark | No |
| **Badged Title Text** | `#FFFFFF` | `#FFFFFF` | **NO** |
| **Body Text** | `#374151` | `#FFFFFF` | Yes |

---

## Dark/Light Mode Behavior

### What Changes

| Element | Light Mode | Dark Mode |
|---------|------------|-----------|
| Slide background | Light/white | Dark/black |
| Text box heading | Dark accent (e.g., `#805AA0`) | Light pastel (e.g., `#E6D2F5`) |
| Text box body | Dark gray (`#374151`) | White (`#FFFFFF`) |

### What Does NOT Change

| Element | Behavior |
|---------|----------|
| Hexagon shape color | Same dark color in both modes |
| Text on hexagon shapes | Always white (`#FFFFFF`) |
| Text box background opacity | Always 60% |
| Font opacity | Always 100% (solid) |

### Visual Example

```
LIGHT MODE                          DARK MODE
┌─────────────────────┐            ┌─────────────────────┐
│ Hexagon: #805AA0    │            │ Hexagon: #805AA0    │
│ Text: #FFFFFF       │            │ Text: #FFFFFF       │
│ (no change)         │            │ (no change)         │
└─────────────────────┘            └─────────────────────┘

┌─────────────────────┐            ┌─────────────────────┐
│ Box: rgba(60%)      │            │ Box: rgba(60%)      │
│ Heading: #805AA0    │  ───────>  │ Heading: #E6D2F5    │
│ Body: #374151       │            │ Body: #FFFFFF       │
└─────────────────────┘            └─────────────────────┘
```

---

## CSS Variable Definitions

```css
:root {
  /* Primary & Secondary */
  --color-primary: #0066CC;
  --color-primary-dark: #004C99;
  --color-primary-light: #3399FF;
  --color-secondary: #FF6B35;
  --color-secondary-dark: #CC4400;
  --color-secondary-light: #FF9966;

  /* Accent 1: Purple */
  --accent-1-dark: #805AA0;
  --accent-1-pastel: rgba(232, 215, 241, 0.6);
  --accent-1-light-pastel: #E6D2F5;
  --accent-1-text: #805AA0;  /* Switches in dark mode */

  /* Accent 2: Blue */
  --accent-2-dark: #2980B9;
  --accent-2-pastel: rgba(189, 224, 249, 0.6);
  --accent-2-light-pastel: #B4DCFF;
  --accent-2-text: #2980B9;

  /* Accent 3: Red */
  --accent-3-dark: #C0392B;
  --accent-3-pastel: rgba(254, 226, 226, 0.6);
  --accent-3-light-pastel: #FFC8C3;
  --accent-3-text: #C0392B;

  /* Accent 4: Green */
  --accent-4-dark: #27AE60;
  --accent-4-pastel: rgba(212, 237, 218, 0.6);
  --accent-4-light-pastel: #B4F5D2;
  --accent-4-text: #27AE60;

  /* Accent 5: Yellow */
  --accent-5-dark: #D39E1E;
  --accent-5-pastel: rgba(253, 230, 138, 0.6);
  --accent-5-light-pastel: #FFF0BE;
  --accent-5-text: #D39E1E;

  /* Accent 6: Cyan */
  --accent-6-dark: #0097A7;
  --accent-6-pastel: rgba(195, 241, 247, 0.6);
  --accent-6-light-pastel: #B2EBF2;
  --accent-6-text: #0097A7;

  /* Accent 7: Orange */
  --accent-7-dark: #E65100;
  --accent-7-pastel: rgba(255, 224, 178, 0.6);
  --accent-7-light-pastel: #FFCCBC;
  --accent-7-text: #E65100;

  /* Accent 8: Teal */
  --accent-8-dark: #00796B;
  --accent-8-pastel: rgba(178, 223, 219, 0.6);
  --accent-8-light-pastel: #B2DFDB;
  --accent-8-text: #00796B;

  /* Accent 9: Pink */
  --accent-9-dark: #C2185B;
  --accent-9-pastel: rgba(225, 213, 246, 0.6);
  --accent-9-light-pastel: #F8BBD9;
  --accent-9-text: #C2185B;

  /* Accent 10: Indigo */
  --accent-10-dark: #3949AB;
  --accent-10-pastel: rgba(197, 202, 233, 0.6);
  --accent-10-light-pastel: #D1D9FF;
  --accent-10-text: #3949AB;

  /* Body Text */
  --text-primary: #374151;
  --text-secondary: #6B7280;
  --text-on-dark: #FFFFFF;
}

/* Dark Mode Overrides */
:root.theme-dark-mode,
:root.theme-dark {
  /* Accent text colors switch to light pastel */
  --accent-1-text: #E6D2F5;
  --accent-2-text: #B4DCFF;
  --accent-3-text: #FFC8C3;
  --accent-4-text: #B4F5D2;
  --accent-5-text: #FFF0BE;
  --accent-6-text: #B2EBF2;
  --accent-7-text: #FFCCBC;
  --accent-8-text: #B2DFDB;
  --accent-9-text: #F8BBD9;
  --accent-10-text: #D1D9FF;

  /* Body text switches to white */
  --text-primary: #FFFFFF;
  --text-secondary: #D1D5DB;
}
```

---

## Quick Reference

### For Hexagon Shapes
```css
background: var(--accent-1-dark);  /* #805AA0 */
color: #FFFFFF;                     /* Always white */
```

### For Text Boxes
```css
background: var(--accent-1-pastel); /* rgba(232, 215, 241, 0.6) */
```

### For Text Box Headings
```css
color: var(--accent-1-text, #805AA0); /* Switches in dark mode */
```

### For Text Box Body
```css
color: var(--text-primary, #374151); /* Switches in dark mode */
```

---

## Source Files

| File | Contents |
|------|----------|
| `app/themes.py` | Theme definitions |
| `app/core/type_constraints.py` | Color schemes |
| `templates/round_table/5.html` | Pastel box examples |
| `templates/pyramid/*.html` | Shape + text box examples |
| Layout Service CSS | CSS variable definitions |

---

*Last updated: January 2025*
