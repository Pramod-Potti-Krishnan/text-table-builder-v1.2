"""
Slide Text Generators for Layout Service v2.0

Generators for slide-specific text content using the 32×18 grid system
with font-aware character/line calculations and theme integration.

Generators:
- SlideTextGenerator: Generic slide text (any text type)
- TitleSlideGenerator: Complete title slide (title + subtitle + content)
- SectionSlideGenerator: Section divider (title + subtitle)
- ClosingSlideGenerator: Closing slide (title + subtitle + CTA)

All generators:
- Use 32×18 grid system (1920×1080px HD slides)
- Calculate precise character constraints based on typography
- Support theme integration via ThemeServiceClient
- Return content with dimension/constraint metadata
"""

import logging
from typing import Dict, Any, Callable, Optional
import uuid

from .base_layout_generator import BaseLayoutGenerator
from .grid_calculator import GridCalculator
from app.models.layout_models import (
    SlideTextRequest,
    SlideTextResponse,
    SlideTextContentData,
    TitleSlideRequest,
    TitleSlideResponse,
    TitleSlideContentData,
    SectionSlideRequest,
    SectionSlideResponse,
    SectionSlideContentData,
    ClosingSlideRequest,
    ClosingSlideResponse,
    ClosingSlideContentData,
    GenericTextElementRequest,
    GridConstraints,
    TypographyConfig,
    ElementDimensions,
    TextConstraintsUsed,
    TypographyApplied,
    ErrorDetails,
    SlideTextType,
    TypographyLevel,
    TextFormat
)
from app.services.theme_service_client import (
    ThemeServiceClient,
    TypographyTheme,
    TypographyToken,
    get_default_typography,
    SLIDE_TEXT_TYPE_TO_LEVEL
)

logger = logging.getLogger(__name__)


