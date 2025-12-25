# Holistic Slide Recommendation System Design

**Version**: 1.0.0
**Status**: DRAFT - For Director Team Review
**Date**: December 2024
**Authors**: Text Service Team + Director Team (Collaborative)

---

## Executive Summary

This document proposes an enhanced slide recommendation system that enables **collaborative decision-making** between Text Service and Director Agent. The system provides:

1. **Holistic Layout Recommendations** - Across all layout families (H/C/I), not just C1 variants
2. **Audience-Aware Mix Targets** - Configurable percentages for different audiences
3. **Context-Aware Variety** - Smart grouping for consistency + diversity for different content
4. **Collaborative Protocol** - Both services contribute signals; Director makes final call

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Current System Limitations](#2-current-system-limitations)
3. [Proposed Solution](#3-proposed-solution)
4. [Audience Mix Targets](#4-audience-mix-targets)
5. [Smart Grouping Logic](#5-smart-grouping-logic)
6. [Weighting & Scoring](#6-weighting--scoring)
7. [API Contract](#7-api-contract)
8. [Integration Flow](#8-integration-flow)
9. [Migration Path](#9-migration-path)
10. [Open Questions for Director Team](#10-open-questions-for-director-team)

---

## 1. Problem Statement

### Current Issues

1. **Limited Scope**: Text Service `/recommend-variant` only recommends C1 variants (34 options)
   - No awareness of H-series (H1, H2, H3) or I-series (I1-I4)
   - Layout family decision is made independently by Director

2. **No Audience Awareness**: Recommendations don't consider target audience
   - Kids presentations should favor I-series (visual/images)
   - Professional presentations should favor C1 (structured text)

3. **Variant Repetition**: Current system tends to recommend same variants repeatedly
   - e.g., `grid_2x2_centered` appears too frequently
   - No mix balancing across presentation

4. **Inconsistent Similar Content**: Slides with similar content (e.g., "Phase 1", "Phase 2") may get different layouts
   - Should use consistent layout for grouped content

5. **Isolated Decision-Making**: Director and Text Service make decisions independently
   - No collaborative weighting of signals

---

## 2. Current System Limitations

### Text Service (`/recommend-variant`)

```
Current Flow:
┌─────────────────┐     ┌─────────────────┐
│  Director asks  │ ──▶ │  Text Service   │
│  "recommend for │     │  returns C1     │
│  this content"  │     │  variant only   │
└─────────────────┘     └─────────────────┘
```

**What it provides**:
- Variant recommendations based on topic count
- Space fit analysis
- Content type detection (comparison, sequential, metrics, etc.)

**What it lacks**:
- H-series / I-series recommendations
- Audience context
- Presentation-level variety tracking
- Smart grouping awareness

### Director (`LayoutAnalyzer`)

```
Current Flow:
┌─────────────────┐     ┌─────────────────┐
│  Strawman has   │ ──▶ │  LayoutAnalyzer │
│  slide_type_hint│     │  maps to layout │
└─────────────────┘     └─────────────────┘
```

**What it provides**:
- slide_type_hint → layout mapping
- Basic content analysis
- Diversity tracking (consecutive variants)

**What it lacks**:
- Text Service content expertise integration
- Audience-aware mix targets
- Smart grouping detection

---

## 3. Proposed Solution

### 3.1 Collaborative Decision Model

```
New Flow:
┌─────────────────────────────────────────────────────────────┐
│                    COLLABORATIVE DECISION                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐                ┌─────────────────┐     │
│  │  TEXT SERVICE   │                │    DIRECTOR     │     │
│  │  (Content Expert)│◀──────────────▶│ (Context Expert)│     │
│  └─────────────────┘                └─────────────────┘     │
│         │                                   │                │
│         │ Content signals (60%)             │ Context (25%)  │
│         │ - Layout family fit               │ - Audience     │
│         │ - Variant suitability             │ - Purpose      │
│         │ - Topic count match               │ - Mix targets  │
│         │                                   │                │
│         └───────────────┬───────────────────┘                │
│                         │                                    │
│                         ▼                                    │
│              ┌─────────────────┐                            │
│              │  FINAL DECISION │                            │
│              │  (Director owns) │                            │
│              │  + Variety (15%) │                            │
│              └─────────────────┘                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Decision Weights

| Signal Source | Weight | Contribution |
|--------------|--------|--------------|
| **Text Service** | 60% | Content analysis, layout family fit, variant suitability |
| **Director Context** | 25% | Audience type, purpose, mix targets |
| **Director Variety** | 15% | Diversity enforcement, smart grouping |

### 3.3 New Endpoint

Text Service will expose a new endpoint:

```
POST /v1.2/recommend-layout
```

This provides **holistic recommendations** across all layout families (H, C, I).

---

## 4. Audience Mix Targets

### 4.1 Predefined Targets

| Audience Preset | H-Series | C-Series | I-Series | Description |
|----------------|----------|----------|----------|-------------|
| `kids_young` | 10% | 25% | 65% | Ages 5-8, maximum imagery |
| `kids_older` | 10% | 35% | 55% | Ages 9-12, balanced |
| `middle_school` | 12% | 45% | 43% | Ages 12-14 |
| `high_school` | 15% | 55% | 30% | Ages 14-18 |
| `college` | 12% | 65% | 23% | University/college |
| `professional` | 10% | 70% | 20% | Business professionals |
| `executive` | 15% | 60% | 25% | C-suite, board meetings |
| `general` | 15% | 50% | 35% | Mixed/unknown audience |
| `balanced` | 20% | 40% | 40% | Equal visual/text balance |
| `visual_heavy` | 15% | 30% | 55% | Visual-focused presentations |
| `text_heavy` | 10% | 80% | 10% | Data/text-heavy presentations |

### 4.2 Custom Targets

Director can override defaults by passing custom mix:

```json
{
  "custom_mix_targets": {
    "H": 15,
    "C": 50,
    "I": 35
  }
}
```

### 4.3 Mix Adjustment Algorithm

```python
def calculate_mix_adjustment(current_mix, target_mix):
    """
    Adjust recommendation scores based on current vs target mix.

    If a family is over-represented → reduce its score
    If a family is under-represented → boost its score
    """
    adjustments = {}
    for family in ["H", "C", "I"]:
        deviation = current_mix[family] - target_mix[family]
        # 10% deviation = 0.10 score adjustment
        adjustments[family] = -deviation * 0.01
    return adjustments

# Example:
# Current: H=25%, C=75%, I=0%
# Target:  H=10%, C=70%, I=20%
# Adjustments: H=-0.15, C=-0.05, I=+0.20
# Result: I-series boosted, H-series reduced
```

---

## 5. Smart Grouping Logic

### 5.1 The Problem

Consider a presentation with slides:
- "Use Case 1: Healthcare"
- "Use Case 2: Finance"
- "Use Case 3: Retail"

Without smart grouping, these might get different layouts:
- Use Case 1 → `grid_2x3`
- Use Case 2 → `comparison_3col`
- Use Case 3 → `I2`

This creates visual inconsistency.

### 5.2 Smart Grouping Rules

**Slides in the same semantic group should use the same layout/variant.**

| Pattern | Group Name | Example Titles |
|---------|-----------|----------------|
| `use\s*case\s*\d` | `use_cases` | "Use Case 1", "Use Case 2" |
| `case\s*study` | `case_studies` | "Case Study: Acme", "Case Study: Beta" |
| `phase\s*\d` | `phases` | "Phase 1", "Phase 2: Implementation" |
| `step\s*\d` | `steps` | "Step 1: Analysis", "Step 2: Design" |
| `milestone\s*\d` | `milestones` | "Milestone 1", "Milestone 2" |
| `q[1-4]|quarter\s*\d` | `quarterly` | "Q1 Results", "Q2 Results" |
| `project\s*\d` | `projects` | "Project Alpha", "Project Beta" |
| `option\s*[a-z\d]` | `options` | "Option A", "Option B", "Option C" |
| `idea\s*\d` | `ideas` | "Idea 1: Expand", "Idea 2: Optimize" |

### 5.3 Grouping Algorithm

```python
def detect_semantic_group(slide_title: str, purpose: str) -> Optional[str]:
    """
    Detect if slide belongs to a semantic group.
    Returns group name or None.
    """
    title_lower = slide_title.lower()

    patterns = [
        (r"use\s*case\s*\d", "use_cases"),
        (r"case\s*study", "case_studies"),
        (r"phase\s*\d", "phases"),
        (r"step\s*\d", "steps"),
        # ... more patterns
    ]

    for pattern, group_name in patterns:
        if re.search(pattern, title_lower):
            return group_name

    return None

def get_group_layout(group_name: str, slides_so_far: List[SlideHistory]) -> Optional[str]:
    """
    If other slides in this group exist, return their layout.
    Otherwise return None (first slide in group picks layout).
    """
    for slide in slides_so_far:
        if slide.semantic_group == group_name:
            return slide.layout_id
    return None
```

### 5.4 Grouping Behavior

| Scenario | Behavior |
|----------|----------|
| First slide in group | Normal recommendation (becomes group template) |
| Subsequent slides in group | Use same layout as first slide |
| Not in any group | Normal recommendation with variety |

---

## 6. Weighting & Scoring

### 6.1 Content-Based Scoring (Text Service)

```python
def score_for_layout_family(slide_content, content_hints, purpose):
    scores = {"H": 0.0, "C": 0.0, "I": 0.0}

    # H-series scoring (hero slides)
    if purpose in ["title_slide", "opening", "closing", "section_divider"]:
        scores["H"] = 0.95
    elif content_hints.topic_count == 0:
        scores["H"] = 0.80

    # I-series scoring (image + text)
    if content_hints.needs_image:
        scores["I"] += 0.40
    if purpose in ["showcase", "demonstrate", "visual", "product"]:
        scores["I"] += 0.25
    if 2 <= content_hints.topic_count <= 5:
        scores["I"] += 0.15
    if "visual" in content_hints.detected_keywords:
        scores["I"] += 0.10

    # C-series scoring (content slides)
    if content_hints.is_comparison:
        scores["C"] = 0.85
    elif content_hints.is_sequential:
        scores["C"] = 0.80
    elif content_hints.has_numbers:
        scores["C"] = 0.75
    elif content_hints.topic_count >= 3:
        scores["C"] = 0.65
    else:
        scores["C"] = 0.55  # Base score

    return scores
```

### 6.2 Final Score Calculation

```python
def calculate_final_recommendation(
    text_service_scores: Dict[str, float],
    mix_adjustment: Dict[str, float],
    variety_penalty: Dict[str, float],
    weights: Dict[str, float] = {"content": 0.60, "context": 0.25, "variety": 0.15}
):
    final_scores = {}

    for family in ["H", "C", "I"]:
        content_score = text_service_scores[family] * weights["content"]
        context_score = mix_adjustment[family] * weights["context"]
        variety_score = variety_penalty[family] * weights["variety"]

        final_scores[family] = content_score + context_score + variety_score

    # Return sorted by score
    return sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
```

### 6.3 Variety Penalty

```python
def calculate_variety_penalty(slides_so_far: List[SlideHistory]) -> Dict[str, float]:
    """
    Penalize families that have been used consecutively.
    """
    penalties = {"H": 0.0, "C": 0.0, "I": 0.0}

    if not slides_so_far:
        return penalties

    # Count consecutive same-family slides
    consecutive = 1
    last_family = slides_so_far[-1].layout_family

    for slide in reversed(slides_so_far[:-1]):
        if slide.layout_family == last_family:
            consecutive += 1
        else:
            break

    # Apply penalty: 3+ consecutive = -0.15, 4+ = -0.25
    if consecutive >= 4:
        penalties[last_family] = -0.25
    elif consecutive >= 3:
        penalties[last_family] = -0.15
    elif consecutive >= 2:
        penalties[last_family] = -0.05

    return penalties
```

---

## 7. API Contract

### 7.1 New Endpoint: POST /v1.2/recommend-layout

#### Request Schema

```json
{
  "slide_content": {
    "title": "Our Key Features",
    "topics": ["Fast performance", "Easy to use", "Secure", "Scalable"],
    "topic_count": 4
  },
  "content_hints": {
    "has_numbers": false,
    "is_comparison": false,
    "is_time_based": false,
    "is_sequential": false,
    "pattern_type": "narrative",
    "topic_count": 4,
    "needs_image": true,
    "detected_keywords": ["features", "benefits"]
  },
  "audience_type": "professional",
  "purpose": "showcase",
  "presentation_context": {
    "total_slides": 12,
    "current_slide_number": 5,
    "slides_so_far": [
      {
        "slide_number": 1,
        "layout_family": "H",
        "layout_id": "H1",
        "variant_id": null,
        "semantic_group": null
      },
      {
        "slide_number": 2,
        "layout_family": "C",
        "layout_id": "C1",
        "variant_id": "grid_2x2_centered",
        "semantic_group": null
      },
      {
        "slide_number": 3,
        "layout_family": "C",
        "layout_id": "C1",
        "variant_id": "comparison_2col",
        "semantic_group": null
      },
      {
        "slide_number": 4,
        "layout_family": "C",
        "layout_id": "C1",
        "variant_id": "metrics_3col",
        "semantic_group": null
      }
    ],
    "semantic_group": null
  },
  "custom_mix_targets": null
}
```

#### Response Schema

```json
{
  "recommended_family": {
    "layout_family": "I",
    "layout_id": "I1",
    "variant_id": null,
    "confidence": 0.82,
    "reason": "Visual content with 4 feature points benefits from image+text layout. Mix adjustment: 3 consecutive C1 slides, I-series recommended to balance.",
    "content_signals": ["visual_keywords", "feature_list", "moderate_topic_count"]
  },
  "alternatives": [
    {
      "layout_family": "C",
      "layout_id": "C1",
      "variant_id": "grid_2x2_centered",
      "confidence": 0.68,
      "reason": "4 topics fit well in 2x2 grid layout",
      "content_signals": ["structured_content", "even_topic_count"]
    },
    {
      "layout_family": "I",
      "layout_id": "I3",
      "variant_id": null,
      "confidence": 0.65,
      "reason": "Narrow image, more content space for 4 topics",
      "content_signals": ["visual_keywords", "text_heavy"]
    }
  ],
  "mix_analysis": {
    "current_mix": {
      "H": 25.0,
      "C": 75.0,
      "I": 0.0
    },
    "target_mix": {
      "H": 10,
      "C": 70,
      "I": 20
    },
    "deviation": {
      "H": 15.0,
      "C": 5.0,
      "I": -20.0
    },
    "adjustment_suggestion": "Add I-series slides to reach 20% target"
  },
  "variety_signals": {
    "consecutive_same_family": 3,
    "consecutive_same_layout": 0,
    "in_semantic_group": false,
    "group_layout": null,
    "variety_concern": "3 consecutive C1 slides - consider I-series for visual variety"
  }
}
```

### 7.2 Existing Endpoint (Unchanged)

`POST /v1.2/recommend-variant` remains available for backward compatibility.

---

## 8. Integration Flow

### 8.1 Strawman Enhancement (New Flow)

```
┌─────────────────────────────────────────────────────────────────┐
│                   STRAWMAN ENHANCEMENT FLOW                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. STORYLINE GENERATION (unchanged)                            │
│     AI generates slides with slide_type_hint, purpose, topics   │
│                                                                  │
│  2. FOR EACH SLIDE:                                             │
│     ┌───────────────────────────────────────────────────────┐   │
│     │ a. Director extracts content_hints (ContentAnalyzer)  │   │
│     │ b. Director extracts audience_type from ContentContext│   │
│     │ c. Director builds presentation_context (slides so far)│  │
│     │ d. Director detects semantic_group (smart grouping)   │   │
│     └───────────────────────────────────────────────────────┘   │
│                            │                                     │
│                            ▼                                     │
│     ┌───────────────────────────────────────────────────────┐   │
│     │ e. Call Text Service: POST /v1.2/recommend-layout     │   │
│     │    - slide_content                                    │   │
│     │    - content_hints                                    │   │
│     │    - audience_type                                    │   │
│     │    - purpose                                          │   │
│     │    - presentation_context                             │   │
│     └───────────────────────────────────────────────────────┘   │
│                            │                                     │
│                            ▼                                     │
│     ┌───────────────────────────────────────────────────────┐   │
│     │ f. Director applies weighting:                        │   │
│     │    - 60% Text Service content signals                 │   │
│     │    - 25% Director context (audience, mix targets)     │   │
│     │    - 15% Director variety enforcement                 │   │
│     └───────────────────────────────────────────────────────┘   │
│                            │                                     │
│                            ▼                                     │
│     ┌───────────────────────────────────────────────────────┐   │
│     │ g. Final decision: layout_family + layout_id + variant│   │
│     │ h. Update presentation_context for next slide         │   │
│     └───────────────────────────────────────────────────────┘   │
│                                                                  │
│  3. RESULT: Enhanced strawman with holistic layout assignments   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Feature Flag

Introduce feature flag for gradual rollout:

```python
USE_HOLISTIC_RECOMMENDATIONS = os.getenv("USE_HOLISTIC_RECOMMENDATIONS", "false") == "true"

if USE_HOLISTIC_RECOMMENDATIONS:
    result = await text_service.recommend_layout(...)
else:
    result = await text_service.recommend_variant(...)  # Legacy
```

---

## 9. Migration Path

### 9.1 Phases

| Phase | Duration | Scope |
|-------|----------|-------|
| **Phase 1** | Week 1-2 | Text Service: Add new endpoint, models |
| **Phase 2** | Week 3-4 | Director: Integrate new endpoint with feature flag |
| **Phase 3** | Week 5-6 | Testing, tuning weights, gathering feedback |
| **Phase 4** | Week 7+ | Gradual rollout (10% → 50% → 100%) |

### 9.2 Backward Compatibility

1. **New endpoint is additive** - `/recommend-variant` unchanged
2. **Feature flag** - Easy rollback if issues
3. **Fallback** - If new endpoint fails, fall back to legacy
4. **6-month deprecation** - Legacy endpoint available for 6 months

### 9.3 Rollback Plan

```python
# If issues detected:
# 1. Set USE_HOLISTIC_RECOMMENDATIONS=false
# 2. All traffic goes to legacy endpoint
# 3. Investigate and fix issues
# 4. Re-enable with fixes
```

---

## 10. Open Questions for Director Team

### 10.1 Weighting Calibration

> **Question**: Are the proposed weights (60% content, 25% context, 15% variety) appropriate?

Current thinking:
- Content signals should dominate (matching content to layout is primary)
- Context provides adjustment (audience preferences)
- Variety prevents monotony but shouldn't override content fit

### 10.2 Audience Mapping

> **Question**: How does Director map user input to audience_type?

Need confirmation on:
- How is audience extracted from `ContentContext`?
- What's the default if audience is unknown?
- Should we add new audience presets?

### 10.3 Smart Grouping Patterns

> **Question**: Are there additional patterns we should detect for smart grouping?

Current patterns:
- Use Cases, Case Studies, Phases, Steps, Milestones, Quarterly

Potential additions:
- Product features ("Feature 1", "Feature 2")
- Agenda items ("Agenda Item 1")
- Competitors ("Competitor A", "Competitor B")

### 10.4 Hero Slide Handling

> **Question**: Should Text Service recommend H-series, or should Director always handle hero slides directly?

Options:
1. **Text Service includes H-series** - Holistic recommendation
2. **Director handles H-series** - Text Service only for text slides
3. **Hybrid** - Text Service recommends but Director can override

### 10.5 Strawman Position

> **Question**: Where exactly in the strawman flow should this integration happen?

Options:
1. During `enhance_strawman_with_layouts()` - After storyline, before content gen
2. During content generation - Real-time as each slide is processed
3. Separate pass - After strawman generation but before user sees it

### 10.6 Mix Target Override

> **Question**: Should users be able to specify their preferred mix in the UI?

Options:
1. Hidden (system decides based on audience)
2. Advanced option (power users only)
3. Simple slider ("More visual" ← → "More text")

---

## Appendix A: Layout Family Reference

### H-Series (Hero Slides)

| Layout ID | Description | When to Use |
|-----------|-------------|-------------|
| H1-generated | Title with AI image | Opening slide with visual impact |
| H1-structured | Title with gradient | Opening slide, no image needed |
| H2-section | Section divider | Between major sections |
| H3-closing | Closing slide | End of presentation with CTA |

### C-Series (Content Slides)

| Layout ID | Variants | When to Use |
|-----------|----------|-------------|
| C1-text | 34 variants | Structured content: grids, comparisons, tables, metrics |

**C1 Variant Categories**:
- Matrix (2): 2x2, 2x3
- Grid (9): Various arrangements with icons/numbers
- Comparison (3): 2-4 column comparisons
- Sequential (3): 3-5 step processes
- Asymmetric (3): Main content + sidebar
- Hybrid (2): Grid + text combinations
- Metrics (4): KPI displays
- Impact Quote (1): Large quotes
- Table (4): 2-5 column tables
- Single Column (3): 3-5 sections

### I-Series (Image + Text)

| Layout ID | Image Position | Best For |
|-----------|---------------|----------|
| I1 | Wide left (660px) | 3-5 topics, balanced |
| I2 | Wide right (660px) | 3-5 topics, image emphasis |
| I3 | Narrow left (360px) | 4-6 topics, text-heavy |
| I4 | Narrow right (360px) | 4-6 topics, text-heavy |

---

## Appendix B: Example Scenarios

### Scenario 1: Kids Presentation (10 slides)

**Input**: Audience = "kids_young", Topic = "Solar System"

**Expected Mix Target**: H=10%, C=25%, I=65%

**Recommended Distribution**:
- H1 (1 slide) - Title
- I-series (6-7 slides) - Visual content about planets
- C1 (2-3 slides) - Structured facts
- H3 (1 slide) - Closing

### Scenario 2: Professional QBR (15 slides)

**Input**: Audience = "executive", Purpose = "QBR"

**Expected Mix Target**: H=15%, C=60%, I=25%

**Recommended Distribution**:
- H1 (1 slide) - Title
- H2 (2 slides) - Section dividers
- C1/metrics (6 slides) - KPIs, data
- C1/comparison (3 slides) - Comparisons, tables
- I-series (2-3 slides) - Product visuals
- H3 (1 slide) - Closing

### Scenario 3: Smart Grouping Example

**Slides in presentation**:
1. "Introduction" → Normal (H1)
2. "Market Overview" → Normal (C1)
3. **"Use Case 1: Healthcare"** → First in group, gets `grid_2x3`
4. **"Use Case 2: Finance"** → Same group, uses `grid_2x3`
5. **"Use Case 3: Retail"** → Same group, uses `grid_2x3`
6. "Implementation Plan" → Normal (C1/sequential)
7. "Closing" → Normal (H3)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | Dec 2024 | Text Service Team | Initial draft for Director team review |

---

## 11. Director Team Response

**Response Date**: December 2024
**Responding Team**: Director Agent v4.5.7

### 11.1 Response to Open Questions

#### 10.1 Weighting Calibration

**Director Response**: The proposed weights (60% content, 25% context, 15% variety) are reasonable and acceptable.

Content fit should dominate - this is the right approach. One enhancement we suggest:
- Make variety weight adjustable based on presentation length
- Short presentations (< 8 slides): 10% variety, 65% content, 25% context
- Medium presentations (8-15 slides): 15% variety (default)
- Long presentations (> 15 slides): 20% variety to prevent monotony

#### 10.2 Audience Mapping

**Director Response**: Audience mapping is already implemented in Director.

Currently extracted via `ExtractedContext.audience_preset` field (see `src/models/decision.py:59-62`).

Available presets:
- `kids_young` (ages 5-8)
- `kids_older` (ages 9-12)
- `middle_school` (ages 12-14)
- `high_school` (ages 14-18)
- `college` (university)
- `professional` (business default)
- `executive` (C-suite, board)
- `general` (mixed/unknown - **default**)

**Suggested Addition**: `technical` preset (engineers, developers) that favors:
- More diagram slides (architecture, flow)
- Code-related content layouts
- Less imagery, more structured data

#### 10.3 Smart Grouping Patterns

**Director Response**: Current patterns are comprehensive. Additional patterns to detect:

| Pattern | Group Name | Example Titles |
|---------|-----------|----------------|
| `feature\s*\d` | `features` | "Feature 1", "Feature 2" |
| `capability\s*\d` | `capabilities` | "Capability A", "Capability B" |
| `team\s*member` | `team` | "Team Member: Alice", "Team Member: Bob" |
| `role\s*\d` | `roles` | "Role 1: Developer", "Role 2: Designer" |
| `region\s*\d` | `regions` | "Region 1: North America", "Region 2: EMEA" |
| `market\s*[a-z]` | `markets` | "Market A", "Market B" |
| `benefit\s*\d` | `benefits` | "Benefit 1", "Benefit 2" |
| `advantage\s*\d` | `advantages` | "Advantage 1", "Advantage 2" |
| `tier\s*\d` | `tiers` | "Tier 1: Enterprise", "Tier 2: Business" |
| `plan\s*\d` | `plans` | "Plan 1", "Plan 2" |

Director will implement `semantic_group` detection in `StrawmanSlide` model (already added in v4.5.3).

#### 10.4 Hero Slide Handling

**Director Response**: **Option 3 (Hybrid)** preferred.

Implementation:
1. Text Service can recommend H-series for completeness in the response
2. Director makes the final call based on `hero_type` mapping:
   - `title_slide` → H1-structured
   - `section_divider` → H2-section
   - `closing_slide` → H3-closing
3. Director already has hero detection logic via `StrawmanSlide.is_hero` and `StrawmanSlide.hero_type`
4. Text Service recommendations serve as input but Director owns the decision

This hybrid approach leverages Text Service's content analysis while preserving Director's architectural control over hero slides.

#### 10.5 Strawman Position

**Director Response**: **Option 1** - During `enhance_strawman_with_layouts()`.

This is the natural integration point. Current flow:
```
StrawmanGenerator → ContentAnalyzer → LayoutAnalyzer → StrawmanTransformer
```

New flow with `/recommend-layout`:
```
StrawmanGenerator
    → ContentAnalyzer (extract content_hints)
    → Text Service POST /v1.2/recommend-layout (get recommendations)
    → Director weighting (60/25/15)
    → LayoutAnalyzer (final assignment)
    → StrawmanTransformer (preview generation)
```

Key integration point: `src/agents/decision_engine.py:_enhance_strawman_with_layouts()`

#### 10.6 Mix Target Override

**Director Response**: **Option 3 (Simple slider)** for MVP.

UI Implementation:
- Add "Visual Balance" slider: "More Text" ←→ "More Visual"
- Slider values map to preset modifiers:
  - Position 0-2: Boosts C-series by 15-20%, reduces I-series
  - Position 3-4: Balanced (uses audience defaults)
  - Position 5-7: Boosts I-series by 15-20%, reduces C-series

Backend: Accept `visual_balance: int` (0-7) in ContentContext, map to `custom_mix_targets`.

### 11.2 I-Series Integration Strategy

#### Current State (v4.5.6)

| Component | Status | Notes |
|-----------|--------|-------|
| ContentAnalyzer | Working | `_detect_image_need()` returns `True` when visual content detected |
| ContentAnalyzer | Working | `_suggest_iseries_layout()` returns I1, I2, I3, or I4 |
| LayoutAnalyzer | **Not Using** | Ignores `needs_image` and `suggested_iseries` signals |
| Config Flag | Disabled | `USE_ISERIES_GENERATION = False` |

#### Root Cause Analysis

ContentAnalyzer correctly populates `needs_image` and `suggested_iseries` on slides, but LayoutAnalyzer has no code path that uses these values. Text slides always get C1/L25, never I-series, regardless of content analysis.

#### Proposed Integration (v4.6)

**Phase 1: Enable Infrastructure** (Director v4.6.0)
1. Set `USE_ISERIES_GENERATION = True` in config
2. Update LayoutAnalyzer to check ContentAnalyzer results
3. Add I-series to `LAYOUT_PREFERENCES[C_AND_H]` for appropriate slide types

```python
# In layout_analyzer.py
def _analyze_text(self, topic_count: int, purpose: str, needs_image: bool = False, suggested_iseries: str = None):
    if needs_image and suggested_iseries and self.series_mode != LayoutSeriesMode.L_ONLY:
        return LayoutAnalysisResult(
            layout=suggested_iseries,  # I1, I2, I3, or I4
            service="text",
            variant_id=None,
            needs_variant_lookup=True,
            generation_instructions=None
        )
    # ... existing text slide logic
```

**Phase 2: Integrate with Text Service** (Director v4.6.0 + Text Service v1.3)
1. Director calls `POST /v1.2/recommend-layout` with `content_hints.needs_image`
2. Text Service returns I-series recommendations when appropriate
3. Director applies audience mix targets to final decision
4. Enable bidirectional coordination protocol

**Phase 3: Smart Grouping for I-series** (Director v4.7.0)
1. If slide is in semantic group and first slide used I-series, subsequent slides use same I-series
2. Selection heuristics:
   - I1 (wide left): Conceptual content, product showcases
   - I2 (wide right): Data-heavy visuals, comparisons
   - I3 (narrow left): Text-heavy with accent image
   - I4 (narrow right): Text-heavy with supporting visual

#### Acceptance Criteria

| Audience | I-Series Target | Notes |
|----------|-----------------|-------|
| Kids (young) | 60-70% | Maximum visual engagement |
| Kids (older) | 50-60% | Balanced imagery |
| Professional | 15-25% | Visual variety without overdoing |
| Executive | 20-30% | Impact visuals for key messages |
| Technical | 10-20% | Prefer diagrams over images |

#### I-Series Variety Rules
- Consecutive I-series slides should alternate: I1 → I3 → I1 (or I2 → I4 → I2)
- Maximum 3 consecutive I-series before forcing a C1
- Minimum 2 I-series per 10-slide presentation for visual variety

### 11.3 Implementation Timeline

| Phase | Version | Task | Owner | Status |
|-------|---------|------|-------|--------|
| 1 | v4.5.7 | Fix subtitle/logo fields in strawman preview | Director | Done |
| 1 | v4.5.7 | Switch LAYOUT_SERIES_MODE to C_AND_H | Director | Done |
| 1 | v4.5.7 | Add Director Response to this document | Director | Done |
| 2 | v4.6.0 | Enable I-series infrastructure | Director | Next sprint |
| 2 | v4.6.0 | Integrate /recommend-layout endpoint | Both teams | Next sprint |
| 2 | v1.3.0 | Build /recommend-layout endpoint | Text Service | Pending |
| 3 | v4.7.0 | UI slider for visual balance | Frontend | TBD |
| 3 | v4.7.0 | Smart grouping enforcement | Director | TBD |

### 11.4 API Integration Notes for Text Service Team

When implementing `POST /v1.2/recommend-layout`, please include:

1. **I-series fields in response**:
```json
{
  "recommended_family": {
    "layout_family": "I",
    "layout_id": "I1",
    "image_position": "left",
    "image_width": "wide",
    "variant_id": null,
    "confidence": 0.78,
    "reason": "Visual content with 3 feature points, image enhances message"
  }
}
```

2. **I-series content_signals**:
- `visual_keywords_detected` - Topics contain visual terms
- `product_showcase` - Content describes product/service
- `conceptual_explanation` - Abstract concept that benefits from imagery
- `data_with_context` - Numbers/metrics that need visual grounding

3. **Image hint in response** (for Illustrator Service):
```json
{
  "recommended_family": {...},
  "image_hint": {
    "suggested_subject": "professional team collaboration",
    "suggested_style": "abstract_shapes",
    "aspect_ratio": "9:16"
  }
}
```

---

**Next Steps**:
1. ~~Director Team reviews this document~~ ✅ Done
2. ~~Clarify open questions~~ ✅ Responses provided above
3. Finalize API contract (Text Service v1.3 sprint)
4. Begin implementation (Director v4.6.0 sprint)
