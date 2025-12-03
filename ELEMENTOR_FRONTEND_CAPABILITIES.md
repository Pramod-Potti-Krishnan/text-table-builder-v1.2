# Elementor Frontend Capabilities Document

**Version**: 1.0.0
**Last Updated**: December 3, 2025
**Status**: Single Source of Truth
**Owner**: Backend Services Team

---

## Overview

This document defines the complete capabilities available to the Frontend for each element type in the Deckster presentation builder. The Frontend communicates **exclusively with Elementor** (the orchestrator), which routes requests to the appropriate backend services.

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────────────────┐
│    Frontend     │ ───▶ │    Elementor    │ ───▶ │     Backend Services        │
│  (User Input)   │      │  (Orchestrator) │      │  (Analytics, Diagrams, etc) │
└─────────────────┘      └─────────────────┘      └─────────────────────────────┘
```

**Important**: The Frontend should use this document to:
1. Build UI configuration panels for each element type
2. Validate user inputs before sending to Elementor
3. Display appropriate options based on element capabilities
4. Handle responses and error states correctly

---

## Table of Contents

1. [Common Concepts](#1-common-concepts)
2. [Analytics Element](#2-analytics-element)
3. [Diagrams Element](#3-diagrams-element)
4. [Infographic Element](#4-infographic-element)
5. [Image Element](#5-image-element)
6. [Text & Table Element](#6-text--table-element)
7. [Error Handling](#7-error-handling)
8. [Appendix: Quick Reference](#8-appendix-quick-reference)

---

## 1. Common Concepts

### 1.1 Grid System

All elements use a **12x8 grid system** for sizing:

| Property | Range | Description |
|----------|-------|-------------|
| `gridWidth` | 1-12 | Horizontal units (each ~80px at 960px slide) |
| `gridHeight` | 1-8 | Vertical units (each ~90px at 720px slide) |

**Grid Area Tiers**:
- **Small**: area ≤ 16 (e.g., 4x4)
- **Medium**: area ≤ 48 (e.g., 8x6)
- **Large**: area > 48 (e.g., 12x6)

### 1.2 Common Request Fields

All element generation requests include:

```typescript
{
  presentationId: string      // UUID - Required
  slideId: string             // UUID - Required
  elementId: string           // UUID - Required
  constraints: {
    gridWidth: number         // 1-12
    gridHeight: number        // 1-8
  }
  context?: {
    presentationTitle: string
    presentationTheme?: string
    slideIndex: number
    slideCount: number
    slideTitle?: string
  }
}
```

### 1.3 Common Response Structure

```typescript
{
  success: boolean
  data?: {
    generationId: string      // UUID for tracking/regeneration
    content: { ... }          // Element-specific content
    metadata: { ... }         // Generation metadata
  }
  error?: {
    code: string              // Error code
    message: string           // Human-readable message
    retryable: boolean        // Can retry this request?
    suggestion?: string       // How to fix
  }
}
```

---

## 2. Analytics Element

**Backend Service**: Analytics Microservice v3.1
**Capabilities**: Chart generation with AI-powered data synthesis and insights

### 2.1 Supported Chart Types

#### Chart.js Charts (14 types)

| Chart Type | ID | Min Points | Max Points | Best For |
|------------|-----|------------|------------|----------|
| Line | `line` | 2 | 50 | Trends over time |
| Area | `area` | 2 | 50 | Cumulative trends |
| Stacked Area | `area_stacked` | 2 | 50 | Part-to-whole over time |
| Vertical Bar | `bar_vertical` | 2 | 20 | Category comparison |
| Horizontal Bar | `bar_horizontal` | 2 | 20 | Ranking, long labels |
| Grouped Bar | `bar_grouped` | 2 | 15 | Multi-series comparison |
| Stacked Bar | `bar_stacked` | 2 | 15 | Part-to-whole by category |
| Pie | `pie` | 2 | 8 | Simple composition |
| Doughnut | `doughnut` | 2 | 8 | Composition with center stat |
| Polar Area | `polar_area` | 3 | 8 | Radial composition |
| Scatter | `scatter` | 3 | 100 | Correlation analysis |
| Bubble | `bubble` | 3 | 50 | 3-variable correlation |
| Radar | `radar` | 3 | 8 | Multi-metric comparison |
| Waterfall | `waterfall` | 3 | 15 | Financial flows |

#### D3.js Advanced Charts (4 types)

| Chart Type | ID | Description |
|------------|-----|-------------|
| Treemap | `d3_treemap` | Hierarchical data visualization |
| Sunburst | `d3_sunburst` | Radial hierarchical diagram |
| USA Choropleth | `d3_choropleth_usa` | Geographic map of US states |
| Sankey | `d3_sankey` | Flow diagram for processes |

### 2.2 Frontend Configuration Options

```typescript
interface AnalyticsConfig {
  // Chart Selection
  chartType: ChartTypeId          // Required - from chart types above

