# How Text Service Handles Layout Constraints (L25)

> **Purpose**: Document how Text Service v1.2 understands and respects the spatial constraints of L25 content slides, to help Diagram Service team implement similar constraints for L24 diagram layouts.

---

## Executive Summary

The Text Service **does NOT receive explicit pixel dimensions** from the Layout Architect. Instead, it uses a **character-based constraint system** derived from **golden examples** that were manually tested and validated to fit perfectly in L25 layouts.

**Key Insight**: The constraint system is **pre-calibrated** through manual testing, not dynamically calculated.

---

## The Constraint Architecture

### 1. **Three-Layer System**

```
┌─────────────────────────────────────────────────────┐
│  Layer 1: HTML Template (Spatial Structure)        │
│  - Defines CSS grid/flexbox layout                 │
│  - Fixed font sizes (20px, 35px, etc.)             │
│  - Fixed padding, margins, gaps                    │
│  - This defines HOW MUCH SPACE each element has    │
└─────────────────┬───────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────┐
│  Layer 2: Variant Spec (Content Constraints)       │
│  - Character count requirements per field           │
│  - Baseline: Target character count                │
│  - Min/Max: Acceptable tolerance (±5%)             │
│  - Derived from golden examples                    │
└─────────────────┬───────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────┐
│  Layer 3: LLM Prompt (Enforcement)                  │
│  - "CHARACTER COUNT REQUIREMENTS (STRICT):"         │
│  - Explicitly tells LLM the constraints             │
│  - LLM generates content within those limits        │
└─────────────────────────────────────────────────────┘
```

### 2. **How Character Counts Were Determined**

The character count baselines came from **manual calibration**:

1. **Golden Example Creation**: Designers/developers manually created perfect example slides
2. **Character Measurement**: Counted characters in each element that looked perfect visually
3. **Validation Testing**: Tested content at ±5% of baseline to confirm it still fits
4. **Codification**: Encoded these measurements into JSON variant specs

**Example: Matrix 2×2 Layout**

```json
{
  "character_requirements": {
    "title": {
      "baseline": 30,    // Perfect length from golden example
      "min": 27,         // 30 × 0.95 (still fits)
      "max": 32          // 30 × 1.05 (still fits)
    },
    "description": {
      "baseline": 240,   // Perfect length from golden example
      "min": 228,        // 240 × 0.95
      "max": 252         // 240 × 1.05
    }
  }
}
```

**Why Character Counts Work**:
- Fixed font sizes in template (e.g., `font-size: 20px`)
- Fixed line-height (e.g., `line-height: 1.5`)
- Fixed container dimensions (CSS grid with `1fr` units)
- Therefore: X characters ≈ Y pixels (predictable)

---

## Concrete Example: Matrix 2×2 Layout

### **HTML Template** (`app/templates/matrix/matrix_2x2.html`)

```html
<div style="display: grid;
            grid-template-columns: 1fr 1fr;   /* 2 equal columns */
            grid-template-rows: 1fr 1fr;      /* 2 equal rows */
            gap: 16px;                         /* Space between boxes */
            padding: 0 40px 40px 0;           /* Outer padding */
            height: 100%;                      /* Fill L25 content area */
            background: white;">

  <!-- Box 1: Top Left -->
  <div style="padding: 40px;                  /* Inner padding */
              border-radius: 12px;
              background: #6366f1;            /* Purple */
              display: flex;
              flex-direction: column;
              justify-content: flex-start;
              align-items: flex-start;">

    <h3 style="font-size: 35px;              /* FIXED title font */
               font-weight: 700;
               color: white;
               margin: 0 0 20px 0;">
      {box_1_title}                          /* Placeholder */
    </h3>

    <p style="font-size: 20px;               /* FIXED description font */
              font-weight: 400;
              color: rgba(255,255,255,0.95);
              line-height: 1.5;               /* FIXED line spacing */
              margin: 0;">
      {box_1_description}                    /* Placeholder */
    </p>
  </div>

  <!-- Boxes 2, 3, 4 identical structure -->
</div>
```

**Key Observations**:
- ✅ **Fixed dimensions**: Grid with `1fr 1fr` means each box gets 50% of width
- ✅ **Fixed fonts**: Title always 35px, description always 20px
- ✅ **Fixed spacing**: Padding, margins, line-height all fixed
- ✅ **Therefore**: Space available for text is **deterministic**

### **Variant Spec** (`app/variant_specs/matrix/matrix_2x2.json`)

