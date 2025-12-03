"""
Text Generators for Layout Service Integration

Three generators for text-related operations:
- TextGenerateGenerator: Generate new text content from prompt
- TextTransformGenerator: Transform existing text (expand, condense, etc.)
- TextAutofitGenerator: Fit text to element dimensions

All generators produce HTML with inline CSS suitable for reveal.js slides.
"""

import logging
import json
from typing import Dict, Any, Callable, List, Optional

from .base_layout_generator import BaseLayoutGenerator
from .grid_calculator import GridCalculator
from app.models.layout_models import (
    TextGenerateRequest,
    TextGenerateResponse,
    TextTransformRequest,
    TextTransformResponse,
    TextAutofitRequest,
    TextAutofitResponse,
    TextContentData,
    TextTransformData,
    TextContent,
    ContentMetadata,
    ContentSuggestions,
    TransformChanges,
    AutofitResult,
    ErrorDetails,
    TextTone,
    TextFormat,
    TextTransformation,
    AutofitStrategy
)

logger = logging.getLogger(__name__)


class TextGenerateGenerator(BaseLayoutGenerator[TextGenerateRequest, TextGenerateResponse]):
    """
    Generate new text content from a prompt.

    Creates HTML content with inline CSS that fits within grid constraints.
    Optionally generates alternative versions for the suggestions feature.
    """

    @property
    def generator_type(self) -> str:
        return "text_generate"

    async def _build_prompt(self, request: TextGenerateRequest) -> str:
        """Build prompt for text generation."""
        # Calculate constraints
        max_chars = request.constraints.maxCharacters
        if not max_chars:
            max_chars = GridCalculator.calculate_max_characters(
                request.constraints.gridWidth,
                request.constraints.gridHeight
            )

        min_chars = request.constraints.minCharacters
        if not min_chars:
            min_chars = GridCalculator.calculate_min_characters(
                request.constraints.gridWidth,
                request.constraints.gridHeight
            )

        # Get guidelines for format recommendations
        guidelines = GridCalculator.get_content_guidelines(
            request.constraints.gridWidth,
            request.constraints.gridHeight
        )

        # Extract options
        options = request.options or {}
        tone = getattr(options, 'tone', TextTone.PROFESSIONAL) or TextTone.PROFESSIONAL
        format_type = getattr(options, 'format', TextFormat.PARAGRAPH) or TextFormat.PARAGRAPH
        bullet_style = getattr(options, 'bulletStyle', None)
        include_emoji = getattr(options, 'includeEmoji', False)

        # Build context section
        context_str = self._build_context_section(request.context)

        prompt = f"""Generate HTML text content for a presentation slide element.

## CONTEXT
{context_str}

## USER REQUEST
{request.prompt}

## CONSTRAINTS
- Character limit: {min_chars}-{max_chars} characters (text content only, not HTML tags)
- Grid size: {request.constraints.gridWidth} columns x {request.constraints.gridHeight} rows
- Recommended format: {guidelines['recommendations']['preferred_format']}
- Lines available: ~{guidelines['layout']['lines']}
- Characters per line: ~{guidelines['layout']['chars_per_line']}

## STYLE REQUIREMENTS
- Tone: {tone.value}
- Format: {format_type.value}
{f"- Bullet style: {bullet_style.value}" if bullet_style else ""}
{f"- Emoji allowed: Yes" if include_emoji else "- Emoji: Do NOT include emoji"}

## OUTPUT FORMAT
Generate ONLY the HTML content with inline CSS styles. The content will be placed inside a reveal.js slide container.

Use these styling guidelines:
- Font family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif
- Base font size: 1.1rem (will scale with reveal.js)
- Line height: 1.6
- Text color: #1f2937 (dark gray)
- For paragraphs: Use <p> tags with margin-bottom: 0.8em
- For bullet lists: Use <ul> with list-style-type appropriate to style
- For numbered lists: Use <ol>
- For headlines: Use <h2> or <h3> with font-weight: 600

## EXAMPLE OUTPUT (for paragraph format)
<p style="font-family: 'Inter', sans-serif; font-size: 1.1rem; line-height: 1.6; color: #1f2937; margin: 0;">
Your generated content here that addresses the user's request while staying within character limits.
</p>

## EXAMPLE OUTPUT (for bullet format)
<ul style="font-family: 'Inter', sans-serif; font-size: 1.1rem; line-height: 1.8; color: #1f2937; margin: 0; padding-left: 1.5em; list-style-type: disc;">
  <li style="margin-bottom: 0.5em;">First key point</li>
  <li style="margin-bottom: 0.5em;">Second key point</li>
  <li style="margin-bottom: 0.5em;">Third key point</li>
</ul>

## INSTRUCTIONS
1. Generate content that directly addresses the user's request
2. Stay within {min_chars}-{max_chars} characters (text only)
3. Use {tone.value} tone throughout
4. Format as {format_type.value}
5. Include inline CSS for all styling
6. Return ONLY the HTML - no explanations or markdown wrappers

Generate the HTML content now:"""

        return prompt

    async def _generate_suggestions(
        self,
        primary_html: str,
        request: TextGenerateRequest,
        max_chars: int
    ) -> ContentSuggestions:
        """
        Generate alternative versions and suggestion hints.

        Args:
            primary_html: The primary generated content
            request: Original request
            max_chars: Maximum character limit

        Returns:
            ContentSuggestions with alternatives and hints
        """
        char_count = self._count_characters(primary_html)

        # Determine expandable/reducible
        min_chars = request.constraints.minCharacters or GridCalculator.calculate_min_characters(
            request.constraints.gridWidth,
            request.constraints.gridHeight
        )

        expandable = char_count < max_chars * 0.6
        reducible = char_count > min_chars * 1.5

        # Generate alternatives via second LLM call
        alternatives = []
        try:
            alt_prompt = f"""Generate 2 alternative versions of this content.
Each version should convey the same core message but with different:
- Word choice
- Sentence structure
- Emphasis

Original content:
{primary_html}

Requirements:
- Stay within {max_chars} characters (text only, not HTML)
- Keep the same HTML structure and styling
- Return as a JSON array of 2 HTML strings

Return ONLY the JSON array, no explanation:
["<first alternative HTML>", "<second alternative HTML>"]"""

            alt_response = await self.llm_service(alt_prompt)
            parsed = self._parse_json_from_response(alt_response)

            if parsed and isinstance(parsed, list):
                alternatives = [self._clean_html(alt) for alt in parsed[:2]]

        except Exception as e:
            logger.warning(f"Failed to generate alternatives: {e}")

        return ContentSuggestions(
            alternativeVersions=alternatives,
            expandable=expandable,
            reducible=reducible
        )

    async def _build_response(
        self,
        content: str,
        request: TextGenerateRequest,
        generation_id: str
    ) -> TextGenerateResponse:
        """Build the response object with metadata and suggestions."""
        # Calculate metrics
        char_count = self._count_characters(content)
        word_count = self._count_words(content)
        read_time = self._estimate_read_time(word_count)

        # Get options
        options = request.options or {}
        tone = getattr(options, 'tone', TextTone.PROFESSIONAL) or TextTone.PROFESSIONAL
        format_type = getattr(options, 'format', TextFormat.PARAGRAPH) or TextFormat.PARAGRAPH

        # Calculate max chars for suggestions
        max_chars = request.constraints.maxCharacters
        if not max_chars:
            max_chars = GridCalculator.calculate_max_characters(
                request.constraints.gridWidth,
                request.constraints.gridHeight
            )

        # Generate suggestions
        suggestions = await self._generate_suggestions(content, request, max_chars)

        return TextGenerateResponse(
            success=True,
            data=TextContentData(
                generationId=generation_id,
                content=TextContent(html=content),
                metadata=ContentMetadata(
                    characterCount=char_count,
                    wordCount=word_count,
                    estimatedReadTime=read_time,
                    format=format_type,
                    tone=tone
                ),
                suggestions=suggestions
            )
        )


