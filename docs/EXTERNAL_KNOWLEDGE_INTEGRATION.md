# External Knowledge Integration for Text Service

**Version**: 1.0
**Date**: December 21, 2024
**Status**: Design Proposal
**Author**: Text Service Team

---

## 1. Problem & Motivation

### Current Limitation: LLM Knowledge Only

Today, the Text Service generates slide content relying **exclusively** on:
1. The narrative/topics provided by Director
2. The LLM's internal knowledge (with training cutoff)

```
┌─────────────────────────────────────────────────────────────┐
│                    CURRENT STATE                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Director Request ──► Text Service ──► LLM ──► HTML       │
│        │                                  ▲                 │
│        │                                  │                 │
│   (narrative,                        (training cutoff,      │
│    topics,                            no user data,         │
│    variant_id)                        generic content)      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### The Problem by Variant Type

| Variant Category | Current Issue | Impact |
|------------------|---------------|--------|
| **metrics_*** | Numbers are illustrative/fabricated | Low credibility |
| **table_*** | Data is generic, not from user's documents | Missing accuracy |
| **impact_quote** | Quotes are LLM-generated, not sourced | Authenticity concern |
| **comparison_*** | Competitor data may be outdated/wrong | Misleading content |
| **bullets/grid** | General points, not user-specific insights | Generic presentations |

### The Opportunity

With external knowledge integration, Text Service can:
- **Pull real metrics** from user's uploaded financial reports
- **Extract actual quotes** from uploaded documents
- **Use current statistics** from web search
- **Include user-specific data** in tables and comparisons
- **Cite sources** for credibility

---

## 2. Knowledge-Value Matrix by Variant

### HIGH VALUE Variants (Priority 1)

These variants benefit MOST from external knowledge:

| Variant | Knowledge Type Needed | Example Use Case |
|---------|----------------------|------------------|
| `metrics_3col` | Extracted metrics from uploads | "Revenue: $45M" from Q4_Report.pdf |
| `metrics_4col` | Web search for industry benchmarks | "Industry avg: 15% growth" |
| `metrics_2x2_grid` | Both uploads + web | Company metrics vs market |
| `table_*` | Extracted tables from uploads | Financial tables, comparisons |
| `impact_quote` | Extracted quotes from uploads | CEO statement, testimonial |
| `comparison_*` | Web search for competitor data | Feature comparison with market |

### MEDIUM VALUE Variants (Priority 2)

| Variant | Knowledge Type Needed | Example Use Case |
|---------|----------------------|------------------|
| `bullets` | Facts from uploads or web | Key points from strategy doc |
| `grid_*` | Specific data points | Product features from spec sheet |
| `sequential_*` | Process steps from uploads | Implementation roadmap |

### LOWER VALUE Variants (Priority 3)

| Variant | Knowledge Type | Notes |
|---------|---------------|-------|
| `matrix_*` | Concepts from uploads | Structure is more important than data |
| `hybrid_*` | Mixed | Benefits from context, not critical |
| `single_column_*` | Narrative flow | LLM handles well without data |

---

## 3. Proposed Architecture

### Knowledge Flow for Text Service

```
┌──────────────────────────────────────────────────────────────────┐
│                ENHANCED KNOWLEDGE FLOW                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│                    ┌─────────────────────┐                       │
│                    │  Knowledge Service  │                       │
│                    │  (Gemini/RAG)       │                       │
│                    └──────────┬──────────┘                       │
│                               │                                  │
│         ┌─────────────────────┼─────────────────────┐           │
│         │                     │                     │           │
│         ▼                     ▼                     ▼           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │  File Search │    │  Data Extract│    │  Web Search  │       │
│  │  (semantic)  │    │  (metrics,   │    │  (current    │       │
│  │              │    │   quotes,    │    │   stats)     │       │
│  │              │    │   tables)    │    │              │       │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘       │
│         │                   │                   │               │
│         └───────────────────┼───────────────────┘               │
│                             │                                   │
│                             ▼                                   │
│         ┌───────────────────────────────────────┐               │
│         │              DIRECTOR                  │               │
│         │  (orchestrates, caches, passes to     │               │
│         │   Text Service as knowledge_context)  │               │
│         └───────────────────┬───────────────────┘               │
│                             │                                   │
│                             ▼                                   │
│         ┌───────────────────────────────────────┐               │
│         │           TEXT SERVICE                 │               │
│         │                                        │               │
│         │  Request includes:                     │               │
│         │  • narrative, topics, variant_id       │               │
│         │  • use_uploads: true/false             │               │
│         │  • use_web_search: true/false          │               │
│         │  • knowledge_context: {...}            │               │
│         │                                        │               │
│         │  Generation modes:                     │               │
│         │  1. LLM-only (flags=false)             │               │
│         │  2. Upload-enhanced (use_uploads=true) │               │
│         │  3. Web-enhanced (use_web_search=true) │               │
│         │  4. Full-enhanced (both=true)          │               │
│         └───────────────────────────────────────┘               │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Decision: Director Pre-fetches, Text Service Consumes