class SlideTextGenerator(BaseLayoutGenerator[SlideTextRequest, SlideTextResponse]):
    """
    Generate slide-specific text content with precise constraints.

    Uses the 32×18 grid system and theme-aware typography for
    accurate character/line calculations.
    """

    def __init__(
        self,
        llm_service: Callable,
        theme_client: Optional[ThemeServiceClient] = None
    ):
        """
        Initialize slide text generator.

        Args:
            llm_service: Async callable for LLM generation
            theme_client: Optional theme service client (creates default if None)
        """
        super().__init__(llm_service)
        self.theme_client = theme_client or ThemeServiceClient()

    @property
    def generator_type(self) -> str:
        return "slide_text"

    def _get_typography_for_text_type(
        self,
        text_type: SlideTextType,
        theme: TypographyTheme,
        override: Optional[TypographyConfig] = None
    ) -> Dict[str, Any]:
        """
        Get typography settings for a text type.

        Args:
            text_type: Type of slide text
            theme: Typography theme
            override: Optional typography override

        Returns:
            Dictionary with typography settings and source
        """
        # Get base typography from theme
        level = SLIDE_TEXT_TYPE_TO_LEVEL.get(text_type.value, "body")
        token = theme.get_token(level)

        # Apply overrides if provided
        if override:
            return {
                "fontFamily": override.fontFamily or theme.font_family,
                "fontSize": override.fontSize or token.size,
                "fontWeight": override.fontWeight or token.weight,
                "lineHeight": override.lineHeight or token.line_height,
                "color": override.color or token.color,
                "letterSpacing": override.letterSpacing or token.letter_spacing,
                "source": "override"
            }

        return {
            "fontFamily": theme.font_family,
            "fontSize": token.size,
            "fontWeight": token.weight,
            "lineHeight": token.line_height,
            "color": token.color,
            "letterSpacing": token.letter_spacing,
            "source": "theme"
        }

    def _calculate_constraints(
        self,
        constraints: GridConstraints,
        typography: Dict[str, Any],
        char_width_ratio: float = 0.5
    ) -> Dict[str, Any]:
        """
        Calculate element dimensions and text constraints.

        Args:
            constraints: Grid constraints
            typography: Typography settings
            char_width_ratio: Character width ratio for font

        Returns:
            Dictionary with dimensions and text constraints
        """
        # Calculate element dimensions
        dimensions = GridCalculator.calculate_element_dimensions(
            grid_width=constraints.gridWidth,
            grid_height=constraints.gridHeight,
            outer_padding=constraints.outerPadding,
            inner_padding=constraints.innerPadding
        )

        # Calculate text constraints
        text_constraints = GridCalculator.calculate_text_constraints(
            content_width=dimensions.content_width,
            content_height=dimensions.content_height,
            font_size=typography["fontSize"],
            line_height=typography["lineHeight"],
            char_width_ratio=char_width_ratio
        )

        return {
            "dimensions": dimensions,
            "text_constraints": text_constraints
        }

    async def _build_prompt(self, request: SlideTextRequest) -> str:
        """Build prompt for slide text generation."""
        # Get theme and typography
        theme = await self.theme_client.get_typography(request.themeId)
        typography = self._get_typography_for_text_type(
            request.textType,
            theme,
            request.typography
        )

        # Calculate constraints
        calc_result = self._calculate_constraints(
            request.constraints,
            typography,
            theme.char_width_ratio
        )
        text_constraints = calc_result["text_constraints"]

        # Determine expected format based on text type
        expected_format = "single line" if text_constraints.max_lines <= 2 else "paragraph or bullets"

        # Build context section
        context_str = ""
        if request.context:
            context_str = self._build_context_section(request.context)

        # Get text type description
        text_type_desc = {
            SlideTextType.SLIDE_TITLE: "slide title (h2 level, impactful and clear)",
            SlideTextType.SLIDE_SUBTITLE: "slide subtitle (supportive text under title)",
            SlideTextType.TITLE_SLIDE_TITLE: "presentation title (h1 level, main title)",
            SlideTextType.TITLE_SLIDE_SUBTITLE: "presentation subtitle/tagline",
            SlideTextType.TITLE_SLIDE_CONTENT: "title slide additional content",
            SlideTextType.SECTION_TITLE: "section divider title (clear section name)",
            SlideTextType.SECTION_SUBTITLE: "section divider subtitle",
            SlideTextType.CLOSING_TITLE: "closing slide title (memorable ending)",
            SlideTextType.CLOSING_SUBTITLE: "closing slide subtitle",
            SlideTextType.CLOSING_CONTENT: "closing slide CTA or contact info",
            SlideTextType.BODY_TEXT: "body text content",
            SlideTextType.CAPTION: "caption or small text"
        }.get(request.textType, "text content")

        # Build options string
        options_str = ""
        if request.options:
            if request.options.tone:
                options_str += f"- Tone: {request.options.tone.value}\n"
            if request.options.format:
                options_str += f"- Format: {request.options.format.value}\n"

        # v1.3.0: Build content context section
        content_context_str = ""
        if request.content_context:
            audience = request.content_context.get("audience", {})
            purpose = request.content_context.get("purpose", {})

            audience_type = audience.get("audience_type", "professional")
            complexity = audience.get("complexity_level", "moderate")
            avoid_jargon = audience.get("avoid_jargon", False)

            purpose_type = purpose.get("purpose_type", "inform")
            include_cta = purpose.get("include_cta", False)

            content_context_str = f"""
## AUDIENCE & PURPOSE
- Audience: {audience_type} ({complexity} complexity)
- Purpose: {purpose_type}
- Avoid jargon: {"Yes" if avoid_jargon else "No"}
- Include call-to-action: {"Yes" if include_cta else "No"}
"""

        prompt = f"""Generate {text_type_desc} for a presentation slide.

## CONTEXT
{context_str if context_str else "No additional context provided"}
{content_context_str}
## USER REQUEST
{request.prompt}

## CONSTRAINTS (CRITICAL - MUST FOLLOW)
- Maximum characters: {text_constraints.target_characters} (aim for this)
- Hard limit: {text_constraints.max_characters} characters (DO NOT EXCEED)
- Minimum characters: {text_constraints.min_characters}
- Characters per line: ~{text_constraints.chars_per_line}
- Maximum lines: {text_constraints.max_lines}
- Expected format: {expected_format}

## TYPOGRAPHY
- Font size: {typography['fontSize']}px
- Font weight: {typography['fontWeight']}
- Line height: {typography['lineHeight']}

{options_str if options_str else ""}

## OUTPUT FORMAT
Generate ONLY the text content. Do NOT include HTML tags or styling.
The text will be wrapped in appropriate elements with styling applied automatically.

For single-line content (titles, subtitles): Output one concise line.
For multi-line content: Use line breaks where natural.
For bullet points: Start each point with "- " on a new line.

## INSTRUCTIONS
1. Generate content that fits within {text_constraints.target_characters} characters
2. Be concise and impactful for {text_type_desc}
3. Do NOT exceed {text_constraints.max_characters} characters
4. Return ONLY the text content, no HTML or explanations

Generate the text now:"""

        return prompt

    async def _build_response(
        self,
        content: str,
        request: SlideTextRequest,
        generation_id: str
    ) -> SlideTextResponse:
        """Build response object from generated content."""
        try:
            # Get theme and typography
            theme = await self.theme_client.get_typography(request.themeId)
            typography = self._get_typography_for_text_type(
                request.textType,
                theme,
                request.typography
            )

            # Calculate constraints
            calc_result = self._calculate_constraints(
                request.constraints,
                typography,
                theme.char_width_ratio
            )

            # Clean content (remove any accidental HTML)
            clean_content = self._clean_text_content(content)

            # Count characters and lines
            char_count = len(clean_content)
            line_count = clean_content.count('\n') + 1

            # Check if content fits
            text_constraints = calc_result["text_constraints"]
            fits = char_count <= text_constraints.max_characters

            if not fits:
                logger.warning(
                    f"Generated content ({char_count} chars) exceeds limit "
                    f"({text_constraints.max_characters} chars) for {request.textType.value}"
                )

            # Build response data
            data = SlideTextContentData(
                generationId=generation_id,
                content=clean_content,
                dimensions=ElementDimensions(
                    gridWidth=request.constraints.gridWidth,
                    gridHeight=request.constraints.gridHeight,
                    elementWidth=calc_result["dimensions"].element_width,
                    elementHeight=calc_result["dimensions"].element_height,
                    contentWidth=calc_result["dimensions"].content_width,
                    contentHeight=calc_result["dimensions"].content_height
                ),
                constraintsUsed=TextConstraintsUsed(
                    charsPerLine=text_constraints.chars_per_line,
                    maxLines=text_constraints.max_lines,
                    maxCharacters=text_constraints.max_characters,
                    targetCharacters=text_constraints.target_characters,
                    minCharacters=text_constraints.min_characters
                ),
                typographyApplied=TypographyApplied(
                    fontFamily=typography["fontFamily"],
                    fontSize=typography["fontSize"],
                    fontWeight=typography["fontWeight"],
                    lineHeight=typography["lineHeight"],
                    color=typography["color"],
                    source=typography["source"]
                ),
                characterCount=char_count,
                lineCount=line_count,
                fits=fits
            )

            return SlideTextResponse(success=True, data=data)

        except Exception as e:
            logger.error(f"Failed to build slide text response: {e}")
            return SlideTextResponse(
                success=False,
                error=ErrorDetails(
                    code="GENERATION_FAILED",
                    message=str(e),
                    retryable=True
                )
            )

    def _clean_text_content(self, content: str) -> str:
        """
        Clean text content from LLM response.

        Removes HTML tags, markdown wrappers, and normalizes whitespace.

        Args:
            content: Raw content from LLM

        Returns:
            Clean text content
        """
        import re

        # Remove markdown code blocks
        content = re.sub(r'```[a-z]*\s*', '', content)
        content = re.sub(r'```', '', content)

        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)

        # Normalize whitespace
        content = content.strip()

        # Normalize line breaks
        content = re.sub(r'\n{3,}', '\n\n', content)

        return content

    def _validate_html(self, content: str) -> Dict[str, Any]:
        """
        Override HTML validation for text content.

        Since we're generating plain text, not HTML, we just check
        for non-empty content.
        """
        if not content or not content.strip():
            return {
                "valid": False,
                "violations": ["Generated content is empty"],
                "warnings": []
            }

        return {
            "valid": True,
            "violations": [],
            "warnings": []
        }