  // Data Source Toggle
  useSyntheticData: boolean       // Default: false
                                  // true = AI generates realistic data
                                  // false = use provided data

  // User-Provided Data (when useSyntheticData = false)
  data?: {
    label: string                 // Category label
    value: number                 // Numeric value
    description?: string          // Optional tooltip text
  }[]

  // Narrative Description
  narrative: string               // Required - describes what to show
                                  // Max: 2000 characters
                                  // Example: "Show quarterly revenue growth for 2024"

  // Synthetic Data Options (when useSyntheticData = true)
  syntheticOptions?: {
    scenario?: SyntheticScenario  // Business pattern to generate
    numPoints?: number            // 1-50, auto-determined if not set
  }
}

// Synthetic Data Scenarios
type SyntheticScenario =
  | 'revenue_growth'        // Upward trending
  | 'revenue_decline'       // Downward trending
  | 'seasonality'           // Cyclical patterns
  | 'market_volatility'     // High variance
  | 'stable_performance'    // Consistent metrics
  | 'regional_distribution' // Geographic spread
  | 'market_share'          // Competitive analysis
  | 'customer_segments'     // Demographics
  | 'product_comparison'    // Feature comparison
  | 'budget_allocation'     // Resource distribution
  | 'performance_metrics'   // KPI dashboard
  | 'growth_trajectory'     // Projection patterns
  | 'cost_breakdown'        // Expense analysis
  | 'conversion_funnel'     // Stage-based metrics
  | 'engagement_metrics'    // User activity
```

### 2.3 UI Controls to Display

| Control | Type | When to Show | Options/Range |
|---------|------|--------------|---------------|
| Chart Type Selector | Dropdown with icons | Always | All 18 chart types |
| Synthetic Data Toggle | Switch | Always | On/Off (default: Off) |
| Narrative Input | Textarea | Always | Max 2000 chars |
| Data Editor | Table editor | When synthetic=false | Label + Value rows |
| Scenario Selector | Dropdown | When synthetic=true | 15 scenarios |
| Data Points Count | Slider | When synthetic=true | 1-50 (chart-specific max) |

### 2.4 Request Format (to Elementor)

```typescript
{
  elementType: 'analytics'
  presentationId: string
  slideId: string
  elementId: string
  constraints: { gridWidth: number, gridHeight: number }
  config: {
    chartType: string
    narrative: string
    useSyntheticData: boolean
    data?: { label: string, value: number }[]
    syntheticOptions?: {
      scenario?: string
      numPoints?: number
    }
  }
  context: { ... }
}
```

### 2.5 Response Format

```typescript
{
  success: true
  data: {
    generationId: string
    content: {
      html: string              // Complete chart HTML (Chart.js/D3.js)
      observations?: string     // AI-generated insights HTML
    }
    metadata: {
      chartType: string
      syntheticDataUsed: boolean
      dataSource: 'synthetic' | 'provided'
      dataPointCount: number
      generationTimeMs: number
    }
    editInfo: {
      editableData: boolean     // Can edit data points inline
      dataSchema: { ... }       // Schema for inline editing
    }
  }
}
```

### 2.6 Validation Rules

| Field | Rule |
|-------|------|
| `chartType` | Must be one of 18 supported types |
| `narrative` | Required, 1-2000 characters |
| `data` | Required if `useSyntheticData=false`, 1-50 points |
| `data[].value` | Must be finite number (no NaN, Infinity) |
| `numPoints` | 1-50, respects chart-specific limits |
| `gridWidth` | 4-12 recommended for charts |
| `gridHeight` | 3-8 recommended for charts |

---

## 3. Diagrams Element

**Backend Service**: Diagram Generator v3.0
**Capabilities**: SVG diagrams, flowcharts, and visual structures

### 3.1 Supported Diagram Types

#### SVG Template Diagrams (21 types) - Fastest

| Category | Types | Variants |
|----------|-------|----------|
| Cycle | `cycle_*` | 3_step, 4_step, 5_step |
| Pyramid | `pyramid_*` | 3_level, 4_level, 5_level |
| Venn | `venn_*` | 2_circle, 3_circle |
| Honeycomb | `honeycomb_*` | 3_cell, 5_cell, 7_cell |
| Hub & Spoke | `hub_spoke_*` | 4, 6, 8 |
| Matrix | `matrix_*` | 2x2, 3x3 |
| Funnel | `funnel_*` | 3_stage, 4_stage, 5_stage |
| Timeline | `timeline_*` | 3_event, 5_event |

#### Mermaid Diagrams (7 types) - AI-Powered

| Type | ID | Description |
|------|-----|-------------|
| Flowchart | `flowchart` | Process flows, decision trees |
| Sequence | `sequence` | Interaction/sequence diagrams |
| Gantt | `gantt` | Project timelines |
| State | `state` | State machines |
| ER Diagram | `erDiagram` | Entity relationships |
| User Journey | `journey` | User experience maps |
| Quadrant | `quadrantChart` | 2x2 analysis matrices |

### 3.2 Frontend Configuration Options

```typescript
interface DiagramConfig {
  // Diagram Type Selection
  diagramType: DiagramTypeId      // Required

