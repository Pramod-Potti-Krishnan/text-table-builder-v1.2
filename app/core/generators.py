"""
Content Generators for Text and Tables
======================================

Core generation logic using LLM with context management.
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional

from app.models.requests import TextGenerationRequest, TableGenerationRequest, StructuredTextGenerationRequest, FieldSpec
from app.models.responses import GeneratedText, GeneratedTable
from app.models.session import SlideContext
from app.core.llm_client import get_llm_client, BaseLLMClient
from app.core.session_manager import get_session_manager, SessionManager
from app.utils.prompt_loader import load_text_generation_prompt, load_table_generation_prompt


logger = logging.getLogger(__name__)


class TextGenerator:
    """
    Text content generator.

    Generates HTML-formatted text content from topics and narrative.
    """

    def __init__(
        self,
        llm_client: Optional[BaseLLMClient] = None,
        session_manager: Optional[SessionManager] = None,
        word_count_tolerance: float = 0.10
    ):
        """
        Initialize text generator.

        Args:
            llm_client: LLM client for generation
            session_manager: Session manager for context
            word_count_tolerance: Acceptable variance from target word count (default: ±10%)
        """
        self.llm_client = llm_client or get_llm_client()
        self.session_manager = session_manager or get_session_manager()
        self.word_count_tolerance = word_count_tolerance

    async def generate(self, request: TextGenerationRequest) -> GeneratedText:
        """
        Generate text content from request.

        Args:
            request: Text generation request with topics, narrative, and context

        Returns:
            GeneratedText with HTML content and metadata
        """
        start_time = time.time()

        try:
            # Get or create session context
            session = await self.session_manager.get_or_create_session(
                presentation_id=request.presentation_id,
                presentation_theme=request.context.get("theme"),
                target_audience=request.context.get("audience")
            )

            # Get previous slides context (reduced to 1 slide to minimize input tokens)
            previous_context = await self.session_manager.get_context_summary(
                request.presentation_id,
                max_slides=1
            )

            # Calculate target word count from max_characters constraint
            max_chars = request.constraints.get("max_characters", 300)
            target_words = self._estimate_words_from_chars(max_chars)

            # Format topics as bullet points
            topics_formatted = "\n".join([f"- {topic}" for topic in request.topics])

            # Build prompt using prompt loader (v3.3: includes layout metadata)
            prompt = load_text_generation_prompt(
                target_words=target_words,
                previous_context=previous_context,
                theme=request.context.get("theme", "professional"),
                audience=request.context.get("audience", "general"),
                slide_title=request.context.get("slide_title", ""),
                narrative=request.narrative,
                topics=topics_formatted,
                # v3.3: Layout metadata for conditional prompt rules
                layout_id=request.layout_id or "unknown",
                slide_purpose=request.slide_purpose or "unknown",
                suggested_pattern=request.suggested_pattern or "standard-content"
            )

            # Generate content using LLM
            llm_response = await self.llm_client.generate(prompt)

            # Extract HTML content (remove any markdown code blocks if present)
            html_content = self._clean_html_output(llm_response.content)

            # Count words in generated content
            actual_word_count = self._count_words(html_content)

            # Calculate variance from target
            variance_percent = ((actual_word_count - target_words) / target_words) * 100
            within_tolerance = abs(variance_percent) <= (self.word_count_tolerance * 100)

            # Extract HTML tags used
            html_tags_used = self._extract_html_tags(html_content)

            # Build metadata
            metadata = {
                "word_count": actual_word_count,
                "target_word_count": target_words,
                "variance_percent": round(variance_percent, 1),
                "within_tolerance": within_tolerance,
                "html_tags_used": html_tags_used,
                "generation_time_ms": round((time.time() - start_time) * 1000, 2),
                "model_used": llm_response.model,
                "provider": llm_response.provider,
                "prompt_tokens": llm_response.prompt_tokens,
                "completion_tokens": llm_response.completion_tokens,
                "total_tokens": llm_response.total_tokens
            }

            # Update session with generated content
            slide_context = SlideContext(
                slide_id=request.slide_id,
                slide_number=request.slide_number,
                slide_title=request.context.get("slide_title"),
                content_summary=self._create_summary(html_content, request.topics),
                key_themes=request.topics[:3],  # First 3 topics as themes
                content_type="text"
            )

            await self.session_manager.add_slide_to_session(
                request.presentation_id,
                slide_context
            )

            logger.info(
                f"Generated text for {request.slide_id}: "
                f"{actual_word_count} words (target: {target_words}, "
                f"variance: {variance_percent:.1f}%)"
            )

            return GeneratedText(
                content=html_content,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Error generating text for {request.slide_id}: {e}")
            raise

    def _estimate_words_from_chars(self, max_chars: int) -> int:
        """
        Estimate word count from character count.

        Uses average of ~5-6 characters per word.
        """
        return int(max_chars / 5.5)

    def _clean_html_output(self, content: str) -> str:
        """
        Clean LLM output to extract pure HTML.

        Removes markdown code blocks and explanatory text.
        """
        # Remove markdown code blocks
        content = content.strip()
        if content.startswith("```html"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        return content.strip()

    def _count_words(self, html_content: str) -> int:
        """
        Count words in HTML content (excluding tags).

        Args:
            html_content: HTML string

        Returns:
            Word count
        """
        # Simple approach: remove all HTML tags and count words
        import re
        text_only = re.sub(r'<[^>]+>', '', html_content)
        words = text_only.split()
        return len(words)

    def _extract_html_tags(self, html_content: str) -> List[str]:
        """
        Extract list of unique HTML tags used.

        Args:
            html_content: HTML string

        Returns:
            List of tag names
        """
        import re
        tags = re.findall(r'<(\w+)', html_content)
        return sorted(set(tags))

    def _create_summary(self, html_content: str, topics: List[str]) -> str:
        """
        Create a brief summary of the generated content.

        Args:
            html_content: Generated HTML
            topics: Original topics

        Returns:
            Brief summary string
        """
        # Use first topic as main theme
        main_theme = topics[0] if topics else "content"
        word_count = self._count_words(html_content)

        return f"{main_theme} - {word_count} words covering {len(topics)} topics"


class TableGenerator:
    """
    Table content generator.

    Generates HTML tables from data and descriptions.
    """

    def __init__(
        self,
        llm_client: Optional[BaseLLMClient] = None,
        session_manager: Optional[SessionManager] = None
    ):
        """
        Initialize table generator.

        Args:
            llm_client: LLM client for generation
            session_manager: Session manager for context
        """
        self.llm_client = llm_client or get_llm_client()
        self.session_manager = session_manager or get_session_manager()

    async def generate(self, request: TableGenerationRequest) -> GeneratedTable:
        """
        Generate table from request.

        Args:
            request: Table generation request with description and data

        Returns:
            GeneratedTable with HTML and metadata
        """
        start_time = time.time()

        try:
            # Get or create session context
            session = await self.session_manager.get_or_create_session(
                presentation_id=request.presentation_id,
                presentation_theme=request.context.get("theme"),
                target_audience=request.context.get("audience")
            )

            # Get previous slides context (reduced to 1 slide to minimize input tokens)
            previous_context = await self.session_manager.get_context_summary(
                request.presentation_id,
                max_slides=1
            )

            # Format data as JSON string
            data_formatted = json.dumps(request.data, indent=2) if request.data else "No data provided"

            # Build prompt using prompt loader
            prompt = load_table_generation_prompt(
                description=request.description,
                data=data_formatted,
                previous_context=previous_context,
                theme=request.context.get("theme", "professional"),
                audience=request.context.get("audience", "general"),
                slide_title=request.context.get("slide_title", ""),
                context=json.dumps(request.context, indent=2)
            )

            # Generate table using LLM
            llm_response = await self.llm_client.generate(prompt)

            # Extract HTML table (remove any markdown code blocks)
            html_table = self._clean_html_output(llm_response.content)

            # Analyze table structure
            table_stats = self._analyze_table(html_table)

            # Build metadata
            metadata = {
                "rows": table_stats["rows"],
                "columns": table_stats["columns"],
                "data_points": table_stats["data_points"],
                "has_header": table_stats["has_header"],
                "numeric_columns": table_stats["numeric_columns"],
                "generation_time_ms": round((time.time() - start_time) * 1000, 2),
                "model_used": llm_response.model,
                "provider": llm_response.provider,
                "prompt_tokens": llm_response.prompt_tokens,
                "completion_tokens": llm_response.completion_tokens,
                "total_tokens": llm_response.total_tokens,
                "table_classes": table_stats["classes"]
            }

            # Update session with generated content
            slide_context = SlideContext(
                slide_id=request.slide_id,
                slide_number=request.slide_number,
                slide_title=request.context.get("slide_title"),
                content_summary=f"Table: {request.description} ({table_stats['rows']}x{table_stats['columns']})",
                key_themes=[request.description],
                content_type="table"
            )

            await self.session_manager.add_slide_to_session(
                request.presentation_id,
                slide_context
            )

            logger.info(
                f"Generated table for {request.slide_id}: "
                f"{table_stats['rows']}x{table_stats['columns']} "
                f"({table_stats['data_points']} data points)"
            )

            return GeneratedTable(
                html=html_table,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Error generating table for {request.slide_id}: {e}")
            raise

    def _clean_html_output(self, content: str) -> str:
        """
        Clean LLM output to extract pure HTML table.

        Removes markdown code blocks and explanatory text.
        """
        # Remove markdown code blocks
        content = content.strip()
        if content.startswith("```html"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        return content.strip()

    def _analyze_table(self, html_table: str) -> Dict[str, Any]:
        """
        Analyze HTML table structure.

        Args:
            html_table: HTML table string

        Returns:
            Dictionary with table statistics
        """
        import re

        stats = {
            "rows": 0,
            "columns": 0,
            "data_points": 0,
            "has_header": False,
            "numeric_columns": 0,
            "classes": []
        }

        # Count rows
        tbody_rows = len(re.findall(r'<tr[^>]*>(?:(?!</tr>).)*</tr>', html_table, re.DOTALL))
        stats["rows"] = tbody_rows

        # Check for header
        has_thead = '<thead>' in html_table
        stats["has_header"] = has_thead

        # Count columns (from first row)
        first_row = re.search(r'<tr[^>]*>((?:(?!</tr>).)*)</tr>', html_table, re.DOTALL)
        if first_row:
            th_count = len(re.findall(r'<th[^>]*>', first_row.group(1)))
            td_count = len(re.findall(r'<td[^>]*>', first_row.group(1)))
            stats["columns"] = max(th_count, td_count)

        # Estimate data points
        stats["data_points"] = stats["rows"] * stats["columns"]

        # Count numeric columns (rough estimate)
        numeric_classes = re.findall(r'class="[^"]*numeric[^"]*"', html_table)
        stats["numeric_columns"] = len(set(numeric_classes))

        # Extract classes used
        all_classes = re.findall(r'class="([^"]+)"', html_table)
        stats["classes"] = sorted(set(' '.join(all_classes).split()))

        return stats


# Convenience functions for direct usage

async def generate_text_content(request: TextGenerationRequest) -> GeneratedText:
    """
    Generate text content (convenience function).

    Args:
        request: Text generation request

    Returns:
        GeneratedText response
    """
    generator = TextGenerator()
    return await generator.generate(request)


async def generate_table_content(request: TableGenerationRequest) -> GeneratedTable:
    """
    Generate table content (convenience function).

    Args:
        request: Table generation request

    Returns:
        GeneratedTable response
    """
    generator = TableGenerator()
    return await generator.generate(request)


# ============================================================================
# v1.1: Structured Text Generator with Format Ownership
# ============================================================================

class StructuredTextGenerator:
    """
    Format-aware text generator (v1.1).

    Implements format ownership architecture where:
    - plain_text fields → generated as plain text (Layout Builder formats)
    - html fields → generated as rich HTML (Text Service formats)

    Uses 90% threshold validation (hit 90% of any limit: chars, words, or lines).
    """

    def __init__(
        self,
        llm_client: Optional[BaseLLMClient] = None,
        session_manager: Optional[SessionManager] = None
    ):
        """
        Initialize structured text generator.

        Args:
            llm_client: LLM client for generation
            session_manager: Session manager for context
        """
        self.llm_client = llm_client or get_llm_client()
        self.session_manager = session_manager or get_session_manager()

    async def generate(self, request: StructuredTextGenerationRequest) -> Dict[str, Any]:
        """
        Generate content for all fields based on format specifications.

        Args:
            request: Structured text generation request with field specifications

        Returns:
            Dictionary with generated content for each field
        """
        start_time = time.time()

        try:
            # Get session context
            session = await self.session_manager.get_or_create_session(
                presentation_id=request.presentation_id,
                presentation_theme=request.content_guidance.get("presentation_context", {}).get("theme"),
                target_audience=request.content_guidance.get("presentation_context", {}).get("audience")
            )

            # Get previous slides context
            previous_context = await self.session_manager.get_context_summary(
                request.presentation_id,
                max_slides=1
            )

            # Generate content for each field
            generated_content = {}
            field_metadata = {}

            for field_name, field_spec in request.field_specifications.items():
                logger.info(f"Generating {field_spec.format_type} content for field: {field_name}")

                if field_spec.format_owner == "text_service":
                    # Text Service owns formatting
                    if field_spec.format_type == "plain_text":
                        content, metadata = await self._generate_plain_text(
                            field_name, field_spec, request
                        )
                    else:  # html
                        content, metadata = await self._generate_html_content(
                            field_name, field_spec, request, previous_context
                        )

                    generated_content[field_name] = content
                    field_metadata[field_name] = metadata

                else:  # layout_builder owns formatting
                    # Generate plain text only (Layout Builder will format)
                    content, metadata = await self._generate_plain_text(
                        field_name, field_spec, request
                    )
                    generated_content[field_name] = content
                    field_metadata[field_name] = metadata

            # Build overall metadata
            generation_time = time.time() - start_time
            result = {
                "layout_id": request.layout_id,
                "content": generated_content,
                "metadata": {
                    "generation_time_ms": round(generation_time * 1000, 2),
                    "fields_generated": len(generated_content),
                    "field_metadata": field_metadata
                }
            }

            # Update session
            slide_context = SlideContext(
                slide_id=request.slide_id,
                slide_number=request.slide_number,
                slide_title=generated_content.get("slide_title", request.content_guidance.get("title")),
                content_summary=f"Structured content for {request.layout_name}",
                key_themes=request.content_guidance.get("key_points", [])[:3],
                content_type="structured"
            )

            await self.session_manager.add_slide_to_session(
                request.presentation_id,
                slide_context
            )

            logger.info(
                f"Generated structured content for {request.slide_id} ({request.layout_id}): "
                f"{len(generated_content)} fields in {generation_time:.2f}s"
            )

            return result

        except Exception as e:
            logger.error(f"Error generating structured content for {request.slide_id}: {e}")
            raise

    async def _generate_plain_text(
        self,
        field_name: str,
        field_spec: FieldSpec,
        request: StructuredTextGenerationRequest
    ) -> tuple[str, Dict[str, Any]]:
        """
        Generate plain text content for a field.

        For plain_text fields owned by layout_builder, we generate
        simple text without HTML formatting.

        Args:
            field_name: Name of the field
            field_spec: Field specification
            request: Full request context

        Returns:
            Tuple of (content, metadata)
        """
        # Build prompt for plain text generation
        prompt = f"""Generate plain text content for the '{field_name}' field.

