# Text & Table Builder v1.2 - Architecture Documentation

## Executive Summary

Text Service v1.2 implements a **dual architecture approach** that separates content slide generation (element-based assembly) from hero slide generation (single-call with inline styling). This design optimizes for both determinism and visual impact while maintaining world-class slide quality.

**Key Architectural Decisions:**
- ✅ **Element-based assembly** for complex content slides (L25 layout, 26 variants)
- ✅ **Single-call generation** for simple hero slides (L29 layout, 3 types)
- ✅ **Inline-styled HTML** for hero slides inspired by v1.1 world-class prompts
- ✅ **Template-driven** content assembly for deterministic output
- ✅ **Async/await** throughout for scalability
- ✅ **Model routing** (Flash vs Pro) for cost optimization

---

## Architecture Philosophy

### Design Principles

1. **Right Tool for the Job**: Use element-based assembly for complex content, single-call for simple heroes
2. **Deterministic Quality**: Template assembly ensures consistent HTML structure
3. **Performance First**: Async operations and model routing for speed and cost
4. **Separation of Concerns**: Clear boundaries between generation, validation, and assembly
5. **Maintainability**: JSON specs and HTML templates separate from code logic

### Why Dual Architecture?

| Decision Factor | Content Slides (L25) | Hero Slides (L29) |
|----------------|---------------------|-------------------|
| **Complexity** | High (4-8 distinct elements) | Low (1-3 elements) |
| **Structure** | Variable layouts, many variants | Fixed layouts, 3 types |
| **Optimization Goal** | Precision per element | Visual impact |
| **Best Approach** | Break into elements, assemble | Generate complete HTML |
| **Model Choice** | Flash + Pro routing | Flash only |

**Rationale**: Hero slides have simple structure (title + subtitle + attribution/CTA), making element-based assembly unnecessary overhead. A single rich prompt produces better visual cohesion with gradients and unified styling.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Text Service v1.2 API Layer                  │
├─────────────────────────────────────────────────────────────────┤
│  POST /v1.2/generate        POST /v1.2/hero/title             │
│  POST /v1.2/hero/section    POST /v1.2/hero/closing           │
│  GET  /v1.2/variants        GET  /v1.2/variant/{id}           │
└────────────┬────────────────────────────────┬───────────────────┘
             │                                │
             ▼                                ▼
┌─────────────────────────────┐  ┌──────────────────────────────┐
│  CONTENT SLIDE PIPELINE     │  │  HERO SLIDE PIPELINE         │
│  (Element-Based Assembly)   │  │  (Single-Call Generation)    │
├─────────────────────────────┤  ├──────────────────────────────┤
│  1. Load Variant Spec       │  │  1. Build Rich Prompt        │
│  2. Build Element Prompts   │  │  2. Single LLM Call          │
│  3. Generate Elements       │  │  3. Clean Markdown Wrapper   │
│     (Parallel/Sequential)   │  │  4. Validate Inline Styles   │
│  4. Assemble Template       │  │  5. Return Complete HTML     │
│  5. Validate Structure      │  │                              │
└────────────┬────────────────┘  └──────────────┬───────────────┘
             │                                  │
             └──────────────┬───────────────────┘
                            ▼
                   ┌────────────────────┐
                   │  LLM Service Layer │
                   │  (Vertex AI/Gemini)│
                   ├────────────────────┤
                   │ - Model Routing    │
                   │ - Token Tracking   │
                   │ - Error Handling   │
                   └────────────────────┘
```

---

## Content Slide Architecture (Element-Based)

### Component Flow

```
Director Request
    ↓
┌───────────────────────────────────────┐
│  ElementPromptBuilder                 │
│  - Load variant spec (JSON)           │
│  - Extract element definitions        │
│  - Build targeted prompts             │
└───────────┬───────────────────────────┘
            ↓
┌───────────────────────────────────────┐
│  ContextBuilder                       │
│  - Build slide context                │
│  - Build presentation context         │
│  - Enrich element prompts             │
└───────────┬───────────────────────────┘
            ↓