**Rationale:**
1. Director already knows the slide topic/purpose
2. Director can cache and batch knowledge queries
3. Text Service stays focused on generation
4. Avoids Text Service needing Knowledge Service credentials

---

## 4. Endpoints NEEDED FROM Knowledge Service

### 4.1 Endpoints Already Proposed by Director (Reuse As-Is)

These endpoints from Director's spec work well for Text Service:

| Endpoint | Text Service Use Case | Enhancement Needed |
|----------|----------------------|-------------------|
| `POST /files/{session_id}/search` | Find content relevant to slide topic | None - works as-is |
| `GET /files/{session_id}/summary` | Context about available documents | None - works as-is |

### 4.2 Endpoints Needing Enhancement for Text Service

#### `POST /files/{session_id}/extract` - ENHANCED

**Current (Director spec):**
```json
{
  "extraction_type": "metrics",  // metrics, quotes, facts, data_tables
  "topic_filter": "revenue"
}
```

**ENHANCEMENT REQUEST - Add `output_format` for Text Service:**

```json
{
  "extraction_type": "metrics",
  "topic_filter": "revenue growth",
  "output_format": "text_service_ready",  // NEW: formats for direct HTML insertion
  "max_items": 4,                         // NEW: limit for slide constraints
  "include_source_citation": true         // NEW: for footnote generation
}
```

**Enhanced Response:**
```json
{
  "extraction_type": "metrics",
  "results": [
    {
      "metric": "YoY Revenue Growth",
      "value": "23%",
      "formatted_html": "<span class='metric-value'>23%</span>",  // NEW
      "context": "Q4 2024 vs Q4 2023",
      "source": {"file": "Q4_Report.pdf", "page": 3},
      "citation_footnote": "Source: Q4 Report, p.3"               // NEW
    }
  ],
  "text_service_hints": {                                          // NEW
    "suggested_variant": "metrics_4col",
    "data_count": 4,
    "has_sufficient_data": true
  }
}
```

### 4.3 NEW Endpoints Needed for Text Service

#### `POST /files/{session_id}/extract-for-variant` - NEW

**Purpose:** Extract data formatted specifically for a C1 variant type.

**Request:**
```json
{
  "session_id": "sess_abc123",
  "variant_id": "metrics_4col",
  "slide_topic": "Q4 Financial Performance",
  "max_items": 4,
  "fallback_to_web": true
}
```

**Response:**
```json
{
  "variant_id": "metrics_4col",
  "extraction_status": "complete",  // complete, partial, insufficient
  "items": [
    {
      "position": 1,
      "label": "Revenue",
      "value": "$45M",
      "subtext": "23% YoY growth",
      "source": "Q4_Report.pdf"
    },
    {
      "position": 2,
      "label": "Active Users",
      "value": "2.3M",
      "subtext": "15% increase",
      "source": "Q4_Report.pdf"
    },
    {
      "position": 3,
      "label": "NPS Score",
      "value": "72",
      "subtext": "Industry avg: 45",
      "source": "web_search"
    },
    {
      "position": 4,
      "label": "Market Share",
      "value": "18%",
      "subtext": "Up from 12%",
      "source": "Q4_Report.pdf"
    }
  ],
  "sources_used": ["Q4_Report.pdf", "web_search"],
  "gaps_filled_by_web": 1
}
```