  // Content Description
  prompt: string                  // Required - what to visualize
                                  // Max: 2000 characters

  // Layout Options
  layout?: {
    direction?: 'TB' | 'BT' | 'LR' | 'RL'  // Top-Bottom, etc.
    theme?: 'default' | 'dark' | 'forest' | 'neutral'
  }

  // Complexity Control
  options?: {
    complexity?: 'simple' | 'moderate' | 'detailed'
    maxNodes?: number             // Limit node count
    includeNotes?: boolean        // Add annotations
    includeSubgraphs?: boolean    // Group related nodes
  }

  // Theming
  theme?: {
    primaryColor?: string         // Hex color
    secondaryColor?: string
    backgroundColor?: string
    textColor?: string
    style?: 'professional' | 'playful' | 'minimal' | 'bold'
  }
}
```

### 3.3 UI Controls to Display

| Control | Type | When to Show | Options |
|---------|------|--------------|---------|
| Diagram Type | Visual grid selector | Always | 28 types with previews |
| Prompt Input | Textarea | Always | Max 2000 chars |
| Direction | Segmented control | For flowchart, sequence | TB, BT, LR, RL |
| Theme Preset | Dropdown | Always | default, dark, forest, neutral |
| Complexity | Slider/Radio | Always | Simple, Moderate, Detailed |
| Max Nodes | Number input | Advanced panel | 3-30 based on grid size |
| Color Picker | Color input | Advanced panel | Primary, Secondary |

### 3.4 Node Limits by Grid Size

| Grid Area | Complexity: Simple | Moderate | Detailed |
|-----------|-------------------|----------|----------|
| Small (≤16) | 3-4 nodes | 5-6 nodes | 7-8 nodes |
| Medium (≤48) | 6-8 nodes | 10-12 nodes | 14-16 nodes |
| Large (>48) | 10-15 nodes | 18-22 nodes | 25-30 nodes |

### 3.5 Request Format (to Elementor)

```typescript
{
  elementType: 'diagram'
  presentationId: string
  slideId: string
  elementId: string
  constraints: { gridWidth: number, gridHeight: number }
  config: {
    diagramType: string
    prompt: string
    layout?: { direction?: string, theme?: string }
    options?: { complexity?: string, maxNodes?: number }
    theme?: { primaryColor?: string, ... }
  }
  context: { ... }
}
```

### 3.6 Response Format

```typescript
{
  success: true
  data: {
    generationId: string
    content: {
      svg: string                 // SVG markup
      mermaidCode?: string        // Source Mermaid code (for Mermaid types)
    }
    metadata: {
      type: string
      direction: string
      nodeCount: number
      edgeCount: number
      generationMethod: 'svg_template' | 'mermaid' | 'python_chart'
      generationTimeMs: number
    }
    editInfo: {
      editableNodes: boolean
      editableEdges: boolean
      canAddNodes: boolean
      canReorder: boolean
    }
  }
}
```

### 3.7 Validation Rules

| Field | Rule |
|-------|------|
| `diagramType` | Must be one of 28 supported types |
| `prompt` | Required, 1-2000 characters |
| `direction` | TB, BT, LR, RL only |
| `complexity` | simple, moderate, detailed |
| `maxNodes` | 3-30, auto-capped by grid size |
| `colors` | Valid hex format (#RRGGBB) |

---

## 4. Infographic Element

**Backend Service**: Illustrator v1.0
**Capabilities**: Visual infographics with LLM-generated content

### 4.1 Supported Infographic Types

#### Template-Based (HTML Output) - 6 types

| Type | ID | Variants | Best For |
|------|-----|----------|----------|
| Pyramid | `pyramid` | 3-6 levels | Hierarchies, priorities |
| Funnel | `funnel` | 3-5 stages | Conversion, filtering |
| Concentric Circles | `concentric_circles` | 3-5 rings | Layered concepts |
| Concept Spread | `concept_spread` | 6 hexagons | Related concepts |
| Venn | `venn` | 2-4 circles | Overlapping ideas |
| Comparison | `comparison` | 2-4 columns | Side-by-side |

#### Dynamic SVG (AI-Generated) - 8 types

| Type | ID | Description |
|------|-----|-------------|
| Timeline | `timeline` | Chronological events |
| Process | `process` | Step-by-step flows |
| Statistics | `statistics` | Numbers & data viz |
| Hierarchy | `hierarchy` | Org charts, trees |
| List | `list` | Visual numbered lists |
| Cycle | `cycle` | Circular processes |
| Matrix | `matrix` | Grid-based layouts |
| Roadmap | `roadmap` | Timeline-based plans |

### 4.2 Frontend Configuration Options

```typescript
interface InfographicConfig {
  // Type Selection
  infographicType: InfographicTypeId   // Required