class TextTransformGenerator(BaseLayoutGenerator[TextTransformRequest, TextTransformResponse]):
    """
    Transform existing text content.

    Supports operations: expand, condense, simplify, formalize, casualize,
    bulletize, paragraphize, rephrase, proofread, translate.
    """

    @property
    def generator_type(self) -> str:
        return "text_transform"

    def _get_transformation_instruction(self, transformation: TextTransformation) -> str:
        """Get specific instruction for transformation type."""
        instructions = {
            TextTransformation.EXPAND: "Add more detail, examples, and explanation while keeping the core message",
            TextTransformation.CONDENSE: "Shorten the content while preserving the key points and meaning",
            TextTransformation.SIMPLIFY: "Use simpler words and shorter sentences for easier understanding",
            TextTransformation.FORMALIZE: "Make the language more professional and formal",
            TextTransformation.CASUALIZE: "Make the language more conversational and approachable",
            TextTransformation.BULLETIZE: "Convert the content into a bullet point list",
            TextTransformation.PARAGRAPHIZE: "Convert bullet points into flowing paragraph(s)",
            TextTransformation.REPHRASE: "Rewrite with different words while keeping the same meaning",
            TextTransformation.PROOFREAD: "Fix grammar, spelling, and punctuation errors",
            TextTransformation.TRANSLATE: "Translate to the target language while maintaining meaning"
        }
        return instructions.get(transformation, "Transform the content as requested")

    async def _build_prompt(self, request: TextTransformRequest) -> str:
        """Build prompt for text transformation."""
        # Calculate constraints
        max_chars = request.constraints.maxCharacters
        if not max_chars:
            max_chars = GridCalculator.calculate_max_characters(
                request.constraints.gridWidth,
                request.constraints.gridHeight
            )

        instruction = self._get_transformation_instruction(request.transformation)

        # Build context
        context_str = self._build_context_section(request.context)

        prompt = f"""Transform the given HTML content according to the specified operation.

## CONTEXT
{context_str}

## ORIGINAL CONTENT
{request.sourceContent}

## TRANSFORMATION
Operation: {request.transformation.value}
Instruction: {instruction}

## CONSTRAINTS
- Maximum characters: {max_chars} (text content only, not HTML tags)
- Grid size: {request.constraints.gridWidth} columns x {request.constraints.gridHeight} rows

## REQUIREMENTS
1. Perform the {request.transformation.value} transformation
2. Preserve the HTML structure and inline CSS styling
3. Stay within the character limit
4. Return ONLY the transformed HTML - no explanations

## OUTPUT
Return the transformed HTML content:"""

        return prompt

    async def _build_response(
        self,
        content: str,
        request: TextTransformRequest,
        generation_id: str
    ) -> TextTransformResponse:
        """Build the response object with change tracking."""
        # Calculate metrics
        char_count = self._count_characters(content)
        word_count = self._count_words(content)
        read_time = self._estimate_read_time(word_count)

        # Calculate original metrics for comparison
        original_char_count = self._count_characters(request.sourceContent)
        char_delta = char_count - original_char_count

        # Get options
        options = request.options or {}
        tone = getattr(options, 'tone', TextTone.PROFESSIONAL) or TextTone.PROFESSIONAL
        format_type = getattr(options, 'format', TextFormat.MIXED) or TextFormat.MIXED

        # Determine significant changes
        significant_changes = []
        if abs(char_delta) > 50:
            if char_delta > 0:
                significant_changes.append(f"Content expanded by {char_delta} characters")
            else:
                significant_changes.append(f"Content condensed by {abs(char_delta)} characters")

        significant_changes.append(f"Applied {request.transformation.value} transformation")

        return TextTransformResponse(
            success=True,
            data=TextTransformData(
                transformationId=generation_id,
                content=TextContent(html=content),
                changes=TransformChanges(
                    characterDelta=char_delta,
                    significantChanges=significant_changes
                ),
                metadata=ContentMetadata(
                    characterCount=char_count,
                    wordCount=word_count,
                    estimatedReadTime=read_time,
                    format=format_type,
                    tone=tone
                )
            )
        )