class TitleSlideGenerator:
    """
    Generate complete title slide content.

    Generates title, subtitle, and optional content for title slides,
    each with appropriate typography and constraints.
    """

    def __init__(
        self,
        llm_service: Callable,
        theme_client: Optional[ThemeServiceClient] = None
    ):
        self.llm_service = llm_service
        self.theme_client = theme_client or ThemeServiceClient()
        self.text_generator = SlideTextGenerator(llm_service, self.theme_client)

    async def generate(self, request: TitleSlideRequest) -> TitleSlideResponse:
        """Generate complete title slide content."""
        generation_id = str(uuid.uuid4())
        logger.info(f"Starting title slide generation (id: {generation_id})")

        try:
            # Generate title
            title_request = SlideTextRequest(
                textType=SlideTextType.TITLE_SLIDE_TITLE,
                prompt=f"Create a presentation title: {request.prompt}",
                context=request.context,
                constraints=request.titleConstraints,
                typography=request.typography,
                themeId=request.themeId
            )
            title_response = await self.text_generator.generate(title_request)

            if not title_response.success:
                return TitleSlideResponse(
                    success=False,
                    error=title_response.error
                )

            # Generate subtitle if constraints provided
            subtitle_data = None
            if request.subtitleConstraints:
                subtitle_request = SlideTextRequest(
                    textType=SlideTextType.TITLE_SLIDE_SUBTITLE,
                    prompt=f"Create a subtitle for: {request.prompt}",
                    context=request.context,
                    constraints=request.subtitleConstraints,
                    typography=request.typography,
                    themeId=request.themeId
                )
                subtitle_response = await self.text_generator.generate(subtitle_request)
                if subtitle_response.success:
                    subtitle_data = subtitle_response.data

            # Generate content if constraints provided
            content_data = None
            if request.contentConstraints:
                content_request = SlideTextRequest(
                    textType=SlideTextType.TITLE_SLIDE_CONTENT,
                    prompt=f"Create additional content for: {request.prompt}",
                    context=request.context,
                    constraints=request.contentConstraints,
                    typography=request.typography,
                    themeId=request.themeId
                )
                content_response = await self.text_generator.generate(content_request)
                if content_response.success:
                    content_data = content_response.data

            return TitleSlideResponse(
                success=True,
                data=TitleSlideContentData(
                    generationId=generation_id,
                    title=title_response.data,
                    subtitle=subtitle_data,
                    content=content_data
                )
            )

        except Exception as e:
            logger.error(f"Title slide generation failed: {e}")
            return TitleSlideResponse(
                success=False,
                error=ErrorDetails(
                    code="GENERATION_FAILED",
                    message=str(e),
                    retryable=True
                )
            )