```json
{
  "variant_id": "matrix_2x2",
  "template_path": "app/templates/matrix/matrix_2x2.html",
  "elements": [
    {
      "element_id": "box_1",
      "element_type": "text_box",
      "required_fields": ["title", "description"],
      "placeholders": {
        "title": "box_1_title",
        "description": "box_1_description"
      },
      "character_requirements": {
        "title": {
          "baseline": 30,      // ~30 chars fits perfectly in 35px font
          "min": 27,
          "max": 32
        },
        "description": {
          "baseline": 240,     // ~240 chars fits in description area
          "min": 228,          // With 20px font, 1.5 line-height
          "max": 252           // This fills ~6-7 lines nicely
        }
      }
    },
    // box_2, box_3, box_4 have identical structure
  ]
}
```

**Key Observations**:
- ✅ Each element has **explicit character limits**
- ✅ Limits are **pre-calculated** to fit the HTML template
- ✅ No dynamic measurement needed at runtime

### **LLM Prompt** (Generated by `element_prompt_builder.py`)

```text
Generate content for slide element: box_1

Element Type: text_box
Required Fields: title, description

CHARACTER COUNT REQUIREMENTS (STRICT):
  - title: 27-32 characters (target: 30)
  - description: 228-252 characters (target: 240)

SLIDE CONTEXT:
This slide presents our core company values to executive stakeholders.
The key message is: Innovation, growth, customer success, team empowerment.

ELEMENT INSTRUCTIONS:
- Title should be concise and descriptive
- Description should explain the concept clearly
- Use professional, business-appropriate language

RESPONSE FORMAT:
Return a JSON object with the required fields. Each field must meet
the character count requirements exactly.

Example format:
{
  "title": "your content here",
  "description": "your content here"
}
```

**Key Observations**:
- ✅ LLM receives **explicit character limits** in the prompt
- ✅ Prompt says "STRICT" to emphasize importance
- ✅ LLM generates content that fits within these bounds

---

## Why This Works for Text Service

### **Advantages of Character-Based Constraints**

1. **Predictable Rendering**: Fixed fonts + fixed spacing = predictable text dimensions
2. **LLM-Friendly**: LLMs are very good at counting characters and generating specific lengths
3. **Pre-Calibrated**: One-time manual calibration, then reusable forever
4. **No Runtime Calculation**: No need to measure or calculate dimensions at runtime
5. **Validation**: Can validate generated content against character limits before returning

### **The Golden Example Process**

```
Step 1: Design Template
├─ Create HTML with fixed fonts, spacing, layout
├─ Test in actual L25 reveal.js slide
└─ Ensure it looks good and fits perfectly

Step 2: Create Golden Example Content
├─ Manually write example content that looks perfect
├─ Count characters for each field
└─ This becomes the "baseline"

Step 3: Test Tolerance
├─ Try content at 95% of baseline (min)
├─ Try content at 105% of baseline (max)
├─ Verify both still look good
└─ If not, adjust baseline or template

Step 4: Codify in JSON
├─ Record baseline, min, max in variant spec
└─ Now LLM can generate content within these bounds
```

---

## How Diagram Service Can Adapt This Pattern

### **Option 1: Character-Based Constraints (If Diagrams Use Fixed Text)**

If diagrams contain text elements (labels, titles, descriptions):

```json
{
  "variant_id": "process_flow_4_steps",
  "layout_id": "L24",
  "template_path": "templates/process_flow_4.svg",
  "elements": [
    {
      "element_id": "step_1",
      "element_type": "process_box",
      "required_fields": ["label", "description"],
      "character_requirements": {
        "label": {
          "baseline": 20,
          "min": 18,
          "max": 22
        },
        "description": {
          "baseline": 80,
          "min": 76,
          "max": 84
        }
      }
    }
  ]
}
```

**Process**:
1. Create SVG template with fixed text sizes
2. Manually test what character counts look good
3. Codify in JSON spec
4. Pass to LLM in prompt

### **Option 2: Structural Constraints (For Complex Diagrams)**

If diagrams are more than just text (shapes, connections, layouts):

```json
{
  "variant_id": "organizational_chart",
  "layout_id": "L24",
  "structural_constraints": {
    "max_hierarchy_levels": 4,      // Max depth
    "max_nodes_per_level": 5,       // Max width
    "max_total_nodes": 15,          // Max complexity
    "node_label_max_chars": 30,     // Text per node
    "connector_style": "orthogonal" // How boxes connect
  }
}
```

**Process**:
1. Define what makes a diagram "fit" in L24
2. Express as structural constraints (counts, limits)
3. Pass to LLM or diagram generation logic
4. Validate output meets constraints

### **Option 3: Template-Based Generation (Like Text Service)**

