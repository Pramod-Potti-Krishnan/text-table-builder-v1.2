# Text Labs: Single Elements + Placeholder Mode

## User Request Summary

1. **Single Element Support**: Add ability to create a single metric, single step, etc. (not forced to create 2+)
2. **Placeholder Mode**: Don't generate LLM content immediately. Use placeholders first, then generate content on demand when user says "generate" with full slide context.

---

## Current State Analysis

### Issue 1: Min Count Constraints

| Component | Current Min | Supports count=1? |
|-----------|-------------|-------------------|
| CALLOUT | 1 | ✅ Yes |
| SECTIONS | 1 | ✅ Yes (updated earlier) |
| COMPARISON | 1 | ✅ Yes (updated earlier) |
| **METRICS** | **2** | ❌ No - needs update |
| **SEQUENTIAL** | **2** | ❌ No - needs update |

### Issue 2: LLM Generation Flow

**Current flow** (always generates content):
```
User: "Add 3 metrics"
  → Parse intent
  → Call atomic endpoint
  → LLM generates content
  → Return HTML with generated content
```

**Desired flow** (placeholder first, generate on demand):
```
User: "Add 3 metrics"
  → Parse intent
  → Return HTML with PLACEHOLDER content (no LLM)
  → User arranges, positions, adds more elements
  → User: "Generate content"
  → LLM generates content with FULL context (title, all elements, etc.)
```

---

## Implementation Plan

### Phase 1: Enable count=1 for METRICS and SEQUENTIAL

**Files to modify:**
- `text_table_builder/v1.2/app/models/atomic_models.py`

**Changes:**
```python
# MetricsAtomicRequest (around line 167)
count: int = Field(
    default=3,
    ge=1,  # Changed from ge=2
    le=4,
    description="Number of metric cards (1-4)"  # Updated description
)

# SequentialAtomicRequest (around line 191)
count: int = Field(
    default=4,
    ge=1,  # Changed from ge=2
    le=6,
    description="Number of sequential steps (1-6)"  # Updated description
)
```

**Also update:**
- `text_table_builder/v1.2/app/components/metrics_card.json` - Set `min_instances: 1`
- `text_table_builder/v1.2/app/components/numbered_card.json` - Set `min_instances: 1`

### Phase 2: Add Placeholder Mode to Atomic Generator

**File:** `text_table_builder/v1.2/app/core/components/atomic_generator.py`

**Add parameter to generate():**
```python
async def generate(
    self,
    component_type: str,
    prompt: str,
    count: int,
    grid_width: int,
    grid_height: int,
    items_per_instance: Optional[int] = None,
    context: Optional[AtomicContext] = None,
    variant: Optional[str] = None,
    placeholder_mode: bool = False  # NEW PARAMETER
) -> AtomicResult:
```

**Add placeholder content generation:**
```python
# In generate() method, before Step 4 (LLM generation):
if placeholder_mode:
    # Generate placeholder content without LLM
    contents = self._generate_placeholder_content(
        component_type=component_type,
        slots=dynamic_slots,
        instance_count=count
    )
else:
    # Existing LLM content generation
    contents = await self._generate_content(...)
```

**Add new method `_generate_placeholder_content()`:**
```python
def _generate_placeholder_content(
    self,
    component_type: str,
    slots: Dict[str, SlotSpec],
    instance_count: int
) -> List[GeneratedContent]:
    """Generate placeholder content without LLM."""

    PLACEHOLDER_TEMPLATES = {
        "metrics_card": {
            "metric_number": ["$X.XM", "$XX%", "XX.X", "$XXK"],
            "metric_label": ["Metric Label", "Key Metric", "Performance", "Growth"],
            "metric_description": ["Description of this metric and its significance"]
        },
        "numbered_card": {
            "step_title": ["Step Title", "Phase Name", "Stage", "Action"],
            "step_description": ["Description of this step in the process"]
        },
        "colored_section": {
            "section_heading": ["Section Heading"],
            "bullet_1": ["First key point for this section"],
            "bullet_2": ["Second key point for this section"],
            "bullet_3": ["Third key point for this section"]
        },
        "comparison_column": {
            "column_heading": ["Column Title"],
            "item_1": ["First comparison point"],
            "item_2": ["Second comparison point"],
            "item_3": ["Third comparison point"]
        },
        "sidebar_box": {
            "sidebar_heading": ["Callout Title"],
            "item_1": ["Key highlight or important note"],
            "item_2": ["Additional detail or context"]
        }
    }

    templates = PLACEHOLDER_TEMPLATES.get(component_type, {})
    contents = []

    for i in range(instance_count):
        slot_values = {}
        for slot_id in slots:
            if slot_id in templates:
                values = templates[slot_id]
                slot_values[slot_id] = values[i % len(values)]
            else:
                # Generic placeholder for dynamic slots
                slot_values[slot_id] = f"[{slot_id.replace('_', ' ').title()}]"

        contents.append(GeneratedContent(
            instance_index=i,
            slot_values=slot_values,
            character_counts={k: len(v) for k, v in slot_values.items()}
        ))

    return contents
```

### Phase 3: Update Atomic API Models

**File:** `text_table_builder/v1.2/app/models/atomic_models.py`

