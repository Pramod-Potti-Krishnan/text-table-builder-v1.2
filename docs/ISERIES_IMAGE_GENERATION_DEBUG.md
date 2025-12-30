# I-Series Image Generation Debug Guide

This document explains the I-series image generation process, how prompts are built, and potential issues (rate limits, poor image quality). Use this to debug image generation issues and test prompts in GCP Vertex AI Studio.

---

## 1. Overview: 2-Step "Intentional Spotlight" Approach (v1.5.0)

The I-series image generation uses a 2-step approach to create focused, intentional images:

1. **Step 1: Extract Visual Concept (WHAT to show)**
   - Analyzes narrative complexity
   - Either uses LLM-based or rule-based extraction
   - Outputs: `primary_subject`, `visual_elements`, `composition_hint`, `emotional_focus`, `abstraction_level`

2. **Step 2: Build Image Prompt (HOW to show it)**
   - Takes the extracted concept
   - Applies context-aware style parameters (audience, purpose, domain)
   - Generates the final prompt for Imagen

**Key Files:**
| File | Purpose |
|------|---------|
| `app/core/iseries/base_iseries_generator.py` | Main orchestrator, `_build_image_prompt_2step()` |
| `app/core/iseries/spotlight_concept_extractor.py` | Step 1: Concept extraction |
| `app/core/iseries/context_style_mapper.py` | Domain detection, style params, spotlight depth |
| `app/core/hero/style_config.py` | Visual style archetypes |
| `app/services/image_service_client.py` | API calls to Image Builder |

---

## 2. Architecture Flow Diagram

```
Request (ISeriesGenerationRequest)
    │
    ├── Extract content_context (audience, purpose)
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: SPOTLIGHT CONCEPT EXTRACTION                        │
├─────────────────────────────────────────────────────────────┤
│  1. Detect domain from narrative + topics                    │
│  2. Get spotlight_depth from audience × purpose matrix       │
│  3. Analyze complexity (0.0 - 1.0 score)                    │
│                                                              │
│  IF score >= 0.35 (complex):                                │
│      → LLM-based extraction (~2-3s, uses LLM call)          │
│  ELSE (simple):                                              │
│      → Rule-based extraction (instant, no LLM call)          │
│                                                              │
│  OUTPUT: SpotlightConcept                                    │
│    - primary_subject: "interconnected circuit board..."      │
│    - visual_elements: ["glowing connections", ...]           │
│    - composition_hint: "centered"                            │
│    - emotional_focus: "professional"                         │
│    - abstraction_level: "abstract"                           │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: PROMPT BUILDING                                     │
├─────────────────────────────────────────────────────────────┤
│  1. Get context_style, context_lighting, context_color       │
│  2. Map abstraction_level to guidance text                   │
│  3. Build prompt template with spotlight focus               │
│  4. Determine archetype (photorealistic, spot_illustration)  │
│  5. Build negative prompt (domain + audience aware)          │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  IMAGE SERVICE API CALL                                      │
├─────────────────────────────────────────────────────────────┤
│  POST /api/v2/generate                                       │
│  - prompt: (built above)                                     │
│  - aspect_ratio: I1=11:18, I2=2:3, I3=1:3, I4=7:18          │
│  - model: imagen-3.0-generate-001 or fast-generate-001       │
│  - archetype: photorealistic | spot_illustration | minimal   │
│  - negative_prompt: (domain + audience aware)                │
│                                                              │
│  Retry: 2 attempts with exponential backoff (2s, 4s)         │
│  Timeout: 20 seconds                                         │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
GCP Vertex AI (Imagen) → Generated Image URL
```

---

## 3. Complexity Analysis (Triggers LLM vs Rules)

The complexity score determines whether to use LLM-based extraction (expensive) or rule-based extraction (free).

**Threshold: 0.35** (score >= 0.35 → LLM extraction)

### Complexity Indicators and Weights

| Category | Weight | Example Terms |
|----------|--------|---------------|
| `abstract_terms` | 0.30 | transformation, journey, evolution, paradigm, synergy, catalyst, ecosystem, framework, architecture, blueprint, roadmap |
| `comparison_terms` | 0.20 | versus, compared to, unlike, whereas, on the other hand, in contrast, alternatively |
| `emotional_terms` | 0.20 | revolutionize, transform, empower, unleash, ignite, breakthrough, game-changing, visionary, pioneering |
| `technical_density` | 0.15 | algorithm, infrastructure, architecture, protocol, framework, integration, microservices, orchestration |
| `structural_markers` | 0.15 | furthermore, moreover, consequently, therefore, hence, as a result, in order to |