class SectionSlideGenerator:
    """
    Generate section divider slide content.

    Generates section title and optional subtitle for section dividers.
    """

    def __init__(
        self,
        llm_service: Callable,
        theme_client: Optional[ThemeServiceClient] = None
    ):
        self.llm_service = llm_service
        self.theme_client = theme_client or ThemeServiceClient()
        self.text_generator = SlideTextGenerator(llm_service, self.theme_client)

    async def generate(self, request: SectionSlideRequest) -> SectionSlideResponse:
        """Generate section slide content."""
        generation_id = str(uuid.uuid4())
        logger.info(f"Starting section slide generation (id: {generation_id})")

        try:
            # Generate section title
            title_request = SlideTextRequest(
                textType=SlideTextType.SECTION_TITLE,
                prompt=f"Create a section title: {request.prompt}",
                context=request.context,
                constraints=request.titleConstraints,
                typography=request.typography,
                themeId=request.themeId
            )
            title_response = await self.text_generator.generate(title_request)

            if not title_response.success:
                return SectionSlideResponse(
                    success=False,
                    error=title_response.error
                )

            # Generate subtitle if constraints provided
            subtitle_data = None
            if request.subtitleConstraints:
                subtitle_request = SlideTextRequest(
                    textType=SlideTextType.SECTION_SUBTITLE,
                    prompt=f"Create a section subtitle for: {request.prompt}",
                    context=request.context,
                    constraints=request.subtitleConstraints,
                    typography=request.typography,
                    themeId=request.themeId
                )
                subtitle_response = await self.text_generator.generate(subtitle_request)
                if subtitle_response.success:
                    subtitle_data = subtitle_response.data

            return SectionSlideResponse(
                success=True,
                data=SectionSlideContentData(
                    generationId=generation_id,
                    title=title_response.data,
                    subtitle=subtitle_data
                )
            )

        except Exception as e:
            logger.error(f"Section slide generation failed: {e}")
            return SectionSlideResponse(
                success=False,
                error=ErrorDetails(
                    code="GENERATION_FAILED",
                    message=str(e),
                    retryable=True
                )
            )


