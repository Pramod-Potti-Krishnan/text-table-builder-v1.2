"""
Table Generators for Layout Service Integration

Three generators for table-related operations:
- TableGenerateGenerator: Generate new table from prompt
- TableTransformGenerator: Transform existing table structure
- TableAnalyzeGenerator: Analyze table data for insights

All generators produce HTML tables with inline CSS suitable for reveal.js slides.
"""

import logging
import re
import json
from typing import Dict, Any, List, Optional

from .base_layout_generator import BaseLayoutGenerator
from .grid_calculator import GridCalculator
from app.models.layout_models import (
    TableGenerateRequest,
    TableGenerateResponse,
    TableTransformRequest,
    TableTransformResponse,
    TableAnalyzeRequest,
    TableAnalyzeResponse,
    TableContentData,
    TableTransformData,
    TableAnalysisData,
    TableContent,
    TableMetadata,
    TableInsight,
    ErrorDetails,
    TableStylePreset,
    TableTransformation,
    TableAnalysisType
)

logger = logging.getLogger(__name__)


class TableGenerateGenerator(BaseLayoutGenerator[TableGenerateRequest, TableGenerateResponse]):
    """
    Generate new table content from a prompt.

    Creates HTML table with inline CSS that fits within grid constraints.
    Supports multiple style presets and automatic dimension calculation.
    """

    @property
    def generator_type(self) -> str:
        return "table_generate"

    def _get_style_css(self, preset: TableStylePreset) -> Dict[str, str]:
        """Get CSS styles for table preset."""
        base_styles = {
            "table": "width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; font-size: 0.95rem;",
            "th": "text-align: left; padding: 12px 16px; font-weight: 600; color: #1f2937;",
            "td": "padding: 10px 16px; color: #374151;",
            "tr_even": "",
            "tr_odd": ""
        }

        if preset == TableStylePreset.MINIMAL:
            base_styles.update({
                "th": base_styles["th"] + " border-bottom: 2px solid #e5e7eb;",
                "td": base_styles["td"] + " border-bottom: 1px solid #f3f4f6;"
            })
        elif preset == TableStylePreset.BORDERED:
            base_styles.update({
                "table": base_styles["table"] + " border: 1px solid #d1d5db;",
                "th": base_styles["th"] + " border: 1px solid #d1d5db; background-color: #f9fafb;",
                "td": base_styles["td"] + " border: 1px solid #e5e7eb;"
            })
        elif preset == TableStylePreset.STRIPED:
            base_styles.update({
                "th": base_styles["th"] + " background-color: #1f2937; color: #ffffff; border: none;",
                "td": base_styles["td"] + " border: none;",
                "tr_even": "background-color: #f9fafb;",
                "tr_odd": "background-color: #ffffff;"
            })
        elif preset == TableStylePreset.MODERN:
            base_styles.update({
                "th": base_styles["th"] + " background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; border: none;",
                "td": base_styles["td"] + " border-bottom: 1px solid #e5e7eb;",
                "tr_even": "background-color: #faf5ff;"
            })
        elif preset == TableStylePreset.PROFESSIONAL:
            base_styles.update({
                "th": base_styles["th"] + " background-color: #1e40af; color: #ffffff; border: none;",
                "td": base_styles["td"] + " border-bottom: 1px solid #e5e7eb;",
                "tr_even": "background-color: #eff6ff;"
            })
        elif preset == TableStylePreset.COLORFUL:
            base_styles.update({
                "th": base_styles["th"] + " background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: #ffffff; border: none;",
                "td": base_styles["td"] + " border-bottom: 1px solid #fce7f3;",
                "tr_even": "background-color: #fdf2f8;"
            })

        return base_styles

    async def _build_prompt(self, request: TableGenerateRequest) -> str:
        """Build prompt for table generation."""
        # Calculate dimensions
        dims = GridCalculator.calculate_table_dimensions(
            request.constraints.gridWidth,
            request.constraints.gridHeight
        )

        # Use requested structure or defaults
        if request.structure:
            columns = min(request.structure.columns, dims["max_columns"])
            rows = min(request.structure.rows, dims["max_rows"])
            has_header = request.structure.hasHeader
            has_footer = request.structure.hasFooter or False
        else:
            columns = min(4, dims["max_columns"])
            rows = min(5, dims["max_rows"])
            has_header = True
            has_footer = False

        # Get style
        style_preset = TableStylePreset.PROFESSIONAL
        if request.style:
            style_preset = request.style.preset or TableStylePreset.PROFESSIONAL

        styles = self._get_style_css(style_preset)

        # Build context
        context_str = self._build_context_section(request.context)

        # Include seed data if provided
        seed_data_str = ""
        if request.seedData:
            seed_data_str = f"""
## SEED DATA (use this as reference)
{json.dumps(request.seedData, indent=2)}
"""

        prompt = f"""Generate an HTML table for a presentation slide.

## CONTEXT
{context_str}

## USER REQUEST
{request.prompt}
{seed_data_str}

## TABLE STRUCTURE
- Columns: {columns}
- Data rows: {rows}
- Header row: {"Yes" if has_header else "No"}
- Footer/Summary row: {"Yes" if has_footer else "No"}
- Cell character limit: ~{dims["cell_char_limit"]} characters per cell

## STYLING
Use these inline styles:
- Table: style="{styles["table"]}"
- Header cells (th): style="{styles["th"]}"
- Data cells (td): style="{styles["td"]}"
{"- Even rows: style=\"" + styles["tr_even"] + "\"" if styles["tr_even"] else ""}
{"- Odd rows: style=\"" + styles["tr_odd"] + "\"" if styles["tr_odd"] else ""}

## OUTPUT FORMAT
Generate a complete HTML table. Example structure:

<table style="{styles["table"]}">
  <thead>
    <tr>
      <th style="{styles["th"]}">Column 1</th>
      <th style="{styles["th"]}">Column 2</th>
    </tr>
  </thead>
  <tbody>
    <tr{' style="' + styles["tr_odd"] + '"' if styles["tr_odd"] else ''}>
      <td style="{styles["td"]}">Data 1</td>
      <td style="{styles["td"]}">Data 2</td>
    </tr>
  </tbody>
</table>

## REQUIREMENTS
1. Generate realistic, relevant data based on the user's request
2. Keep cell content concise (~{dims["cell_char_limit"]} chars max per cell)
3. Include ALL inline styles (no external CSS)
4. Use semantic HTML (thead, tbody, tfoot if footer)
5. Return ONLY the HTML table - no explanations

Generate the HTML table now:"""

        return prompt

    def _parse_table_metadata(self, html: str) -> TableMetadata:
        """Extract metadata from generated table HTML."""
        # Count columns (from first row)
        th_matches = re.findall(r'<th[^>]*>', html, re.IGNORECASE)
        td_first_row = re.search(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)

        column_count = len(th_matches)
        if column_count == 0 and td_first_row:
            column_count = len(re.findall(r'<td[^>]*>', td_first_row.group(1), re.IGNORECASE))

        # Count data rows (excluding header)
        tbody_match = re.search(r'<tbody[^>]*>(.*?)</tbody>', html, re.DOTALL | re.IGNORECASE)
        row_count = 0
        if tbody_match:
            row_count = len(re.findall(r'<tr[^>]*>', tbody_match.group(1), re.IGNORECASE))
        else:
            # Count all rows minus header
            all_rows = len(re.findall(r'<tr[^>]*>', html, re.IGNORECASE))
            row_count = max(0, all_rows - 1)

        has_header = '<thead' in html.lower() or len(th_matches) > 0
        has_footer = '<tfoot' in html.lower()

        # Detect column types (basic heuristic)
        column_types = []
        # Extract first data row
        if tbody_match:
            first_row = re.search(r'<tr[^>]*>(.*?)</tr>', tbody_match.group(1), re.DOTALL | re.IGNORECASE)
            if first_row:
                cells = re.findall(r'<td[^>]*>(.*?)</td>', first_row.group(1), re.DOTALL | re.IGNORECASE)
                for cell in cells:
                    cell_text = re.sub(r'<[^>]+>', '', cell).strip()
                    if re.match(r'^[\$\€\£]?[\d,]+\.?\d*%?$', cell_text):
                        column_types.append("numeric")
                    elif re.match(r'^\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}$', cell_text):
                        column_types.append("date")
                    else:
                        column_types.append("text")

        # Pad column types if needed
        while len(column_types) < column_count:
            column_types.append("text")

        has_numeric = "numeric" in column_types
        has_date = "date" in column_types

        return TableMetadata(
            rowCount=row_count,
            columnCount=column_count,
            hasHeader=has_header,
            hasFooter=has_footer,
            columnTypes=column_types,
            hasNumericData=has_numeric,
            hasDateData=has_date
        )

    async def _build_response(
        self,
        content: str,
        request: TableGenerateRequest,
        generation_id: str
    ) -> TableGenerateResponse:
        """Build the response object with metadata."""
        metadata = self._parse_table_metadata(content)

        # Calculate suggested column widths (equal distribution)
        suggested_widths = []
        if metadata.columnCount > 0:
            width_per_col = 100 / metadata.columnCount
            suggested_widths = [round(width_per_col, 1)] * metadata.columnCount

        return TableGenerateResponse(
            success=True,
            data=TableContentData(
                generationId=generation_id,
                content=TableContent(html=content),
                metadata=metadata,
                editInfo={
                    "editableCells": True,
                    "suggestedColumnWidths": suggested_widths
                }
            )
        )


