"""
Response Models for Text and Table Content Builder
===================================================

Pydantic models for API responses matching Content Orchestrator expectations.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class GeneratedText(BaseModel):
    """
    Generated text content response.

    Matches Content Orchestrator's GeneratedText model.
    """
    content: str = Field(
        description="HTML-formatted text content"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Generation metadata (word_count, html_tags_used, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "<p>Q3 demonstrated <strong>exceptional revenue growth</strong> across all key markets.</p><ul><li>Revenue increased by <span class=\"metric\">32%</span> quarter-over-quarter</li><li>Market expansion into <em>three new regions</em></li><li>Cost efficiency improved through <mark>strategic automation</mark></li></ul>",
                "metadata": {
                    "word_count": 42,
                    "target_word_count": 50,
                    "variance_percent": -16.0,
                    "within_tolerance": False,
                    "html_tags_used": ["p", "strong", "ul", "li", "span", "em", "mark"],
                    "generation_time_ms": 842,
                    "model_used": "gemini-2.5-flash",
                    "prompt_tokens": 245,
                    "completion_tokens": 156
                }
            }
        }


class GeneratedTable(BaseModel):
    """
    Generated table content response.
    """
    html: str = Field(
        description="Complete HTML table markup"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Table metadata (rows, columns, data_points)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "html": "<table class=\"data-table\"><thead><tr><th>Region</th><th>Q2 Revenue ($M)</th><th>Q3 Revenue ($M)</th><th>Growth %</th></tr></thead><tbody><tr><td>North America</td><td class=\"numeric\">45.2</td><td class=\"numeric\">58.3</td><td class=\"metric positive\">+29.0%</td></tr><tr><td>Europe</td><td class=\"numeric\">32.1</td><td class=\"numeric\">39.4</td><td class=\"metric positive\">+22.7%</td></tr><tr><td>Asia</td><td class=\"numeric\">28.7</td><td class=\"numeric\">35.6</td><td class=\"metric positive\">+24.0%</td></tr></tbody></table>",
                "metadata": {
                    "rows": 3,
                    "columns": 4,
                    "data_points": 12,
                    "has_header": True,
                    "numeric_columns": 3,
                    "generation_time_ms": 1245,
                    "model_used": "gemini-2.5-flash"
                }
            }
        }


class BatchTextGenerationResponse(BaseModel):
    """
    Batch text generation response.
    """
    results: List[GeneratedText] = Field(
        description="List of generated text contents"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Batch processing metadata"
    )


class BatchTableGenerationResponse(BaseModel):
    """
    Batch table generation response.
    """
    results: List[GeneratedTable] = Field(
        description="List of generated tables"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Batch processing metadata"
    )


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(default="healthy")
    version: str = Field(default="1.0.0")
    service: str = Field(default="text-table-builder")
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None


class SessionInfoResponse(BaseModel):
    """Session information response."""
    presentation_id: str
    slides_in_context: int
    context_size_bytes: int
    last_updated: str
    ttl_remaining_seconds: int
