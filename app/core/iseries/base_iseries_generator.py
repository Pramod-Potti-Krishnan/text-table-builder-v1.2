"""
Base I-Series Generator for Text Service v1.2

Abstract base class for I-series layout generators.
Implements the parallel image + content generation pattern
used by hero generators, adapted for portrait aspect ratio images.

Pattern follows:
- Parallel execution of image and content generation
- Graceful fallback if image fails
- Style-aware image prompts (professional, illustrated, kids)
- Content validation and HTML builders

Version: 1.3.0 - Added content_context support for audience-adapted text
Version: 1.3.1 - Always use multi-step generation with hardcoded dimensions
Version: 1.3.2 - Added content_variant support for I-series specific character constraints
Version: 1.4.0 - Context-aware image generation using audience/purpose from ContentContext
Version: 1.5.0 - 2-Step Intentional Spotlight Image Generation
              - Step 1: Extract visual concept (WHAT to show)
              - Step 2: Build prompt from concept (HOW to show it)
              - Hybrid extraction (LLM for complex, rules for simple)
"""

import asyncio
import json
import logging
import os
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Callable, Optional, List


# =============================================================================
# Hardcoded Layout Specifications (from Layout Service)
# =============================================================================
# These dimensions are FIXED per layout. The Text Service knows exactly
# what space is available without needing external parameters.

ISERIES_LAYOUT_SPECS = {
    "I1": {
        "content": {"width_px": 1200, "height_px": 840},
        "image": {"width_px": 660, "height_px": 1080, "aspect_ratio": "11:18"}
    },
    "I2": {
        "content": {"width_px": 1140, "height_px": 840},
        "image": {"width_px": 720, "height_px": 1080, "aspect_ratio": "2:3"}
    },
    "I3": {
        "content": {"width_px": 1500, "height_px": 840},
        "image": {"width_px": 360, "height_px": 1080, "aspect_ratio": "1:3"}
    },
    "I4": {
        "content": {"width_px": 1440, "height_px": 840},
        "image": {"width_px": 420, "height_px": 1080, "aspect_ratio": "7:18"}
    },
}

from app.services.image_service_client import get_image_service_client, ImageServiceClient
from app.models.iseries_models import (
    ISeriesGenerationRequest,
    ISeriesGenerationResponse,
    ISeriesVisualStyle,
    ISeriesContentStyle,
    get_layout_dimensions
)
from app.core.hero.style_config import (
    get_style_config,
    get_domain_theme
)
from app.core.iseries.context_style_mapper import (
    get_image_style_params,
    detect_domain_from_text,
    build_context_aware_negative_prompt,
    get_spotlight_depth
)
from app.core.iseries.spotlight_concept_extractor import SpotlightConceptExtractor
from app.core.iseries.prompt_assembler import (
    GlobalBrandVars,
    LocalMessageVars,
    assemble_prompt,
    assemble_prompt_with_fallback
)
from app.models.iseries_models import SpotlightConcept, SpotlightDepth, AbstractionLevel

logger = logging.getLogger(__name__)

# Path to variant specs directory
VARIANT_SPECS_DIR = Path(__file__).parent.parent.parent / "variant_specs" / "iseries"


