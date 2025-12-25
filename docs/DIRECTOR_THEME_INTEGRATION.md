# Director Service: Theme Integration Guide

**Version**: 1.0
**Date**: December 2024
**For**: Director Agent v4.0+
**Prepared by**: Text Service Team

---

## Executive Summary

This document outlines how the Director Service should integrate the unified theming system across two stages:
1. **Strawman Stage** - Decide theme, audience, and purpose
2. **Generation Stage** - Pass theming parameters to content services

The Director already has foundational infrastructure (`theme_config.py`, `content_context.py`). This guide specifies enhancements for full theming support.

---

## Current State Analysis

### What Director Already Has

**Theme System** (`src/models/theme_config.py`):
- 4 predefined themes: `professional`, `executive`, `educational`, `children`
- ThemeConfig with typography (9 levels) and colors (16 variants)
- Theme expansion via THEME_REGISTRY lookup

**Content Context** (`src/models/content_context.py`):
- AudienceConfig with audience_type, complexity_level, max_sentence_words
- PurposeConfig with purpose_type, emotional_tone, structure_pattern
- TimeConfig for duration and slide count

**Context Extraction** (`src/models/decision.py` - ExtractedContext):
- audience_preset: kids_young, professional, executive, etc.
- purpose_preset: inform, educate, persuade, inspire, qbr
- Automatic extraction from user natural language

### What Needs Enhancement

1. **Theme Selection** - Add to strawman stage decision-making
2. **Dark/Light Mode** - Each theme needs both variants
3. **Theme Sync** - Sync with Layout Service's theme registry
4. **Pass-through** - Ensure theme flows to all downstream services

---

## Part 1: Strawman Stage Integration

### 1.1 When to Decide Theme, Audience, Purpose

During strawman generation, the Director must establish:

| Setting | When Decided | How Decided |
|---------|--------------|-------------|
| **Audience** | During context extraction | Extracted from user input or asked explicitly |
| **Purpose** | During context extraction | Extracted from user input or asked explicitly |
| **Theme** | At strawman generation | Default based on audience, or user selection |

### 1.2 Enhanced ExtractedContext Model

**Current** (`src/models/decision.py`):
```python
class ExtractedContext(BaseModel):
    topic: str
    audience: str
    duration: int
    purpose: str
    tone: str
    audience_preset: str
    purpose_preset: str
    # ... existing fields
```

**Enhanced**:
```python
class ExtractedContext(BaseModel):
    # ... existing fields ...

    # NEW: Theme settings
    theme_id: Optional[str] = None          # e.g., "corporate-blue", "elegant-emerald"
    theme_mode: Optional[str] = "light"     # "light" or "dark"

    # Detection flags
    has_theme: bool = False
```

### 1.3 Theme Selection Logic

Add to `StrawmanGenerator` or `DecisionEngine`:

```python
def determine_theme(self, context: ExtractedContext) -> Tuple[str, str]:
    """
    Determine theme_id and theme_mode based on context.
    Returns: (theme_id, theme_mode)
    """

    # If user explicitly specified theme
    if context.has_theme and context.theme_id:
        return (context.theme_id, context.theme_mode or "light")

    # Default theme based on audience
    AUDIENCE_TO_THEME = {
        "kids_young": ("playful-colors", "light"),      # Bright, engaging
        "kids_older": ("playful-colors", "light"),
        "teens": ("modern-gradient", "light"),          # Contemporary
        "professional": ("corporate-blue", "light"),    # Business default
        "executive": ("elegant-emerald", "dark"),       # Premium feel
        "academic": ("classic-serif", "light"),         # Traditional
        "general": ("corporate-blue", "light"),         # Safe default
    }

    audience = context.audience_preset or "general"
    return AUDIENCE_TO_THEME.get(audience, ("corporate-blue", "light"))
```

### 1.4 Enhanced Strawman Model

**Current** (`src/models/decision.py`):
```python
class Strawman(BaseModel):
    title: str
    slides: List[StrawmanSlide]
    metadata: Optional[Dict]
```

**Enhanced**:
```python
class Strawman(BaseModel):
    title: str
    slides: List[StrawmanSlide]
    metadata: Optional[Dict]

    # NEW: Presentation-level theming
    theming: Optional[PresentationTheming] = None

class PresentationTheming(BaseModel):
    """Presentation-level theming decisions made at strawman stage."""
    theme_id: str                    # e.g., "corporate-blue"
    theme_mode: str = "light"        # "light" or "dark"
    audience: str                    # e.g., "professional", "kids_young"
    purpose: str                     # e.g., "sales", "educational"

    # Optional overrides (user can customize)
    custom_primary_color: Optional[str] = None
    custom_font_family: Optional[str] = None
```