Most similar to Text Service approach:

```json
{
  "variant_id": "swot_matrix",
  "layout_id": "L24",
  "template_path": "templates/swot.svg",
  "elements": [
    {
      "element_id": "strengths",
      "element_type": "quadrant",
      "required_fields": ["items"],
      "item_constraints": {
        "min_items": 3,
        "max_items": 5,
        "chars_per_item": {
          "baseline": 40,
          "min": 35,
          "max": 45
        }
      }
    }
    // weaknesses, opportunities, threats similar
  ]
}
```

**Process**:
1. Create SVG template with placeholders
2. Define how many items fit in each section
3. Define character limits per item
4. LLM generates content meeting constraints
5. Assemble SVG by replacing placeholders

---

## Key Takeaways for Diagram Service

### **1. Text Service Does NOT Receive Pixel Dimensions**

The Layout Architect does **not** tell Text Service:
- ❌ "You have 800px width × 600px height"
- ❌ "Use this bounding box"
- ❌ "Calculate how much text fits"

Instead:
- ✅ Text Service uses **pre-calibrated character counts**
- ✅ Character counts were derived from manual testing
- ✅ HTML templates have fixed fonts/spacing that make counts predictable

### **2. The Pre-Calibration Approach**

**How to Apply to Diagrams**:

1. **Create Template**: Design your L24 diagram template (SVG/Mermaid/etc.)
2. **Manual Testing**: Create example diagrams that look perfect
3. **Measure Constraints**: Count what fits (nodes, text length, hierarchy depth)
4. **Codify**: Record measurements in JSON specs
5. **Enforce**: Pass constraints to LLM or generation logic
6. **Validate**: Check output meets constraints before returning

### **3. Constraint Types for Diagrams**

Depending on diagram type, you might constrain:

| Diagram Type | Possible Constraints |
|--------------|---------------------|
| **Flowcharts** | Max nodes, max connections, max text per node |
| **Org Charts** | Max hierarchy levels, max width, max nodes total |
| **SWOT Matrix** | Items per quadrant, characters per item |
| **Process Flow** | Max steps, characters per step label |
| **Mind Maps** | Max branches, max depth, nodes per branch |
| **Timelines** | Max events, characters per event |
| **Network Diagrams** | Max nodes, max edges, label length |

### **4. Recommended Approach for Diagram Service**

```python
# 1. Define variant with constraints
variant_spec = {
    "variant_id": "process_flow_5_steps",
    "layout_id": "L24",
    "constraints": {
        "max_steps": 5,
        "step_label_chars": {"min": 15, "max": 25},
        "step_description_chars": {"min": 40, "max": 60},
        "layout_style": "horizontal"
    }
}

# 2. Pass constraints to LLM in prompt
prompt = f"""
Generate a process flow diagram with these constraints:
- Maximum {constraints['max_steps']} steps
- Each step label: {constraints['step_label_chars']['min']}-{constraints['step_label_chars']['max']} characters
- Each description: {constraints['step_description_chars']['min']}-{constraints['step_description_chars']['max']} characters
- Layout: {constraints['layout_style']}

Return JSON with steps array, each step having label and description fields.
"""

# 3. Generate with LLM
response = llm_client.generate(prompt)

# 4. Validate output
validate_constraints(response, variant_spec['constraints'])

# 5. Assemble diagram
diagram_svg = assemble_diagram_template(
    template_path=variant_spec['template_path'],
    content=response
)
```

### **5. Directory Structure (Like Text Service)**

```
diagram_service/
├── templates/              # SVG/Mermaid templates
│   ├── flowchart/
│   │   ├── flow_3_steps.svg
│   │   ├── flow_4_steps.svg
│   │   └── flow_5_steps.svg
│   ├── swot/
│   │   └── swot_matrix.svg
│   └── org_chart/
│       └── hierarchy_3_levels.svg
├── variant_specs/          # JSON constraint definitions
│   ├── flowchart/
│   │   ├── flow_3_steps.json
│   │   ├── flow_4_steps.json
│   │   └── flow_5_steps.json
│   ├── swot/
│   │   └── swot_matrix.json
│   └── variant_index.json
└── core/
    ├── constraint_builder.py    # Builds prompts with constraints
    ├── diagram_generator.py     # Generates diagram content
    ├── template_assembler.py    # Assembles SVG/Mermaid
    └── validator.py             # Validates constraints
```

---

## Example: SWOT Matrix for L24 Layout

### **Step 1: Create Template** (`templates/swot/swot_matrix.svg`)