### Additional Heuristics

| Condition | Score Addition |
|-----------|----------------|
| Average sentence length > 20 words | +0.10 |
| 4+ topics | +0.10 |
| 3+ sentences | +0.05 |

### Example Calculations

**Simple Narrative (Rule-based):**
```
Narrative: "Our three-phase approach delivers results"
Topics: ["Plan", "Execute", "Review"]

- No abstract_terms found: +0.00
- No comparison_terms found: +0.00
- No emotional_terms found: +0.00
- No technical_density found: +0.00
- No structural_markers found: +0.00
- Avg sentence length < 20: +0.00
- 3 topics (< 4): +0.00
- 1 sentence (< 3): +0.00

TOTAL: 0.00 → RULE-BASED (instant, free)
```

**Complex Narrative (LLM-based):**
```
Narrative: "Our platform revolutionizes digital transformation by leveraging
cutting-edge machine learning infrastructure. Furthermore, this paradigm
shift empowers organizations to unlock unprecedented synergies."
Topics: ["Speed", "Reliability", "Cost", "Innovation"]

- abstract_terms: "transformation", "paradigm", "synergy" → 3 matches → 0.30
- emotional_terms: "revolutionize", "empower" → 2 matches → 0.13
- technical_density: "machine learning", "infrastructure" → 2 matches → 0.10
- structural_markers: "furthermore" → 1 match → 0.05
- Avg sentence length > 20: +0.10
- 4 topics: +0.10
- 2 sentences: +0.00

TOTAL: 0.78 → LLM-BASED (2-3s, uses LLM call)
```

---

## 4. Domain Detection

Domain is detected from narrative + topics text using keyword matching.

### 7 Domains and Keywords

| Domain | Keywords |
|--------|----------|
| **technology** | tech, software, digital, ai, data, cloud, code, algorithm, computing, system, cyber, machine learning, automation, programming, developer, api, platform, infrastructure, stack, database, server, network |
| **business** | finance, business, market, trading, investment, bank, revenue, profit, economy, financial, stock, portfolio, capital, corporate, enterprise, strategy, growth, expansion, customer, sales |
| **healthcare** | health, medical, hospital, patient, diagnostic, clinical, doctor, nurse, healthcare, medicine, therapy, treatment, wellness, pharmaceutical |
| **education** | school, university, student, learning, education, teach, academic, classroom, course, curriculum, professor, degree, graduate, college, training |
| **science** | research, experiment, laboratory, chemistry, physics, biology, scientific, discovery, hypothesis, analysis, study, findings, methodology, empirical, scientist |
| **nature** | nature, environment, climate, green, sustainable, wildlife, forest, ocean, conservation, ecosystem, biodiversity, ecological, renewable, earth, planet |
| **creative** | art, design, creative, music, artist, gallery, paint, sculpture, photography, illustration, visual, aesthetic, artistic, exhibition, performance, culture |

---

## 5. Spotlight Depth Matrix

Maps (audience_type, purpose_type) to visual complexity level.

### Spotlight Depth Levels

| Level | Visual Elements | Use Case |
|-------|----------------|----------|
| **MINIMAL** | Single clean element, no metaphor | Executives, technical audiences |
| **FOCUSED** | Primary element + 1 supporting | Professional presentations |
| **RICH** | Full concept with metaphor and mood | Educational, inspiring content |
| **LAYERED** | Complex multi-element composition | Creative, storytelling |

### Matrix (Audience × Purpose)

| Audience | inform | persuade | inspire | educate | entertain |
|----------|--------|----------|---------|---------|-----------|
| executives | MINIMAL | FOCUSED | FOCUSED | MINIMAL | FOCUSED |
| professional | MINIMAL | FOCUSED | FOCUSED | FOCUSED | RICH |
| technical | MINIMAL | MINIMAL | FOCUSED | FOCUSED | FOCUSED |
| developers | MINIMAL | MINIMAL | FOCUSED | FOCUSED | FOCUSED |
| general | FOCUSED | RICH | RICH | RICH | LAYERED |
| students | FOCUSED | RICH | LAYERED | RICH | LAYERED |
| kids_tween | RICH | RICH | LAYERED | LAYERED | LAYERED |
| kids_teen | FOCUSED | RICH | LAYERED | RICH | LAYERED |