  // Content Description
  prompt: string                       // Required - topic/content
                                       // Example: "Benefits of cloud computing"

  // Item Count (type-specific)
  itemCount?: number                   // Varies by type

  // Style Options
  styleOptions?: {
    colorScheme?: 'professional' | 'vibrant' | 'pastel' | 'bold' | 'minimal'
    iconStyle?: 'emoji' | 'outlined' | 'filled' | 'none'
    density?: 'compact' | 'balanced' | 'spacious'
    orientation?: 'horizontal' | 'vertical' | 'auto'
    customColors?: string[]            // Up to 6 hex colors
  }

  // Content Options
  contentOptions?: {
    includeIcons?: boolean             // Default: true
    includeDescriptions?: boolean      // Default: true
    includeNumbers?: boolean           // Default: false
    maxTextLength?: number             // Per-item character limit
  }

  // Tone & Audience
  tone?: 'professional' | 'casual' | 'academic' | 'playful'
  audience?: 'general' | 'technical' | 'executive' | 'students'
}
```

### 4.3 Item Count Limits by Type

| Type | Min | Max | Default |
|------|-----|-----|---------|
| Pyramid | 3 | 6 | 4 |
| Funnel | 3 | 5 | 4 |
| Concentric Circles | 3 | 5 | 4 |
| Concept Spread | 6 | 6 | 6 (fixed) |
| Venn | 2 | 4 | 3 |
| Comparison | 2 | 4 | 2 |
| Timeline | 3 | 8 | 5 |
| Process | 3 | 8 | 5 |
| List | 3 | 10 | 5 |
| Others | 3 | 8 | 5 |

### 4.4 UI Controls to Display

| Control | Type | When to Show | Options |
|---------|------|--------------|---------|
| Type Selector | Visual grid | Always | 14 types with previews |
| Prompt Input | Textarea | Always | Topic description |
| Item Count | Stepper/Slider | Always | Type-specific range |
| Color Scheme | Dropdown | Always | 5 presets |
| Icon Style | Segmented | Always | emoji, outlined, filled, none |
| Density | Radio | Always | compact, balanced, spacious |
| Include Icons | Toggle | Advanced | On/Off |
| Include Descriptions | Toggle | Advanced | On/Off |
| Tone | Dropdown | Advanced | 4 options |
| Audience | Dropdown | Advanced | 4 options |

### 4.5 Request Format (to Elementor)

```typescript
{
  elementType: 'infographic'
  presentationId: string
  slideId: string
  elementId: string
  constraints: { gridWidth: number, gridHeight: number }
  config: {
    infographicType: string
    prompt: string
    itemCount?: number
    styleOptions?: { ... }
    contentOptions?: { ... }
    tone?: string
    audience?: string
  }
  context: { ... }
}
```

### 4.6 Response Format

```typescript
{
  success: true
  data: {
    generationId: string
    content: {
      html: string                    // L25-compatible HTML
      svg?: string                    // For dynamic SVG types
    }
    metadata: {
      type: string
      itemCount: number
      dimensions: { width: number, height: number }
      colorPalette: string[]
      generationMethod: 'template' | 'dynamic_svg'
      generationTimeMs: number
    }
    generatedContent: {               // LLM-generated text
      items: {
        label: string
        description?: string
      }[]
    }
    editInfo: {
      editableItems: boolean
      reorderableItems: boolean
      addableItems: boolean
      maxItems: number
      minItems: number
    }
  }
}
```

### 4.7 Validation Rules

| Field | Rule |
|-------|------|
| `infographicType` | Must be one of 14 supported types |
| `prompt` | Required, 1-1000 characters |
| `itemCount` | Within type-specific min/max |
| `customColors` | Valid hex, max 6 colors |
| `gridWidth` | Min 4 for most types |
| `gridHeight` | Min 3 for most types |

---

## 5. Image Element

**Backend Service**: Image Builder v2.0
**Capabilities**: AI-generated images via Vertex AI Imagen

### 5.1 Supported Styles

| Style | ID | Description | Best For |
|-------|-----|-------------|----------|
| Realistic | `realistic` | Photorealistic rendering | Business, corporate |
| Illustration | `illustration` | Digital art, vector style | Creative, educational |
| Abstract | `abstract` | Artistic interpretation | Conceptual, artistic |
| Minimal | `minimal` | Clean, simple design | Tech, startup, icons |
| Photo | `photo` | Stock photography style | Marketing, corporate |

### 5.2 Supported Aspect Ratios

| Ratio | ID | Use Case |
|-------|-----|----------|
| 16:9 | `16:9` | Widescreen, presentations (default) |
| 4:3 | `4:3` | Traditional slides |
| 1:1 | `1:1` | Square, social media |
| 9:16 | `9:16` | Mobile, portrait |
| 3:4 | `3:4` | Portrait photos |
| Custom | `W:H` | Any custom ratio (intelligent crop) |

### 5.3 Quality Tiers & Credits

| Quality | ID | Resolution | Credits | Speed |
|---------|-----|------------|---------|-------|
| Draft | `draft` | 512px | 1 | Fastest |
| Standard | `standard` | 1024px | 2 | Normal |
| High | `high` | 1536px | 4 | Slower |
| Ultra | `ultra` | 2048px | 8 | Slowest |

**Default Credits**: 100 per presentation

### 5.4 Frontend Configuration Options

```typescript
interface ImageConfig {
  // Content Description
  prompt: string                      // Required - image description
                                      // 10-1000 characters

