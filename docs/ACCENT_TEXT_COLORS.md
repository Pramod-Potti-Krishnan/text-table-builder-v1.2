# Accent Text Colors - Theming Guide

## Overview

The Layout Service provides **9 accent text color CSS variables** that automatically switch between light and dark modes. Use these for colored headings in illustration templates to ensure proper visibility in both themes.

## Available Colors

| Variable | Light Mode | Dark Mode | Use Case |
|----------|------------|-----------|----------|
| `--accent-text-purple` | #805aa0 | #e6d2f5 | Purple/Violet headings |
| `--accent-text-blue` | #2980b9 | #b4dcff | Blue headings |
| `--accent-text-red` | #c0392b | #ffc8c3 | Red headings |
| `--accent-text-green` | #27ae60 | #b4f5d2 | Green headings |
| `--accent-text-yellow` | #d39e1e | #fff0be | Yellow/Gold headings |
| `--accent-text-cyan` | #0097a7 | #b2ebf2 | Cyan/Aqua headings |
| `--accent-text-orange` | #e65100 | #ffccbc | Orange headings |
| `--accent-text-teal` | #00796b | #b2dfdb | Teal headings |
| `--accent-text-pink` | #c2185b | #f8bbd9 | Pink/Magenta headings |

## Usage in Templates

### For Headings (h3, labels)

```html
<h3 style="color: var(--accent-text-purple, #805aa0);">Heading Text</h3>
```

Always include the fallback color (light mode value) for cases where CSS variables aren't loaded.

### Example - Star Diagram Template

```html
<!-- Element 1 - Purple -->
<h3 style="color: var(--accent-text-purple, #805aa0);">{element_1_label}</h3>

<!-- Element 2 - Blue -->
<h3 style="color: var(--accent-text-blue, #2980b9);">{element_2_label}</h3>

<!-- Element 3 - Red -->
<h3 style="color: var(--accent-text-red, #c0392b);">{element_3_label}</h3>

<!-- Element 4 - Green -->
<h3 style="color: var(--accent-text-green, #27ae60);">{element_4_label}</h3>

<!-- Element 5 - Yellow -->
<h3 style="color: var(--accent-text-yellow, #d39e1e);">{element_5_label}</h3>
```

## Behavior

- **Light Mode**: Dark, saturated colors for readability on light backgrounds
- **Dark Mode**: Light, pastel colors (near-white with color tinge) for visibility on dark backgrounds

The switching happens automatically when the Layout Service's dark mode is activated (`.theme-dark-mode` or `.theme-dark` class on `:root`).

## Related Variables

For bullet points and body text, use:
```css
color: var(--text-primary, #374151);
```

This switches between dark gray (light mode) and white (dark mode).

## Source File

CSS variables are defined in:
```
layout_builder_main/v7.5-main/src/styles/theme-variables.css
```

## Color Associations by Template

| Template | Suggested Colors |
|----------|------------------|
| Star Diagram (5 points) | purple, blue, red, green, yellow |
| Hexagon (6 elements) | purple, blue, cyan, green, orange, yellow |
| Funnel/Pyramid | purple, blue, cyan, green, yellow (top to bottom) |
| Concept Spread | Match hexagon colors to corresponding boxes |

## Adding New Colors

To add more accent text colors:

1. Edit `layout_builder_main/v7.5-main/src/styles/theme-variables.css`
2. Add to light mode `:root` section (dark color value)
3. Add to dark mode `:root.theme-dark-mode` section (light pastel value)
4. Update cache-buster in `viewer/presentation-viewer.html`
5. Deploy layout service
