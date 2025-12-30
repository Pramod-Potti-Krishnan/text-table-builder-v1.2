# Theming Implementation Guide for C-Series and I-Series

## Overview

This document explains how theming (specifically font colors black/white switching) is implemented in the Text Service v1.2 for C-series (Content) and I-series (Image+Content) layouts. This pattern can be reused by other services that need similar theming capabilities.

---

## Architecture Summary

The theming system uses a **pre-configured template-based approach** where:

1. **HTML Templates** contain CSS variables with fallback values
2. **Variant Specs** (JSON) define which template to use
3. **Theme Presets** provide color palettes and typography
4. **Theme Config** is passed at runtime to override defaults

---

## File Structure

```
app/
├── core/
│   └── theme/
│       ├── __init__.py
│       ├── theming_config.py    # CSS variable mappings, feature flags
│       └── presets.py           # 4 pre-defined theme presets
├── templates/
│   ├── grid/
│   │   ├── grid_2x2_centered_c1.html         # Base C1 template
│   │   └── grid_2x2_centered_c1_themed.html  # CSS variable version
│   ├── multilateral_comparison/
│   │   ├── comparison_2col_c1.html
│   │   └── comparison_2col_c1_themed.html
│   └── ...
├── variant_specs/
│   ├── grid/
│   │   └── grid_2x2_centered_c1.json         # Maps to themed template
│   └── iseries/
│       ├── comparison_2col_i1.json           # Wide layout (I1/I2)
│       └── comparison_2col_i3.json           # Narrow layout (I3/I4)
└── models/
    └── requests.py               # ThemeConfig, TypographyConfig models
```

---

## Key Pattern: Template-Based Theming

### 1. Base Template (Hardcoded Colors)

```html
<!-- comparison_2col_c1.html -->
<div style="color: #1f2937;">  <!-- Hardcoded dark text -->
  <h3 style="color: #1a73e8;">Column Heading</h3>
  <p>{column_1_item_1}</p>
</div>
```

### 2. Themed Template (CSS Variables with Fallbacks)

```html
<!-- comparison_2col_c1_themed.html -->
<div style="color: var(--text-primary, #1f2937);">  <!-- CSS variable with fallback -->
  <h3 style="color: #1a73e8;">Column Heading</h3>
  <p>{column_1_item_1}</p>
</div>
```

**Key Insight**: The `_themed.html` templates use CSS variables like `var(--text-primary, #1f2937)` which:
- Use the CSS variable if defined by the parent document
- Fall back to the hardcoded value (`#1f2937`) if not defined

---

## Color Conventions by Slide Type

| Slide Type | Background | Text Color | Reasoning |
|------------|------------|------------|-----------|
| **H-series (Hero)** | Gradient/Image | `white` / `rgba(255,255,255,0.95)` | Dark backgrounds need light text |
| **C-series (Content)** | Light/White | `#1f2937` (dark gray) | Light backgrounds need dark text |
| **I-series (Image+Content)** | Light content area | `#1f2937` (dark gray) | Content panel is light |

---

## CSS Variable Mapping

Defined in `app/core/theme/theming_config.py`:

```python
CSS_VARIABLE_MAPPING = {
    # Text Colors
    "--text-primary": {"light": "#1f2937", "dark": "#f8fafc"},
    "--text-secondary": {"light": "#374151", "dark": "#e2e8f0"},
    "--text-body": {"light": "#4b5563", "dark": "#cbd5e1"},
    "--text-muted": {"light": "#6b7280", "dark": "#94a3b8"},
    "--text-on-dark": {"light": "#ffffff", "dark": "#ffffff"},

    # Box Backgrounds (for grid layouts)
    "--box-1-bg": {"light": "#dbeafe", "dark": "#1e3a8a"},
    "--box-2-bg": {"light": "#d1fae5", "dark": "#065f46"},
    "--box-3-bg": {"light": "#fef3c7", "dark": "#78350f"},
    "--box-4-bg": {"light": "#fce7f3", "dark": "#831843"},

    # Borders
    "--border-default": {"light": "#d1d5db", "dark": "#4b5563"},
    "--border-light": {"light": "#e5e7eb", "dark": "#374151"},
}
```

---

## Theme Presets

Defined in `app/core/theme/presets.py`. Four pre-configured themes:

### 1. Professional (Default)
```python
{
    "theme_id": "professional",
    "typography": {
        "t1": {"size": 40, "weight": 700, "color": "#1f2937"},  # Dark
        "t2": {"size": 24, "weight": 600, "color": "#374151"},
        "t3": {"size": 20, "weight": 500, "color": "#4b5563"},
        "t4": {"size": 16, "weight": 400, "color": "#6b7280"},
    },
    "colors": {
        "primary": "#1e3a5f",
        "text_primary": "#1f2937",  # Dark text
        "background": "#ffffff",    # Light background
    }
}
```

### 2. Executive
- Darker navy primary, gold/amber accents
- `text_primary`: `#111827`

### 3. Educational
- Educational blue primary, green accents
- `text_primary`: `#1e3a8a`

### 4. Children
- Fun purple primary, bright pink accents
- `text_primary`: `#581c87`
- `background`: `#fefce8` (soft yellow)

---

## Typography Hierarchy (t1-t4)

All C-series and I-series content uses a 4-level typography system:

| Level | Default Size | Weight | Purpose |
|-------|-------------|--------|---------|
| `t1` | 32-40px | 700 | Headings |
| `t2` | 24px | 600 | Subheadings |
| `t3` | 20px | 500 | Body emphasized |
| `t4` | 16px | 400 | Body normal |

Defined in `app/models/requests.py`:

```python
class TypographySpec(BaseModel):
    size: int           # Font size in pixels
    weight: int = 400   # Font weight (100-900)
    color: str          # Text color (hex)
    line_height: float = 1.5
```

---

## How Font Colors Switch (Black/White)

### Pattern 1: Hero Slides (White Text)

Hero slides (title, section divider, closing) have gradient or image backgrounds:

```python
# From title_slide_generator.py
prompt = f"""
...
### Visual Requirements:
- Gradient background: {gradient}
- White text color on all elements    # <-- White text hardcoded
- Text shadows on ALL text
...
```

Example HTML output:
```html
<h1 style="color: white; text-shadow: 0 4px 12px rgba(0,0,0,0.3);">
  Presentation Title
</h1>
<p style="color: rgba(255,255,255,0.95);">
  Subtitle text here
</p>
```

### Pattern 2: C-Series/I-Series (Dark Text)

Content slides use templates with dark text:

```html
<!-- grid_2x2_centered_c1_themed.html -->
<h3 style="color: var(--text-primary, #1f2937);">
  {box_1_title}
</h3>
<p style="color: var(--text-primary, #6b7280);">
  {box_1_description}
</p>
```

The Layout Service injects CSS variables at render time:
```html
<style>
:root {
  --text-primary: #1f2937;  /* Light mode: dark text */
  /* OR */
  --text-primary: #f8fafc;  /* Dark mode: light text */
}
</style>
```

---

## Variant Specs Connection

Each variant has a JSON spec that points to its template:

```json
// grid_2x2_centered_c1.json
{
  "variant_id": "grid_2x2_centered_c1",
  "template_path": "app/templates/grid/grid_2x2_centered_c1_themed.html",
  "description": "2x2 grid with explicit placeholders (C1 layout)"
}
```

### I-Series Variant Specs

I-series variants include `iseries_layout` to indicate content width:

```json
// comparison_2col_i1.json
{
  "variant_id": "comparison_2col_i1",
  "iseries_layout": "wide",           // I1/I2 have more content space
  "template_path": "app/templates/multilateral_comparison/comparison_2col_c1_themed.html"
}

// comparison_2col_i3.json
{
  "variant_id": "comparison_2col_i3",
  "iseries_layout": "narrow",         // I3/I4 have less content space
  "template_path": "app/templates/multilateral_comparison/comparison_2col_c1_themed.html"
}
```

---

## Template Assembler

The `TemplateAssembler` class handles loading templates and selecting themed versions:

```python
# app/core/template_assembler.py
class TemplateAssembler:
    def get_themed_template_path(self, template_path, variant_id):
        """
        If CSS variable theming is enabled for this variant,
        return path to _themed.html version
        """
        if self._theming_settings.uses_css_variables(variant_id):
            return template_path.replace('.html', '_themed.html')
        return template_path
```

---

## Runtime Theme Config

Theme configuration is passed at runtime via API request context:

```python
# Example request context
{
    "theme_config": {
        "theme_id": "professional",
        "colors": {
            "primary": "#1e3a5f",
            "text_primary": "#1f2937",
            "background": "#ffffff"
        },
        "typography": {
            "t1": {"size": 32, "weight": 700, "color": "#1f2937"}
        }
    },
    "styling_mode": "inline_styles"  # or "css_classes"
}
```

---

## Implementation Checklist for New Services

To implement this theming pattern in a new service:

### 1. Create Template Files
- [ ] Create base HTML templates with hardcoded colors
- [ ] Create `_themed.html` versions using CSS variables
- [ ] Use fallback pattern: `var(--variable-name, #fallback)`

### 2. Define CSS Variable Mapping
```python
CSS_VARIABLES = {
    "--text-primary": {"light": "#1f2937", "dark": "#f8fafc"},
    "--bg-primary": {"light": "#ffffff", "dark": "#1e293b"},
}
```

### 3. Create Variant Specs
```json
{
  "variant_id": "my_layout_c1",
  "template_path": "templates/my_layout_c1_themed.html"
}
```

### 4. Create Theme Presets
```python
THEME_PRESETS = {
    "professional": {...},
    "executive": {...},
}
```

### 5. Accept Theme Config in API
```python
class MyRequest(BaseModel):
    theme_config: Optional[ThemeConfig] = None
    styling_mode: str = "inline_styles"
```

---

## Summary

| Component | Purpose | Location |
|-----------|---------|----------|
| Templates | HTML with CSS variable placeholders | `app/templates/` |
| Variant Specs | Map variant_id to template | `app/variant_specs/` |
| Presets | Pre-defined theme configurations | `app/core/theme/presets.py` |
| CSS Variables | Light/dark mode color mappings | `app/core/theme/theming_config.py` |
| ThemeConfig | Runtime theme override | `app/models/requests.py` |

**Key Insight**: Font colors "switch" between black and white through:
1. **Hero slides**: Always white text (hardcoded for dark backgrounds)
2. **Content slides**: CSS variables with fallbacks that the Layout Service can override

---

*Version: 1.0.0*
*Last Updated: December 2024*