---

## 6. Prompt Building (Key Section for Vertex AI Testing)

### 6.1 Rule-Based Primary Subjects by Domain

When using rule-based extraction, these are the primary subjects used:

**Technology:**
```
- interconnected circuit board patterns with glowing pathways
- abstract data stream visualization with flowing particles
- network node constellation with luminous connections
- digital mesh gradient with geometric tech patterns
```

**Business:**
```
- modern cityscape silhouette with rising towers
- ascending growth chart with dynamic upward motion
- interconnected building blocks in structured formation
- professional workspace vista with clean lines
```

**Healthcare:**
```
- modern medical technology abstract with clean aesthetics
- wellness symbol composition with life-affirming imagery
- health monitoring interface with vital signs visualization
- clinical environment vista with pristine surfaces
```

**Education:**
```
- knowledge pathway visualization with enlightenment symbolism
- learning journey landscape with growth elements
- academic achievement symbolism with aspiration
- enlightenment imagery with illumination
```

**Science:**
```
- laboratory equipment abstract with precision focus
- molecular structure visualization with atomic detail
- research discovery moment with eureka symbolism
- scientific process imagery with methodical flow
```

### 6.2 Final Prompt Template (2-Step)

This is the actual prompt template used by `_build_image_prompt_2step()`:

```
High-quality {context_style} portrait image for presentation slide.

VISUAL FOCUS (Intentional Spotlight):
- Primary Subject: {concept.primary_subject}
- Supporting Elements: {visual_elements_str}
- Composition: {concept.composition_hint}, vertical portrait orientation

STYLE:
- Visual approach: {abstraction_guidance}
- Lighting: {context_lighting}
- Color scheme: {context_color}
- Mood: {concept.emotional_focus}
- Aspect ratio: Tall portrait (9:16)

CRITICAL REQUIREMENTS:
- Absolutely NO text, words, letters, numbers, or typography
- NO human faces, people, or characters
- Clean, professional appearance
- Subject should be clearly prominent and intentionally spotlighted
- Background should complement but not compete with main subject
```

### 6.3 Abstraction Guidance Mapping

| Abstraction Level | Guidance Text |
|-------------------|---------------|
| `literal` | Direct, realistic representation |
| `metaphorical` | Visual metaphor, symbolic representation |
| `abstract` | Abstract, geometric, conceptual imagery |

### 6.4 LLM Concept Extraction Prompt

When complexity >= 0.35, this prompt is sent to the LLM:

```
Extract the core visual concept for an image that represents this slide content.

NARRATIVE:
{narrative}

TOPICS:
{topics}

DOMAIN: {domain}
AUDIENCE: {audience_type}
PURPOSE: {purpose_type}
SPOTLIGHT DEPTH: {spotlight_depth}

Based on the narrative, identify:
1. PRIMARY SUBJECT: The single most important visual element that captures the main message
2. VISUAL ELEMENTS: 1-3 supporting visual elements (based on spotlight depth)
3. COMPOSITION: How elements should be arranged (centered, environmental, left-weighted, right-weighted)
4. EMOTIONAL FOCUS: The feeling the image should evoke (professional, inspiring, energetic, calm, serious, encouraging, uplifting)
5. ABSTRACTION LEVEL: How literal vs abstract (literal, metaphorical, abstract)

SPOTLIGHT DEPTH GUIDANCE:
- minimal: Single clean element, no metaphor, executives/technical audiences
- focused: Primary element + 1 supporting, professional presentations
- rich: Full concept with metaphor and mood, educational/inspiring content
- layered: Complex multi-element composition, creative/storytelling

CRITICAL REQUIREMENTS:
- Focus on WHAT to show, not HOW to show it
- Choose imagery that represents the core message, not just the topic
- For abstract concepts, use visual metaphors
- NEVER include text, words, letters, numbers in the concept
- NEVER include human faces, people, or characters in the concept
- Focus purely on objects, environments, patterns, and abstract visuals

Return ONLY valid JSON (no markdown, no explanation):
{
    "primary_subject": "main visual element description (50-150 chars)",
    "visual_elements": ["element1", "element2"],
    "composition_hint": "centered|environmental|left-weighted|right-weighted",
    "emotional_focus": "professional|inspiring|energetic|calm|serious|encouraging|uplifting",
    "abstraction_level": "literal|metaphorical|abstract",
    "spotlight_rationale": "brief explanation (under 100 chars)"
}
```