class TableTransformGenerator(BaseLayoutGenerator[TableTransformRequest, TableTransformResponse]):
    """
    Transform existing table structure.

    Supports: add_column, add_row, remove_column, remove_row,
    sort, summarize, transpose, expand, merge_cells, split_column.
    """

    @property
    def generator_type(self) -> str:
        return "table_transform"

    def _get_transformation_instruction(self, transformation: TableTransformation, options: Optional[Dict[str, Any]]) -> str:
        """Get specific instruction for transformation type."""
        opts = options or {}

        instructions = {
            TableTransformation.ADD_COLUMN: f"Add a new column{' at position ' + str(opts.get('position', 'end')) if 'position' in opts else ' at the end'}. {opts.get('content', 'Generate appropriate data for the new column.')}",
            TableTransformation.ADD_ROW: f"Add a new row{' at position ' + str(opts.get('position', 'end')) if 'position' in opts else ' at the end'}. {opts.get('content', 'Generate appropriate data for the new row.')}",
            TableTransformation.REMOVE_COLUMN: f"Remove column at index {opts.get('index', 'last')}",
            TableTransformation.REMOVE_ROW: f"Remove row at index {opts.get('index', 'last')}",
            TableTransformation.SORT: f"Sort by column {opts.get('sortColumn', 0)} in {opts.get('sortDirection', 'asc')} order",
            TableTransformation.SUMMARIZE: f"Add a summary row with {opts.get('summaryType', 'totals')} for numeric columns",
            TableTransformation.TRANSPOSE: "Swap rows and columns (transpose the table)",
            TableTransformation.EXPAND: f"Add more rows with similar data patterns. {opts.get('expandPrompt', '')}",
            TableTransformation.MERGE_CELLS: "Merge cells where adjacent cells have the same value",
            TableTransformation.SPLIT_COLUMN: f"Split column {opts.get('index', 0)} into multiple columns"
        }

        return instructions.get(transformation, "Transform the table as requested")

    async def _build_prompt(self, request: TableTransformRequest) -> str:
        """Build prompt for table transformation."""
        instruction = self._get_transformation_instruction(request.transformation, request.options)

        # Calculate constraints
        dims = GridCalculator.calculate_table_dimensions(
            request.constraints.gridWidth,
            request.constraints.gridHeight
        )

        prompt = f"""Transform the given HTML table according to the specified operation.

## ORIGINAL TABLE
{request.sourceTable}

## TRANSFORMATION
Operation: {request.transformation.value}
Instructions: {instruction}

## CONSTRAINTS
- Maximum columns: {dims["max_columns"]}
- Maximum rows: {dims["max_rows"]}
- Cell character limit: ~{dims["cell_char_limit"]} characters

## REQUIREMENTS
1. Perform the {request.transformation.value} transformation
2. Preserve the existing styling (inline CSS)
3. Stay within the size constraints
4. Maintain proper HTML table structure (thead, tbody)
5. Return ONLY the transformed HTML table - no explanations

Transform and return the table:"""

        return prompt

    async def _build_response(
        self,
        content: str,
        request: TableTransformRequest,
        generation_id: str
    ) -> TableTransformResponse:
        """Build response with updated metadata."""
        # Parse metadata from transformed table
        # Reuse the same parsing logic
        metadata = self._parse_table_metadata(content)

        return TableTransformResponse(
            success=True,
            data=TableTransformData(
                transformationId=generation_id,
                content=TableContent(html=content),
                metadata=metadata
            )
        )

    def _parse_table_metadata(self, html: str) -> TableMetadata:
        """Extract metadata from table HTML."""
        # Count columns
        th_matches = re.findall(r'<th[^>]*>', html, re.IGNORECASE)
        column_count = len(th_matches)

        if column_count == 0:
            first_row = re.search(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
            if first_row:
                column_count = len(re.findall(r'<td[^>]*>', first_row.group(1), re.IGNORECASE))

        # Count rows
        tbody_match = re.search(r'<tbody[^>]*>(.*?)</tbody>', html, re.DOTALL | re.IGNORECASE)
        row_count = 0
        if tbody_match:
            row_count = len(re.findall(r'<tr[^>]*>', tbody_match.group(1), re.IGNORECASE))
        else:
            all_rows = len(re.findall(r'<tr[^>]*>', html, re.IGNORECASE))
            row_count = max(0, all_rows - 1)

        return TableMetadata(
            rowCount=row_count,
            columnCount=column_count,
            hasHeader='<thead' in html.lower() or len(th_matches) > 0,
            hasFooter='<tfoot' in html.lower(),
            columnTypes=["text"] * column_count,
            hasNumericData=False,
            hasDateData=False
        )


class TableAnalyzeGenerator(BaseLayoutGenerator[TableAnalyzeRequest, TableAnalyzeResponse]):
    """
    Analyze table data for insights.

    Supports analysis types: summary, trends, outliers, visualization.
    Returns natural language insights and recommendations.
    """

    @property
    def generator_type(self) -> str:
        return "table_analyze"

    async def _build_prompt(self, request: TableAnalyzeRequest) -> str:
        """Build prompt for table analysis."""
        analysis_instructions = {
            TableAnalysisType.SUMMARY: "Provide a comprehensive summary of the data including key statistics, notable patterns, and main takeaways.",
            TableAnalysisType.TRENDS: "Identify trends, patterns, and relationships in the data. Look for growth, decline, correlations, and sequences.",
            TableAnalysisType.OUTLIERS: "Identify outliers, anomalies, and unusual values in the data. Explain why they stand out.",
            TableAnalysisType.VISUALIZATION: "Recommend the best visualization type for this data and explain why it would be effective."
        }

        instruction = analysis_instructions.get(request.analysisType, analysis_instructions[TableAnalysisType.SUMMARY])

        prompt = f"""Analyze the following HTML table data and provide insights.

## TABLE DATA
{request.sourceTable}

## ANALYSIS TYPE
{request.analysisType.value}

## INSTRUCTIONS
{instruction}

## OUTPUT FORMAT
Return your analysis as a JSON object with this structure:
{{
  "summary": "A 2-3 sentence natural language summary of the table data",
  "insights": [
    {{
      "type": "trend|comparison|highlight|outlier",
      "title": "Short insight title",
      "description": "Detailed description of the insight",
      "confidence": 0.0-1.0
    }}
  ],
  "statistics": {{
    "columnName": {{
      "min": number or null,
      "max": number or null,
      "average": number or null
    }}
  }},
  "recommendations": {{
    "suggestedChartType": "bar|line|pie|scatter|table",
    "suggestedHighlights": [row indices to highlight],
    "suggestedSorting": {{"column": index, "direction": "asc|desc"}}
  }}
}}

Analyze the table and return ONLY the JSON object:"""

        return prompt

    async def generate(self, request: TableAnalyzeRequest) -> TableAnalyzeResponse:
        """Override to handle JSON parsing from analysis."""
        generation_id = self._generate_id()
        logger.info(f"Starting {self.generator_type} (id: {generation_id})")

        try:
            prompt = await self._build_prompt(request)
            raw_response = await self.llm_service(prompt)

            # Parse JSON from response
            analysis_data = self._parse_json_from_response(raw_response)

            if not analysis_data:
                raise ValueError("Failed to parse analysis response as JSON")

            # Extract metadata from original table
            metadata = self._parse_table_metadata(request.sourceTable)

            # Build insights
            insights = []
            for insight_data in analysis_data.get("insights", []):
                insights.append(TableInsight(
                    type=insight_data.get("type", "highlight"),
                    title=insight_data.get("title", "Insight"),
                    description=insight_data.get("description", ""),
                    confidence=float(insight_data.get("confidence", 0.8))
                ))

            return TableAnalyzeResponse(
                success=True,
                data=TableAnalysisData(
                    analysisId=generation_id,
                    summary=analysis_data.get("summary", "Analysis complete."),
                    insights=insights,
                    statistics=analysis_data.get("statistics"),
                    recommendations=analysis_data.get("recommendations"),
                    metadata=metadata
                )
            )

        except Exception as e:
            logger.error(f"Table analysis failed: {e}")
            return TableAnalyzeResponse(
                success=False,
                error=ErrorDetails(
                    code="ANALYSIS_FAILED",
                    message=str(e),
                    retryable=True
                )
            )

    async def _build_response(
        self,
        content: str,
        request: TableAnalyzeRequest,
        generation_id: str
    ) -> TableAnalyzeResponse:
        """Not used - analysis handles its own response building."""
        pass

    def _parse_table_metadata(self, html: str) -> TableMetadata:
        """Extract metadata from table HTML."""
        th_matches = re.findall(r'<th[^>]*>', html, re.IGNORECASE)
        column_count = len(th_matches)

        if column_count == 0:
            first_row = re.search(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
            if first_row:
                column_count = len(re.findall(r'<td[^>]*>', first_row.group(1), re.IGNORECASE))

        tbody_match = re.search(r'<tbody[^>]*>(.*?)</tbody>', html, re.DOTALL | re.IGNORECASE)
        row_count = 0
        if tbody_match:
            row_count = len(re.findall(r'<tr[^>]*>', tbody_match.group(1), re.IGNORECASE))
        else:
            all_rows = len(re.findall(r'<tr[^>]*>', html, re.IGNORECASE))
            row_count = max(0, all_rows - 1)

        return TableMetadata(
            rowCount=row_count,
            columnCount=column_count,
            hasHeader='<thead' in html.lower() or len(th_matches) > 0,
            hasFooter='<tfoot' in html.lower(),
            columnTypes=["text"] * column_count,
            hasNumericData=False,
            hasDateData=False
        )