Layout: {request.layout_name} ({request.layout_id})
Field Type: {field_spec.type}
Content Guidance:
- Title: {request.content_guidance.get('title', 'N/A')}
- Narrative: {request.content_guidance.get('narrative', 'N/A')}
- Key Points: {', '.join(request.content_guidance.get('key_points', []))}

Constraints:
- Max characters: {field_spec.max_chars or 'flexible'}
- Max lines: {field_spec.max_lines or 'flexible'}
- Format: Plain text ONLY (no HTML, no formatting)

Generate concise, clear text that fits within the constraints. Return ONLY the plain text content, nothing else."""

        # Generate using LLM
        llm_response = await self.llm_client.generate(prompt)
        content = llm_response.content.strip()

        # Validate against constraints
        validation = self._validate_plain_text(content, field_spec)

        metadata = {
            "format_type": "plain_text",
            "format_owner": field_spec.format_owner,
            "char_count": len(content),
            "line_count": len(content.split('\n')),
            "validation": validation,
            "model_used": llm_response.model
        }

        return content, metadata

    async def _generate_html_content(
        self,
        field_name: str,
        field_spec: FieldSpec,
        request: StructuredTextGenerationRequest,
        previous_context: Optional[str] = None
    ) -> tuple[str, Dict[str, Any]]:
        """
        Generate HTML content for a field.

        For html fields owned by text_service, we generate rich HTML
        with proper structure (ul>li, p, etc.) and validate density.

        Args:
            field_name: Name of the field
            field_spec: Field specification
            request: Full request context
            previous_context: Context from previous slides

        Returns:
            Tuple of (content, metadata)
        """
        # Build prompt for HTML generation
        prompt = f"""Generate HTML content for the '{field_name}' field.

