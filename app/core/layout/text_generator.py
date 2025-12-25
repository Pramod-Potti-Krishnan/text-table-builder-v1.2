"""
Text Generators for Layout Service Integration v2.0

Three generators for text-related operations:
- TextGenerateGenerator: Generate new text content from prompt
- TextTransformGenerator: Transform existing text (expand, condense, etc.)
- TextAutofitGenerator: Fit text to element dimensions

All generators produce HTML with inline CSS suitable for reveal.js slides.

Updated for 32×18 grid system (1920×1080px HD slides, 60×60px cells)
with font-aware character calculations and theme integration.
"""

import logging
import json
from typing import Dict, Any, Callable, List, Optional

from .base_layout_generator import BaseLayoutGenerator
from .grid_calculator import GridCalculator, TypographySpec
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
from app.services import (
    get_default_typography,
    FONT_CHAR_WIDTH_RATIOS,
    TypographyTheme
)

logger = logging.getLogger(__name__)


class TextGenerateGenerator(BaseLayoutGenerator[TextGenerateRequest, TextGenerateResponse]):
    """
    Generate new text content from a prompt.

    Creates HTML content with inline CSS that fits within grid constraints.
    Optionally generates alternative versions for the suggestions feature.

    Updated for 32×18 grid system with font-aware character calculations.
    """

    def __init__(self):
        """Initialize with default typography."""
        super().__init__()
        self._typography_theme: Optional[TypographyTheme] = None

    def _get_typography_theme(self) -> TypographyTheme:
        """Get typography theme (cached)."""
        if self._typography_theme is None:
            self._typography_theme = get_default_typography()
        return self._typography_theme

    def _get_char_width_ratio(self, font_family: str) -> float:
        """Get character width ratio for font family."""
        font_lower = font_family.lower()
        for font, ratio in FONT_CHAR_WIDTH_RATIOS.items():
            if font in font_lower:
                return ratio
        return 0.5  # Default ratio

    @property
    def generator_type(self) -> str:
        return "text_generate"

    async def _build_prompt(self, request: TextGenerateRequest) -> str:
        """Build prompt for text generation with 32×18 grid constraints."""
        # Get outer/inner padding from constraints (with defaults)
        outer_padding = getattr(request.constraints, 'outerPadding', None) or GridCalculator.DEFAULT_OUTER_PADDING
        inner_padding = getattr(request.constraints, 'innerPadding', None) or GridCalculator.DEFAULT_INNER_PADDING

        # Get typography for body text
        theme = self._get_typography_theme()
        body_token = theme.get_token("body")
        char_width_ratio = self._get_char_width_ratio(theme.font_family)

        # Calculate element dimensions with new 32×18 grid
        dimensions = GridCalculator.calculate_element_dimensions(
            grid_width=request.constraints.gridWidth,
            grid_height=request.constraints.gridHeight,
            outer_padding=outer_padding,
            inner_padding=inner_padding
        )

        # Calculate text constraints based on typography
        text_constraints = GridCalculator.calculate_text_constraints(
            content_width=dimensions.content_width,
            content_height=dimensions.content_height,
            font_size=body_token.size,
            line_height=body_token.line_height,
            char_width_ratio=char_width_ratio
        )

        # Use explicit constraints if provided, otherwise use calculated
        max_chars = request.constraints.maxCharacters or text_constraints.max_characters
        min_chars = request.constraints.minCharacters or text_constraints.min_characters

        # Get comprehensive guidelines
        guidelines = GridCalculator.get_content_guidelines(
            request.constraints.gridWidth,
            request.constraints.gridHeight,
            text_type="body",
            outer_padding=outer_padding,
            inner_padding=inner_padding
        )

        # Extract options
        options = request.options or {}
        tone = getattr(options, 'tone', TextTone.PROFESSIONAL) or TextTone.PROFESSIONAL
        format_type = getattr(options, 'format', TextFormat.PARAGRAPH) or TextFormat.PARAGRAPH
        bullet_style = getattr(options, 'bulletStyle', None)
        include_emoji = getattr(options, 'includeEmoji', False)

        # Build context section
        context_str = self._build_context_section(request.context)

        # Get typography info for prompt
        font_family = theme.font_family
        text_layout = guidelines.get('text', {}).get('layout', {})
        lines_available = text_layout.get('lines', text_constraints.max_lines)
        chars_per_line = text_layout.get('chars_per_line', text_constraints.chars_per_line)

        prompt = f"""Generate HTML text content for a presentation slide element.

## CONTEXT
{context_str}

## USER REQUEST
{request.prompt}

## CONSTRAINTS (32×18 Grid System)
- Grid size: {request.constraints.gridWidth} columns × {request.constraints.gridHeight} rows (60px per cell)
- Element dimensions: {dimensions.element_width:.0f}px × {dimensions.element_height:.0f}px
- Content area: {dimensions.content_width:.0f}px × {dimensions.content_height:.0f}px (after padding)
- Character limit: {min_chars}-{max_chars} characters (text content only, not HTML tags)
- Lines available: ~{lines_available}
- Characters per line: ~{chars_per_line}
- Recommended format: {guidelines.get('recommendations', {}).get('preferred_format', 'paragraph')}

## STYLE REQUIREMENTS
- Tone: {tone.value}
- Format: {format_type.value}
{f"- Bullet style: {bullet_style.value}" if bullet_style else ""}
{f"- Emoji allowed: Yes" if include_emoji else "- Emoji: Do NOT include emoji"}

## OUTPUT FORMAT
Generate ONLY the HTML content with inline CSS styles. The content will be placed inside a reveal.js slide container.

Use these styling guidelines from theme typography:
- Font family: '{font_family}'
- Font size: {body_token.size}px
- Line height: {body_token.line_height}
- Text color: {body_token.color}
- Font weight: {body_token.weight}
- For paragraphs: Use <p> tags with margin-bottom: 0.8em
- For bullet lists: Use <ul> with list-style-type: {theme.list_styles.bullet_type}
- For numbered lists: Use <ol>
- For headlines: Use <h2> or <h3> with font-weight: 600

## EXAMPLE OUTPUT (for paragraph format)
<p style="font-family: '{font_family}'; font-size: {body_token.size}px; line-height: {body_token.line_height}; color: {body_token.color}; font-weight: {body_token.weight}; margin: 0;">
Your generated content here that addresses the user's request while staying within character limits.
</p>

## EXAMPLE OUTPUT (for bullet format)
<ul style="font-family: '{font_family}'; font-size: {body_token.size}px; line-height: {body_token.line_height * 1.1}; color: {body_token.color}; margin: 0; padding-left: {theme.list_styles.list_indent}; list-style-type: {theme.list_styles.bullet_type};">
  <li style="margin-bottom: {theme.list_styles.item_spacing};">First key point</li>
  <li style="margin-bottom: {theme.list_styles.item_spacing};">Second key point</li>
  <li style="margin-bottom: {theme.list_styles.item_spacing};">Third key point</li>
</ul>

## INSTRUCTIONS
1. Generate content that directly addresses the user's request
2. Stay within {min_chars}-{max_chars} characters (text only)
3. Use {tone.value} tone throughout
4. Format as {format_type.value}
5. Include inline CSS for all styling using the typography values above
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

        # Get padding values
        outer_padding = getattr(request.constraints, 'outerPadding', None) or GridCalculator.DEFAULT_OUTER_PADDING
        inner_padding = getattr(request.constraints, 'innerPadding', None) or GridCalculator.DEFAULT_INNER_PADDING

        # Calculate min_chars using new grid system
        if request.constraints.minCharacters:
            min_chars = request.constraints.minCharacters
        else:
            theme = self._get_typography_theme()
            body_token = theme.get_token("body")
            char_width_ratio = self._get_char_width_ratio(theme.font_family)

            dimensions = GridCalculator.calculate_element_dimensions(
                grid_width=request.constraints.gridWidth,
                grid_height=request.constraints.gridHeight,
                outer_padding=outer_padding,
                inner_padding=inner_padding
            )
            text_constraints = GridCalculator.calculate_text_constraints(
                content_width=dimensions.content_width,
                content_height=dimensions.content_height,
                font_size=body_token.size,
                line_height=body_token.line_height,
                char_width_ratio=char_width_ratio
            )
            min_chars = text_constraints.min_characters

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

        # Calculate max chars using new 32×18 grid system
        if request.constraints.maxCharacters:
            max_chars = request.constraints.maxCharacters
        else:
            # Get padding values
            outer_padding = getattr(request.constraints, 'outerPadding', None) or GridCalculator.DEFAULT_OUTER_PADDING
            inner_padding = getattr(request.constraints, 'innerPadding', None) or GridCalculator.DEFAULT_INNER_PADDING

            theme = self._get_typography_theme()
            body_token = theme.get_token("body")
            char_width_ratio = self._get_char_width_ratio(theme.font_family)

            dimensions = GridCalculator.calculate_element_dimensions(
                grid_width=request.constraints.gridWidth,
                grid_height=request.constraints.gridHeight,
                outer_padding=outer_padding,
                inner_padding=inner_padding
            )
            text_constraints = GridCalculator.calculate_text_constraints(
                content_width=dimensions.content_width,
                content_height=dimensions.content_height,
                font_size=body_token.size,
                line_height=body_token.line_height,
                char_width_ratio=char_width_ratio
            )
            max_chars = text_constraints.max_characters

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

    Updated for 32×18 grid system with font-aware character calculations.
    """

    def __init__(self):
        """Initialize with default typography."""
        super().__init__()
        self._typography_theme: Optional[TypographyTheme] = None

    def _get_typography_theme(self) -> TypographyTheme:
        """Get typography theme (cached)."""
        if self._typography_theme is None:
            self._typography_theme = get_default_typography()
        return self._typography_theme

    def _get_char_width_ratio(self, font_family: str) -> float:
        """Get character width ratio for font family."""
        font_lower = font_family.lower()
        for font, ratio in FONT_CHAR_WIDTH_RATIOS.items():
            if font in font_lower:
                return ratio
        return 0.5  # Default ratio

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
        """Build prompt for text transformation with 32×18 grid constraints."""
        # Get outer/inner padding from constraints (with defaults)
        outer_padding = getattr(request.constraints, 'outerPadding', None) or GridCalculator.DEFAULT_OUTER_PADDING
        inner_padding = getattr(request.constraints, 'innerPadding', None) or GridCalculator.DEFAULT_INNER_PADDING

        # Get typography for body text
        theme = self._get_typography_theme()
        body_token = theme.get_token("body")
        char_width_ratio = self._get_char_width_ratio(theme.font_family)

        # Calculate element dimensions with new 32×18 grid
        dimensions = GridCalculator.calculate_element_dimensions(
            grid_width=request.constraints.gridWidth,
            grid_height=request.constraints.gridHeight,
            outer_padding=outer_padding,
            inner_padding=inner_padding
        )

        # Calculate text constraints based on typography
        text_constraints = GridCalculator.calculate_text_constraints(
            content_width=dimensions.content_width,
            content_height=dimensions.content_height,
            font_size=body_token.size,
            line_height=body_token.line_height,
            char_width_ratio=char_width_ratio
        )

        # Use explicit constraints if provided, otherwise use calculated
        max_chars = request.constraints.maxCharacters or text_constraints.max_characters

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