### 1.5 Strawman Generation Prompt Update

In `StrawmanGenerator._generate_with_ai()`, update the system prompt to include:

```markdown
## THEMING DECISIONS

Based on the audience and purpose, you must include theming in your strawman:

1. **Theme Selection**:
   - For executives/board: Use "elegant-emerald" or "corporate-blue" with dark mode
   - For professionals: Use "corporate-blue" with light mode
   - For educational/training: Use "educational-warm" with light mode
   - For kids/young audience: Use "playful-colors" with light mode

2. **Include in Output**:
   Your strawman JSON must include:
   ```json
   {
     "title": "...",
     "slides": [...],
     "theming": {
       "theme_id": "corporate-blue",
       "theme_mode": "light",
       "audience": "professional",
       "purpose": "sales"
     }
   }
   ```
```

### 1.6 User Confirmation in Plan/Strawman

When presenting the strawman to the user, include theming info:

```markdown
## Presentation Outline

**Title**: [Presentation Title]
**Theme**: Corporate Blue (Light Mode)
**Audience**: Professional/Business
**Purpose**: Sales/Persuasion
**Slides**: 12

### Slide Structure:
1. Title Slide (Hero) - [Topic]
2. ...
```

This allows the user to request changes: "Make it dark mode" or "Use a more playful theme".

---

## Part 2: Generation Stage Integration

### 2.1 Text Service API Contract

When calling Text Service for content generation, include theming:

**Current Call** (observed in `text_service_client_v1_2.py`):
```python
payload = {
    "variant_id": slide.variant_id,
    "layout": slide.layout,
    "topics": slide.topics,
    "target_points": target_points,
    "notes": slide.notes,
    "purpose": slide.purpose,
    "theme": theme_config,           # Already exists
    "content_context": content_ctx   # Already exists
}
```

**Enhanced Theming in Theme Config**:
```python
theme_config = {
    "theme_id": strawman.theming.theme_id,
    "mode": strawman.theming.theme_mode,  # NEW: "light" or "dark"

    # Full theme details (from Layout Service sync or local registry)
    "colors": {
        "primary": "#1e40af",
        "primary_light": "#3b82f6",
        "accent": "#f59e0b",
        "text_primary": "#1f2937",      # Light mode
        "text_secondary": "#374151",
        "background": "#ffffff",
        # ... or dark mode equivalents
    },
    "typography": {
        "font_family": "Poppins, sans-serif",
        "t1": {"size": "88px", "weight": 900},
        "t2": {"size": "29px", "weight": 700},
        # ...
    }
}
```

### 2.2 Content Context Enhancement

**Current ContentContext** already has audience and purpose. Ensure it's passed:

```python
content_context = {
    "audience": {
        "audience_type": strawman.theming.audience,  # e.g., "professional"
        "complexity_level": "moderate",
        "max_sentence_words": 20,
        "avoid_jargon": False
    },
    "purpose": {
        "purpose_type": strawman.theming.purpose,    # e.g., "sales"
        "include_cta": True,
        "emotional_tone": "confident",
        "structure_pattern": "problem_solution"
    }
}
```

### 2.3 Hero Slide Generation

For hero slides (title, section divider, closing), pass theming:

```python
# Title slide with image
response = await text_client.generate_title_slide_with_image(
    title=strawman.title,
    subtitle=context.topic,
    theme={
        "theme_id": strawman.theming.theme_id,
        "mode": strawman.theming.theme_mode,
        "colors": {...}
    },
    image_style="professional"  # Based on audience
)
```

### 2.4 Layout Service API Contract

When sending to Layout Service for assembly:

```python
presentation_payload = {
    "title": strawman.title,
    "slides": formatted_slides,

    # NEW: Theme specification
    "theme_id": strawman.theming.theme_id,
    "theme_mode": strawman.theming.theme_mode,

    # Derivative elements (existing)
    "derivative_elements": {
        "footer": {...},
        "logo": {...}
    }
}

response = await deck_builder_client.create_presentation(presentation_payload)
```

---

## Part 3: Theme Sync Protocol

### 3.1 Startup Theme Sync

At Director startup, sync themes from Layout Service:

```python
# In main.py or startup handler
async def sync_themes_from_layout_service():
    """Fetch available themes from Layout Service."""
    try:
        response = await httpx.get(
            f"{LAYOUT_SERVICE_URL}/api/themes/sync",
            timeout=10.0
        )
        themes = response.json()

        # Store in THEME_REGISTRY
        for theme in themes["themes"]:
            THEME_REGISTRY[theme["id"]] = theme

        logger.info(f"Synced {len(themes['themes'])} themes from Layout Service")
    except Exception as e:
        logger.warning(f"Theme sync failed, using local defaults: {e}")
```

### 3.2 Theme Availability Check

Before using a theme, verify it exists:

```python
def get_theme_or_default(theme_id: str) -> ThemeConfig:
    """Get theme config, falling back to default if not found."""
    if theme_id in THEME_REGISTRY:
        return THEME_REGISTRY[theme_id]

    logger.warning(f"Theme '{theme_id}' not found, using 'corporate-blue'")
    return THEME_REGISTRY["corporate-blue"]
```

### 3.3 Dark/Light Mode Variants

Each theme in the registry should have both variants:

```python
THEME_REGISTRY = {
    "corporate-blue": {
        "id": "corporate-blue",
        "name": "Corporate Blue",
        "has_dark_mode": True,
        "light": {
            "colors": {
                "primary": "#1e40af",
                "text_primary": "#1f2937",
                "background": "#ffffff",
                # ...
            }
        },
        "dark": {
            "colors": {
                "primary": "#3b82f6",
                "text_primary": "#ffffff",
                "background": "#0f172a",
                # ...
            }
        }
    }
}
```

---

## Part 4: Implementation Checklist

### Phase 1: Model Updates (Low Risk)

- [ ] Add `theme_id`, `theme_mode` to ExtractedContext
- [ ] Add `PresentationTheming` model
- [ ] Add `theming` field to Strawman model
- [ ] Update theme_config.py with dark/light variants

### Phase 2: Strawman Stage (Medium Risk)

- [ ] Add `determine_theme()` logic to StrawmanGenerator
- [ ] Update strawman generation prompt with theming instructions
- [ ] Update user-facing plan/strawman display to show theme
- [ ] Handle user theme change requests in refinement

### Phase 3: Generation Stage (Low Risk)

- [ ] Ensure theme_config includes mode in Text Service calls
- [ ] Ensure content_context includes audience/purpose from theming
- [ ] Pass theme_id and theme_mode to Layout Service

### Phase 4: Theme Sync (Medium Risk)

- [ ] Add startup theme sync from Layout Service
- [ ] Add fallback to local registry
- [ ] Add theme validation before use

---

## Part 5: API Changes Summary

### Outbound to Text Service

```json
POST /api/ai/slide/c1
{
  "variant_id": "comparison_3col",
  "layout": "L25",
  "topics": ["..."],
  "theme": {
    "theme_id": "corporate-blue",
    "mode": "light",
    "colors": {...},
    "typography": {...}
  },
  "content_context": {
    "audience": {
      "audience_type": "professional",
      "complexity_level": "moderate"
    },
    "purpose": {
      "purpose_type": "sales",
      "emotional_tone": "confident"
    }
  }
}
```

### Outbound to Layout Service

```json
POST /api/presentations
{
  "title": "Q4 Sales Strategy",
  "theme_id": "corporate-blue",
  "theme_mode": "light",
  "slides": [...],
  "derivative_elements": {...}
}
```

---

## Part 6: User Experience Flow

### Example Conversation

```
User: Create a presentation about AI trends for our executive team

Director (extracts):
- Topic: AI trends
- Audience: executive
- Purpose: inform (inferred)

Director (determines theming):
- Theme: elegant-emerald (executive default)
- Mode: dark (premium feel)

Director (presents plan):
"I'll create a presentation about AI trends for your executive team.

**Style**: Elegant Emerald theme (Dark Mode) - sophisticated look for senior leadership
**Tone**: Authoritative, data-driven
**Length**: 15 slides (~20 minutes)

Shall I proceed with this outline?"

User: Can you make it light mode instead?

Director (updates):
- Theme: elegant-emerald
- Mode: light

Director: "Updated to light mode. Here's the outline..."
```

---

## Appendix: Theme ID Reference

| Theme ID | Best For | Default Mode |
|----------|----------|--------------|
| `corporate-blue` | General business, professional | light |
| `elegant-emerald` | Executive, premium | dark |
| `vibrant-orange` | Marketing, creative | light |
| `educational-warm` | Training, academic | light |
| `playful-colors` | Kids, casual | light |
| `modern-gradient` | Tech, startup | light |
| `classic-serif` | Traditional, formal | light |
| `dark-mode` | Developer, technical | dark |

---

*Document prepared for Director Agent team*