Layout: {request.layout_name} ({request.layout_id})
Field Type: {field_spec.type}
Content Guidance:
- Title: {request.content_guidance.get('title', 'N/A')}
- Narrative: {request.content_guidance.get('narrative', 'N/A')}
- Key Points: {', '.join(request.content_guidance.get('key_points', []))}

HTML Structure Requirements:
- Expected structure: {field_spec.expected_structure or 'flexible'}
- Use semantic HTML tags
- NO empty elements (filter out empty <li>, <p>, etc.)
- Ensure proper nesting for sub-bullets (use nested <ul> or <ol>)

Content Constraints (90% Threshold):
- Max characters: {field_spec.max_chars or 'flexible'}
- Max lines: {field_spec.max_lines or 'flexible'}
- Validation threshold: {field_spec.validation_threshold or 0.9}
- Goal: Hit at least {int((field_spec.validation_threshold or 0.9) * 100)}% of ANY limit for visual balance

{f"Previous slide context:\\n{previous_context}" if previous_context else ""}

Generate rich, well-formatted HTML content. Ensure good visual density without overcrowding.
Return ONLY the HTML content, no markdown code blocks or explanations."""

        # Generate using LLM
        llm_response = await self.llm_client.generate(prompt)
        html_content = self._clean_html_output(llm_response.content)

        # Validate HTML density (90% threshold)
        validation = self._validate_html_density(html_content, field_spec)

        # Extract HTML structure info
        html_tags = self._extract_html_tags(html_content)
        word_count = self._count_words(html_content)

        metadata = {
            "format_type": "html",
            "format_owner": field_spec.format_owner,
            "char_count": len(html_content),
            "word_count": word_count,
            "html_tags_used": html_tags,
            "validation": validation,
            "model_used": llm_response.model
        }

        return html_content, metadata

    def _validate_plain_text(
        self,
        content: str,
        field_spec: FieldSpec
    ) -> Dict[str, Any]:
        """
        Validate plain text against constraints.

        Args:
            content: Generated plain text
            field_spec: Field specification

        Returns:
            Validation result dictionary
        """
        char_count = len(content)
        line_count = len(content.split('\n'))

        validation = {
            "valid": True,
            "violations": []
        }

        if field_spec.max_chars and char_count > field_spec.max_chars:
            validation["valid"] = False
            validation["violations"].append(
                f"Exceeds max_chars: {char_count} > {field_spec.max_chars}"
            )

        if field_spec.max_lines and line_count > field_spec.max_lines:
            validation["valid"] = False
            validation["violations"].append(
                f"Exceeds max_lines: {line_count} > {field_spec.max_lines}"
            )

        return validation

    def _validate_html_density(
        self,
        html_content: str,
        field_spec: FieldSpec
    ) -> Dict[str, Any]:
        """
        Validate HTML content using 90% threshold model.

        Checks if content hits at least 90% of ANY limit (chars, words, or lines).
        This ensures visual balance without rigid constraints.

        Args:
            html_content: Generated HTML
            field_spec: Field specification

        Returns:
            Validation result with density metrics
        """
        import re

        # Metrics
        char_count = len(html_content)
        word_count = self._count_words(html_content)
        line_count = len(html_content.split('\n'))

        threshold = field_spec.validation_threshold or 0.9
        densities = []

        # Calculate density for each constraint
        if field_spec.max_chars:
            char_density = char_count / field_spec.max_chars
            densities.append(("chars", char_density, char_count, field_spec.max_chars))

        if field_spec.max_words:
            word_density = word_count / field_spec.max_words
            densities.append(("words", word_density, word_count, field_spec.max_words))

        if field_spec.max_lines:
            line_density = line_count / field_spec.max_lines
            densities.append(("lines", line_density, line_count, field_spec.max_lines))

        # Validation result
        max_density = max([d[1] for d in densities]) if densities else 0
        meets_threshold = max_density >= threshold

        validation = {
            "valid": max_density <= 1.0,  # Must not exceed any limit
            "meets_threshold": meets_threshold,
            "max_density": round(max_density, 2),
            "threshold": threshold,
            "densities": {
                d[0]: {
                    "density": round(d[1], 2),
                    "actual": d[2],
                    "max": d[3]
                }
                for d in densities
            },
            "violations": []
        }

        # Check for violations
        for metric, density, actual, max_val in densities:
            if density > 1.0:
                validation["violations"].append(
                    f"Exceeds {metric} limit: {actual} > {max_val}"
                )

        if not meets_threshold:
            validation["warnings"] = [
                f"Content density ({max_density:.0%}) below threshold ({threshold:.0%}). "
                f"Consider adding more content for better visual balance."
            ]

        return validation

    def _clean_html_output(self, content: str) -> str:
        """Clean LLM output to extract pure HTML."""
        content = content.strip()
        if content.startswith("```html"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return content.strip()

    def _count_words(self, html_content: str) -> int:
        """Count words in HTML content (excluding tags)."""
        import re
        text_only = re.sub(r'<[^>]+>', '', html_content)
        words = text_only.split()
        return len(words)

    def _extract_html_tags(self, html_content: str) -> List[str]:
        """Extract list of unique HTML tags used."""
        import re
        tags = re.findall(r'<(\w+)', html_content)
        return sorted(set(tags))


async def generate_structured_content(request: StructuredTextGenerationRequest) -> Dict[str, Any]:
    """
    Generate structured content with format specifications (v1.1 convenience function).

    Args:
        request: Structured text generation request

    Returns:
        Dictionary with generated content and metadata
    """
    generator = StructuredTextGenerator()
    return await generator.generate(request)


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_generators():
        """Test text and table generators."""

        # Test text generation
        text_request = TextGenerationRequest(
            presentation_id="test_pres_001",
            slide_id="slide_001",
            slide_number=1,
            topics=["Revenue growth", "Market expansion", "Cost efficiency"],
            narrative="Strong Q3 performance across all metrics",
            context={
                "theme": "professional",
                "audience": "executives",
                "slide_title": "Q3 Results"
            },
            constraints={
                "max_characters": 250
            }
        )

        print("Generating text content...")
        text_result = await generate_text_content(text_request)

        print("\n" + "="*80)
        print("TEXT GENERATION RESULT:")
        print("="*80)
        print(f"Content: {text_result.content[:200]}...")
        print(f"Metadata: {json.dumps(text_result.metadata, indent=2)}")

        # Test table generation
        table_request = TableGenerationRequest(
            presentation_id="test_pres_001",
            slide_id="slide_002",
            slide_number=2,
            description="Regional revenue comparison Q2 vs Q3",
            data={
                "Q2": {"North America": 45.2, "Europe": 32.1, "Asia": 28.7},
                "Q3": {"North America": 58.3, "Europe": 39.4, "Asia": 35.6}
            },
            context={
                "theme": "professional",
                "audience": "executives",
                "slide_title": "Regional Performance"
            }
        )

        print("\n\nGenerating table content...")
        table_result = await generate_table_content(table_request)

        print("\n" + "="*80)
        print("TABLE GENERATION RESULT:")
        print("="*80)
        print(f"HTML: {table_result.html[:300]}...")
        print(f"Metadata: {json.dumps(table_result.metadata, indent=2)}")

    asyncio.run(test_generators())