┌───────────────────────────────────────┐
│  ElementBasedContentGenerator         │
│  - Orchestrate generation             │
│  - Execute parallel/sequential        │
│  - Track token usage                  │
└───────────┬───────────────────────────┘
            ↓
        [Parallel]
    ┌───────┴───────┐
    ▼               ▼
┌─────────┐    ┌─────────┐
│ Element │    │ Element │  (4-8 elements)
│ Prompt  │    │ Prompt  │
└────┬────┘    └────┬────┘
     │              │
     ▼              ▼
┌─────────┐    ┌─────────┐
│ LLM Call│    │ LLM Call│
│ (Flash/ │    │ (Flash/ │
│  Pro)   │    │  Pro)   │
└────┬────┘    └────┬────┘
     │              │
     └──────┬───────┘
            ▼
┌───────────────────────────────────────┐
│  TemplateAssembler                    │
│  - Load HTML template                 │
│  - Map element content to placeholders│
│  - Assemble complete HTML             │
└───────────┬───────────────────────────┘
            ▼
    Final HTML Content
```

### Key Components

#### 1. ElementPromptBuilder
**Responsibility**: Transform variant specifications into LLM-ready prompts

**Input**:
- Variant ID (e.g., `matrix_2x2`)
- Slide context (title, purpose, message)
- Presentation context (position, prior slides)

**Output**:
- List of element prompts with:
  - Element ID
  - Element type (text_box, metric_card, etc.)
  - Character count requirements
  - Element-specific instructions
  - Contextual information

**Key Methods**:
```python
load_variant_spec(variant_id: str) -> Dict
    └─> Loads JSON spec from app/variant_specs/{type}/{variant_id}.json

build_element_prompt(element_def: Dict, contexts: Dict) -> str
    └─> Creates targeted prompt with character limits and context

build_all_element_prompts(variant_id: str, ...) -> List[Dict]
    └─> Orchestrates prompt building for all elements in variant
```

**Caching Strategy**: Variant specs cached after first load (performance optimization)

---

#### 2. ContextBuilder
**Responsibility**: Build rich contextual information for content generation

**Slide-Level Context**:
- Title, purpose, key message
- Tone (professional, casual, technical)
- Audience (executives, technical team, general)
- Relationships between elements

**Presentation-Level Context**:
- Presentation title and type
- Current slide position (3 of 15)
- Prior slides summary
- Overall narrative arc

**Output Format**:
```
"This slide presents [purpose] to [audience]. The key message is [message].
Previous slides covered [summary]. This is slide [N] of [total]."
```

**Integration**: Context automatically injected into each element prompt by ElementPromptBuilder

---

#### 3. ElementBasedContentGenerator
**Responsibility**: Orchestrate complete content generation workflow

**Generation Modes**:

**Parallel Mode** (default, 3-5x faster):
```python
async def generate_slide_content(..., enable_parallel=True):
    tasks = [generate_element(prompt) for prompt in element_prompts]
    elements = await asyncio.gather(*tasks)
    return assemble_template(elements)
```

**Sequential Mode** (fallback for debugging):
```python
async def generate_slide_content(..., enable_parallel=False):
    elements = []
    for prompt in element_prompts:
        element = await generate_element(prompt)
        elements.append(element)
    return assemble_template(elements)
```

**Character Count Validation**:
- Each element validated against spec requirements
- Baseline ± 5% tolerance
- Violations logged but generation continues
- Future: Retry logic for violations

**Token Tracking**:
- Tracks total LLM calls
- Separates Flash vs Pro usage
- Reports total token consumption
- Enables cost analysis

---

#### 4. TemplateAssembler
**Responsibility**: Load templates and assemble with generated content

**Template Structure**:
```html
<!-- app/templates/matrix/matrix_2x2.html -->
<div class="matrix-layout">
  <div class="box-1">
    <h3>{{box_1_title}}</h3>
    <p>{{box_1_description}}</p>
  </div>
  <!-- ... more boxes ... -->