```svg
<svg width="100%" height="100%" viewBox="0 0 800 600">
  <!-- Top Left: Strengths (Green) -->
  <rect x="0" y="0" width="390" height="290" fill="#10b981" />
  <text x="195" y="30" text-anchor="middle" font-size="24" fill="white">
    STRENGTHS
  </text>
  <text x="20" y="70" font-size="16" fill="white">
    {strengths_items}  <!-- Placeholder -->
  </text>

  <!-- Top Right: Weaknesses (Red) -->
  <rect x="410" y="0" width="390" height="290" fill="#ef4444" />
  <!-- ... similar structure ... -->

  <!-- Bottom Left: Opportunities (Blue) -->
  <!-- Bottom Right: Threats (Orange) -->
</svg>
```

### **Step 2: Test & Measure**

Manually create perfect example:
- **Strengths**: 4 items, each 35-45 characters
- **Weaknesses**: 4 items, each 35-45 characters
- **Opportunities**: 4 items, each 35-45 characters
- **Threats**: 4 items, each 35-45 characters

Test with font-size 16px, see what fits nicely.

### **Step 3: Codify** (`variant_specs/swot/swot_matrix.json`)

```json
{
  "variant_id": "swot_matrix",
  "layout_id": "L24",
  "template_path": "templates/swot/swot_matrix.svg",
  "elements": [
    {
      "element_id": "strengths",
      "element_type": "quadrant",
      "required_fields": ["items"],
      "item_constraints": {
        "min_items": 3,
        "max_items": 5,
        "chars_per_item": {
          "baseline": 40,
          "min": 35,
          "max": 45
        }
      }
    },
    {
      "element_id": "weaknesses",
      "element_type": "quadrant",
      "required_fields": ["items"],
      "item_constraints": {
        "min_items": 3,
        "max_items": 5,
        "chars_per_item": {
          "baseline": 40,
          "min": 35,
          "max": 45
        }
      }
    }
    // opportunities, threats similar
  ]
}
```

### **Step 4: Generate with LLM**

```python
prompt = f"""
Generate SWOT analysis content for a business strategy presentation.

CONSTRAINTS (STRICT):
- Strengths: 3-5 items, each 35-45 characters
- Weaknesses: 3-5 items, each 35-45 characters
- Opportunities: 3-5 items, each 35-45 characters
- Threats: 3-5 items, each 35-45 characters

Return JSON:
{{
  "strengths": ["item1", "item2", "item3"],
  "weaknesses": ["item1", "item2", "item3"],
  "opportunities": ["item1", "item2", "item3"],
  "threats": ["item1", "item2", "item3"]
}}
"""

response = llm_client.generate(prompt)
```

### **Step 5: Validate & Assemble**

```python
# Validate
for quadrant, items in response.items():
    assert 3 <= len(items) <= 5, f"{quadrant} has wrong item count"
    for item in items:
        assert 35 <= len(item) <= 45, f"{quadrant} item wrong length"

# Assemble
svg = template_assembler.assemble(
    template_path="templates/swot/swot_matrix.svg",
    content_map={
        "strengths_items": format_as_svg_text(response['strengths']),
        "weaknesses_items": format_as_svg_text(response['weaknesses']),
        "opportunities_items": format_as_svg_text(response['opportunities']),
        "threats_items": format_as_svg_text(response['threats'])
    }
)
```

---

## Summary

**Text Service's Layout Constraint Strategy**:

1. ✅ **Pre-calibration**: Manually test and measure what fits in L25
2. ✅ **Character counts**: Express spatial constraints as character limits
3. ✅ **Fixed templates**: HTML with fixed fonts/spacing makes counts predictable
4. ✅ **LLM enforcement**: Pass character limits explicitly in prompts
5. ✅ **Validation**: Check generated content meets constraints
6. ✅ **Assembly**: Replace template placeholders with generated content

**For Diagram Service (L24)**:

1. ✅ Adapt the **same pattern** using diagram-appropriate constraints
2. ✅ Express constraints as **structural limits** (node counts, text lengths)
3. ✅ Use **templates** (SVG/Mermaid) with placeholders
4. ✅ Pass **explicit constraints** to LLM or generation logic
5. ✅ **Validate** output before returning
6. ✅ **Assemble** diagram by replacing placeholders

**The key insight**: Text Service does NOT receive dynamic layout dimensions. It uses **pre-calibrated constraints** encoded in JSON that were derived from manual testing. Diagram Service can follow the exact same pattern.

---

**Document Version**: 1.0
**Created**: December 2025
**For**: Diagram Service Team
**Source**: Text & Table Builder v1.2 Architecture Analysis