#### `POST /search/statistics` - NEW (Web Search Enhancement)

**Purpose:** Find current statistics for a specific domain/topic.

**Request:**
```json
{
  "topic": "SaaS market size 2024",
  "data_format": "metric",  // metric, percentage, currency, ranking
  "prefer_sources": ["Gartner", "Statista", "McKinsey"],
  "for_comparison_with": "Our revenue: $45M"  // Optional context
}
```

**Response:**
```json
{
  "topic": "SaaS market size 2024",
  "primary_result": {
    "value": "$232B",
    "description": "Global SaaS market size 2024",
    "source": "Gartner",
    "confidence": "high",
    "date": "2024-10"
  },
  "comparison_context": {
    "user_value": "$45M",
    "market_percentage": "0.019%",
    "insight": "Significant growth opportunity in $232B market"
  },
  "related_stats": [
    {"metric": "YoY Growth", "value": "18%", "source": "Statista"}
  ]
}
```

---

## 5. Text Service API Changes

### 5.1 Enhanced Request Model

**Add to `UnifiedSlideRequest`:**

```python
class UnifiedSlideRequest(BaseModel):
    # ... existing fields ...

    # =========================================================================
    # v1.4.0: External Knowledge Integration
    # =========================================================================

    # Feature flags
    use_uploads: bool = Field(
        default=False,
        description="Enable content from user-uploaded documents"
    )
    use_web_search: bool = Field(
        default=False,
        description="Enable content from web search results"
    )

    # Pre-fetched knowledge context (from Director)
    knowledge_context: Optional[KnowledgeContext] = Field(
        default=None,
        description="Pre-fetched knowledge from Director"
    )

    # Source attribution preference
    include_source_citations: bool = Field(
        default=True,
        description="Include source citations in generated content"
    )
```

**New `KnowledgeContext` Model:**

```python
class KnowledgeContext(BaseModel):
    """
    Knowledge context passed from Director to Text Service.
    Contains pre-fetched relevant content for the slide.
    """
    # From user uploads
    from_uploads: Optional[List[UploadSnippet]] = None

    # From web search
    from_web: Optional[List[WebFinding]] = None

    # Pre-extracted data (for metrics, tables, quotes)
    extracted_data: Optional[ExtractedData] = None

    # Metadata
    session_id: str
    fetch_timestamp: str
    sources_available: List[str]  # ["Q4_Report.pdf", "Strategy.docx"]


class UploadSnippet(BaseModel):
    """Relevant snippet from user upload."""
    content: str
    source_file: str
    page: Optional[int] = None
    relevance_score: float
    content_type: str  # "text", "metric", "quote", "table_row"


class WebFinding(BaseModel):
    """Finding from web search."""
    finding: str
    source: str
    url: Optional[str] = None
    confidence: str  # "high", "medium", "low"
    date: Optional[str] = None


class ExtractedData(BaseModel):
    """Pre-extracted structured data."""
    metrics: Optional[List[ExtractedMetric]] = None
    quotes: Optional[List[ExtractedQuote]] = None
    table_data: Optional[List[Dict[str, Any]]] = None
    facts: Optional[List[str]] = None
```

### 5.2 Enhanced Response Model

**Add to response models:**

```python
class ContentSlideResponse(BaseModel):
    # ... existing fields ...

    # v1.4.0: Source attribution
    sources_used: Optional[List[SourceAttribution]] = Field(
        default=None,
        description="Sources used in content generation"
    )

    # v1.4.0: Knowledge utilization metadata
    knowledge_metadata: Optional[KnowledgeMetadata] = Field(
        default=None,
        description="How external knowledge was used"
    )


class SourceAttribution(BaseModel):
    """Source attribution for generated content."""
    source_type: str  # "upload", "web_search", "llm"
    source_name: str  # "Q4_Report.pdf" or "Gartner Research"
    content_used: str  # What content was used
    location: Optional[str] = None  # "Page 3" or URL


class KnowledgeMetadata(BaseModel):
    """Metadata about knowledge utilization."""
    uploads_used: bool
    web_search_used: bool
    llm_only_fields: List[str]  # Fields generated without external knowledge
    knowledge_enhanced_fields: List[str]  # Fields that used external data
    data_coverage: str  # "complete", "partial", "llm_fallback"
```