  // Style Selection
  style: ImageStyle                   // Required

  // Aspect Ratio
  aspectRatio?: string                // Default: '16:9'

  // Quality Tier
  quality?: 'draft' | 'standard' | 'high' | 'ultra'  // Default: 'standard'

  // Advanced Options
  options?: {
    negativePrompt?: string           // What to avoid
    seed?: number                     // For reproducibility
    guidanceScale?: number            // 1.0-20.0 (default: 7.5)
    colorScheme?: 'warm' | 'cool' | 'neutral' | 'vibrant'
    lighting?: 'natural' | 'studio' | 'dramatic' | 'soft'
    removeBackground?: boolean        // Transparent PNG
  }
}
```

### 5.5 UI Controls to Display

| Control | Type | When to Show | Options |
|---------|------|--------------|---------|
| Prompt Input | Textarea | Always | 10-1000 chars |
| Style Selector | Visual cards | Always | 5 styles with previews |
| Aspect Ratio | Dropdown/Visual | Always | 6 presets + custom |
| Quality | Radio/Dropdown | Always | 4 tiers with credit cost |
| Credit Balance | Display | Always | Show remaining credits |
| Negative Prompt | Textarea | Advanced panel | Optional |
| Color Scheme | Dropdown | Advanced | 4 options |
| Lighting | Dropdown | Advanced | 4 options |
| Remove Background | Toggle | Advanced | On/Off |

### 5.6 Request Format (to Elementor)

```typescript
{
  elementType: 'image'
  presentationId: string
  slideId: string
  elementId: string
  constraints: { gridWidth: number, gridHeight: number }
  config: {
    prompt: string
    style: string
    aspectRatio?: string
    quality?: string
    options?: {
      negativePrompt?: string
      colorScheme?: string
      lighting?: string
      removeBackground?: boolean
    }
  }
  context: {
    presentationTitle: string
    brandColors?: string[]            // For style consistency
  }
}
```

### 5.7 Response Format

```typescript
{
  success: true
  data: {
    generationId: string
    content: {
      url: string                     // Full resolution image URL
      thumbnailUrl: string            // 256px thumbnail
      transparentUrl?: string         // If background removed
    }
    metadata: {
      style: string
      aspectRatio: string
      dimensions: { width: number, height: number }
      format: 'png' | 'jpeg' | 'webp'
      sizeBytes: number
      generationTimeMs: number
    }
    usage: {
      creditsUsed: number
      creditsRemaining: number
    }
  }
}
```

### 5.8 Validation Rules

| Field | Rule |
|-------|------|
| `prompt` | Required, 10-1000 characters |
| `style` | Must be one of 5 supported styles |
| `aspectRatio` | Valid format W:H (e.g., "16:9", "3:2") |
| `quality` | draft, standard, high, ultra |
| `guidanceScale` | 1.0-20.0 |
| Credits | Must have sufficient balance |

### 5.9 Credit Display Guidelines

Show users:
- Current credit balance
- Cost of selected quality tier
- Warning when balance < 10 credits
- Option to generate at lower quality if insufficient

---

## 6. Text & Table Element

**Backend Service**: Text & Table Builder v1.2
**Capabilities**: AI-generated text content and structured tables

### 6.1 Text Operations

#### 6.1.1 Text Generation

Generate new text content from a prompt.

```typescript
interface TextGenerateConfig {
  // Content Description
  prompt: string                      // Required - what to write
                                      // Example: "Write 3 bullet points about AI benefits"