</div>
```

**Placeholder Convention**: `{{element_id_field_name}}`
- Element ID: Matches variant spec element IDs
- Field name: Matches element type fields (title, description, etc.)

**Assembly Process**:
1. Load template from disk (cached)
2. Extract all placeholders via regex
3. Build content map from generated elements
4. Replace placeholders with content
5. Return complete HTML

**Template Caching**: Templates cached after first load for performance

---

## Hero Slide Architecture (Single-Call)

### Component Flow

```
Director Request
    ↓
┌───────────────────────────────────────┐
│  BaseHeroGenerator                    │
│  - Route to specific generator        │
│    (TitleSlide/SectionDivider/Closing)│
└───────────┬───────────────────────────┘
            ↓
┌───────────────────────────────────────┐
│  Specific Hero Generator              │
│  - Build rich v1.1-style prompt       │
│  - Include gradient backgrounds       │
│  - Specify exact typography           │
│  - Provide golden examples            │
└───────────┬───────────────────────────┘
            ↓
┌───────────────────────────────────────┐
│  Single LLM Call (Flash)              │
│  - Generate complete inline HTML      │
│  - No template assembly needed        │
└───────────┬───────────────────────────┘
            ↓
┌───────────────────────────────────────┐
│  Clean Markdown Wrapper               │
│  - Strip ```html``` fences            │
│  - Ensure raw HTML output             │
└───────────┬───────────────────────────┘
            ↓
┌───────────────────────────────────────┐
│  Validate Inline Styles               │
│  - Check gradient background          │
│  - Verify large typography (96px)     │
│  - Confirm text shadows                │
│  - Validate character counts          │
└───────────┬───────────────────────────┘
            ▼
    Complete Hero HTML
```

### Key Components

#### 1. BaseHeroGenerator (Abstract Base Class)
**Responsibility**: Define common hero generation workflow

**Template Method Pattern**:
```python
async def generate(request: HeroGenerationRequest) -> HeroResponse:
    # 1. Build rich prompt (implemented by subclass)
    prompt = await self._build_prompt(request)

    # 2. Call LLM
    content = await self.llm_service(prompt, model="flash")

    # 3. Clean markdown wrappers
    content = self._clean_markdown_wrapper(content)

    # 4. Validate output (implemented by subclass)
    validation = self._validate_output(content, request)

    # 5. Return structured response
    return HeroResponse(content=content, metadata={...})
```

**Common Utilities**:
- `_clean_markdown_wrapper()`: Strip ```html fences from LLM output
- `_extract_text_from_html()`: Extract text for character count validation
- `_count_characters()`: Count visible characters (excluding HTML tags)

**Abstract Methods**:
- `_build_prompt()`: Subclass implements specific prompt
- `_validate_output()`: Subclass implements validation rules
- `slide_type`: Property returning slide type identifier

---

#### 2. TitleSlideGenerator
**Responsibility**: Generate opening slides with maximum visual impact

**Prompt Strategy**:
- **Typography**: 96px title, 42px subtitle, 32px attribution
- **Visual**: Gradient backgrounds, text shadows, center alignment
- **Content**: Title (40-80 chars), subtitle (80-120 chars), attribution (60-100 chars)
- **Golden Example**: Full inline-styled HTML provided in prompt

**Gradient Options** (theme-based):
```python
"professional": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
"bold": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
"warm": "linear-gradient(135deg, #ffa751 0%, #ffe259 100%)"
"navy": "linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)"
```

**Validation Rules**:
```python
# Check for inline style patterns (not CSS classes)
has_gradient = re.search(r'<div[^>]*style=.*linear-gradient', content, re.DOTALL)
has_96px_font = re.search(r'<h1[^>]*style=.*font-size:\s*96px', content, re.DOTALL)
has_white_text = re.search(r'color:\s*white', content)

# Character count validation
title_length: 40-80 (warn), >100 (error)
subtitle_length: 80-120 (warn), >150 (error)
```

