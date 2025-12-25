# Layout Service: Theme Capabilities Specification

**Version**: 1.0
**Date**: December 2024
**For**: Layout Builder v7.5+
**Prepared by**: Text Service Team

---

## Executive Summary

This document specifies the theme capabilities the Layout Service needs to:
1. **Store & Manage** themes with dark/light variants
2. **Expose to Director** for theme selection and content generation
3. **Expose to Frontend** for user theme switching
4. **Apply themes** consistently across presentations

The Layout Service already has robust theme infrastructure. This guide specifies enhancements for the unified theming system.

---

## Current State Analysis

### What Layout Service Already Has

**Theme Model** (`models.py`):
- ThemeConfig with colors (30+ properties), typography, spacing, effects
- ThemeColors includes: primary, accent, text colors, hero colors, chart colors
- ThemeTypography with standard and hero variants
- Custom theme support per user

**Theme Endpoints** (`server.py`):
- `GET /api/themes` - List all themes
- `GET /api/themes/{id}` - Get single theme
- `GET /api/themes/sync` - Bulk sync for services
- `PUT /api/presentations/{id}/theme` - Set presentation theme
- `GET /api/presentations/{id}/theme/css-variables` - Get CSS variables

**Theme Manager** (`src/themes/theme-manager.js`):
- Injects CSS variables into document
- Maps theme properties to `--theme-*` variables
- Generates Deckster typography classes