## CONSTRAINTS (32×18 Grid System)
- Grid size: {request.constraints.gridWidth} columns × {request.constraints.gridHeight} rows (60px per cell)
- Element dimensions: {dimensions.element_width:.0f}px × {dimensions.element_height:.0f}px
- Content area: {dimensions.content_width:.0f}px × {dimensions.content_height:.0f}px (after padding)
- Maximum characters: {max_chars} (text content only, not HTML tags)
- Lines available: ~{text_constraints.max_lines}
- Characters per line: ~{text_constraints.chars_per_line}

## STYLING (from theme typography)
- Font family: '{theme.font_family}'
- Font size: {body_token.size}px
- Line height: {body_token.line_height}
- Text color: {body_token.color}

## REQUIREMENTS
1. Perform the {request.transformation.value} transformation
2. Preserve or update the HTML structure and inline CSS styling
3. Stay within the character limit ({max_chars} characters max)
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

    Updated for 32×18 grid system with font-aware character calculations.
    """

    def __init__(self):
        """Initialize with default typography."""
        super().__init__()
        self._typography_theme: Optional[TypographyTheme] = None

    def _get_typography_theme(self) -> TypographyTheme:
        """Get typography theme (cached)."""
        if self._typography_theme is None:
            self._typography_theme = get_default_typography()
        return self._typography_theme

    def _get_char_width_ratio(self, font_family: str) -> float:
        """Get character width ratio for font family."""
        font_lower = font_family.lower()
        for font, ratio in FONT_CHAR_WIDTH_RATIOS.items():
            if font in font_lower:
                return ratio
        return 0.5  # Default ratio

    def _calculate_max_chars_for_target(self, target_fit) -> int:
        """Calculate max characters for target fit dimensions."""
        # Get padding values
        outer_padding = getattr(target_fit, 'outerPadding', None) or GridCalculator.DEFAULT_OUTER_PADDING
        inner_padding = getattr(target_fit, 'innerPadding', None) or GridCalculator.DEFAULT_INNER_PADDING

        # Get typography
        theme = self._get_typography_theme()
        body_token = theme.get_token("body")
        char_width_ratio = self._get_char_width_ratio(theme.font_family)

        # Calculate dimensions
        dimensions = GridCalculator.calculate_element_dimensions(
            grid_width=target_fit.gridWidth,
            grid_height=target_fit.gridHeight,
            outer_padding=outer_padding,
            inner_padding=inner_padding
        )

        # Calculate text constraints
        text_constraints = GridCalculator.calculate_text_constraints(
            content_width=dimensions.content_width,
            content_height=dimensions.content_height,
            font_size=body_token.size,
            line_height=body_token.line_height,
            char_width_ratio=char_width_ratio
        )

        return text_constraints.max_characters

    @property
    def generator_type(self) -> str:
        return "text_autofit"

    async def _build_prompt(self, request: TextAutofitRequest) -> str:
        """Build prompt for autofit operation with 32×18 grid constraints."""
        max_chars = self._calculate_max_chars_for_target(request.targetFit)

        current_chars = self._count_characters(request.content)

        # Only need AI for smart_condense
        if request.strategy != AutofitStrategy.SMART_CONDENSE:
            return ""  # Will be handled in generate() override

        # Get typography info for prompt
        theme = self._get_typography_theme()
        body_token = theme.get_token("body")

        # Get dimensions for context
        outer_padding = getattr(request.targetFit, 'outerPadding', None) or GridCalculator.DEFAULT_OUTER_PADDING
        inner_padding = getattr(request.targetFit, 'innerPadding', None) or GridCalculator.DEFAULT_INNER_PADDING

        dimensions = GridCalculator.calculate_element_dimensions(
            grid_width=request.targetFit.gridWidth,
            grid_height=request.targetFit.gridHeight,
            outer_padding=outer_padding,
            inner_padding=inner_padding
        )

        prompt = f"""Condense the following HTML content to fit within {max_chars} characters while preserving the key message.