### 6.5 Sample Prompts by Audience/Domain

**Example 1: Technology + Executives**
```
High-quality photo portrait image for presentation slide.

VISUAL FOCUS (Intentional Spotlight):
- Primary Subject: interconnected circuit board patterns with glowing pathways
- Supporting Elements: (minimal - executives prefer clean)
- Composition: centered, vertical portrait orientation

STYLE:
- Visual approach: Abstract, geometric, conceptual imagery
- Lighting: professional
- Color scheme: neutral
- Mood: professional
- Aspect ratio: Tall portrait (9:16)

CRITICAL REQUIREMENTS:
- Absolutely NO text, words, letters, numbers, or typography
- NO human faces, people, or characters
- Clean, professional appearance
- Subject should be clearly prominent and intentionally spotlighted
- Background should complement but not compete with main subject
```

**Example 2: Education + Students**
```
High-quality illustration portrait image for presentation slide.

VISUAL FOCUS (Intentional Spotlight):
- Primary Subject: knowledge pathway visualization with enlightenment symbolism
- Supporting Elements: book and document motifs, growth symbolism
- Composition: environmental, vertical portrait orientation

STYLE:
- Visual approach: Visual metaphor, symbolic representation
- Lighting: bright
- Color scheme: vibrant
- Mood: encouraging
- Aspect ratio: Tall portrait (9:16)

CRITICAL REQUIREMENTS:
- Absolutely NO text, words, letters, numbers, or typography
- NO human faces, people, or characters
- Clean, professional appearance
- Subject should be clearly prominent and intentionally spotlighted
- Background should complement but not compete with main subject
```

---

## 7. Negative Prompt Construction

### Base Negatives (Always Applied)

```
text, words, letters, numbers, typography, labels, titles, captions,
watermarks, logos, brands, signatures, writing, symbols,
human faces, people, persons, humans, portraits, bodies, crowds,
anime characters, cartoon people, cartoon characters, illustrated people,
low quality, blurry, pixelated, noisy, distorted, cluttered, busy,
horizontal composition, landscape orientation
```

### Domain-Specific Negatives

| Domain | Additional Negatives |
|--------|---------------------|
| technology | clipart, generic stock photo, smiling businesspeople, office workers, meeting rooms with people, handshakes, outdated technology, old computers |
| business | anime style, cartoon style, childish imagery, casual settings, unprofessional imagery, generic clip art, outdated graphics |
| healthcare | graphic surgery, blood, patients in distress, scary medical imagery, needles close-up, hospital beds with patients |
| education | boring lecture halls, outdated classrooms, generic school clipart, childish cartoons for adult education |
| science | mad scientist tropes, dangerous experiments, unrealistic sci-fi, generic science clipart |
| nature | environmental damage, pollution, deforestation, dying animals, climate disaster imagery |
| creative | corporate sterility, generic stock photos, boring office settings, uncreative imagery |

---

## 8. Model & Archetype Selection

### Imagen Models

| Model | Generation Time | Cost | Use Case |
|-------|-----------------|------|----------|
| `imagen-3.0-fast-generate-001` | ~5s | $0.02 | Illustrations, non-photo styles |
| `imagen-3.0-generate-001` | ~10s | $0.04 | Standard quality, photorealistic |
| `imagen-3.0-generate-002` | ~11s | $0.04 | High quality (rarely used) |

### Model Selection Logic

From `image_service_client.py`:

```python
if archetype == "photorealistic":
    model = "imagen-3.0-generate-001"  # Standard quality for photos
else:
    model = "imagen-3.0-fast-generate-001"  # Fast for illustrations
```

### Archetypes

| Archetype | Style | Audience |
|-----------|-------|----------|
| `photorealistic` | Realistic photography | Executives, professional |
| `spot_illustration` | Illustrated/cartoon style | Kids, illustrated visual_style |
| `minimalist_vector_art` | Minimal, clean | Technical, developers |

### Archetype Selection Logic

From `base_iseries_generator.py`:

```python
archetype = style_config.archetype  # Default from visual_style

# Override based on audience type
if audience_type in ["executives", "professional"]:
    archetype = "photorealistic"
elif audience_type in ["technical", "developers"]:
    archetype = "minimalist_vector_art"
elif context_style == "minimal":
    archetype = "minimalist_vector_art"

# If concept is abstract, prefer minimalist archetype
if concept.abstraction_level == AbstractionLevel.ABSTRACT:
    if archetype not in ["photorealistic", "minimalist_vector_art"]:
        archetype = "minimalist_vector_art"
```

---

## 9. Image Service API Call

### Endpoint

```
POST {IMAGE_SERVICE_URL}/api/v2/generate
```

Default: `https://web-production-1b5df.up.railway.app`

### Request Payload

```json
{
  "prompt": "<final prompt from step 2>",
  "aspect_ratio": "11:18",  // Per-layout: I1=11:18, I2=2:3, I3=1:3, I4=7:18
  "model": "imagen-3.0-generate-001",
  "archetype": "photorealistic",
  "negative_prompt": "<domain + audience aware negatives>",
  "options": {
    "remove_background": false,
    "crop_anchor": "center",
    "store_in_cloud": true,
    "return_base64": false
  },
  "metadata": {
    "layout_type": "I1",
    "visual_style": "professional",
    "aspect_ratio": "11:18",
    "context_style": "photo",
    "context_domain": "technology"
  }
}
```

### Aspect Ratios by Layout

| Layout | Aspect Ratio | Dimensions |
|--------|--------------|------------|
| I1 | 11:18 | 660×1080 |
| I2 | 2:3 | 720×1080 |
| I3 | 1:3 | 360×1080 (very narrow) |
| I4 | 7:18 | 420×1080 (narrow) |

### Retry Logic

```python
max_retries = 2
timeout = 20.0  # seconds

for attempt in range(max_retries + 1):
    try:
        response = await client.post(...)
    except:
        if attempt < max_retries:
            backoff_time = 2.0 * (attempt + 1)  # 2s, 4s
            await asyncio.sleep(backoff_time)
```

---

## 10. Potential Issues & Debugging

### 10.1 Rate Limiting at GCP

**Symptom:** 429 errors, generation timeouts, requests failing after retries

**Cause:** Too many parallel image requests hitting GCP Vertex AI quotas

**Investigation:**
1. Check if multiple slides are generating images simultaneously
2. Look for the 2-step process making double LLM calls (concept extraction + image)
3. Check GCP Vertex AI quotas in console

**Potential Fixes:**
- Add queue-based throttling to limit concurrent image requests
- Increase retry backoff times (currently 2s, 4s)
- Reduce parallelism - serialize image generation across slides
- Use `skip_image_generation=True` for testing content without images

### 10.2 Poor Image Quality / Images Don't Match Narrative

**Symptom:** Generated images are generic, don't represent the content well

**Causes:**
1. Complexity threshold too low (0.35) - using LLM for simple narratives that work fine with rules
2. Overly complex prompts confusing the model
3. Wrong abstraction level for the audience
4. SpotlightConceptExtractor returning generic subjects

**Investigation:**
1. Check the `extraction_method` in metadata: "llm" vs "rules"
2. Check `complexity_score` - is it correctly triggering LLM?
3. Check `primary_subject` in spotlight_concept - is it meaningful?
4. Check `domain` detection - is it correct?

**Potential Fixes:**
- Raise complexity threshold (0.35 → 0.45) to prefer rule-based extraction
- Simplify prompts - less is more with Imagen
- Ensure audience_type is correctly propagating from Director
- Check the domain detection keywords

### 10.3 Multi-Step LLM Overhead

**Symptom:** Rate limits triggered more than before, slower generation

**Cause:** The 2-step process makes 2× LLM calls for complex narratives:
1. LLM call for concept extraction (Step 1)
2. LLM call for content generation (separate process)

Both happen in parallel, but the concept extraction LLM call is NEW in v1.5.0.

**Investigation:**
1. Check logs for "LLM concept extraction" vs "Rule-based extraction"
2. Count LLM calls per slide generation
3. Check complexity scores - are most narratives hitting >= 0.35?

**Potential Fixes:**
- Raise complexity threshold (0.35 → 0.50) to reduce LLM usage
- Force rule-based extraction with `force_rules=True` for testing
- Cache concept extraction results for similar narratives