**Predefined Themes**:
- `corporate-blue` (primary: #1e40af)
- `elegant-emerald` (primary: #059669)
- `vibrant-orange` (primary: #ea580c)
- `dark-mode` (primary: #60a5fa)

### What Needs Enhancement

1. **Dark/Light Variants** - Each theme needs both modes
2. **Theme Sync API** - Enhanced for Director integration
3. **Frontend Theme Picker** - UI for theme switching
4. **Real-time Theme Switch** - Apply without reload
5. **Audience/Purpose Metadata** - Store with presentation

---

## Part 1: Theme Structure Enhancement

### 1.1 Enhanced Theme Model

**Current ThemeConfig** has flat color structure. Enhance to support variants:

```python
class ThemeVariant(BaseModel):
    """Colors and settings for a specific mode (light/dark)."""
    colors: ThemeColors
    typography_adjustments: Optional[Dict] = None  # Mode-specific tweaks

class EnhancedThemeConfig(BaseModel):
    """Theme with both light and dark variants."""
    id: str
    name: str
    description: str
    category: str                           # "professional", "creative", "educational"

    # Mode variants
    has_dark_mode: bool = True
    light: ThemeVariant                     # Light mode colors
    dark: Optional[ThemeVariant] = None     # Dark mode colors (if has_dark_mode)

    # Shared settings (same for both modes)
    typography: ThemeTypography
    spacing: ThemeSpacing
    effects: ThemeEffects

    # Metadata
    is_custom: bool = False
    created_by: Optional[str] = None
    is_public: bool = True
```

### 1.2 Color Inversions for Dark Mode

Each theme should define explicit dark mode colors (not auto-calculated):

```python
# Example: corporate-blue theme
CORPORATE_BLUE = EnhancedThemeConfig(
    id="corporate-blue",
    name="Corporate Blue",
    description="Professional blue theme for business presentations",
    category="professional",
    has_dark_mode=True,

    light=ThemeVariant(
        colors=ThemeColors(
            # Primary
            primary="#1e40af",
            primary_light="#3b82f6",
            primary_dark="#1e3a8a",
            accent="#f59e0b",

            # Background
            background="#ffffff",
            background_alt="#f8fafc",

            # Text
            text_primary="#1f2937",
            text_secondary="#374151",
            text_body="#4b5563",

            # Hero (typically inverted)
            hero_text_primary="#ffffff",
            hero_text_secondary="#e5e7eb",
            hero_background="#1e40af",

            # UI
            border="#d1d5db",
            footer_text="#6b7280",

            # Tertiary (for boxes, groupings)
            tertiary_1="#dbeafe",
            tertiary_2="#d1fae5",
            tertiary_3="#fef3c7",
            tertiary_4="#fce7f3",
            tertiary_5="#ede9fe",

            # Charts
            chart_1="#3b82f6",
            chart_2="#10b981",
            chart_3="#f59e0b",
            chart_4="#ec4899",
            chart_5="#8b5cf6",
            chart_6="#14b8a6",
        )
    ),

    dark=ThemeVariant(
        colors=ThemeColors(
            # Primary (slightly lighter for dark bg)
            primary="#3b82f6",
            primary_light="#60a5fa",
            primary_dark="#2563eb",
            accent="#fbbf24",

            # Background (dark)
            background="#0f172a",
            background_alt="#1e293b",

            # Text (inverted)
            text_primary="#f8fafc",
            text_secondary="#e2e8f0",
            text_body="#cbd5e1",

            # Hero (can stay dark on dark)
            hero_text_primary="#ffffff",
            hero_text_secondary="#e5e7eb",
            hero_background="#1e3a8a",

            # UI
            border="#475569",
            footer_text="#94a3b8",

            # Tertiary (darker variants)
            tertiary_1="#1e3a8a",
            tertiary_2="#065f46",
            tertiary_3="#78350f",
            tertiary_4="#831843",
            tertiary_5="#4c1d95",

            # Charts (same, good contrast on dark)
            chart_1="#60a5fa",
            chart_2="#34d399",
            chart_3="#fbbf24",
            chart_4="#f472b6",
            chart_5="#a78bfa",
            chart_6="#2dd4bf",
        )
    ),

    typography=ThemeTypography(...),
    spacing=ThemeSpacing(...),
    effects=ThemeEffects(...)
)
```

### 1.3 Theme Registry Update

Update the theme registry to use enhanced structure:

```python
# In server.py or separate theme_registry.py
ENHANCED_THEME_REGISTRY = {
    "corporate-blue": CORPORATE_BLUE,
    "elegant-emerald": ELEGANT_EMERALD,
    "vibrant-orange": VIBRANT_ORANGE,
    "playful-colors": PLAYFUL_COLORS,
    "educational-warm": EDUCATIONAL_WARM,
    "modern-gradient": MODERN_GRADIENT,
    "classic-serif": CLASSIC_SERIF,
    "dark-professional": DARK_PROFESSIONAL,
}
```

---

## Part 2: API Enhancements for Director

### 2.1 Enhanced Theme Sync Endpoint

**Current**: `GET /api/themes/sync`
Returns flat list of themes.

**Enhanced**:
```python
@app.get("/api/themes/sync")
async def sync_themes() -> ThemeSyncResponse:
    """
    Returns all themes with full variant information for Director sync.
    Called at Director startup and periodically.
    """
    return {
        "version": "2.0",
        "timestamp": datetime.utcnow().isoformat(),
        "themes": [
            {
                "id": "corporate-blue",
                "name": "Corporate Blue",
                "category": "professional",
                "has_dark_mode": True,
                "default_mode": "light",
                "recommended_for": ["professional", "executive"],

                # Full color definitions for both modes
                "light": {
                    "colors": {...},
                },
                "dark": {
                    "colors": {...},
                },

                # Shared
                "typography": {...},
                "spacing": {...},
            },
            # ... more themes
        ]
    }
```

### 2.2 Theme Recommendation Endpoint

New endpoint for Director to get theme suggestions:

```python
@app.post("/api/themes/recommend")
async def recommend_theme(
    audience: str,
    purpose: str,
    preferences: Optional[Dict] = None
) -> ThemeRecommendation:
    """
    Recommend a theme based on audience and purpose.

    Args:
        audience: "kids_young", "professional", "executive", etc.
        purpose: "sales", "educational", "informational", etc.
        preferences: Optional user preferences (color family, etc.)

    Returns:
        Recommended theme with rationale.
    """

    # Recommendation logic
    RECOMMENDATIONS = {
        ("executive", "sales"): ("elegant-emerald", "dark"),
        ("executive", "informational"): ("corporate-blue", "dark"),
        ("professional", "sales"): ("corporate-blue", "light"),
        ("professional", "educational"): ("educational-warm", "light"),
        ("kids_young", "*"): ("playful-colors", "light"),
        ("academic", "*"): ("classic-serif", "light"),
    }

    key = (audience, purpose)
    if key in RECOMMENDATIONS:
        theme_id, mode = RECOMMENDATIONS[key]
    else:
        # Fallback logic
        theme_id, mode = ("corporate-blue", "light")

    return {
        "theme_id": theme_id,
        "mode": mode,
        "rationale": f"Recommended for {audience} audience with {purpose} purpose",
        "alternatives": [...]
    }
```

### 2.3 Presentation Creation with Theme

**Current**: Presentation created with flat theme_id.

**Enhanced**:
```python
class CreatePresentationRequest(BaseModel):
    title: str
    slides: List[SlideRequest]

    # Theme specification
    theme_id: str = "corporate-blue"
    theme_mode: str = "light"              # NEW: "light" or "dark"

    # Presentation context (for audit/reference)
    audience: Optional[str] = None         # NEW
    purpose: Optional[str] = None          # NEW

    # Existing
    derivative_elements: Optional[DerivativeElements] = None

@app.post("/api/presentations")
async def create_presentation(request: CreatePresentationRequest):
    """Create presentation with theme and mode."""

    # Resolve theme with mode
    theme = get_theme_for_mode(request.theme_id, request.theme_mode)

    presentation = Presentation(
        id=str(uuid4()),
        title=request.title,
        theme_id=request.theme_id,
        theme_mode=request.theme_mode,     # Store mode
        audience=request.audience,         # Store for reference
        purpose=request.purpose,
        slides=request.slides,
        # ...
    )

    # Store and return
    await storage.save(presentation)
    return {"id": presentation.id, "url": f"/p/{presentation.id}"}
```

---

## Part 3: API Enhancements for Frontend

### 3.1 Get Available Themes for Picker

```python
@app.get("/api/themes/picker")
async def get_themes_for_picker() -> List[ThemePickerItem]:
    """
    Returns themes formatted for frontend theme picker UI.
    Includes preview colors and mode indicators.
    """
    return [
        {
            "id": "corporate-blue",
            "name": "Corporate Blue",
            "category": "Professional",
            "has_dark_mode": True,
            "preview": {
                "light": {
                    "primary": "#1e40af",
                    "accent": "#f59e0b",
                    "background": "#ffffff",
                    "text": "#1f2937"
                },
                "dark": {
                    "primary": "#3b82f6",
                    "accent": "#fbbf24",
                    "background": "#0f172a",
                    "text": "#f8fafc"
                }
            }
        },
        # ... more themes
    ]
```

### 3.2 Switch Presentation Theme

```python
@app.put("/api/presentations/{presentation_id}/theme")
async def update_presentation_theme(
    presentation_id: str,
    theme_id: str,
    theme_mode: str = "light"
) -> Dict:
    """
    Change presentation theme. Frontend calls this when user switches theme.

    Args:
        presentation_id: Presentation UUID
        theme_id: New theme ID
        theme_mode: "light" or "dark"

    Returns:
        Updated theme CSS variables for immediate application.
    """
    presentation = await storage.load(presentation_id)
    presentation.theme_id = theme_id
    presentation.theme_mode = theme_mode
    await storage.save(presentation)

    # Return CSS variables for immediate application
    theme = get_theme_for_mode(theme_id, theme_mode)
    return {
        "success": True,
        "theme_id": theme_id,
        "theme_mode": theme_mode,
        "css_variables": generate_css_variables(theme)
    }
```

### 3.3 Toggle Dark/Light Mode

```python
@app.post("/api/presentations/{presentation_id}/theme/toggle-mode")
async def toggle_theme_mode(presentation_id: str) -> Dict:
    """
    Toggle between light and dark mode for current theme.
    Quick action for frontend dark mode button.
    """
    presentation = await storage.load(presentation_id)

    # Toggle mode
    new_mode = "dark" if presentation.theme_mode == "light" else "light"

    # Check if theme supports this mode
    theme = ENHANCED_THEME_REGISTRY.get(presentation.theme_id)
    if new_mode == "dark" and not theme.has_dark_mode:
        return {"success": False, "error": "Theme does not support dark mode"}

    presentation.theme_mode = new_mode
    await storage.save(presentation)

    # Return new CSS variables
    theme_variant = theme.dark if new_mode == "dark" else theme.light
    return {
        "success": True,
        "theme_mode": new_mode,
        "css_variables": generate_css_variables(theme_variant)
    }
```

### 3.4 Get CSS Variables for Current Theme

```python
@app.get("/api/presentations/{presentation_id}/theme/css-variables")
async def get_theme_css_variables(presentation_id: str) -> Dict:
    """
    Get CSS variables for presentation's current theme and mode.
    Frontend uses this to apply theme without reload.
    """
    presentation = await storage.load(presentation_id)
    theme = get_theme_for_mode(presentation.theme_id, presentation.theme_mode)

    return {
        "theme_id": presentation.theme_id,
        "theme_mode": presentation.theme_mode,
        "variables": {
            "--theme-primary": theme.colors.primary,
            "--theme-primary-light": theme.colors.primary_light,
            "--theme-accent": theme.colors.accent,
            "--theme-background": theme.colors.background,
            "--theme-text-primary": theme.colors.text_primary,
            "--theme-text-secondary": theme.colors.text_secondary,
            "--theme-border": theme.colors.border,
            "--theme-tertiary-1": theme.colors.tertiary_1,
            "--theme-tertiary-2": theme.colors.tertiary_2,
            "--theme-tertiary-3": theme.colors.tertiary_3,
            "--theme-tertiary-4": theme.colors.tertiary_4,
            "--theme-tertiary-5": theme.colors.tertiary_5,
            "--theme-chart-1": theme.colors.chart_1,
            # ... all variables
        }
    }
```

---

## Part 4: Frontend Theme Application

### 4.1 Theme Manager Enhancement

Update `src/themes/theme-manager.js`:

```javascript
const ThemeManager = (function() {

    // Apply theme from API response
    function applyTheme(cssVariables) {
        const root = document.documentElement;
        for (const [variable, value] of Object.entries(cssVariables)) {
            root.style.setProperty(variable, value);
        }
    }

    // Fetch and apply theme
    async function loadTheme(presentationId) {
        const response = await fetch(
            `/api/presentations/${presentationId}/theme/css-variables`
        );
        const data = await response.json();
        applyTheme(data.variables);
        return data;
    }

    // Switch theme
    async function switchTheme(presentationId, themeId, mode) {
        const response = await fetch(
            `/api/presentations/${presentationId}/theme`,
            {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({theme_id: themeId, theme_mode: mode})
            }
        );
        const data = await response.json();
        if (data.success) {
            applyTheme(data.css_variables);
        }
        return data;
    }

    // Toggle dark/light mode
    async function toggleMode(presentationId) {
        const response = await fetch(
            `/api/presentations/${presentationId}/theme/toggle-mode`,
            {method: 'POST'}
        );
        const data = await response.json();
        if (data.success) {
            applyTheme(data.css_variables);
        }
        return data;
    }

    return {
        applyTheme,
        loadTheme,
        switchTheme,
        toggleMode,
        // ... existing methods
    };
})();
```

### 4.2 Theme Picker Component

Add a theme picker to the viewer:

```javascript
// In presentation-viewer.html or separate component

function renderThemePicker(themes, currentThemeId, currentMode) {
    const picker = document.createElement('div');
    picker.className = 'theme-picker';
    picker.innerHTML = `
        <div class="theme-picker-header">
            <h3>Theme</h3>
            <button class="mode-toggle" onclick="ThemeManager.toggleMode('${presentationId}')">
                ${currentMode === 'light' ? '🌙 Dark' : '☀️ Light'}
            </button>
        </div>
        <div class="theme-grid">
            ${themes.map(theme => `
                <div class="theme-option ${theme.id === currentThemeId ? 'selected' : ''}"
                     onclick="ThemeManager.switchTheme('${presentationId}', '${theme.id}', '${currentMode}')">
                    <div class="theme-preview" style="
                        background: ${theme.preview[currentMode].background};
                        border: 2px solid ${theme.preview[currentMode].primary};
                    ">
                        <div style="color: ${theme.preview[currentMode].text}">${theme.name}</div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    return picker;
}
```

### 4.3 Keyboard Shortcuts

Add to viewer:

```javascript
document.addEventListener('keydown', (e) => {
    // 'T' - Toggle theme picker
    if (e.key === 't' || e.key === 'T') {
        toggleThemePicker();
    }

    // 'D' - Toggle dark/light mode
    if (e.key === 'd' || e.key === 'D') {
        ThemeManager.toggleMode(presentationId);
    }
});
```

---

## Part 5: Content Area Theme Application

### 5.1 CSS Variable Usage in Content

The Text Service generates content using CSS variables. Layout Service must ensure these are available:

```css
/* src/styles/content-typography.css */

/* Text colors use theme variables */
.content-area h1,
.content-area h2,
.content-area h3 {
    color: var(--theme-text-primary);
}

.content-area p,
.content-area li {
    color: var(--theme-text-secondary);
}

/* Box backgrounds use tertiary colors */
.content-area .box-1 { background: var(--theme-tertiary-1); }
.content-area .box-2 { background: var(--theme-tertiary-2); }
.content-area .box-3 { background: var(--theme-tertiary-3); }
.content-area .box-4 { background: var(--theme-tertiary-4); }
.content-area .box-5 { background: var(--theme-tertiary-5); }

/* Borders */
.content-area .bordered {
    border-color: var(--theme-border);
}

/* Accent elements */
.content-area .accent {
    color: var(--theme-accent);
}
```

### 5.2 Theme Variable Injection

Ensure theme variables are injected before content renders:

```javascript
// In presentation-viewer.html
document.addEventListener('DOMContentLoaded', async () => {
    // 1. Load presentation data (embedded)
    const presentation = PRESENTATION_DATA;

    // 2. Apply theme before rendering
    await ThemeManager.loadTheme(presentation.id);

    // 3. Initialize Reveal.js
    Reveal.initialize({...});

    // 4. Render slides
    renderSlides(presentation.slides);
});
```

---

## Part 6: Implementation Checklist

### Phase 1: Model Updates

- [ ] Create `ThemeVariant` model with light/dark colors
- [ ] Create `EnhancedThemeConfig` model with both variants
- [ ] Add `theme_mode` field to Presentation model
- [ ] Add `audience`, `purpose` fields to Presentation model
- [ ] Update theme registry with enhanced themes

### Phase 2: Director-Facing APIs

- [ ] Enhance `/api/themes/sync` with variant data
- [ ] Add `/api/themes/recommend` endpoint
- [ ] Update `POST /api/presentations` to accept `theme_mode`
- [ ] Store audience/purpose with presentation

### Phase 3: Frontend-Facing APIs

- [ ] Add `/api/themes/picker` endpoint
- [ ] Update `PUT /api/presentations/{id}/theme` for mode
- [ ] Add `/api/presentations/{id}/theme/toggle-mode`
- [ ] Enhance `/api/presentations/{id}/theme/css-variables`

### Phase 4: Frontend Components

- [ ] Update ThemeManager.js with new methods
- [ ] Add theme picker component
- [ ] Add dark mode toggle button
- [ ] Add keyboard shortcuts (T, D)
- [ ] Ensure real-time theme switching works

### Phase 5: CSS Integration

- [ ] Update content-typography.css with CSS variables
- [ ] Ensure all content uses theme variables
- [ ] Test dark mode rendering
- [ ] Verify tertiary colors for boxes

---

## Part 7: API Summary

### For Director Service

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/themes/sync` | GET | Sync all themes with variants |
| `/api/themes/recommend` | POST | Get theme recommendation |
| `/api/presentations` | POST | Create with theme_id + theme_mode |
| `/capabilities` | GET | Get service capabilities |

### For Frontend

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/themes/picker` | GET | Get themes for picker UI |
| `/api/presentations/{id}/theme` | PUT | Change presentation theme |
| `/api/presentations/{id}/theme/toggle-mode` | POST | Toggle dark/light |
| `/api/presentations/{id}/theme/css-variables` | GET | Get CSS variables |

---

## Part 8: Theme Definition Template

For adding new themes, use this template:

```python
NEW_THEME = EnhancedThemeConfig(
    id="theme-id",                          # kebab-case identifier
    name="Theme Display Name",
    description="Brief description",
    category="professional|creative|educational|playful",
    has_dark_mode=True,

    light=ThemeVariant(
        colors=ThemeColors(
            # Primary family
            primary="#______",
            primary_light="#______",
            primary_dark="#______",
            accent="#______",

            # Backgrounds
            background="#ffffff",           # Usually white for light mode
            background_alt="#______",       # Slightly off-white

            # Text
            text_primary="#______",         # Dark for light mode
            text_secondary="#______",
            text_body="#______",

            # Hero (inverted)
            hero_text_primary="#ffffff",
            hero_text_secondary="#______",
            hero_background="#______",

            # UI
            border="#______",
            footer_text="#______",

            # Tertiary (for boxes) - typically light pastels
            tertiary_1="#______",
            tertiary_2="#______",
            tertiary_3="#______",
            tertiary_4="#______",
            tertiary_5="#______",

            # Charts
            chart_1="#______",
            chart_2="#______",
            chart_3="#______",
            chart_4="#______",
            chart_5="#______",
            chart_6="#______",
        )
    ),

    dark=ThemeVariant(
        colors=ThemeColors(
            # Primary family (slightly lighter)
            primary="#______",
            primary_light="#______",
            primary_dark="#______",
            accent="#______",

            # Backgrounds (dark)
            background="#______",           # Dark, e.g., #0f172a
            background_alt="#______",

            # Text (inverted - light)
            text_primary="#______",         # Light for dark mode
            text_secondary="#______",
            text_body="#______",

            # Hero
            hero_text_primary="#ffffff",
            hero_text_secondary="#______",
            hero_background="#______",

            # UI
            border="#______",
            footer_text="#______",

            # Tertiary (darker variants)
            tertiary_1="#______",
            tertiary_2="#______",
            tertiary_3="#______",
            tertiary_4="#______",
            tertiary_5="#______",

            # Charts (brighter for dark bg)
            chart_1="#______",
            chart_2="#______",
            chart_3="#______",
            chart_4="#______",
            chart_5="#______",
            chart_6="#______",
        )
    ),

    typography=ThemeTypography(
        font_family="Font Name, sans-serif",
        font_family_heading="Optional Heading Font",
        # ...
    ),

    spacing=ThemeSpacing(
        slide_padding="60px",
        element_gap="24px",
        section_gap="48px",
    ),

    effects=ThemeEffects(
        border_radius="8px",
        shadow_small="...",
        shadow_medium="...",
        shadow_large="...",
    ),
)
```

---

*Document prepared for Layout Builder team*