**Add to base AtomicComponentRequest:**
```python
class AtomicComponentRequest(BaseModel):
    prompt: str = Field(...)
    gridWidth: int = Field(...)
    gridHeight: int = Field(...)
    context: Optional[AtomicContext] = None
    variant: Optional[str] = None
    placeholder_mode: bool = Field(
        default=False,
        description="If true, generate placeholder content without LLM"
    )  # NEW FIELD
```

### Phase 4: Update Atomic Routes

**File:** `text_table_builder/v1.2/app/api/atomic_routes.py`

**Pass placeholder_mode to generator:**
```python
# In each endpoint handler (METRICS, SEQUENTIAL, etc.):
result = await generator.generate(
    component_type=component_id,
    prompt=request.prompt,
    count=request.count,
    grid_width=request.gridWidth,
    grid_height=request.gridHeight,
    items_per_instance=items_per_instance,
    context=atomic_context,
    variant=request.variant,
    placeholder_mode=request.placeholder_mode  # NEW
)
```

### Phase 5: Update Text-Labs Atomic Client

**File:** `text-labs/backend/services/atomic_client.py`

**Add placeholder_mode parameter:**
```python
async def generate(
    self,
    component_type: ComponentType,
    prompt: str,
    count: int,
    grid_width: int,
    grid_height: int,
    items_per_instance: Optional[int] = None,
    context: Optional[AtomicContext] = None,
    placeholder_mode: bool = False  # NEW
) -> AtomicResponse:

    request_data = {
        "prompt": prompt,
        "count": count,
        "gridWidth": grid_width,
        "gridHeight": grid_height,
        "placeholder_mode": placeholder_mode,  # NEW
    }
```

### Phase 6: Update Text-Labs Chat Routes

**File:** `text-labs/backend/api/chat_routes.py`

**Default to placeholder_mode=True for initial adds:**
```python
# In ActionType.ADD handler (around line 300):
atomic_response = await ac.generate(
    component_type=intent.component_type,
    prompt=intent.content_prompt,
    count=count,
    grid_width=28,
    grid_height=12,
    context=context,
    placeholder_mode=True  # NEW: Don't generate content immediately
)
```

**Add "generate content" action:**
```python
# New action type in orchestrator_models.py:
class ActionType(str, Enum):
    ADD = "add"
    REMOVE = "remove"
    MOVE = "move"
    MODIFY = "modify"
    CLEAR = "clear"
    GENERATE = "generate"  # NEW

# In chat_routes.py, add handler for GENERATE action:
if intent.action == ActionType.GENERATE:
    # Get all elements on canvas
    elements = canvas_state.elements

    # Build rich context from full slide
    full_context = AtomicContext(
        slide_title=canvas_state.slide_title,
        slide_purpose=canvas_state.slide_purpose or "presentation slide",
        key_message=extract_key_message_from_elements(elements),
        audience=canvas_state.audience,
        tone=canvas_state.tone or "professional"
    )

    # Regenerate each element with LLM
    for element in elements:
        atomic_response = await ac.generate(
            component_type=element.component_type,
            prompt=intent.content_prompt or element.original_prompt,
            count=element.instance_count,
            grid_width=element.grid_width,
            grid_height=element.grid_height,
            context=full_context,
            placeholder_mode=False  # NOW generate real content
        )
        # Update element HTML
        element.html = atomic_response.html

    return ChatResponse(
        success=True,
        response_text=f"Generated content for {len(elements)} elements",
        ...
    )
```

---

## Files Summary

| File | Changes |
|------|---------|
| `text_table_builder/v1.2/app/models/atomic_models.py` | Add `placeholder_mode` field, update count constraints |
| `text_table_builder/v1.2/app/core/components/atomic_generator.py` | Add placeholder mode logic + `_generate_placeholder_content()` |
| `text_table_builder/v1.2/app/api/atomic_routes.py` | Pass `placeholder_mode` to generator |
| `text_table_builder/v1.2/app/components/metrics_card.json` | Set `min_instances: 1` |
| `text_table_builder/v1.2/app/components/numbered_card.json` | Set `min_instances: 1` |
| `text-labs/backend/services/atomic_client.py` | Add `placeholder_mode` parameter |
| `text-labs/backend/api/chat_routes.py` | Default to placeholder mode, add GENERATE action |
| `text-labs/backend/models/orchestrator_models.py` | Add `GENERATE` action type |

---

## Testing Plan

```bash
# Test single metric (should work after Phase 1)
curl -X POST "http://localhost:8505/v1.2/atomic/METRICS" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Revenue", "count": 1, "gridWidth": 10, "gridHeight": 8}'

# Test placeholder mode (after Phase 2-4)
curl -X POST "http://localhost:8505/v1.2/atomic/METRICS" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "KPIs", "count": 3, "gridWidth": 28, "gridHeight": 8, "placeholder_mode": true}'

# Test via text-labs (after Phase 5-6)
# 1. "Add 3 metrics" → Should show placeholders
# 2. Arrange elements, set title
# 3. "Generate content" → Should fill with LLM content
```

---

## Success Criteria

- [ ] Can add single metric (count=1)
- [ ] Can add single step (count=1)
- [ ] Elements initially show placeholder content (no LLM delay)
- [ ] "Generate" action fills content using full slide context
- [ ] Faster initial element placement (no waiting for LLM)