### 5.3 Generation Modes

| Mode | `use_uploads` | `use_web_search` | Behavior |
|------|---------------|------------------|----------|
| **LLM-Only** | `false` | `false` | Current behavior, no external data |
| **Upload-Enhanced** | `true` | `false` | Uses uploaded docs, no web |
| **Web-Enhanced** | `false` | `true` | Uses web search, no uploads |
| **Full-Enhanced** | `true` | `true` | Uses both sources |

---

## 6. Text Service Internal Changes

### 6.1 Knowledge-Aware Prompt Building

**Current prompt building (simplified):**
```python
prompt = f"""Generate content for {variant_id}:
Narrative: {narrative}
Topics: {topics}
"""
```

**Enhanced prompt building:**
```python
def _build_knowledge_enhanced_prompt(
    self,
    request: UnifiedSlideRequest,
    variant_config: Dict[str, Any]
) -> str:
    """Build prompt with external knowledge context."""

    base_prompt = self._build_base_prompt(request, variant_config)

    # If no knowledge context, return base prompt
    if not request.knowledge_context:
        return base_prompt

    knowledge_section = """

## EXTERNAL KNOWLEDGE (PRIORITIZE THIS DATA!)

"""

    # Add upload content
    if request.use_uploads and request.knowledge_context.from_uploads:
        knowledge_section += "### From User Documents:\n"
        for snippet in request.knowledge_context.from_uploads:
            knowledge_section += f'- "{snippet.content}" (Source: {snippet.source_file})\n'

    # Add web search findings
    if request.use_web_search and request.knowledge_context.from_web:
        knowledge_section += "\n### From Current Research:\n"
        for finding in request.knowledge_context.from_web:
            knowledge_section += f'- {finding.finding} (Source: {finding.source})\n'

    # Add extracted data for specific variants
    if request.knowledge_context.extracted_data:
        if variant_config.get("variant_id", "").startswith("metrics"):
            knowledge_section += "\n### Extracted Metrics (USE THESE EXACT VALUES!):\n"
            for metric in request.knowledge_context.extracted_data.metrics or []:
                knowledge_section += f'- {metric.label}: {metric.value}\n'

        if variant_config.get("variant_id") == "impact_quote":
            knowledge_section += "\n### Extracted Quote (USE THIS EXACT QUOTE!):\n"
            for quote in request.knowledge_context.extracted_data.quotes or []:
                knowledge_section += f'"{quote.text}" - {quote.attribution}\n'

    knowledge_section += """
## INSTRUCTIONS FOR USING EXTERNAL KNOWLEDGE:
1. PRIORITIZE user document content over web research
2. USE exact values/quotes from extracted data when available
3. DO NOT invent metrics - use only provided data or mark as [DATA NEEDED]
4. CITE sources naturally in content where appropriate
5. For missing data, use LLM knowledge but indicate it's general information
"""

    return base_prompt + knowledge_section
```

### 6.2 Variant-Specific Knowledge Handling

```python
class C1TextGenerator:

    VARIANT_KNOWLEDGE_CONFIG = {
        # HIGH VALUE - require specific data types
        "metrics_3col": {
            "required_data": "metrics",
            "min_items": 3,
            "fallback": "illustrative_with_warning"
        },
        "metrics_4col": {
            "required_data": "metrics",
            "min_items": 4,
            "fallback": "illustrative_with_warning"
        },
        "impact_quote": {
            "required_data": "quotes",
            "min_items": 1,
            "fallback": "generate_generic"
        },
        "table_3col": {
            "required_data": "table_data",
            "min_items": 3,
            "fallback": "generate_structure_only"
        },
        "comparison_3col": {
            "required_data": "comparison_data",
            "min_items": 3,
            "fallback": "use_web_search"
        },

        # MEDIUM VALUE - benefit from but don't require
        "bullets": {
            "required_data": None,
            "preferred_data": ["facts", "metrics"],
            "fallback": "llm_generation"
        },
        "grid_2x3": {
            "required_data": None,
            "preferred_data": ["facts"],
            "fallback": "llm_generation"
        }
    }

    async def _handle_knowledge_for_variant(
        self,
        variant_id: str,
        knowledge_context: Optional[KnowledgeContext]
    ) -> Dict[str, Any]:
        """Process knowledge context based on variant requirements."""

        config = self.VARIANT_KNOWLEDGE_CONFIG.get(variant_id, {})
        required = config.get("required_data")

        result = {
            "has_sufficient_data": True,
            "data_source": "llm",
            "warnings": []
        }

        if not knowledge_context:
            if required:
                result["has_sufficient_data"] = False
                result["warnings"].append(
                    f"Variant {variant_id} benefits from {required} data"
                )
            return result

        # Check if required data is available
        if required == "metrics":
            metrics = knowledge_context.extracted_data.metrics if knowledge_context.extracted_data else []
            if len(metrics) >= config.get("min_items", 1):
                result["data_source"] = "external"
                result["data"] = metrics
            else:
                result["has_sufficient_data"] = False
                result["warnings"].append(
                    f"Need {config.get('min_items')} metrics, found {len(metrics)}"
                )

        # Similar handling for quotes, tables, etc.

        return result
```

