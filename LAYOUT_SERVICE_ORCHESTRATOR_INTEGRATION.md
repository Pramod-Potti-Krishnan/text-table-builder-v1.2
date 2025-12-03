# Layout Service Orchestrator Integration

## Service Configuration

Add the following configuration to your Layout Service orchestrator:

```typescript
// services/text-table-builder.config.ts

export const TextTableBuilderConfig = {
  name: "text-table-builder",
  version: "1.2.0",
  baseUrl: process.env.TEXT_TABLE_BUILDER_URL || "http://localhost:8000",

  endpoints: {
    // Text Operations
    textGenerate: "/api/ai/text/generate",
    textTransform: "/api/ai/text/transform",
    textAutofit: "/api/ai/text/autofit",

    // Table Operations
    tableGenerate: "/api/ai/table/generate",
    tableTransform: "/api/ai/table/transform",
    tableAnalyze: "/api/ai/table/analyze",

    // Utility
    health: "/api/ai/health",
    constraints: "/api/ai/constraints/{gridWidth}/{gridHeight}"
  },

  timeout: 60000, // 60 seconds for LLM operations
  retryCount: 2,
  retryDelay: 1000
};
```

## Service Client

```typescript
// services/text-table-builder.client.ts

import { TextTableBuilderConfig } from './text-table-builder.config';

interface GridConstraints {
  gridWidth: number;  // 1-12
  gridHeight: number; // 1-8
  maxCharacters?: number;
  minCharacters?: number;
}

interface SlideContext {
  presentationTitle: string;
  slideIndex: number;
  slideCount: number;
  slideTitle?: string;
  slideContext?: string;
  previousSlideContent?: string;
  nextSlideContent?: string;
}

interface TextGenerateRequest {
  prompt: string;
  presentationId: string;
  slideId: string;
  elementId: string;
  context: SlideContext;
  constraints: GridConstraints;
  options?: {
    tone?: 'professional' | 'conversational' | 'academic' | 'persuasive' | 'casual' | 'technical';
    format?: 'paragraph' | 'bullets' | 'numbered' | 'headline' | 'quote' | 'mixed';
    bulletStyle?: 'disc' | 'circle' | 'square' | 'dash' | 'arrow' | 'checkmark';
    includeEmoji?: boolean;
  };
}

interface TableGenerateRequest {
  prompt: string;
  presentationId: string;
  slideId: string;
  elementId: string;
  context: SlideContext;
  constraints: GridConstraints;
  structure?: {
    columns?: number;
    rows?: number;
    hasHeader?: boolean;
    hasFooter?: boolean;
  };
  style?: {
    preset?: 'minimal' | 'bordered' | 'striped' | 'modern' | 'professional' | 'colorful';
    alternatingRows?: boolean;
  };
  seedData?: Array<Record<string, any>>;
}

export class TextTableBuilderClient {
  private baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || TextTableBuilderConfig.baseUrl;
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/ai/health`);
      const data = await response.json();
      return data.status === 'healthy';
    } catch {
      return false;
    }
  }

  // Get constraints for grid size
  async getConstraints(gridWidth: number, gridHeight: number) {
    const response = await fetch(
      `${this.baseUrl}/api/ai/constraints/${gridWidth}/${gridHeight}`
    );
    return response.json();
  }

  // Text generation
  async generateText(request: TextGenerateRequest) {
    const response = await fetch(`${this.baseUrl}/api/ai/text/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    return response.json();
  }

  // Text transformation
  async transformText(request: {
    sourceContent: string;
    transformation: 'expand' | 'condense' | 'simplify' | 'formalize' | 'casualize' |
                    'bulletize' | 'paragraphize' | 'rephrase' | 'proofread' | 'translate';
    presentationId: string;
    slideId: string;
    elementId: string;
    context: SlideContext;
    constraints: GridConstraints;
  }) {
    const response = await fetch(`${this.baseUrl}/api/ai/text/transform`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    return response.json();
  }

  // Text autofit
  async autofitText(request: {
    content: string;
    presentationId: string;
    slideId: string;
    elementId: string;
    targetFit: GridConstraints;
    strategy: 'reduce_font' | 'truncate' | 'smart_condense' | 'overflow';
    preserveFormatting?: boolean;
  }) {
    const response = await fetch(`${this.baseUrl}/api/ai/text/autofit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    return response.json();
  }

  // Table generation
  async generateTable(request: TableGenerateRequest) {
    const response = await fetch(`${this.baseUrl}/api/ai/table/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    return response.json();
  }

  // Table transformation
  async transformTable(request: {
    sourceTable: string;
    transformation: 'add_column' | 'add_row' | 'remove_column' | 'remove_row' |
                    'sort' | 'summarize' | 'transpose' | 'expand' | 'merge_cells' | 'split_column';
    presentationId: string;
    slideId: string;
    elementId: string;
    constraints: GridConstraints;
    options?: Record<string, any>;
  }) {
    const response = await fetch(`${this.baseUrl}/api/ai/table/transform`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    return response.json();
  }

  // Table analysis
  async analyzeTable(request: {
    sourceTable: string;
    analysisType: 'summary' | 'trends' | 'outliers' | 'visualization';
    presentationId: string;
    slideId: string;
    elementId: string;
  }) {
    const response = await fetch(`${this.baseUrl}/api/ai/table/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    return response.json();
  }
}

// Export singleton instance
export const textTableBuilder = new TextTableBuilderClient();
```

## Usage in Layout Service Orchestrator

```typescript
// orchestrator/ai-content-handler.ts

import { textTableBuilder } from '../services/text-table-builder.client';

export class AIContentHandler {

  // Called when user creates a new text element with AI prompt
  async handleTextGeneration(
    elementId: string,
    prompt: string,
    presentation: Presentation,
    slide: Slide,
    element: Element
  ) {
    const result = await textTableBuilder.generateText({
      prompt,
      presentationId: presentation.id,
      slideId: slide.id,
      elementId,
      context: {
        presentationTitle: presentation.title,
        slideIndex: slide.index,
        slideCount: presentation.slides.length,
        slideTitle: slide.title
      },
      constraints: {
        gridWidth: element.gridWidth,
        gridHeight: element.gridHeight
      },
      options: {
        tone: element.aiSettings?.tone || 'professional',
        format: element.aiSettings?.format || 'paragraph'
      }
    });

    if (result.success) {
      // Update element with generated content
      element.content = result.data.content.html;
      element.metadata = result.data.metadata;
      element.suggestions = result.data.suggestions;
    }

    return result;
  }

  // Called when user resizes an element
  async handleElementResize(element: Element, newWidth: number, newHeight: number) {
    if (!element.content) return;

    const result = await textTableBuilder.autofitText({
      content: element.content,
      presentationId: element.presentationId,
      slideId: element.slideId,
      elementId: element.id,
      targetFit: {
        gridWidth: newWidth,
        gridHeight: newHeight
      },
      strategy: 'smart_condense',
      preserveFormatting: true
    });

    if (result.success) {
      element.content = result.data.content;
      element.fits = result.data.fits;
    }

    return result;
  }

  // Called when user requests a transformation (expand, condense, etc.)
  async handleTextTransformation(
    element: Element,
    transformation: string,
    presentation: Presentation,
    slide: Slide
  ) {
    const result = await textTableBuilder.transformText({
      sourceContent: element.content,
      transformation: transformation as any,
      presentationId: presentation.id,
      slideId: slide.id,
      elementId: element.id,
      context: {
        presentationTitle: presentation.title,
        slideIndex: slide.index,
        slideCount: presentation.slides.length
      },
      constraints: {
        gridWidth: element.gridWidth,
        gridHeight: element.gridHeight
      }
    });

    if (result.success) {
      element.content = result.data.content.html;
      element.metadata = result.data.metadata;
    }

    return result;
  }
}
```

## Environment Variables

Add to your Layout Service environment:

```bash
# Text & Table Builder Service URL
TEXT_TABLE_BUILDER_URL=http://localhost:8000

# For production
TEXT_TABLE_BUILDER_URL=https://text-table-builder.railway.app
```

## Docker Compose Integration

```yaml
# docker-compose.yml

services:
  layout-service:
    build: ./layout-service
    environment:
      - TEXT_TABLE_BUILDER_URL=http://text-table-builder:8000
    depends_on:
      - text-table-builder

  text-table-builder:
    build: ./text-table-builder
    environment:
      - GCP_PROJECT_ID=${GCP_PROJECT_ID}
      - GCP_SERVICE_ACCOUNT_JSON=${GCP_SERVICE_ACCOUNT_JSON}
    ports:
      - "8000:8000"
```

## API Capabilities Summary

| Endpoint | Purpose | Key Features |
|----------|---------|--------------|
| `POST /api/ai/text/generate` | Generate text from prompt | Suggestions, alternatives, tone/format options |
| `POST /api/ai/text/transform` | Transform existing text | 10 transformation types, change tracking |
| `POST /api/ai/text/autofit` | Fit text to element | 4 strategies, smart AI condensing |
| `POST /api/ai/table/generate` | Generate table from prompt | 6 style presets, grid-aware sizing |
| `POST /api/ai/table/transform` | Modify table structure | 10 transformation types |
| `POST /api/ai/table/analyze` | Analyze table data | Insights, statistics, recommendations |
| `GET /api/ai/health` | Service health check | Full capabilities list |
| `GET /api/ai/constraints/{w}/{h}` | Get grid constraints | Character limits, table dimensions |

## Grid System Quick Reference

```
Grid System: 12 columns x 8 rows
Slide Size: 960px x 540px

Character Limits by Grid Size:
- 3x2:  ~153 characters (small callout)
- 6x4:  ~612 characters (half-width block)
- 12x4: ~1224 characters (full-width)
- 12x8: ~2448 characters (full slide)

Table Limits by Grid Size:
- 6x4:  5 columns x 7 rows
- 10x5: 8 columns x 9 rows
- 12x6: 10 columns x 11 rows
```