  // Format Options
  options?: {
    tone?: TextTone                   // Writing style
    format?: TextFormat               // Output structure
    bulletStyle?: BulletStyle         // For bullet lists
    language?: string                 // ISO code (default: 'en')
    includeEmoji?: boolean            // Default: false
  }
}

type TextTone =
  | 'professional'    // Default - business appropriate
  | 'conversational'  // Friendly, approachable
  | 'academic'        // Formal, scholarly
  | 'persuasive'      // Compelling, action-oriented
  | 'casual'          // Relaxed, informal
  | 'technical'       // Precise, specialized

type TextFormat =
  | 'paragraph'       // Default - flowing text
  | 'bullets'         // Unordered list
  | 'numbered'        // Ordered list
  | 'headline'        // Short, impactful
  | 'quote'           // Quotation style
  | 'mixed'           // Paragraph with bullets

type BulletStyle =
  | 'disc'            // Default - filled circle
  | 'circle'          // Empty circle
  | 'square'          // Square marker
  | 'dash'            // Dash/hyphen
  | 'arrow'           // Arrow marker
  | 'check'           // Checkmark
```

#### 6.1.2 Text Transformation

Transform existing text content.

```typescript
interface TextTransformConfig {
  sourceContent: string               // Existing HTML content
  transformation: TextTransformation
}

type TextTransformation =
  | 'expand'          // Add more detail
  | 'condense'        // Shorten, keep key points
  | 'simplify'        // Simpler language
  | 'formalize'       // More professional
  | 'casualize'       // More conversational
  | 'bulletize'       // Convert to bullets
  | 'paragraphize'    // Convert bullets to paragraphs
  | 'rephrase'        // Rewrite differently
  | 'proofread'       // Fix grammar/spelling
  | 'translate'       // Language translation
```

#### 6.1.3 Text Autofit

Fit text to element dimensions.

```typescript
interface TextAutofitConfig {
  content: string                     // Current HTML content
  strategy: AutofitStrategy
  preserveFormatting?: boolean        // Default: true
}

type AutofitStrategy =
  | 'reduce_font'     // Suggest smaller font
  | 'truncate'        // Cut with ellipsis
  | 'smart_condense'  // AI-powered shortening (recommended)
  | 'overflow'        // Allow overflow (no change)
```

### 6.2 Table Operations

#### 6.2.1 Table Generation

Generate a structured table from a prompt.

```typescript
interface TableGenerateConfig {
  prompt: string                      // Required - table description
                                      // Example: "Q3 vs Q4 revenue by region"

  // Structure Options (optional - auto-calculated from grid)
  structure?: {
    columns?: number                  // 1-10
    rows?: number                     // 1-20
    hasHeader?: boolean               // Default: true
    hasFooter?: boolean               // Default: false
  }

  // Style Options
  style?: {
    preset?: TableStylePreset
    headerStyle?: 'bold' | 'highlight' | 'minimal'
    alternatingRows?: boolean         // Default: true
    borderStyle?: 'none' | 'light' | 'medium' | 'heavy'
    alignment?: 'left' | 'center' | 'right' | 'auto'
  }

  // Data Options
  dataOptions?: {
    includeUnits?: boolean            // Add units to numbers
    formatNumbers?: boolean           // Apply formatting (default: true)
    currency?: string                 // Currency code (e.g., 'USD')
    dateFormat?: string               // Date format pattern
  }

  // Seed Data (optional)
  seedData?: Record<string, any>      // Base data for table
}

type TableStylePreset =
  | 'minimal'         // Clean, borderless
  | 'bordered'        // All borders visible
  | 'striped'         // Alternating row colors
  | 'modern'          // Contemporary gradients
  | 'professional'    // Default - corporate blue
  | 'colorful'        // Vibrant pink/purple
```

#### 6.2.2 Table Transformation

Modify table structure.

```typescript
interface TableTransformConfig {
  sourceTable: string                 // Existing table HTML
  transformation: TableTransformation
  options?: {
    position?: number                 // For add_column/add_row
    content?: string                  // Content description
    index?: number                    // For remove operations
    sortColumn?: number               // For sort
    sortDirection?: 'asc' | 'desc'
    summaryType?: 'totals' | 'averages' | 'counts'
    expandPrompt?: string             // For expand operation
  }
}