---

## 7. Pre-Fetched Data from Director

### 7.1 What Director Should Pre-Fetch

For each slide, Director should pre-fetch and pass:

| Slide Property | Knowledge to Pre-Fetch |
|----------------|----------------------|
| Any slide with `narrative` | Semantic search in uploads matching narrative |
| Slides with `topics` | Search for each topic in uploads |
| `variant_id: metrics_*` | Extract metrics from uploads |
| `variant_id: impact_quote` | Extract quotes from uploads |
| `variant_id: table_*` | Extract table data from uploads |
| `variant_id: comparison_*` | Web search for competitor/market data |

### 7.2 Enhanced Director-to-Text-Service Request

**Current Director request:**
```json
{
  "slide_number": 5,
  "narrative": "Q4 Financial Performance",
  "topics": ["revenue growth", "user metrics", "market position"],
  "variant_id": "metrics_4col"
}
```

**Enhanced Director request (v1.4.0):**
```json
{
  "slide_number": 5,
  "narrative": "Q4 Financial Performance",
  "topics": ["revenue growth", "user metrics", "market position"],
  "variant_id": "metrics_4col",

  "use_uploads": true,
  "use_web_search": true,
  "include_source_citations": true,

  "knowledge_context": {
    "session_id": "sess_abc123",
    "fetch_timestamp": "2024-12-21T10:30:00Z",
    "sources_available": ["Q4_Report.pdf", "Strategy_2025.docx"],

    "from_uploads": [
      {
        "content": "Revenue grew 23% YoY to $45M in Q4",
        "source_file": "Q4_Report.pdf",
        "page": 3,
        "relevance_score": 0.95,
        "content_type": "metric"
      },
      {
        "content": "Active users reached 2.3M, up 15% from Q3",
        "source_file": "Q4_Report.pdf",
        "page": 5,
        "relevance_score": 0.92,
        "content_type": "metric"
      }
    ],

    "from_web": [
      {
        "finding": "Industry average NPS is 45 for B2B SaaS",
        "source": "Gartner Research",
        "confidence": "high",
        "date": "2024-10"
      }
    ],

    "extracted_data": {
      "metrics": [
        {"label": "Revenue", "value": "$45M", "subtext": "23% YoY", "source": "Q4_Report.pdf"},
        {"label": "Active Users", "value": "2.3M", "subtext": "15% growth", "source": "Q4_Report.pdf"},
        {"label": "NPS Score", "value": "72", "subtext": "vs 45 industry avg", "source": "Q4_Report.pdf"},
        {"label": "Market Share", "value": "18%", "subtext": "Up from 12%", "source": "Q4_Report.pdf"}
      ]
    }
  }
}
```

### 7.3 Request for Additional Pre-Fetch Data

**Director Team: Please consider pre-fetching these additional items:**

| Data Type | When to Fetch | Text Service Use |
|-----------|---------------|------------------|
| **Document themes** | At session start | Inform overall tone/style |
| **Key entities** | When uploads processed | Ensure correct names/terms |
| **Available chart data** | For metrics variants | Pass to Analytics if needed |
| **Competitor names** | For comparison slides | Ensure accurate comparisons |