### 10.4 Wrong Archetype/Style

**Symptom:** Cartoon images for executives, photorealistic for kids

**Cause:** Audience type not propagating correctly, fallback defaults being used

**Investigation:**
1. Check request's `context.content_context.audience.audience_type`
2. Check if style_params is correctly built
3. Verify archetype selection logic

**Potential Fixes:**
- Ensure Director is sending correct audience_type
- Check context flow from request → _build_image_prompt_2step → style_params
- Add logging at archetype selection point

### 10.5 Image Generation Skipped/Fallback Used

**Symptom:** Slides show gradient placeholder instead of image

**Cause:** Image generation failed, `image_fallback=True` in response

**Investigation:**
1. Check logs for "Image generation attempt X failed"
2. Look for specific error messages (timeout, 429, etc.)
3. Check if `skip_image_generation=True` was set

**Potential Fixes:**
- Increase timeout from 20s if images are timing out
- Add more retries (currently 2)
- Check Image Builder service health

---

## 11. Testing Prompts in Vertex AI Studio

### How to Access

1. Go to [GCP Console](https://console.cloud.google.com)
2. Navigate to **Vertex AI** → **Generative AI Studio** → **Image Generation**
3. Select model: `imagen-3.0-fast-generate-001` or `imagen-3.0-generate-001`

### Steps to Test

1. **Copy prompt from logs** or construct manually using templates above
2. **Set aspect ratio**:
   - For I-series: Use 9:16 (portrait) or specific ratio (11:18, 2:3, 1:3, 7:18)
   - Note: Vertex AI Studio may not support all ratios - use 9:16 as fallback
3. **Add negative prompt** in the advanced settings
4. **Generate** and compare results
5. **Iterate** on prompt wording until quality improves

### Test Cases

**Test Case 1: Simple Narrative (Should use rule-based)**
```
Narrative: "Three steps to success"
Topics: ["Plan", "Execute", "Review"]
Expected: Fast generation, domain-appropriate primary subject
```

**Test Case 2: Complex Narrative (Should use LLM extraction)**
```
Narrative: "Our platform revolutionizes digital transformation by leveraging
cutting-edge machine learning infrastructure"
Topics: ["Speed", "Reliability", "Cost", "Innovation"]
Expected: LLM-extracted concept, more specific primary subject
```

**Test Case 3: Executive Audience**
```
audience_type: "executives"
Expected: photorealistic archetype, MINIMAL spotlight depth, neutral colors
```

**Test Case 4: Kids Audience**
```
audience_type: "kids_tween"
Expected: spot_illustration archetype, LAYERED spotlight depth, vibrant colors
```

### Sample Prompt for Direct Testing

Copy this prompt to Vertex AI Studio and modify as needed:

```
High-quality professional photography portrait image for presentation slide.

VISUAL FOCUS (Intentional Spotlight):
- Primary Subject: interconnected circuit board patterns with glowing pathways
- Supporting Elements: subtle data particle flow
- Composition: centered, vertical portrait orientation

STYLE:
- Visual approach: Abstract, geometric, conceptual imagery
- Lighting: professional studio lighting
- Color scheme: neutral blue and gray tones
- Mood: professional, innovative
- Aspect ratio: Tall portrait (9:16)

CRITICAL REQUIREMENTS:
- Absolutely NO text, words, letters, numbers, or typography
- NO human faces, people, or characters
- Clean, professional appearance
- Subject should be clearly prominent and intentionally spotlighted
- Background should complement but not compete with main subject
```

**Negative prompt for testing:**
```
text, words, letters, numbers, typography, watermarks, logos, signatures,
human faces, people, persons, portraits, anime characters, cartoon characters,
low quality, blurry, pixelated, noisy, distorted, cluttered, busy,
horizontal composition, landscape orientation, clipart, generic stock photo,
smiling businesspeople, office workers, handshakes
```

---

## 12. Sample Debug Session

### Scenario: Image not matching "Digital Transformation" narrative

**1. Check the Request**
```python
request = {
    "narrative": "Our platform drives digital transformation across enterprise",
    "topics": ["Cloud", "AI", "Automation"],
    "layout_type": "I1",
    "visual_style": "professional",
    "context": {
        "content_context": {
            "audience": {"audience_type": "executives"},
            "purpose": {"purpose_type": "persuade"}
        }
    }
}
```

**2. Check Complexity Analysis**
```
narrative = "Our platform drives digital transformation across enterprise"
topics = ["Cloud", "AI", "Automation"]

Indicators found:
- abstract_terms: "transformation" → 1 match → 0.10
- emotional_terms: "drives" → 0 matches
- technical_density: "cloud", "ai", "automation" → 3 matches → 0.15

Complexity Score: 0.25 → RULE-BASED (< 0.35 threshold)
```

**3. Check Domain Detection**
```
combined_text = "our platform drives digital transformation across enterprise cloud ai automation"

Keywords matched: "digital", "cloud", "ai", "automation"
Domain: "technology"
```

**4. Check Spotlight Depth**
```
audience_type = "executives"
purpose_type = "persuade"

Matrix lookup: (executives, persuade) → FOCUSED
```

**5. Check Rule-Based Concept**
```python
concept = SpotlightConcept(
    primary_subject="interconnected circuit board patterns with glowing pathways",
    visual_elements=["glowing connection lines"],  # 1 element for FOCUSED
    composition_hint="centered",
    emotional_focus="inspiring",  # From purpose_type "persuade"
    abstraction_level=AbstractionLevel.ABSTRACT,
    spotlight_rationale="Rule-based extraction for technology domain (depth: focused)"
)
```

**6. Check Final Prompt**
```
High-quality photo portrait image for presentation slide.

VISUAL FOCUS (Intentional Spotlight):
- Primary Subject: interconnected circuit board patterns with glowing pathways
- Supporting Elements: glowing connection lines
- Composition: centered, vertical portrait orientation

STYLE:
- Visual approach: Abstract, geometric, conceptual imagery
- Lighting: professional
- Color scheme: neutral
- Mood: inspiring
- Aspect ratio: Tall portrait (9:16)

...
```

**7. Check Archetype Selection**
```python
audience_type = "executives" → archetype = "photorealistic"
model = "imagen-3.0-generate-001"  # Standard quality for photos
```

**8. Diagnosis**

The prompt looks correct, but the image is generic. Possible issues:
- "interconnected circuit board patterns" is too common/generic
- Need more specific primary_subject for "digital transformation"

**9. Solution Options**

Option A: Lower complexity threshold to trigger LLM extraction
```python
complexity_threshold = 0.20  # Instead of 0.35
```

Option B: Add "transformation" to complexity indicators with higher weight

Option C: Improve rule-based subjects for technology domain
```python
"primary_subjects": [
    "digital ecosystem transformation with flowing data streams",  # More specific
    ...
]
```

---

## 13. Quick Reference: Context Fields from Director

When Director calls the Text Service, these context fields control image generation:

```json
{
  "context": {
    "content_context": {
      "audience": {
        "audience_type": "executives|professional|technical|developers|general|students|kids_tween|kids_teen",
        "complexity_level": "low|moderate|high"
      },
      "purpose": {
        "purpose_type": "inform|persuade|inspire|educate|entertain",
        "emotional_tone": "professional|inspiring|energetic|calm|serious|encouraging|uplifting"
      }
    },
    "image_style_agreement": {
      "archetype": "photorealistic|spot_illustration|minimalist_vector_art",
      "mood": "professional|inspiring|...",
      "color_scheme": "neutral|cool|warm|vibrant",
      "lighting": "professional|clean|soft|bright|playful",
      "avoid_elements": ["anime", "cartoon", "playful", "childish"],
      "quality_tier": "smart|fast|high"
    },
    "image_model": "imagen-3.0-generate-001|imagen-3.0-fast-generate-001",
    "styling_mode": "inline_styles"
  }
}
```

---

## Summary

The I-series image generation is a 2-step process:

1. **Concept Extraction**: Analyzes complexity → LLM or rule-based → SpotlightConcept
2. **Prompt Building**: Concept + context → Final prompt + negative prompt

**Key Debugging Points:**
- Check `complexity_score` - is it triggering correct extraction method?
- Check `domain` detection - is it finding the right domain?
- Check `audience_type` propagation - is archetype correct?
- Check `spotlight_depth` - is visual richness appropriate?

**Common Fixes:**
- Raise complexity threshold to reduce LLM calls (rate limits)
- Simplify prompts (better image quality)
- Ensure context flows correctly from Director
- Test prompts directly in Vertex AI Studio