def load_iseries_variant_spec(variant_id: str) -> Optional[Dict[str, Any]]:
    """
    Load I-series variant spec from JSON file.

    Args:
        variant_id: Variant ID (e.g., 'single_column_3section_i1')

    Returns:
        Variant spec dict or None if not found
    """
    spec_path = VARIANT_SPECS_DIR / f"{variant_id}.json"
    if not spec_path.exists():
        logger.warning(f"Variant spec not found: {spec_path}")
        return None

    try:
        with open(spec_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load variant spec {variant_id}: {e}")
        return None


class BaseISeriesGenerator(ABC):
    """
    Abstract base class for I-series layout generators.

    Implements the parallel image + content generation pattern:
    1. Build image prompt based on narrative and visual style
    2. Build content prompt for text generation
    3. Execute both in parallel
    4. Handle image failure gracefully
    5. Assemble final response with HTML for each slot
    """

    def __init__(self, llm_service: Callable):
        """
        Initialize generator with LLM service.

        Args:
            llm_service: Async callable for LLM text generation
        """
        self.llm_service = llm_service
        self.image_client: ImageServiceClient = get_image_service_client()

    @property
    @abstractmethod
    def layout_type(self) -> str:
        """Return layout type: I1, I2, I3, I4"""
        pass

    @property
    @abstractmethod
    def image_position(self) -> str:
        """Return image position: left or right"""
        pass

    @property
    @abstractmethod
    def image_dimensions(self) -> Dict[str, int]:
        """Return image dimensions: {width: int, height: int}"""
        pass

    @property
    @abstractmethod
    def content_dimensions(self) -> Dict[str, int]:
        """Return content area dimensions: {width: int, height: int}"""
        pass

    async def generate(
        self,
        request: ISeriesGenerationRequest
    ) -> ISeriesGenerationResponse:
        """
        Main generation workflow - parallel image + multi-step content.

        v1.3.1: ALWAYS uses multi-step content generation with hardcoded
        layout dimensions. No need to wait for available_space parameter.

        Args:
            request: I-series generation request

        Returns:
            ISeriesGenerationResponse with HTML for each slot
        """
        import time
        start_time = time.time()

        # Get hardcoded layout specifications
        layout_spec = ISERIES_LAYOUT_SPECS.get(self.layout_type)
        if not layout_spec:
            logger.warning(f"Unknown layout type {self.layout_type}, falling back to I1")
            layout_spec = ISERIES_LAYOUT_SPECS["I1"]

        content_dims = layout_spec["content"]
        image_spec = layout_spec["image"]

        # Extract v1.3.0 context params
        context = request.context if hasattr(request, 'context') and request.context else {}
        theme_config = context.get("theme_config")
        content_context = context.get("content_context")
        styling_mode = context.get("styling_mode", "inline_styles")
        # v1.5.0: Extract image_model from Director for quality tier selection
        image_model = context.get("image_model")

        # v1.3.2: Load variant spec if content_variant is specified
        # v1.3.3: Also check context["variant_spec"] from slides_routes auto-selection
        variant_spec = None

        # First, check if variant_spec is passed in context (auto-selected by slides_routes)
        if context.get("variant_spec"):
            variant_spec = context["variant_spec"]
            logger.info(
                f"Using auto-selected variant spec from context: {variant_spec.get('variant_id')} "
                f"(layout: {variant_spec.get('iseries_layout', 'unknown')})"
            )
        # Fallback: check if content_variant is specified on request (legacy way)
        elif hasattr(request, 'content_variant') and request.content_variant:
            variant_spec = load_iseries_variant_spec(request.content_variant)
            if variant_spec:
                logger.info(
                    f"Using I-series variant spec from request: {request.content_variant} "
                    f"(layout: {variant_spec.get('iseries_layout', 'unknown')})"
                )

        logger.info(
            f"Generating {self.layout_type} layout "
            f"(slide #{request.slide_number}, style={request.visual_style.value}, "
            f"multi-step={content_dims['width_px']}x{content_dims['height_px']}px, "
            f"variant={request.content_variant if hasattr(request, 'content_variant') else 'default'})"
        )

        # v1.5.0: 2-step intentional spotlight image generation
        # Step 1: Extract visual concept (WHAT to show)
        # Step 2: Build prompt from concept (HOW to show it)
        image_prompt, archetype, style_params = await self._build_image_prompt_2step(
            request,
            content_context=content_context
        )

        # Parallel generation: image + multi-step content
        # v1.6.0: Support skip_image_generation flag for testing
        if getattr(request, 'skip_image_generation', False):
            logger.info("Skipping image generation (skip_image_generation=True)")
            image_task = asyncio.create_task(self._skip_image_task())
        else:
            image_task = asyncio.create_task(
                self._generate_image(
                    image_prompt, archetype, request,
                    aspect_ratio=image_spec["aspect_ratio"],
                    style_params=style_params,  # v1.4.0: Pass style params
                    image_model=image_model  # v1.5.0: Pass model for quality tier
                )
            )
        content_task = asyncio.create_task(
            self._generate_content_multi_step(
                request,
                content_dims["width_px"],
                content_dims["height_px"],
                theme_config,
                content_context,
                styling_mode,
                variant_spec  # v1.3.2: Pass variant spec for character constraints
            )
        )

        results = await asyncio.gather(
            image_task,
            content_task,
            return_exceptions=True
        )

        image_result = results[0]
        content_result = results[1]

        # Handle content result (fatal if fails)
        if isinstance(content_result, Exception):
            logger.error(f"Content generation failed: {content_result}")
            raise content_result

        # Handle image result (non-fatal if fails)
        image_url = None
        image_fallback = False
        image_metadata = {}

        if isinstance(image_result, Exception):
            logger.warning(
                f"Image generation failed, using fallback: {image_result}"
            )
            image_fallback = True
        elif image_result and image_result.get("success"):
            image_url = (
                image_result["urls"].get("cropped") or
                image_result["urls"]["original"]
            )
            image_metadata = image_result.get("metadata", {})
            logger.info(
                f"Image generated in {image_metadata.get('generation_time_ms', 0)}ms"
            )
        else:
            logger.warning("Image generation returned unsuccessful, using fallback")
            image_fallback = True

        # Calculate generation time
        generation_time_ms = int((time.time() - start_time) * 1000)

        # Build response
        response = self._build_response(
            image_url=image_url,
            image_fallback=image_fallback,
            content_result=content_result,
            request=request,
            generation_time_ms=generation_time_ms
        )

        logger.info(
            f"{self.layout_type} layout generated in {generation_time_ms}ms "
            f"(image_fallback={image_fallback})"
        )

        return response

    def _build_image_prompt_legacy(
        self,
        request: ISeriesGenerationRequest,
        content_context: Optional[Dict[str, Any]] = None
    ) -> tuple[str, str, Dict[str, Any]]:
        """
        Build context-aware image generation prompt (legacy 1-step method).

        v1.4.0: Uses ContentContext (audience, purpose) to generate
        contextually relevant images instead of generic illustrations.

        DEPRECATED: Use _build_image_prompt_2step() for intentional spotlight images.

        Args:
            request: Generation request with narrative and visual_style
            content_context: Optional dict with audience/purpose info

        Returns:
            Tuple of (image_prompt, archetype, style_params)
            - style_params contains: style, color_scheme, lighting, domain
        """
        narrative = request.narrative
        topics = request.topics
        visual_style = request.visual_style.value

        # Get base style configuration
        style_config = get_style_config(visual_style)

        # Determine domain from narrative and topics
        combined_text = f"{narrative} {' '.join(topics) if topics else ''}".lower()

        # v1.4.0: Extract audience and purpose from content_context
        audience_type = None
        purpose_type = None
        if content_context:
            audience_info = content_context.get("audience", {})
            purpose_info = content_context.get("purpose", {})
            audience_type = audience_info.get("audience_type")
            purpose_type = purpose_info.get("purpose_type")

        # v1.4.0: Get context-aware style parameters
        style_params = get_image_style_params(
            audience_type=audience_type,
            purpose_type=purpose_type,
            narrative_text=combined_text
        )

        # Determine domain and imagery elements
        detected_domain = style_params.get("domain", "default")
        positive_elements = style_params.get("elements", [])
        avoid_elements = style_params.get("avoid", [])
        prompt_hints = style_params.get("prompt_hints", [])

        # Fallback to legacy domain detection for imagery description
        domain_imagery = get_domain_theme(style_config, combined_text)

        # Build topic focus
        topic_focus = ', '.join(topics[:2]) if topics else 'professional setting'

        # Use image_prompt_hint if provided
        if request.image_prompt_hint:
            topic_focus = request.image_prompt_hint

        # v1.4.0: Build context-aware prompt with domain-specific elements
        elements_str = ', '.join(positive_elements[:3]) if positive_elements else domain_imagery
        hints_str = ', '.join(prompt_hints) if prompt_hints else ""

        # v1.4.0: Override visual style based on context for executives/technical
        context_style = style_params.get("style", "illustration")
        context_lighting = style_params.get("lighting", "professional")
        context_color = style_params.get("color_scheme", "neutral")

        # Build prompt with context awareness
        prompt = f"""High-quality {context_style} portrait image for presentation slide.

Style: {context_style}, {context_lighting} lighting, {context_color} color scheme
Orientation: Tall portrait (9:16 aspect ratio)
Subject: {elements_str}
Focus: {topic_focus}
Mood: {style_params.get("mood", "professional")}
Composition: Subject centered, vertical composition, clean background{f', {hints_str}' if hints_str else ''}

CRITICAL REQUIREMENTS:
- Absolutely NO text, words, letters, numbers, or typography
- NO human faces, people, or characters
- Abstract, conceptual imagery preferred
- Clean, professional appearance"""

        # v1.4.0: Determine archetype based on context
        # Executives/professional → photorealistic
        # Technical → minimal/abstract
        # Kids/students → spot_illustration
        archetype = style_config.archetype  # Default from visual_style
        if audience_type in ["executives", "professional"]:
            archetype = "photorealistic"
        elif audience_type in ["technical", "developers"]:
            archetype = "minimalist_vector_art"
        elif context_style == "minimal":
            archetype = "minimalist_vector_art"

        # v1.4.0: Include domain in style_params for negative prompt building
        style_params["domain"] = detected_domain

        logger.info(
            f"Built context-aware image prompt (audience={audience_type}, "
            f"purpose={purpose_type}, domain={detected_domain}, archetype={archetype})"
        )

        return prompt, archetype, style_params

    async def _build_image_prompt_2step(
        self,
        request: ISeriesGenerationRequest,
        content_context: Optional[Dict[str, Any]] = None
    ) -> tuple[str, str, Dict[str, Any]]:
        """
        Build image prompt using 2-step intentional spotlight approach.

        v1.5.0: 2-Step Intentional Spotlight Image Generation
        - Step 1: Extract visual concept (WHAT to show) using SpotlightConceptExtractor
        - Step 2: Build prompt from concept (HOW to show it)

        v1.2.3: When global_brand is provided, uses simplified prompting:
        - Global variables (brand) from Director
        - Local variables (message) from slide content
        - Simple ~30 word natural language prompt

        This produces more intentional, focused images by first understanding
        the core message before generating the image prompt.

        Args:
            request: Generation request with narrative and visual_style
            content_context: Optional dict with audience/purpose info

        Returns:
            Tuple of (image_prompt, archetype, style_params)
        """
        narrative = request.narrative
        topics = request.topics or []
        visual_style = request.visual_style.value

        # =================================================================
        # v1.2.3: SIMPLIFIED PROMPTING (when global_brand provided)
        # =================================================================
        if request.global_brand and request.global_brand.visual_style:
            return await self._build_image_prompt_simplified(request, content_context)

        # =================================================================
        # LEGACY: 2-Step Intentional Spotlight (when no global_brand)
        # =================================================================

        # Extract audience and purpose from content_context
        audience_type = None
        purpose_type = None
        if content_context:
            audience_info = content_context.get("audience", {})
            purpose_info = content_context.get("purpose", {})
            audience_type = audience_info.get("audience_type")
            purpose_type = purpose_info.get("purpose_type")

        # Combined text for domain detection
        combined_text = f"{narrative} {' '.join(topics)}".lower()

        # Get base style configuration
        style_config = get_style_config(visual_style)

        # Get context-aware style parameters
        style_params = get_image_style_params(
            audience_type=audience_type,
            purpose_type=purpose_type,
            narrative_text=combined_text
        )

        detected_domain = style_params.get("domain", "default")

        # =================================================================
        # STEP 1: Extract Visual Concept (WHAT to show)
        # =================================================================
        extractor = SpotlightConceptExtractor(llm_service=self.llm_service)

        try:
            concept, extraction_metadata = await extractor.extract(
                narrative=narrative,
                topics=topics,
                audience_type=audience_type,
                purpose_type=purpose_type,
                content_context=content_context
            )

            logger.info(
                f"Spotlight concept extracted: primary_subject='{concept.primary_subject}', "
                f"method={extraction_metadata.get('extraction_method')}, "
                f"complexity={extraction_metadata.get('complexity_score', 0):.2f}"
            )
        except Exception as e:
            logger.warning(f"Spotlight extraction failed, using fallback: {e}")
            # Fallback to legacy 1-step method
            return self._build_image_prompt_legacy(request, content_context)

        # =================================================================
        # STEP 2: Build Prompt from Concept (HOW to show it)
        # =================================================================

        # Get context style parameters
        context_style = style_params.get("style", "illustration")
        context_lighting = style_params.get("lighting", "professional")
        context_color = style_params.get("color_scheme", "neutral")
        mood = style_params.get("mood", "professional")

        # Build visual elements string
        visual_elements_str = ", ".join(concept.visual_elements[:3]) if concept.visual_elements else ""

        # Map abstraction level to prompt language
        abstraction_guidance = {
            "literal": "Direct, realistic representation",
            "metaphorical": "Visual metaphor, symbolic representation",
            "abstract": "Abstract, geometric, conceptual imagery"
        }
        abstraction_hint = abstraction_guidance.get(
            concept.abstraction_level.value if hasattr(concept.abstraction_level, 'value') else concept.abstraction_level,
            "Professional imagery"
        )

        # Build intentional spotlight prompt
        prompt = f"""High-quality {context_style} portrait image for presentation slide.

VISUAL FOCUS (Intentional Spotlight):
- Primary Subject: {concept.primary_subject}
- Supporting Elements: {visual_elements_str if visual_elements_str else "minimal background elements"}
- Composition: {concept.composition_hint}, vertical portrait orientation

STYLE:
- Visual approach: {abstraction_hint}
- Lighting: {context_lighting}
- Color scheme: {context_color}
- Mood: {concept.emotional_focus}
- Aspect ratio: Tall portrait (9:16)

CRITICAL REQUIREMENTS:
- Absolutely NO text, words, letters, numbers, or typography
- NO human faces, people, or characters
- Clean, professional appearance
- Subject should be clearly prominent and intentionally spotlighted
- Background should complement but not compete with main subject"""

        # Determine archetype based on context and concept
        archetype = style_config.archetype  # Default from visual_style

        # Override based on audience type
        if audience_type in ["executives", "professional"]:
            archetype = "photorealistic"
        elif audience_type in ["technical", "developers"]:
            archetype = "minimalist_vector_art"
        elif context_style == "minimal":
            archetype = "minimalist_vector_art"

        # If concept is abstract, prefer minimalist archetype
        if concept.abstraction_level == AbstractionLevel.ABSTRACT:
            if archetype not in ["photorealistic", "minimalist_vector_art"]:
                archetype = "minimalist_vector_art"

        # Add extraction metadata to style_params
        style_params["domain"] = detected_domain
        style_params["spotlight_concept"] = {
            "primary_subject": concept.primary_subject,
            "visual_elements": concept.visual_elements,
            "composition_hint": concept.composition_hint,
            "emotional_focus": concept.emotional_focus,
            "abstraction_level": concept.abstraction_level.value if hasattr(concept.abstraction_level, 'value') else str(concept.abstraction_level),
            "spotlight_rationale": concept.spotlight_rationale
        }
        style_params["extraction_metadata"] = extraction_metadata

        logger.info(
            f"Built 2-step spotlight image prompt (audience={audience_type}, "
            f"purpose={purpose_type}, domain={detected_domain}, archetype={archetype}, "
            f"spotlight='{concept.primary_subject[:50]}...')"
        )

        return prompt, archetype, style_params

    async def _build_image_prompt_simplified(
        self,
        request: ISeriesGenerationRequest,
        content_context: Optional[Dict[str, Any]] = None
    ) -> tuple[str, str, Dict[str, Any]]:
        """
        Build image prompt using simplified Global + Local variable approach.

        v1.2.3: When Director provides global_brand, we use this simplified
        prompting approach instead of the complex 2-step spotlight extraction.

        Formula: [Visual Style] of a [Anchor Subject] [Action/Composition].
                 [Lighting & Mood]. [Color Palette]. [Target Demographic Keywords].

        Args:
            request: Generation request with global_brand and narrative
            content_context: Optional dict with audience/purpose info

        Returns:
            Tuple of (image_prompt, archetype, style_params)
        """
        # Extract global brand variables from request
        global_brand = GlobalBrandVars.from_dict(
            request.global_brand.model_dump() if request.global_brand else None
        )

        # Extract local message variables from content
        narrative = request.narrative
        topics = request.topics or []

        # Build local variables - simple extraction without LLM
        local_vars = LocalMessageVars(
            content_archetype=self._detect_content_archetype(narrative, topics),
            topic=topics[0] if topics else narrative[:100],
            anchor_subject=self._extract_anchor_subject(narrative, topics),
            action_composition=self._extract_action_composition(narrative),
            semantic_link="",  # Optional, not needed for simplified prompts
            aspect_ratio="9:16"  # I-series uses portrait orientation
        )

        # Assemble the simplified prompt (~30 words)
        prompt = assemble_prompt(global_brand, local_vars)

        # Determine archetype from visual style
        visual_style = request.visual_style.value
        archetype = self._map_visual_style_to_archetype(visual_style, global_brand)

        # Build style_params for API call
        style_params = {
            "visual_style": visual_style,
            "archetype": archetype,
            "prompt_type": "simplified_global_local",
            "global_brand_provided": True,
            "aspect_ratio": "9:16"
        }

        logger.info(
            f"Built simplified image prompt (visual_style={visual_style}, "
            f"archetype={archetype}, anchor='{local_vars.anchor_subject[:50]}...')"
        )
        logger.debug(f"Simplified prompt: {prompt}")

        return prompt, archetype, style_params

    def _detect_content_archetype(self, narrative: str, topics: List[str]) -> str:
        """Detect content archetype from narrative and topics."""
        combined = f"{narrative} {' '.join(topics)}".lower()

        # Simple keyword-based detection
        if any(word in combined for word in ["compare", "vs", "versus", "difference", "better"]):
            return "comparison"
        elif any(word in combined for word in ["step", "process", "workflow", "phase", "stage"]):
            return "process"
        elif any(word in combined for word in ["metric", "kpi", "percent", "%", "growth", "increase"]):
            return "metrics"
        elif any(word in combined for word in ["benefit", "advantage", "feature", "capability"]):
            return "benefits"
        elif any(word in combined for word in ["problem", "solution", "challenge", "solve"]):
            return "problem_solution"
        else:
            return "general"

    def _extract_anchor_subject(self, narrative: str, topics: List[str]) -> str:
        """Extract anchor subject (concrete visual noun) from content."""
        combined = f"{narrative} {' '.join(topics)}"

        # Look for concrete nouns that can be visualized
        # Simple heuristic: use first topic if available, or extract from narrative
        if topics and len(topics[0]) > 5:
            # Use first topic as anchor, but make it more visual
            topic = topics[0]
            # Add visual context based on topic
            return f"abstract visualization representing {topic}"

        # Fallback: create abstract visual from narrative
        words = narrative.split()[:5]  # First 5 words
        concept = " ".join(words)
        return f"abstract geometric shapes representing {concept}"

    def _extract_action_composition(self, narrative: str) -> str:
        """Extract action/composition hint from narrative."""
        # Look for action verbs or descriptive phrases
        narrative_lower = narrative.lower()

        if any(word in narrative_lower for word in ["transform", "change", "evolve"]):
            return "transforming with flowing energy"
        elif any(word in narrative_lower for word in ["grow", "expand", "scale"]):
            return "expanding with dynamic motion"
        elif any(word in narrative_lower for word in ["connect", "integrate", "link"]):
            return "with interconnected flowing lines"
        elif any(word in narrative_lower for word in ["speed", "fast", "quick", "efficient"]):
            return "with swift dynamic movement"
        elif any(word in narrative_lower for word in ["secure", "protect", "safe"]):
            return "with protective geometric patterns"
        elif any(word in narrative_lower for word in ["innovate", "create", "new"]):
            return "emerging with creative energy"
        else:
            return "with elegant flowing composition"

    def _map_visual_style_to_archetype(
        self,
        visual_style: str,
        global_brand: GlobalBrandVars
    ) -> str:
        """Map visual style to image archetype."""
        # Check global brand style for hints
        brand_style = global_brand.visual_style.lower() if global_brand.visual_style else ""

        if "photorealistic" in brand_style or visual_style == "professional":
            return "photorealistic"
        elif "minimalist" in brand_style or "technical" in brand_style:
            return "minimalist_vector_art"
        elif "vibrant" in brand_style or "playful" in brand_style or visual_style == "kids":
            return "illustration_flat_minimal"
        else:
            # Default for illustrated style
            return "illustration_detailed"

    def _build_content_prompt(
        self,
        request: ISeriesGenerationRequest
    ) -> str:
        """
        Build LLM prompt for text content generation.

        v1.3.0: Extracts content_context from request.context for
        audience-adapted language and vocabulary.

        Args:
            request: Generation request with narrative and content config

        Returns:
            LLM prompt string
        """
        content_style = request.content_style.value
        max_bullets = request.max_bullets
        content_dims = self.content_dimensions

        # v1.3.0: Extract content_context from request context
        context = request.context if hasattr(request, 'context') and request.context else {}
        content_context = context.get("content_context")
        theme_config = context.get("theme_config")

        # v1.3.0: Build audience section
        audience_section = ""
        if content_context:
            audience_info = content_context.get("audience", {})
            purpose_info = content_context.get("purpose", {})
            audience_type = audience_info.get("audience_type", "professional")
            complexity = audience_info.get("complexity_level", "moderate")
            avoid_jargon = audience_info.get("avoid_jargon", False)
            purpose_type = purpose_info.get("purpose_type", "inform")
            include_data = purpose_info.get("include_data", True)

            # Adjust max_bullets based on audience
            if audience_type in ["kids_tween", "kids_teen"]:
                max_bullets = min(max_bullets, 3)
            elif complexity == "low":
                max_bullets = min(max_bullets, 4)

            audience_section = f"""
## 📊 AUDIENCE & PURPOSE
- **Audience**: {audience_type} ({complexity} complexity)
- **Purpose**: {purpose_type}
- **Language**: {"Simple, clear language without jargon" if avoid_jargon else f"Professional language appropriate for {audience_type}"}
- **Data/Stats**: {"Include relevant numbers and data" if include_data else "Focus on concepts, minimize data"}
- **Tone**: {"Educational and encouraging" if audience_type.startswith("kids") else "Professional and authoritative" if purpose_type == "inform" else "Compelling and persuasive" if purpose_type == "persuade" else "Clear and instructive"}
"""

        # v1.3.0: Extract colors from theme_config with defaults
        if theme_config and "colors" in theme_config:
            colors = theme_config["colors"]
            text_color = colors.get("text_primary", "#374151")
        else:
            text_color = "#374151"

        # Determine format instructions based on content style
        if content_style == "bullets":
            format_instructions = f"""Format as a bullet list:
- Maximum {max_bullets} bullet points
- Each bullet: 60-100 characters
- Start with action verbs where appropriate
- Clear, professional language"""
        elif content_style == "paragraphs":
            format_instructions = """Format as paragraphs:
- 2-3 short paragraphs
- Each paragraph: 2-3 sentences
- Clear, professional language
- Logical flow between paragraphs"""
        else:  # mixed
            format_instructions = f"""Format as mixed content:
- Opening paragraph (1-2 sentences)
- {max_bullets - 1} bullet points
- Optional closing statement"""

        prompt = f"""Generate content for a presentation slide.

## Slide Information
Title: {request.title}
{f"Subtitle: {request.subtitle}" if request.subtitle else ""}
{audience_section}
## Narrative/Topic
{request.narrative}

## Key Topics to Cover
{', '.join(request.topics) if request.topics else 'General overview based on narrative'}

## Content Constraints
Content area size: {content_dims['width']}x{content_dims['height']} pixels
{format_instructions}

## Output Format
Return ONLY the HTML content (no code blocks, no explanations):
- For bullets: <ul class="content-list"><li>...</li></ul>
- For paragraphs: <div class="content-body"><p>...</p></div>
- For mixed: combine both formats

## Required Inline Styling
Include these inline CSS styles:
- Font family: 'Inter', -apple-system, sans-serif
- Font size: 1.5rem for body text
- Line height: 1.7
- Color: {text_color}
- Bullet/list spacing: margin-bottom: 0.75rem per item
- List style: disc for bullets

Generate the content HTML now:"""

        return prompt

    async def _generate_image(
        self,
        prompt: str,
        archetype: str,
        request: ISeriesGenerationRequest,
        aspect_ratio: str = "9:16",
        style_params: Optional[Dict[str, Any]] = None,
        image_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate portrait image via Image Service with correct aspect ratio.

        v1.3.1: Uses per-layout aspect ratio from ISERIES_LAYOUT_SPECS.
        - I1: 11:18 (660×1080)
        - I2: 2:3 (720×1080)
        - I3: 1:3 (360×1080, very narrow)
        - I4: 7:18 (420×1080, narrow)

        v1.4.0: Uses context-aware style_params for Image Builder v2.0 API.
        v1.5.0: Accepts image_model from Director for quality tier selection.

        Args:
            prompt: Image generation prompt
            archetype: Image style archetype
            request: Original request for metadata
            aspect_ratio: Target aspect ratio (e.g., "11:18", "2:3")
            style_params: Context-aware style parameters (style, color_scheme, lighting, domain)
            image_model: Imagen model to use (from Director ImageStyleAgreement)

        Returns:
            Image API response dict
        """
        metadata = {
            "slide_number": request.slide_number,
            "layout_type": self.layout_type,
            "narrative": request.narrative[:100],
            "visual_style": request.visual_style.value,
            "aspect_ratio": aspect_ratio
        }

        # v1.4.0: Add context info to metadata
        if style_params:
            metadata["context_style"] = style_params.get("style")
            metadata["context_domain"] = style_params.get("domain")

        # v1.5.0: Extract image_model from style_params if not explicitly provided
        model = image_model or (style_params.get("image_model") if style_params else None)

        return await self.image_client.generate_iseries_image(
            prompt=prompt,
            layout_type=self.layout_type,
            visual_style=request.visual_style.value,
            metadata=metadata,
            model=model,  # v1.5.0: Pass model for quality tier selection
            archetype=archetype,
            aspect_ratio=aspect_ratio,
            style_params=style_params  # v1.4.0: Pass style params to image client
        )

    async def _skip_image_task(self) -> Dict[str, Any]:
        """
        Return empty result when skipping image generation.

        v1.6.0: Used when skip_image_generation=True for testing content-only.

        Returns:
            Dict indicating image was skipped (triggers fallback placeholder)
        """
        return {
            "success": False,
            "skipped": True,
            "message": "Image generation skipped (skip_image_generation=True)"
        }

    async def _generate_content(
        self,
        prompt: str,
        request: ISeriesGenerationRequest
    ) -> Dict[str, Any]:
        """
        Generate text content via LLM.

        Args:
            prompt: LLM prompt
            request: Original request for validation

        Returns:
            Dict with content and validation results
        """
        # Generate with LLM
        raw_content = await self.llm_service(prompt)

        # Clean markdown wrappers
        content = self._clean_markdown_wrapper(raw_content)

        # Validate
        validation = self._validate_content(content, request)

        return {
            "content": content,
            "validation": validation
        }

    async def _generate_content_multi_step(
        self,
        request: ISeriesGenerationRequest,
        width_px: int,
        height_px: int,
        theme_config: Optional[Dict[str, Any]],
        content_context: Optional[Dict[str, Any]],
        styling_mode: str,
        variant_spec: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate content using multi-step pipeline or template assembly.

        v1.3.1: Uses MultiStepGenerator with hardcoded layout dimensions.
        v1.3.2: Added variant_spec support for I-series character constraints.
        v1.3.3: Template-based generation when variant_spec has template_path.
                Uses TemplateAssembler for rich styled HTML (colored headings,
                gradient underlines, etc.) matching C1 quality.

        Args:
            request: Original generation request
            width_px: Content area width in pixels (from ISERIES_LAYOUT_SPECS)
            height_px: Content area height in pixels (from ISERIES_LAYOUT_SPECS)
            theme_config: Optional theme configuration for styling
            content_context: Optional audience/purpose context
            styling_mode: "inline_styles" or "css_classes"
            variant_spec: Optional I-series variant spec with template_path and character requirements

        Returns:
            Dict with content HTML, validation, and metadata
        """
        # v1.3.3: Check if variant_spec has template_path for template-based generation
        if variant_spec and variant_spec.get("template_path"):
            try:
                return await self._generate_content_with_template(
                    request=request,
                    variant_spec=variant_spec,
                    theme_config=theme_config,
                    content_context=content_context
                )
            except Exception as e:
                logger.warning(f"Template-based generation failed: {e}. Falling back to multi-step.")

        # Original multi-step generation (fallback)
        try:
            from app.core.content import MultiStepGenerator
            from app.models.content_context import ContentContext, get_default_content_context
            from app.models.requests import ThemeConfig

            # Parse content_context if provided
            parsed_context = None
            if content_context:
                try:
                    parsed_context = ContentContext(**content_context)
                except Exception as e:
                    logger.warning(f"Failed to parse content_context: {e}")

            if parsed_context is None:
                parsed_context = get_default_content_context()

            # Parse theme_config if provided
            parsed_theme = None
            if theme_config:
                try:
                    parsed_theme = ThemeConfig(**theme_config)
                except Exception as e:
                    logger.warning(f"Failed to parse theme_config: {e}")

            # Create generator and run multi-step pipeline
            generator = MultiStepGenerator(self.llm_service)

            # v1.3.2: If variant_spec is provided, use its variant_id
            variant_id_hint = None
            if variant_spec:
                variant_id_hint = variant_spec.get("variant_id")

            result = await generator.generate(
                narrative=request.narrative,
                topics=request.topics or [],
                available_width_px=width_px,
                available_height_px=height_px,
                theme_config=parsed_theme,
                content_context=parsed_context,
                styling_mode=styling_mode,
                slide_number=request.slide_number,
                variant_id=variant_id_hint
            )

            # Extract content from multi-step result
            # v1.3.2: Include variant spec info in metadata
            multi_step_metadata = result.metadata.copy() if result.metadata else {}
            if variant_spec:
                multi_step_metadata["variant_spec"] = {
                    "variant_id": variant_spec.get("variant_id"),
                    "slide_type": variant_spec.get("slide_type"),
                    "iseries_layout": variant_spec.get("iseries_layout"),
                    "layout": variant_spec.get("layout", {})
                }

            return {
                "content": result.body,
                "validation": {
                    "valid": True,
                    "multi_step": True,
                    "phases_completed": result.metadata.get("multi_step", {}).get("phases_completed", []),
                    "layout_type": result.metadata.get("multi_step", {}).get("structure_plan", {}).get("layout_type"),
                    "variant_id": variant_id_hint
                },
                "metadata": multi_step_metadata
            }

        except Exception as e:
            logger.error(f"Multi-step content generation failed: {e}")
            # Fall back to single-step generation
            logger.warning("Falling back to single-step content generation")
            content_prompt = self._build_content_prompt(request)
            return await self._generate_content(content_prompt, request)

    async def _generate_content_with_template(
        self,
        request: ISeriesGenerationRequest,
        variant_spec: Dict[str, Any],
        theme_config: Optional[Dict[str, Any]],
        content_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate content using template-based assembly for rich styled HTML.

        v1.3.3: New method that uses TemplateAssembler like C1 variants.
        Produces rich HTML with colored headings, gradient underlines, etc.

        Args:
            request: Original generation request
            variant_spec: Variant spec with template_path and elements
            theme_config: Optional theme configuration
            content_context: Optional audience/purpose context

        Returns:
            Dict with rich styled HTML content, validation, and metadata
        """
        from app.core.template_assembler import TemplateAssembler
        from app.models.requests import ThemeConfig

        template_path = variant_spec.get("template_path")
        variant_id = variant_spec.get("variant_id")
        elements = variant_spec.get("elements", [])

        logger.info(f"Using template-based generation for {variant_id}")

        # Build LLM prompt to generate content for all placeholders
        prompt = self._build_template_content_prompt(
            request=request,
            variant_spec=variant_spec,
            content_context=content_context
        )

        # Generate content with LLM
        llm_response = await self.llm_service(prompt)

        # Parse LLM response into content map
        content_map = self._parse_template_response(
            llm_response=llm_response,
            variant_spec=variant_spec
        )

        # Assemble template with content
        assembler = TemplateAssembler()

        # Parse theme_config if provided
        parsed_theme = None
        if theme_config:
            try:
                parsed_theme = ThemeConfig(**theme_config)
            except Exception as e:
                logger.warning(f"Failed to parse theme_config: {e}")

        # Assemble with theme (handles themed template selection and color overrides)
        assembled_html = assembler.assemble_with_theme(
            template_path=template_path,
            content_map=content_map,
            theme_config=parsed_theme,
            variant_id=variant_id
        )

        return {
            "content": assembled_html,
            "validation": {
                "valid": True,
                "template_based": True,
                "template_path": template_path,
                "variant_id": variant_id
            },
            "metadata": {
                "generation_mode": "template_assembly",
                "variant_spec": {
                    "variant_id": variant_id,
                    "slide_type": variant_spec.get("slide_type"),
                    "iseries_layout": variant_spec.get("iseries_layout"),
                    "template_path": template_path
                }
            }
        }

    def _build_template_content_prompt(
        self,
        request: ISeriesGenerationRequest,
        variant_spec: Dict[str, Any],
        content_context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Build LLM prompt to generate content for template placeholders.

        Args:
            request: Generation request with narrative and topics
            variant_spec: Variant spec with elements and character requirements
            content_context: Optional audience/purpose context

        Returns:
            Prompt string for LLM
        """
        elements = variant_spec.get("elements", [])
        layout_info = variant_spec.get("layout", {})

        # Build placeholder specifications
        placeholder_specs = []
        for element in elements:
            element_id = element.get("element_id", "")
            placeholders = element.get("placeholders", {})
            char_reqs = element.get("character_requirements", {})

            for field_name, placeholder_name in placeholders.items():
                char_req = char_reqs.get(field_name, {})
                baseline = char_req.get("baseline", 50)
                min_chars = char_req.get("min", 20)
                max_chars = char_req.get("max", 100)

                placeholder_specs.append(
                    f"- {placeholder_name}: {field_name} for {element_id} "
                    f"(target: {baseline} chars, range: {min_chars}-{max_chars})"
                )

        placeholders_section = "\n".join(placeholder_specs)

        # Build audience section if content_context provided
        audience_section = ""
        if content_context:
            audience_info = content_context.get("audience", {})
            audience_type = audience_info.get("audience_type", "professional")
            complexity = audience_info.get("complexity_level", "moderate")
            audience_section = f"""
## Audience
- Type: {audience_type}
- Complexity: {complexity}
"""

        # Build prompt
        prompt = f"""Generate slide content for the following presentation slide.

## Slide Information
Title: {request.title}
{f"Subtitle: {request.subtitle}" if request.subtitle else ""}

## Narrative/Topic
{request.narrative}

## Key Topics
{', '.join(request.topics) if request.topics else 'Based on narrative'}
{audience_section}
## Required Placeholders
Generate content for each placeholder below. Follow character limits carefully.
{placeholders_section}

## Output Format
Return a JSON object with each placeholder as a key and the generated content as the value.
Example:
{{
  "section_1_heading": "First Section Title",
  "section_1_bullet_1": "First bullet point content here",
  ...
}}

IMPORTANT:
1. Generate ONLY plain text content (no HTML tags)
2. Stay within character limits
3. Make content cohesive and complementary across all sections
4. Use professional, concise language
5. Start bullet points with action verbs where appropriate

Generate the JSON object now:"""

        return prompt

    def _parse_template_response(
        self,
        llm_response: str,
        variant_spec: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Parse LLM response into content map for template assembly.

        Args:
            llm_response: Raw LLM response (expected JSON format)
            variant_spec: Variant spec with expected placeholders

        Returns:
            Content map dictionary
        """
        # Try to parse as JSON
        try:
            # Clean markdown wrappers if present
            cleaned = llm_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            content_map = json.loads(cleaned)

            # Validate all expected placeholders are present
            elements = variant_spec.get("elements", [])
            expected_placeholders = set()
            for element in elements:
                placeholders = element.get("placeholders", {})
                expected_placeholders.update(placeholders.values())

            missing = expected_placeholders - set(content_map.keys())
            if missing:
                logger.warning(f"Missing placeholders in LLM response: {missing}")
                # Fill missing with placeholder text
                for placeholder in missing:
                    content_map[placeholder] = f"[{placeholder}]"

            return content_map

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Raw response: {llm_response[:500]}")

            # Fallback: try to extract key-value pairs
            content_map = {}
            elements = variant_spec.get("elements", [])
            for element in elements:
                placeholders = element.get("placeholders", {})
                for field_name, placeholder_name in placeholders.items():
                    content_map[placeholder_name] = f"[{placeholder_name}]"

            return content_map

    def _clean_markdown_wrapper(self, content: str) -> str:
        """
        Remove markdown code fences that LLMs often add.

        Args:
            content: Raw LLM output

        Returns:
            Cleaned HTML content
        """
        # Remove ```html ... ``` wrappers
        content = re.sub(r'^```html?\s*\n?', '', content, flags=re.IGNORECASE)
        content = re.sub(r'\n?```\s*$', '', content)

        # Remove leading/trailing whitespace
        content = content.strip()

        return content

    def _validate_content(
        self,
        content: str,
        request: ISeriesGenerationRequest
    ) -> Dict[str, Any]:
        """
        Validate generated content for security and structure.

        Args:
            content: Generated HTML content
            request: Original request for context

        Returns:
            Validation result dictionary
        """
        violations = []
        warnings = []

        # Security checks
        dangerous_patterns = [
            (r'<script', 'script tags not allowed'),
            (r'javascript:', 'javascript: protocol not allowed'),
            (r'onerror\s*=', 'onerror handlers not allowed'),
            (r'onclick\s*=', 'onclick handlers not allowed'),
        ]

        for pattern, message in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(message)

        # Structure checks
        if not content.strip():
            violations.append("Content is empty")

        # Check for expected elements
        has_list = bool(re.search(r'<ul|<ol', content, re.IGNORECASE))
        has_paragraph = bool(re.search(r'<p|<div', content, re.IGNORECASE))

        if request.content_style == ISeriesContentStyle.BULLETS and not has_list:
            warnings.append("Bullets requested but no list found")
        if request.content_style == ISeriesContentStyle.PARAGRAPHS and not has_paragraph:
            warnings.append("Paragraphs requested but no paragraph found")

        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "has_list": has_list,
            "has_paragraph": has_paragraph
        }

    def _build_response(
        self,
        image_url: Optional[str],
        image_fallback: bool,
        content_result: Dict[str, Any],
        request: ISeriesGenerationRequest,
        generation_time_ms: int
    ) -> ISeriesGenerationResponse:
        """
        Build final response with all slot HTML.

        Args:
            image_url: Generated image URL or None
            image_fallback: Whether using fallback
            content_result: Content generation result
            request: Original request
            generation_time_ms: Total generation time

        Returns:
            ISeriesGenerationResponse
        """
        # Build image HTML
        image_html = self._build_image_html(image_url, request)

        # Build title HTML
        title_html = self._build_title_html(request.title)

        # Build subtitle HTML (if provided)
        subtitle_html = None
        if request.subtitle:
            subtitle_html = self._build_subtitle_html(request.subtitle)

        # Get content HTML
        content_html = content_result["content"]

        # Build metadata with multi-step info
        layout_spec = ISERIES_LAYOUT_SPECS.get(self.layout_type, ISERIES_LAYOUT_SPECS["I1"])
        metadata = {
            "layout_type": self.layout_type,
            "slide_number": request.slide_number,
            "image_position": self.image_position,
            "image_dimensions": self.image_dimensions,
            "image_aspect_ratio": layout_spec["image"]["aspect_ratio"],
            "content_dimensions": self.content_dimensions,
            "visual_style": request.visual_style.value,
            "content_style": request.content_style.value,
            "generation_time_ms": generation_time_ms,
            "validation": content_result.get("validation", {}),
            # v1.3.1: Multi-step generation metadata
            "multi_step": content_result.get("metadata", {}).get("multi_step", {
                "enabled": content_result.get("validation", {}).get("multi_step", False)
            }),
            "generation_mode": "multi_step" if content_result.get("validation", {}).get("multi_step") else "single_step"
        }

        # Per SLIDE_GENERATION_INPUT_SPEC.md: I-series uses background_color #ffffff
        return ISeriesGenerationResponse(
            image_html=image_html,
            title_html=title_html,
            subtitle_html=subtitle_html,
            content_html=content_html,
            image_url=image_url,
            image_fallback=image_fallback,
            background_color="#ffffff",  # Default per SPEC
            metadata=metadata
        )

    def _build_image_html(
        self,
        image_url: Optional[str],
        request: ISeriesGenerationRequest
    ) -> str:
        """
        Build HTML for image slot.

        Args:
            image_url: Generated image URL or None
            request: Original request for context

        Returns:
            HTML string for image slot
        """
        if image_url:
            return f'''<div style="width: 100%; height: 100%; overflow: hidden;">
    <img src="{image_url}"
         alt="Slide visual"
         style="width: 100%; height: 100%; object-fit: cover;"
    />
</div>'''
        else:
            # Placeholder gradient based on visual style
            gradient = self._get_fallback_gradient(request.visual_style)
            return f'''<div style="width: 100%; height: 100%;
    background: {gradient};
    display: flex; align-items: center; justify-content: center;">
    <span style="color: rgba(255,255,255,0.3); font-size: 48px; font-family: 'Inter', sans-serif;">IMAGE</span>
</div>'''

    def _get_fallback_gradient(self, visual_style: ISeriesVisualStyle) -> str:
        """
        Get fallback gradient based on visual style.

        Args:
            visual_style: Visual style enum

        Returns:
            CSS gradient string
        """
        gradients = {
            ISeriesVisualStyle.PROFESSIONAL: "linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%)",
            ISeriesVisualStyle.ILLUSTRATED: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            ISeriesVisualStyle.KIDS: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        }
        return gradients.get(visual_style, gradients[ISeriesVisualStyle.ILLUSTRATED])

    def _build_title_html(self, title: str) -> str:
        """
        Build HTML for title slot.

        Args:
            title: Slide title text

        Returns:
            HTML string for title
        """
        return f'''<h2 style="margin: 0 0 16px 0; font-size: 2.75rem; font-weight: 700;
    color: #1f2937; font-family: 'Inter', -apple-system, sans-serif;
    line-height: 1.2; letter-spacing: -0.02em;">{title}</h2>'''

    def _build_subtitle_html(self, subtitle: str) -> str:
        """
        Build HTML for subtitle slot.

        Args:
            subtitle: Subtitle text

        Returns:
            HTML string for subtitle
        """
        return f'''<p style="margin: 0 0 24px 0; font-size: 1.5rem; font-weight: 400;
    color: #6b7280; font-family: 'Inter', -apple-system, sans-serif;
    line-height: 1.5;">{subtitle}</p>'''