---

## 8. Endpoint Summary for Text Service v1.4.0

### 8.1 Enhanced Existing Endpoints

| Endpoint | Change | New Parameters |
|----------|--------|----------------|
| `POST /v1.2/slides/C1-text` | Add knowledge support | `use_uploads`, `use_web_search`, `knowledge_context` |
| `POST /v1.2/slides/H1-*` | Add knowledge support | Same |
| `POST /v1.2/slides/I*` | Add knowledge support | Same |
| `POST /v1.2/generate` | Add knowledge support | Same |

### 8.2 New Endpoints Needed

| Endpoint | Purpose | Priority |
|----------|---------|----------|
| `GET /v1.2/knowledge/requirements/{variant_id}` | Return what data a variant needs | P1 |
| `POST /v1.2/knowledge/validate` | Validate if knowledge_context is sufficient | P2 |

**`GET /v1.2/knowledge/requirements/{variant_id}`**

```json
// GET /v1.2/knowledge/requirements/metrics_4col

{
  "variant_id": "metrics_4col",
  "knowledge_requirements": {
    "required_data_type": "metrics",
    "minimum_items": 4,
    "ideal_items": 4,
    "benefits_from_web_search": true,
    "extraction_endpoint": "/files/{session_id}/extract",
    "extraction_params": {
      "extraction_type": "metrics",
      "max_items": 4
    }
  },
  "example_knowledge_context": {
    "extracted_data": {
      "metrics": [
        {"label": "Metric 1", "value": "XX%", "source": "document.pdf"}
      ]
    }
  }
}
```

---

## 9. Cost & Performance Considerations

### 9.1 Latency Impact

| Operation | Added Latency | Mitigation |
|-----------|---------------|------------|
| Knowledge context parsing | ~5ms | Minimal |
| Enhanced prompt (larger) | ~50-100ms | Acceptable for quality |
| Source attribution | ~10ms | Optional |

**Total impact**: ~60-110ms per request when knowledge is provided.

### 9.2 Token Usage

| Mode | Avg Prompt Tokens | Avg Response Tokens |
|------|-------------------|---------------------|
| LLM-Only | ~500 | ~300 |
| Upload-Enhanced | ~800 | ~350 |
| Full-Enhanced | ~1000 | ~400 |

**Cost increase**: ~40-60% more tokens when using external knowledge.

### 9.3 Graceful Degradation

```python
async def generate_with_fallback(
    self,
    request: UnifiedSlideRequest
) -> ContentSlideResponse:
    """Generate with graceful degradation if knowledge unavailable."""

    try:
        if request.knowledge_context:
            return await self._generate_knowledge_enhanced(request)
    except KnowledgeProcessingError as e:
        logger.warning(f"Knowledge processing failed, falling back: {e}")

    # Fallback to LLM-only generation
    logger.info("Generating with LLM-only mode")
    return await self._generate_llm_only(request)
```

---

## 10. Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Add `use_uploads`, `use_web_search` flags to request model
- [ ] Add `knowledge_context` model
- [ ] Implement knowledge-aware prompt building for `bullets` variant
- [ ] Add `sources_used` to response model

### Phase 2: High-Value Variants (Week 2)
- [ ] Implement metrics extraction handling for `metrics_*` variants
- [ ] Implement quote handling for `impact_quote` variant
- [ ] Implement table data handling for `table_*` variants
- [ ] Add `/knowledge/requirements/{variant_id}` endpoint

### Phase 3: Full Integration (Week 3)
- [ ] Support all C1 variants with knowledge
- [ ] Add H-series knowledge support (contact info, branding)
- [ ] Add I-series knowledge support
- [ ] Implement graceful degradation

### Phase 4: Optimization (Week 4)
- [ ] Token usage optimization
- [ ] Caching for repeated variant generations
- [ ] Metrics and monitoring
- [ ] Documentation and examples

---

## 11. Summary

### What Text Service Needs FROM Knowledge Service

| Endpoint | Purpose | Priority |
|----------|---------|----------|
| `POST /files/{session_id}/extract` (enhanced) | Extract metrics/quotes/tables with formatting | P0 |
| `POST /files/{session_id}/extract-for-variant` (NEW) | Variant-specific extraction | P1 |
| `POST /search/statistics` (NEW) | Current statistics for comparisons | P2 |