type TableTransformation =
  | 'add_column'      // Add new column
  | 'add_row'         // Add new row
  | 'remove_column'   // Remove column at index
  | 'remove_row'      // Remove row at index
  | 'sort'            // Sort by column
  | 'summarize'       // Add totals/averages row
  | 'transpose'       // Swap rows and columns
  | 'expand'          // Add more rows with similar data
  | 'merge_cells'     // Merge adjacent same-value cells
  | 'split_column'    // Split column into multiple
```

#### 6.2.3 Table Analysis

Get insights from table data.

```typescript
interface TableAnalyzeConfig {
  sourceTable: string                 // Table HTML to analyze
  analysisType: TableAnalysisType
}

type TableAnalysisType =
  | 'summary'         // Key statistics and takeaways
  | 'trends'          // Patterns, correlations
  | 'outliers'        // Unusual values
  | 'visualization'   // Recommended chart type
```

### 6.3 Character Limits by Grid Size

| Grid Size | Max Characters | Recommended Format |
|-----------|----------------|-------------------|
| 3x2 | ~150 | Headline or 2 bullets |
| 4x3 | ~300 | Short paragraph or 3 bullets |
| 6x4 | ~600 | Paragraph with bullets |
| 8x5 | ~1000 | Multi-paragraph |
| 12x6 | ~1800 | Detailed content |

### 6.4 UI Controls to Display

#### For Text Generation:
| Control | Type | When to Show |
|---------|------|--------------|
| Prompt Input | Textarea | Always |
| Tone Selector | Dropdown | Always |
| Format Selector | Segmented | Always |
| Bullet Style | Dropdown | When format=bullets |
| Include Emoji | Toggle | Advanced |

#### For Text Transform:
| Control | Type | When to Show |
|---------|------|--------------|
| Transformation | Button group | Always |
| Preview | Side-by-side | After selection |

#### For Table Generation:
| Control | Type | When to Show |
|---------|------|--------------|
| Prompt Input | Textarea | Always |
| Style Preset | Visual selector | Always |
| Column/Row Count | Steppers | Advanced |
| Alternating Rows | Toggle | Style panel |
| Header Style | Dropdown | Style panel |

#### For Table Transform:
| Control | Type | When to Show |
|---------|------|--------------|
| Transformation | Button group | Always |
| Position/Index | Number input | For add/remove |
| Sort Options | Dropdowns | For sort |

### 6.5 Request Format (to Elementor)

```typescript
// Text Generation
{
  elementType: 'text'
  operation: 'generate'
  presentationId: string
  slideId: string
  elementId: string
  constraints: { gridWidth: number, gridHeight: number }
  config: {
    prompt: string
    options?: { tone?: string, format?: string, ... }
  }
  context: { ... }
}

// Text Transform
{
  elementType: 'text'
  operation: 'transform'
  ...
  config: {
    sourceContent: string
    transformation: string
  }
}

// Table Generation
{
  elementType: 'table'
  operation: 'generate'
  ...
  config: {
    prompt: string
    structure?: { ... }
    style?: { ... }
    dataOptions?: { ... }
  }
}

// Table Transform
{
  elementType: 'table'
  operation: 'transform'
  ...
  config: {
    sourceTable: string
    transformation: string
    options?: { ... }
  }
}
```

### 6.6 Response Format

```typescript
// Text Response
{
  success: true
  data: {
    generationId: string
    content: {
      html: string                    // HTML with inline CSS
    }
    metadata: {
      characterCount: number
      wordCount: number
      estimatedReadTime: number       // seconds
      format: string
      tone: string
    }
    suggestions?: {
      alternativeVersions: string[]   // Up to 3 alternatives
      expandable: boolean
      reducible: boolean
    }
  }
}

// Table Response
{
  success: true
  data: {
    generationId: string
    content: {
      html: string                    // Complete table HTML
    }
    metadata: {
      rowCount: number
      columnCount: number
      hasHeader: boolean
      hasFooter: boolean
      columnTypes: string[]           // 'text', 'numeric', 'date', 'mixed'
      hasNumericData: boolean
      hasDateData: boolean
    }
    editInfo: {
      editableCells: boolean
      suggestedColumnWidths: number[]
    }
  }
}