class TextAutofitGenerator(BaseLayoutGenerator[TextAutofitRequest, TextAutofitResponse]):
    """
    Auto-fit text content to element dimensions.

    Strategies:
    - reduce_font: Suggest smaller font size
    - truncate: Cut content with ellipsis
    - smart_condense: AI-powered content shortening
    - overflow: Allow overflow (return unchanged)
    """

    @property
    def generator_type(self) -> str:
        return "text_autofit"

    async def _build_prompt(self, request: TextAutofitRequest) -> str:
        """Build prompt for autofit operation."""
        max_chars = GridCalculator.calculate_max_characters(
            request.targetFit.gridWidth,
            request.targetFit.gridHeight
        )

        current_chars = self._count_characters(request.content)

        # Only need AI for smart_condense
        if request.strategy != AutofitStrategy.SMART_CONDENSE:
            return ""  # Will be handled in generate() override

        prompt = f"""Condense the following HTML content to fit within {max_chars} characters while preserving the key message.

## ORIGINAL CONTENT
{request.content}

## CURRENT LENGTH
{current_chars} characters

## TARGET LENGTH
Maximum {max_chars} characters (text only, not HTML tags)

## REQUIREMENTS
1. {"Preserve the formatting structure (bullets, paragraphs)" if request.preserveFormatting else "You may change the formatting structure"}
2. Keep the most important information
3. Maintain inline CSS styling
4. Return ONLY the condensed HTML

## OUTPUT
Return the condensed HTML:"""

        return prompt

    async def generate(self, request: TextAutofitRequest) -> TextAutofitResponse:
        """
        Override generate to handle non-AI strategies.
        """
        generation_id = self._generate_id()
        current_chars = self._count_characters(request.content)
        max_chars = GridCalculator.calculate_max_characters(
            request.targetFit.gridWidth,
            request.targetFit.gridHeight
        )

        # Check if content already fits
        fits = current_chars <= max_chars

        if fits or request.strategy == AutofitStrategy.OVERFLOW:
            # Content fits or user wants overflow - return unchanged
            return TextAutofitResponse(
                success=True,
                data=AutofitResult(
                    content=request.content,
                    recommendedFontSize=None,
                    fits=fits,
                    overflow={
                        "hasOverflow": not fits,
                        "overflowCharacters": max(0, current_chars - max_chars)
                    } if not fits else None
                )
            )

        if request.strategy == AutofitStrategy.REDUCE_FONT:
            # Calculate recommended font size
            # If content is 20% over, reduce font by ~15%
            overflow_ratio = current_chars / max_chars
            base_font = 18  # Base font size in pixels
            recommended_font = max(12, int(base_font / (overflow_ratio ** 0.5)))

            return TextAutofitResponse(
                success=True,
                data=AutofitResult(
                    content=request.content,
                    recommendedFontSize=recommended_font,
                    fits=False,
                    overflow={
                        "hasOverflow": True,
                        "overflowCharacters": current_chars - max_chars,
                        "suggestion": f"Reduce font size to {recommended_font}px"
                    }
                )
            )

        if request.strategy == AutofitStrategy.TRUNCATE:
            # Simple truncation with ellipsis
            text = self._extract_text_from_html(request.content)
            truncated_text = text[:max_chars - 3] + "..."

            # Wrap in basic styling
            truncated_html = f'<p style="font-family: \'Inter\', sans-serif; font-size: 1.1rem; line-height: 1.6; color: #1f2937;">{truncated_text}</p>'

            return TextAutofitResponse(
                success=True,
                data=AutofitResult(
                    content=truncated_html,
                    recommendedFontSize=None,
                    fits=True,
                    overflow=None
                )
            )

        # SMART_CONDENSE - use AI
        return await super().generate(request)

    async def _build_response(
        self,
        content: str,
        request: TextAutofitRequest,
        generation_id: str
    ) -> TextAutofitResponse:
        """Build response for smart_condense strategy."""
        char_count = self._count_characters(content)
        max_chars = GridCalculator.calculate_max_characters(
            request.targetFit.gridWidth,
            request.targetFit.gridHeight
        )

        fits = char_count <= max_chars

        return TextAutofitResponse(
            success=True,
            data=AutofitResult(
                content=content,
                recommendedFontSize=None,
                fits=fits,
                overflow={
                    "hasOverflow": not fits,
                    "overflowCharacters": max(0, char_count - max_chars)
                } if not fits else None
            )
        )