### What Text Service Will Expose

| Change | Type | Description |
|--------|------|-------------|
| `use_uploads` flag | Enhancement | Enable upload-based content |
| `use_web_search` flag | Enhancement | Enable web-based content |
| `knowledge_context` parameter | Enhancement | Accept pre-fetched knowledge |
| `sources_used` in response | Enhancement | Source attribution |
| `/knowledge/requirements/{variant_id}` | New endpoint | Variant requirements |

### Generation Modes

```
┌────────────────────────────────────────────────────────────────┐
│                   TEXT SERVICE GENERATION MODES                 │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────────┐    use_uploads=false                      │
│  │   LLM-ONLY      │    use_web_search=false                   │
│  │  (Current)      │    → Pure LLM generation                  │
│  └─────────────────┘                                           │
│                                                                │
│  ┌─────────────────┐    use_uploads=true                       │
│  │ UPLOAD-ENHANCED │    use_web_search=false                   │
│  │                 │    → Uses user document data              │
│  └─────────────────┘                                           │
│                                                                │
│  ┌─────────────────┐    use_uploads=false                      │
│  │  WEB-ENHANCED   │    use_web_search=true                    │
│  │                 │    → Uses current web statistics          │
│  └─────────────────┘                                           │
│                                                                │
│  ┌─────────────────┐    use_uploads=true                       │
│  │ FULL-ENHANCED   │    use_web_search=true                    │
│  │  (Recommended)  │    → Uses both, prioritizes uploads       │
│  └─────────────────┘                                           │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Appendix A: Knowledge Context JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "KnowledgeContext",
  "type": "object",
  "properties": {
    "session_id": {"type": "string"},
    "fetch_timestamp": {"type": "string", "format": "date-time"},
    "sources_available": {
      "type": "array",
      "items": {"type": "string"}
    },
    "from_uploads": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "content": {"type": "string"},
          "source_file": {"type": "string"},
          "page": {"type": "integer"},
          "relevance_score": {"type": "number"},
          "content_type": {"type": "string", "enum": ["text", "metric", "quote", "table_row"]}
        },
        "required": ["content", "source_file", "relevance_score", "content_type"]
      }
    },
    "from_web": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "finding": {"type": "string"},
          "source": {"type": "string"},
          "url": {"type": "string"},
          "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
          "date": {"type": "string"}
        },
        "required": ["finding", "source", "confidence"]
      }
    },
    "extracted_data": {
      "type": "object",
      "properties": {
        "metrics": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "label": {"type": "string"},
              "value": {"type": "string"},
              "subtext": {"type": "string"},
              "source": {"type": "string"}
            },
            "required": ["label", "value"]
          }
        },
        "quotes": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "text": {"type": "string"},
              "attribution": {"type": "string"},
              "source": {"type": "string"}
            },
            "required": ["text"]
          }
        },
        "table_data": {
          "type": "array",
          "items": {"type": "object"}
        },
        "facts": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    }
  },
  "required": ["session_id", "fetch_timestamp"]
}
```

---

## Appendix B: Request to Knowledge Service Team

### Enhancement Requests

1. **`/files/{session_id}/extract` Enhancement**
   - Add `output_format: "text_service_ready"` option
   - Add `max_items` parameter for slide constraints
   - Add `include_source_citation` for footnotes
   - Return `text_service_hints` with suggested variant

2. **New Endpoint: `/files/{session_id}/extract-for-variant`**
   - Accept `variant_id` to return properly formatted data
   - Handle multi-source aggregation
   - Support fallback to web search when uploads insufficient

3. **New Endpoint: `/search/statistics`**
   - Specialized for numerical data search
   - Support comparison context
   - Return formatted for metric variants

### Questions for Knowledge Service Team

1. Can `/files/{session_id}/extract` support batch extraction for multiple topics in one call?
2. What's the latency expectation for `extract-for-variant` endpoint?
3. Should web search results include confidence scores?
4. Can we get "data coverage" metric (e.g., "found 3/4 requested metrics")?

---

**END OF DOCUMENT**