## ORIGINAL CONTENT
{request.content}

## CURRENT LENGTH
{current_chars} characters (needs to reduce by {current_chars - max_chars} characters)

## TARGET CONSTRAINTS (32×18 Grid System)
- Grid size: {request.targetFit.gridWidth} columns × {request.targetFit.gridHeight} rows
- Content area: {dimensions.content_width:.0f}px × {dimensions.content_height:.0f}px
- Maximum {max_chars} characters (text only, not HTML tags)

## STYLING (from theme typography)
- Font family: '{theme.font_family}'
- Font size: {body_token.size}px
- Line height: {body_token.line_height}

## REQUIREMENTS
1. {"Preserve the formatting structure (bullets, paragraphs)" if request.preserveFormatting else "You may change the formatting structure"}
2. Keep the most important information
3. Maintain inline CSS styling using the typography above
4. Return ONLY the condensed HTML

## OUTPUT
Return the condensed HTML:"""

        return prompt

    async def generate(self, request: TextAutofitRequest) -> TextAutofitResponse:
        """
        Override generate to handle non-AI strategies.
        Uses new 32×18 grid system with font-aware calculations.
        """
        generation_id = self._generate_id()
        current_chars = self._count_characters(request.content)
        max_chars = self._calculate_max_chars_for_target(request.targetFit)

        # Get typography for styling
        theme = self._get_typography_theme()
        body_token = theme.get_token("body")

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
            # Calculate recommended font size based on typography
            overflow_ratio = current_chars / max_chars
            base_font = body_token.size  # Use theme font size as base
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
                        "suggestion": f"Reduce font size to {recommended_font}px (from {base_font}px)"
                    }
                )
            )

        if request.strategy == AutofitStrategy.TRUNCATE:
            # Simple truncation with ellipsis
            text = self._extract_text_from_html(request.content)
            truncated_text = text[:max_chars - 3] + "..."

            # Wrap in styling from theme
            truncated_html = f'<p style="font-family: \'{theme.font_family}\'; font-size: {body_token.size}px; line-height: {body_token.line_height}; color: {body_token.color}; font-weight: {body_token.weight};">{truncated_text}</p>'

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
        """Build response for smart_condense strategy with 32×18 grid calculations."""
        char_count = self._count_characters(content)
        max_chars = self._calculate_max_chars_for_target(request.targetFit)

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