**Why Inline Styles?**: Layout architect expects ready-to-render HTML with all styling included. No external CSS dependencies.

---

#### 3. SectionDividerGenerator
**Responsibility**: Generate dramatic section transition slides

**Prompt Strategy**:
- **Typography**: 84px section title, 42px context text (muted gray)
- **Visual**: Dark background (#1f2937), 12px colored left border, left-aligned
- **Content**: Section title (40-60 chars), context (80-120 chars)
- **Aesthetic**: Minimal, high-contrast, dramatic

**Border Color Options** (section theme):
```python
"strategy": "border-left: 12px solid #667eea"  # Purple
"execution": "border-left: 12px solid #1a73e8"  # Blue
"results": "border-left: 12px solid #34a853"    # Green
"innovation": "border-left: 12px solid #9333ea" # Deep Purple
```

**Layout Pattern**:
```html
<div style="background: #1f2937; display: flex; align-items: center; ...">
  <div style="border-left: 12px solid #667eea; padding-left: 48px;">
    <h2 style="font-size: 84px; color: white; ...">Section Title</h2>
    <p style="font-size: 42px; color: #9ca3af; ...">Context Text</p>
  </div>
</div>
```

**Validation Rules**: Check for dark background, left border, 84px title, muted gray context text

---

#### 4. ClosingSlideGenerator
**Responsibility**: Generate final slides with clear call-to-action

**Prompt Strategy**:
- **Typography**: 72px closing message, 36px supporting text, 32px CTA button, 28px contact
- **Visual**: Gradient background, white CTA button with colored text, button shadow
- **Content**: Closing message (50-80 chars), supporting text (variable), CTA (3-5 words), contact (3-5 items)
- **CTA Button**: White background, colored text matching gradient, large padding, prominent shadow

**Button Styling** (critical):
```css
padding: 32px 72px;
background: white;
color: #667eea;  /* Matches gradient */
border-radius: 12px;
box-shadow: 0 8px 24px rgba(0,0,0,0.3);
font-weight: 700;
```

**Contact Format**: `email | website | phone` (pipe-separated)

**Validation Rules**:
- Check for gradient, 72px message, 32px white button
- Validate contact contains email or website pattern
- Verify CTA is 3-5 words (actionable)

---

## Model Routing Strategy

### Intelligence-Based Routing

Text Service v1.2 routes LLM calls to different Gemini models based on content complexity:

| Element Type | Model | Rationale | Cost |
|-------------|-------|-----------|------|
| text_box | **Flash** | Simple title + description | Low |
| metric_card | **Flash** | Number + label + description | Low |
| quote | **Flash** | Quote text + attribution | Low |
| impact_quote | **Flash** | Large quote + attribution | Low |
| table_row | **Pro** | Multi-column structured data | Medium |
| comparison_column | **Pro** | Header + items + nuance | Medium |
| sequential_step | **Pro** | Number + title + description + order | Medium |
| colored_section | **Pro** | Title + description + context | Medium |
| insights_box | **Pro** | Analytical summary content | Medium |
| **Hero slides** | **Flash** | Single-call complete HTML | Low |

**Cost Savings**: 60-70% reduction compared to using Pro for everything

**Configuration**:
```python
# app/core/llm_client.py
ELEMENT_MODEL_ROUTING = {
    "text_box": "flash",
    "metric_card": "flash",
    "quote": "flash",
    "table_row": "pro",
    "colored_section": "pro",
    # ...
}

MODELS = {
    "flash": "gemini-2.0-flash-exp",
    "pro": "gemini-1.5-pro"
}
```

**Token Tracking**:
```python
{
    "total_calls": 4,
    "flash_calls": 2,
    "pro_calls": 2,
    "flash_percentage": 50.0,
    "total_tokens": 624
}
```

---

## Data Flow Diagrams

### Content Slide Generation Flow

```
┌─────────────────────────────────────────────────────────────┐
│  POST /v1.2/generate                                        │
│  {                                                           │
│    "variant_id": "matrix_2x2",                              │
│    "slide_spec": {...},                                     │
│    "presentation_spec": {...}                               │
│  }                                                           │
└───────────────────┬─────────────────────────────────────────┘
                    ▼
         ┌──────────────────────┐
         │  Load Variant Spec   │
         │  matrix_2x2.json     │
         └──────────┬───────────┘
                    ▼
         ┌──────────────────────┐
         │  Extract 4 Elements  │
         │  - box_1 (text_box)  │
         │  - box_2 (text_box)  │
         │  - box_3 (text_box)  │
         │  - box_4 (text_box)  │
         └──────────┬───────────┘
                    ▼
         ┌──────────────────────┐
         │  Build Element       │
         │  Prompts with        │
         │  Context             │
         └──────────┬───────────┘
                    ▼
            [Parallel Execution]
    ┌───────┬───────┬───────┬───────┐
    ▼       ▼       ▼       ▼       ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ Flash  │ │ Flash  │ │ Flash  │ │ Flash  │
│ Call 1 │ │ Call 2 │ │ Call 3 │ │ Call 4 │
└────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘
     │          │          │          │
     └──────────┴──────────┴──────────┘
                    ▼
         ┌──────────────────────┐
         │  Gather Results      │
         │  {                   │
         │   "box_1_title": "...",│
         │   "box_1_desc": "...",│
         │   ...                 │
         │  }                    │
         └──────────┬───────────┘
                    ▼
         ┌──────────────────────┐
         │  Load Template       │
         │  matrix_2x2.html     │
         └──────────┬───────────┘
                    ▼
         ┌──────────────────────┐
         │  Replace Placeholders│
         │  {{box_1_title}} →   │
         │  "Innovation"        │
         └──────────┬───────────┘
                    ▼
         ┌──────────────────────┐
         │  Validate & Return   │
         │  Complete HTML       │
         └──────────────────────┘
```

### Hero Slide Generation Flow

```
┌─────────────────────────────────────────────────────────────┐
│  POST /v1.2/hero/title                                      │
│  {                                                           │
│    "slide_number": 1,                                       │
│    "slide_type": "title_slide",                             │
│    "narrative": "...",                                      │
│    "topics": [...],                                         │
│    "context": {...}                                         │
│  }                                                           │
└───────────────────┬─────────────────────────────────────────┘
                    ▼
         ┌──────────────────────┐
         │  TitleSlideGenerator │
         │  _build_prompt()     │
         └──────────┬───────────┘
                    ▼
         ┌──────────────────────┐
         │  Rich Prompt with:   │
         │  - 96px/42px/32px    │
         │  - Gradient options  │
         │  - Golden example    │
         │  - Character limits  │
         └──────────┬───────────┘
                    ▼
         ┌──────────────────────┐
         │  Single Flash Call   │
         │  (Complete HTML)     │
         └──────────┬───────────┘
                    ▼
         ┌──────────────────────┐
         │  Clean Markdown      │
         │  Strip ```html```    │
         └──────────┬───────────┘
                    ▼
         ┌──────────────────────┐
         │  Validate Inline     │
         │  Styles:             │
         │  ✓ linear-gradient   │
         │  ✓ font-size: 96px   │
         │  ✓ text-shadow       │
         │  ✓ Character counts  │
         └──────────┬───────────┘
                    ▼
         ┌──────────────────────┐
         │  Return Complete     │
         │  Inline-Styled HTML  │
         └──────────────────────┘
```

---

## Integration with Director v3.4

### Service Router Integration

**Director v3.4** uses `service_router_v1_2.py` to route slides to Text Service v1.2:

```python
# src/utils/service_router_v1_2.py

async def route_slide_to_text_service(slide: Slide, context: Dict) -> Dict:
    """Route slide to appropriate Text Service v1.2 endpoint."""

    classification = slide.classification

    # Hero slides → /v1.2/hero/* endpoints
    if classification in ["title_slide", "section_divider", "closing_slide"]:
        hero_type = classification.replace("_slide", "")
        endpoint = f"{TEXT_SERVICE_URL}/v1.2/hero/{hero_type}"
        payload = build_hero_request(slide, context)

    # Content slides → /v1.2/generate endpoint
    else:
        endpoint = f"{TEXT_SERVICE_URL}/v1.2/generate"
        payload = build_content_request(slide, context)

    # Make async HTTP call
    response = await async_post(endpoint, payload)

    # Package response (FLAT STRUCTURE)
    return {
        "slide_number": slide.slide_number,
        "slide_id": slide.slide_id,
        "content": response["content"],      # HTML string directly
        "metadata": response["metadata"]     # Top-level metadata
    }
```

**Critical Design Decision**: Hero and content slides both return **flat structure** with `content` as HTML string and `metadata` as separate top-level key. This ensures consistent handling by `content_transformer.py`.

### Hero Request Transformer

**Director v3.4** uses `hero_request_transformer.py` to build hero endpoint payloads:

```python
# src/utils/hero_request_transformer.py

def transform_to_hero_request(slide: Slide, context: Dict) -> Dict:
    """Transform Director slide to hero endpoint format."""

    return {
        "slide_number": slide.slide_number,
        "slide_type": slide.classification,
        "narrative": slide.narrative or context.get("narrative", ""),
        "topics": slide.topics or context.get("topics", []),
        "context": {
            "theme": context.get("theme", "professional"),
            "audience": context.get("audience", "business stakeholders"),
            "presentation_title": context.get("presentation_title", ""),
            "contact_info": context.get("contact_info", "")
        }
    }
```

### Content Transformer

**Director v3.4** uses `content_transformer.py` to map Text Service responses to layout formats:

```python
# src/utils/content_transformer.py

def _map_hero_slide(content: Any, layout_id: str) -> Dict:
    """Map hero slide content to L29 layout format."""

    # Content is already complete inline-styled HTML string
    if isinstance(content, str):
        html = content
    elif isinstance(content, dict):
        # Legacy support for nested structures
        html = content.get("hero_content") or content.get("rich_content") or ""
    else:
        html = ""

    return {
        "layout_id": "L29",
        "hero_content": html,  # Complete inline HTML
        "metadata": {
            "layout_type": "hero",
            "generation_source": "text_service_v1.2"
        }
    }
```

**Key Insight**: Text Service v1.2 returns complete inline-styled HTML. Content transformer passes it directly to layout service without modification. Layout architect renders it as-is.

---

## Error Handling & Resilience

### Content Slide Error Handling

**Element Generation Failures**:
```python
try:
    element_content = await generate_element(prompt)
except LLMException as e:
    logger.error(f"Element {element_id} generation failed: {e}")
    # Use fallback content or retry
    element_content = fallback_content_for_element(element_id)
```

**Template Assembly Failures**:
```python
try:
    html = assembler.assemble_template(template_path, content_map)
except TemplateError as e:
    logger.error(f"Template assembly failed: {e}")
    # Return error HTML with diagnostic info
    return error_html_response(e)
```

**Character Count Violations**:
- **Warning**: Element slightly over/under (5-15% deviation)
- **Error**: Element significantly over/under (>15% deviation)
- **Action**: Log but continue (retry logic planned for future)

### Hero Slide Error Handling

**Markdown Wrapper Cleaning**:
```python
def _clean_markdown_wrapper(content: str) -> str:
    """Remove markdown code fences if present."""
    content = content.strip()
    if content.startswith("```html"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()
```

**Validation Failures**:
```python
validation = self._validate_output(content, request)
if not validation["valid"]:
    logger.warning(f"Hero slide validation failed: {validation['violations']}")
    # Return anyway with validation metadata
    # Future: Retry with modified prompt
```

**Why Allow Invalid Output?**: Better to return imperfect HTML than fail completely. Validation metadata helps debugging.

---

## Performance Characteristics

### Content Slides (Matrix 2×2 Benchmark)

| Mode | Time | LLM Calls | Cost |
|------|------|-----------|------|
| Sequential | ~4.2s | 4 serial | Baseline |
| Parallel (5 workers) | ~1.1s | 4 concurrent | Same |

**3.8x speedup** with parallel generation!

**Token Usage** (typical matrix_2x2):
- Total tokens: ~600-800
- Per element: ~150-200
- Model mix: 100% Flash (all text_box elements)

### Hero Slides (Title Slide Benchmark)

| Metric | Value |
|--------|-------|
| Generation time | ~0.8-1.2s |
| LLM calls | 1 (Flash) |
| Token usage | ~200-300 |
| HTML size | ~1000-1500 chars |

**Why Fast?**: Single LLM call, Flash model, no assembly overhead

### Comparison: Element-Based vs Single-Call

| Factor | Element-Based (Matrix 2×2) | Single-Call (Title Slide) |
|--------|---------------------------|--------------------------|
| Total time | 1.1s (parallel) | 0.8s |
| LLM calls | 4 | 1 |
| Total tokens | 600-800 | 200-300 |
| Assembly overhead | Yes (template + placeholders) | No (complete HTML) |
| Cost | 4× Flash calls | 1× Flash call |

**Takeaway**: Single-call is 25% faster and 75% cheaper for simple structures. Element-based is necessary for complex content.

---

## Scalability Considerations

### Horizontal Scaling

**Stateless Design**: Text Service v1.2 is completely stateless
- No session storage
- No database dependencies
- Template/spec caching in memory (cleared on restart)

**Load Balancing**: Can run multiple instances behind load balancer
- Async/await throughout enables high concurrency
- Each request independent
- No shared state between requests

### Vertical Scaling

**Concurrency Control**:
```python
# Limit parallel element generation
max_workers = 5  # Prevents overwhelming LLM service

# Async HTTP client connection pooling
async with httpx.AsyncClient(limits=httpx.Limits(
    max_connections=50,
    max_keepalive_connections=20
)) as client:
    ...
```

**Memory Management**:
- Template cache: ~500KB for 26 templates
- Variant spec cache: ~100KB for 26 specs
- Total footprint: <10MB per worker process

### Rate Limiting

**Vertex AI Rate Limits** (per project):
- Flash: 2,000 requests/min
- Pro: 1,000 requests/min

**Text Service Protection**:
```python
# Future: Implement rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    # Check request rate per client
    # Return 429 Too Many Requests if exceeded
    ...
```

---

## Testing Strategy

### Unit Tests

**Component-Level Tests**:
- `ElementPromptBuilder`: Variant spec loading, prompt building
- `ContextBuilder`: Slide/presentation context construction
- `TemplateAssembler`: Template loading, placeholder replacement
- `Hero Generators`: Prompt building, validation logic

### Integration Tests

**End-to-End Workflows**:
- Complete content slide generation (all variants)
- Complete hero slide generation (all types)
- Parallel vs sequential generation
- Character count validation
- Error handling paths

**Test File**: `tests/test_v1_2_integration.py`

### Performance Tests

**Load Testing**:
```bash
# Simulate 100 concurrent requests
python3 tests/performance/load_test.py \
    --variant matrix_2x2 \
    --requests 100 \
    --concurrency 10
```

**Metrics Tracked**:
- P50, P95, P99 latency
- Throughput (requests/sec)
- Error rate
- Token usage per request

---

## Design Decisions & Rationale

### 1. Why Dual Architecture?

**Decision**: Use element-based for content, single-call for hero

**Rationale**:
- Content slides have 4-8 elements → element-based enables parallel generation (3-5x faster)
- Hero slides have 1-3 elements → single-call simpler and sufficient
- Hero slides need unified visual design (gradients, typography) → single prompt ensures cohesion
- Element-based assembly would add unnecessary complexity to heroes

**Outcome**: Optimal speed/quality balance for each slide type

### 2. Why Inline Styles for Heroes?

**Decision**: Generate complete inline-styled HTML (no CSS classes)

**Rationale**:
- Layout architect expects ready-to-render HTML
- No external CSS dependencies to manage
- v1.1 world-class prompts proved inline styles produce best visual quality
- Validation can check specific style attributes (96px fonts, gradients)

**Outcome**: Self-contained HTML that renders consistently across environments

### 3. Why Markdown Wrapper Cleaning?

**Decision**: Strip ```html fences from LLM output

**Rationale**:
- LLMs often wrap HTML in markdown code blocks by default
- Layout architect can't parse markdown-wrapped HTML
- Cleaning step makes output robust to LLM variations

**Outcome**: Reliable HTML extraction regardless of LLM formatting habits

### 4. Why Flat Response Structure?

**Decision**: Both hero and content slides return `{"content": "...", "metadata": {...}}`

**Rationale**:
- Content transformer expects consistent structure
- Nested structures caused blank slide bug (resolved in recent fix)
- Flat structure simplifies Director's content mapping logic

**Outcome**: Reliable content extraction and transformation

### 5. Why Model Routing?

**Decision**: Route simple elements to Flash, complex to Pro

**Rationale**:
- Flash 10× cheaper than Pro
- Flash sufficient for simple title+description elements
- Pro needed for structured data (tables) and analytical content (insights)
- 60-70% cost savings without quality loss

**Outcome**: Cost-optimized generation maintaining quality standards

### 6. Why Template Caching?

**Decision**: Cache templates and variant specs after first load

**Rationale**:
- Templates/specs don't change during runtime
- File I/O overhead (10-20ms) adds up with parallel generation
- Memory footprint minimal (<1MB total)

**Outcome**: ~15% performance improvement on repeated requests

### 7. Why Character Count Validation?

**Decision**: Validate generated content against spec requirements

**Rationale**:
- Golden examples established baseline character counts
- ±5% tolerance accommodates natural language variation
- Warnings help identify prompt drift over time
- Future retry logic can use violations to improve quality

**Outcome**: Quality monitoring without blocking generation

---

## Future Enhancements

### Short-Term (Next 3 Months)

1. **Retry Logic for Character Count Violations**
   - Auto-retry with adjusted prompt if element violates limits
   - Maximum 2 retries per element
   - Fallback to violation if retries fail

2. **Enhanced Caching**
   - Redis cache for generated content (deduplication)
   - Cache key: hash(variant_id + slide_context)
   - TTL: 1 hour

3. **Rate Limiting Middleware**
   - Per-client rate limiting (100 req/min)
   - Circuit breaker for Vertex AI failures
   - Graceful degradation

4. **Additional Variants**
   - Grid 4×2, 2×4 layouts
   - Table 6-column, 7-column
   - Asymmetric 6-section, 7-section

### Long-Term (6-12 Months)

1. **Dynamic Template Generation**
   - Generate templates on-the-fly for custom layouts
   - AI-driven template optimization based on content

2. **Multi-Model Support**
   - Support OpenAI GPT-4, Anthropic Claude
   - Model selection via API parameter
   - A/B testing between models

3. **Content Quality Scoring**
   - ML-based scoring of generated content
   - Automatic retry for low-quality content
   - Quality metrics dashboard

4. **Variant Recommendation Engine**
   - Suggest best variant based on content analysis
   - Consider: content length, structure, audience
   - API: `POST /v1.2/recommend-variant`

---

## Conclusion

Text Service v1.2's dual architecture successfully balances **determinism** (element-based assembly for content) with **visual impact** (single-call with inline styles for heroes). This design achieves:

✅ **3-5× faster generation** via parallel element processing
✅ **60-70% cost reduction** via intelligent model routing
✅ **World-class visual quality** via v1.1-inspired rich prompts
✅ **Deterministic output** via template-based assembly
✅ **Maintainable codebase** via separation of concerns

The architecture is **production-ready**, **scalable**, and **extensible**, providing a solid foundation for future enhancements while delivering exceptional slide quality today.

---

**Document Version**: 1.0
**Last Updated**: December 2025
**Maintainer**: Deckster Engineering Team