// Table Analysis Response
{
  success: true
  data: {
    analysisId: string
    summary: string                   // Natural language summary
    insights: [{
      type: string                    // trend, comparison, highlight, outlier
      title: string
      description: string
      confidence: number              // 0.0-1.0
    }]
    statistics?: { ... }              // Column statistics
    recommendations: {
      suggestedChartType: string
      suggestedHighlights: number[]
      suggestedSorting: { column: number, direction: string }
    }
  }
}
```

### 6.7 Validation Rules

| Field | Rule |
|-------|------|
| `prompt` | Required, 1-2000 characters |
| `sourceContent` | Required for transform operations |
| `tone` | One of 6 supported tones |
| `format` | One of 6 supported formats |
| `transformation` | One of 10 text or 10 table transformations |
| `structure.columns` | 1-10 |
| `structure.rows` | 1-20 |
| `analysisType` | summary, trends, outliers, visualization |

---

## 7. Error Handling

### 7.1 Common Error Codes

| Code | Description | Retryable | Frontend Action |
|------|-------------|-----------|-----------------|
| `INVALID_PROMPT` | Prompt validation failed | No | Show validation error |
| `INVALID_TYPE` | Unknown element/chart type | No | Check type selection |
| `INVALID_GRID` | Grid constraints invalid | No | Adjust element size |
| `GENERATION_FAILED` | AI generation error | Yes | Show retry button |
| `RATE_LIMITED` | Too many requests | Yes | Show wait message |
| `QUOTA_EXCEEDED` | API quota exceeded | Yes | Wait and retry |
| `INSUFFICIENT_CREDITS` | Not enough credits | No | Show credit purchase |
| `CONTENT_POLICY` | Content policy violation | No | Modify prompt |
| `SERVICE_UNAVAILABLE` | Backend service down | Yes | Show maintenance message |
| `TIMEOUT` | Request timed out | Yes | Show retry button |

### 7.2 Error Response Handling

```typescript
// Frontend error handling pattern
if (!response.success) {
  const { code, message, retryable, suggestion } = response.error

  if (retryable) {
    showRetryableError(message, suggestion)
  } else {
    showValidationError(message, suggestion)
  }
}
```

### 7.3 Loading States

| Element Type | Expected Duration | Show Progress |
|--------------|-------------------|---------------|
| Analytics | 2-5 seconds | Spinner |
| Diagrams | 3-10 seconds | Progress bar (async polling) |
| Infographic | 2-5 seconds | Spinner |
| Image | 5-20 seconds | Progress with cancel option |
| Text | 1-3 seconds | Spinner |
| Table | 2-4 seconds | Spinner |

---

## 8. Appendix: Quick Reference

### 8.1 Element Type Summary

| Element | Types | Key Config | Async |
|---------|-------|------------|-------|
| Analytics | 18 charts | chartType, narrative, useSyntheticData | No |
| Diagrams | 28 types | diagramType, prompt, complexity | Yes (polling) |
| Infographic | 14 types | infographicType, prompt, itemCount | No |
| Image | 5 styles | prompt, style, quality, aspectRatio | No |
| Text | 3 operations | prompt OR sourceContent, tone/format | No |
| Table | 3 operations | prompt OR sourceTable, style/structure | No |

### 8.2 Minimum Grid Sizes

| Element | Min Width | Min Height | Recommended |
|---------|-----------|------------|-------------|
| Analytics | 4 | 3 | 6x4 or larger |
| Diagrams | 3 | 2 | 6x4 or larger |
| Infographic | 4 | 3 | 6x4 or larger |
| Image | 2 | 2 | Any ratio |
| Text | 2 | 1 | 4x3 or larger |
| Table | 4 | 2 | 6x4 or larger |

### 8.3 Default Values Reference

| Element | Field | Default |
|---------|-------|---------|
| Analytics | chartType | `bar_vertical` |
| Analytics | useSyntheticData | `false` |
| Diagrams | complexity | `moderate` |
| Diagrams | direction | `TB` |
| Infographic | colorScheme | `professional` |
| Infographic | density | `balanced` |
| Image | style | `realistic` |
| Image | aspectRatio | `16:9` |
| Image | quality | `standard` |
| Text | tone | `professional` |
| Text | format | `paragraph` |
| Table | stylePreset | `professional` |
| Table | alternatingRows | `true` |

### 8.4 Character/Content Limits

| Element | Prompt Limit | Other Limits |
|---------|--------------|--------------|
| Analytics | 2000 chars | 1-50 data points |
| Diagrams | 2000 chars | 3-30 nodes |
| Infographic | 1000 chars | 2-10 items |
| Image | 1000 chars | - |
| Text | 2000 chars | Auto by grid |
| Table | 2000 chars | 1-10 cols, 1-20 rows |

---

## Document Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Dec 3, 2025 | Initial release |

---

**Contact**: Backend Services Team
**Questions**: Route through Elementor orchestrator documentation or team channels