class ClosingSlideGenerator:
    """
    Generate closing slide content.

    Generates title, subtitle, and call-to-action content for closing slides.
    """

    def __init__(
        self,
        llm_service: Callable,
        theme_client: Optional[ThemeServiceClient] = None
    ):
        self.llm_service = llm_service
        self.theme_client = theme_client or ThemeServiceClient()
        self.text_generator = SlideTextGenerator(llm_service, self.theme_client)

    async def generate(self, request: ClosingSlideRequest) -> ClosingSlideResponse:
        """Generate closing slide content."""
        generation_id = str(uuid.uuid4())
        logger.info(f"Starting closing slide generation (id: {generation_id})")

        try:
            # Generate closing title
            title_request = SlideTextRequest(
                textType=SlideTextType.CLOSING_TITLE,
                prompt=f"Create a closing slide title: {request.prompt}",
                context=request.context,
                constraints=request.titleConstraints,
                typography=request.typography,
                themeId=request.themeId
            )
            title_response = await self.text_generator.generate(title_request)

            if not title_response.success:
                return ClosingSlideResponse(
                    success=False,
                    error=title_response.error
                )

            # Generate subtitle if constraints provided
            subtitle_data = None
            if request.subtitleConstraints:
                subtitle_request = SlideTextRequest(
                    textType=SlideTextType.CLOSING_SUBTITLE,
                    prompt=f"Create a closing subtitle for: {request.prompt}",
                    context=request.context,
                    constraints=request.subtitleConstraints,
                    typography=request.typography,
                    themeId=request.themeId
                )
                subtitle_response = await self.text_generator.generate(subtitle_request)
                if subtitle_response.success:
                    subtitle_data = subtitle_response.data

            # Generate CTA content if constraints provided
            content_data = None
            if request.contentConstraints:
                content_request = SlideTextRequest(
                    textType=SlideTextType.CLOSING_CONTENT,
                    prompt=f"Create CTA/contact content for: {request.prompt}",
                    context=request.context,
                    constraints=request.contentConstraints,
                    typography=request.typography,
                    themeId=request.themeId
                )
                content_response = await self.text_generator.generate(content_request)
                if content_response.success:
                    content_data = content_response.data

            return ClosingSlideResponse(
                success=True,
                data=ClosingSlideContentData(
                    generationId=generation_id,
                    title=title_response.data,
                    subtitle=subtitle_data,
                    content=content_data
                )
            )

        except Exception as e:
            logger.error(f"Closing slide generation failed: {e}")
            return ClosingSlideResponse(
                success=False,
                error=ErrorDetails(
                    code="GENERATION_FAILED",
                    message=str(e),
                    retryable=True
                )
            )


class GenericTextElementGenerator(SlideTextGenerator):
    """
    Generate generic text element content with full styling control.

    Extends SlideTextGenerator with support for typography levels
    and custom styling.
    """

    @property
    def generator_type(self) -> str:
        return "generic_text_element"

    async def generate_from_request(
        self,
        request: GenericTextElementRequest
    ) -> SlideTextResponse:
        """Generate text element from GenericTextElementRequest."""
        # Map typography level to text type
        level_to_type = {
            TypographyLevel.H1: SlideTextType.TITLE_SLIDE_TITLE,
            TypographyLevel.H2: SlideTextType.SLIDE_TITLE,
            TypographyLevel.H3: SlideTextType.SLIDE_TITLE,
            TypographyLevel.H4: SlideTextType.SLIDE_TITLE,
            TypographyLevel.BODY: SlideTextType.BODY_TEXT,
            TypographyLevel.SUBTITLE: SlideTextType.SLIDE_SUBTITLE,
            TypographyLevel.CAPTION: SlideTextType.CAPTION
        }

        text_type = level_to_type.get(
            request.typographyLevel or TypographyLevel.BODY,
            SlideTextType.BODY_TEXT
        )

        # Create SlideTextRequest
        slide_request = SlideTextRequest(
            textType=text_type,
            prompt=request.prompt,
            context=request.context,
            constraints=request.constraints,
            typography=request.typography,
            style=request.style,
            listStyle=request.listStyle,
            themeId=request.themeId,
            options=request.options,
            # v1.3.0: Pass content_context for audience/purpose-aware generation
            content_context=request.content_context
        )

        return await self.generate(slide_request)


# =============================================================================
# Factory Functions
# =============================================================================

def create_slide_text_generator(
    llm_service: Callable,
    theme_client: Optional[ThemeServiceClient] = None
) -> SlideTextGenerator:
    """Create a SlideTextGenerator instance."""
    return SlideTextGenerator(llm_service, theme_client)


def create_title_slide_generator(
    llm_service: Callable,
    theme_client: Optional[ThemeServiceClient] = None
) -> TitleSlideGenerator:
    """Create a TitleSlideGenerator instance."""
    return TitleSlideGenerator(llm_service, theme_client)


def create_section_slide_generator(
    llm_service: Callable,
    theme_client: Optional[ThemeServiceClient] = None
) -> SectionSlideGenerator:
    """Create a SectionSlideGenerator instance."""
    return SectionSlideGenerator(llm_service, theme_client)


def create_closing_slide_generator(
    llm_service: Callable,
    theme_client: Optional[ThemeServiceClient] = None
) -> ClosingSlideGenerator:
    """Create a ClosingSlideGenerator instance."""
    return ClosingSlideGenerator(llm_service, theme_client)


def create_generic_text_generator(
    llm_service: Callable,
    theme_client: Optional[ThemeServiceClient] = None
) -> GenericTextElementGenerator:
    """Create a GenericTextElementGenerator instance."""
    return GenericTextElementGenerator(llm_service, theme_client)
