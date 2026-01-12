"""
Spotlight Concept Extractor for I-Series 2-Step Image Generation

Step 1 of 2-step image generation: Extracts visual concept from narrative.
Uses hybrid approach - LLM for complex narratives, rules for simple ones.

Key Features:
- Complexity detection via keyword analysis
- Rule-based extraction for simple narratives (instant)
- LLM-based extraction for complex narratives (~2-3s)
- Domain-aware subject mappings
- Spotlight depth based on audience/purpose

Version: 1.0.0
"""

import logging
import re
import json
from typing import Optional, Dict, Any, List, Tuple, Callable
from dataclasses import dataclass

from app.models.iseries_models import (
    SpotlightConcept,
    AbstractionLevel,
    SpotlightDepth
)
from app.core.iseries.context_style_mapper import detect_domain_from_text

logger = logging.getLogger(__name__)


# =============================================================================
# Complexity Detection
# =============================================================================

@dataclass
class ComplexityAnalysis:
    """Result of narrative complexity analysis."""
    is_complex: bool
    score: float  # 0.0 - 1.0
    indicators: List[str]


# Complexity indicators with categories
COMPLEXITY_INDICATORS = {
    # Abstract/metaphorical language (weight: 0.30)
    "abstract_terms": [
        "transformation", "journey", "evolution", "paradigm", "synergy",
        "catalyst", "ecosystem", "framework", "landscape", "architecture",
        "blueprint", "roadmap", "bridge", "foundation", "pillar",
        "horizon", "frontier", "cornerstone", "vision", "revolution"
    ],
    # Comparative/contrasting language (weight: 0.20)
    "comparison_terms": [
        "versus", "compared to", "unlike", "whereas", "on the other hand",
        "in contrast", "alternatively", "similarly", "just as", "like a",
        "analogous", "parallel to", "distinct from", "differentiate"
    ],
    # Emotional/evocative language (weight: 0.20)
    "emotional_terms": [
        "revolutionize", "transform", "empower", "unleash", "ignite",
        "inspire", "breakthrough", "game-changing", "visionary", "pioneering",
        "disruptive", "innovative", "groundbreaking", "reimagine", "elevate"
    ],
    # Technical complexity markers (weight: 0.15)
    "technical_density": [
        "algorithm", "infrastructure", "architecture", "protocol", "framework",
        "integration", "implementation", "optimization", "scalability",
        "microservices", "orchestration", "containerization", "distributed"
    ],
    # Structural complexity (weight: 0.15)
    "structural_markers": [
        "furthermore", "moreover", "consequently", "therefore", "hence",
        "as a result", "in order to", "by leveraging", "through",
        "subsequently", "accordingly", "whereby", "insofar as"
    ]
}

COMPLEXITY_WEIGHTS = {
    "abstract_terms": 0.30,
    "comparison_terms": 0.20,
    "emotional_terms": 0.20,
    "technical_density": 0.15,
    "structural_markers": 0.15
}


def analyze_narrative_complexity(
    narrative: str,
    topics: List[str],
    threshold: float = 0.35
) -> ComplexityAnalysis:
    """
    Analyze narrative complexity to determine LLM vs rule-based extraction.

    Args:
        narrative: Main narrative text
        topics: List of topic strings
        threshold: Score threshold for is_complex (default: 0.35)

    Returns:
        ComplexityAnalysis with is_complex flag and score
    """
    combined_text = f"{narrative} {' '.join(topics)}".lower()
    indicators_found = []

    total_score = 0.0

    for category, terms in COMPLEXITY_INDICATORS.items():
        matches = [t for t in terms if t in combined_text]
        if matches:
            # Score based on number of matches (capped at 3)
            category_score = min(len(matches) / 3.0, 1.0) * COMPLEXITY_WEIGHTS[category]
            total_score += category_score
            indicators_found.extend(matches[:2])  # Track up to 2 per category

    # Additional heuristics
    sentences = re.split(r'[.!?]+', narrative)
    sentence_count = len([s for s in sentences if s.strip()])
    word_count = len(narrative.split())
    avg_sentence_length = word_count / max(sentence_count, 1)

    # Long sentences indicate complexity
    if avg_sentence_length > 20:
        total_score += 0.10
        indicators_found.append("long_sentences")

    # Multiple topics indicate complexity
    if len(topics) >= 4:
        total_score += 0.10
        indicators_found.append("many_topics")

    # Multiple sentences indicate complexity
    if sentence_count >= 3:
        total_score += 0.05
        indicators_found.append("multi_sentence")

    # Clamp score to [0, 1]
    total_score = min(max(total_score, 0.0), 1.0)

    is_complex = total_score >= threshold

    logger.debug(
        f"Complexity analysis: score={total_score:.2f}, "
        f"is_complex={is_complex}, indicators={indicators_found[:5]}"
    )

    return ComplexityAnalysis(
        is_complex=is_complex,
        score=total_score,
        indicators=indicators_found
    )


# =============================================================================
# Domain -> Subject Mappings for Rule-Based Extraction
# =============================================================================

DOMAIN_SUBJECT_MAPPING: Dict[str, Dict[str, Any]] = {
    "technology": {
        "primary_subjects": [
            "interconnected circuit board patterns with glowing pathways",
            "abstract data stream visualization with flowing particles",
            "network node constellation with luminous connections",
            "digital mesh gradient with geometric tech patterns"
        ],
        "visual_elements": [
            "glowing connection lines",
            "data particle flow",
            "holographic interface elements",
            "geometric tech patterns"
        ],
        "default_abstraction": AbstractionLevel.ABSTRACT
    },
    "business": {
        "primary_subjects": [
            "modern cityscape silhouette with rising towers",
            "ascending growth chart with dynamic upward motion",
            "interconnected building blocks in structured formation",
            "professional workspace vista with clean lines"
        ],
        "visual_elements": [
            "subtle grid overlay",
            "progress indicator elements",
            "clean geometric shapes",
            "professional gradient backdrop"
        ],
        "default_abstraction": AbstractionLevel.METAPHORICAL
    },
    "healthcare": {
        "primary_subjects": [
            "modern medical technology abstract with clean aesthetics",
            "wellness symbol composition with life-affirming imagery",
            "health monitoring interface with vital signs visualization",
            "clinical environment vista with pristine surfaces"
        ],
        "visual_elements": [
            "clean white surfaces",
            "subtle blue medical accents",
            "health iconography",
            "wellness gradient"
        ],
        "default_abstraction": AbstractionLevel.LITERAL
    },
    "education": {
        "primary_subjects": [
            "knowledge pathway visualization with enlightenment symbolism",
            "learning journey landscape with growth elements",
            "academic achievement symbolism with aspiration",
            "enlightenment imagery with illumination"
        ],
        "visual_elements": [
            "book and document motifs",
            "growth symbolism",
            "pathway elements",
            "light and clarity"
        ],
        "default_abstraction": AbstractionLevel.METAPHORICAL
    },
    "science": {
        "primary_subjects": [
            "laboratory equipment abstract with precision focus",
            "molecular structure visualization with atomic detail",
            "research discovery moment with eureka symbolism",
            "scientific process imagery with methodical flow"
        ],
        "visual_elements": [
            "molecular patterns",
            "experimental apparatus",
            "data visualization",
            "discovery symbolism"
        ],
        "default_abstraction": AbstractionLevel.ABSTRACT
    },
    "nature": {
        "primary_subjects": [
            "pristine natural landscape with untouched beauty",
            "sustainable ecosystem view with biodiversity",
            "environmental harmony scene with balance",
            "natural balance imagery with organic flow"
        ],
        "visual_elements": [
            "organic patterns",
            "natural textures",
            "environmental elements",
            "life and growth symbols"
        ],
        "default_abstraction": AbstractionLevel.LITERAL
    },
    "creative": {
        "primary_subjects": [
            "artistic expression abstract with color dynamics",
            "creative process visualization with inspiration flow",
            "design studio atmosphere with tools and materials",
            "artistic inspiration scene with imaginative elements"
        ],
        "visual_elements": [
            "color splash effects",
            "artistic tools",
            "creative textures",
            "expressive patterns"
        ],
        "default_abstraction": AbstractionLevel.ABSTRACT
    },
    "default": {
        "primary_subjects": [
            "professional gradient backdrop with subtle depth",
            "abstract geometric composition with clean lines",
            "modern minimalist scene with elegant simplicity",
            "clean professional environment with refined aesthetics"
        ],
        "visual_elements": [
            "subtle patterns",
            "professional colors",
            "geometric shapes",
            "clean lines"
        ],
        "default_abstraction": AbstractionLevel.ABSTRACT
    }
}

# Emotional focus based on purpose
PURPOSE_EMOTIONAL_MAP: Dict[str, str] = {
    "inform": "professional",
    "educate": "encouraging",
    "persuade": "inspiring",
    "entertain": "energetic",
    "inspire": "uplifting",
    "report": "serious"
}


# =============================================================================
# Rule-Based Concept Extraction
# =============================================================================

def extract_concept_rule_based(
    narrative: str,
    topics: List[str],
    domain: str,
    audience_type: Optional[str] = None,
    purpose_type: Optional[str] = None,
    spotlight_depth: SpotlightDepth = SpotlightDepth.FOCUSED
) -> SpotlightConcept:
    """
    Extract visual concept using rule-based mapping.

    Used for simple narratives where LLM call is unnecessary.

    Args:
        narrative: Main narrative text
        topics: List of topic strings
        domain: Detected content domain
        audience_type: Target audience
        purpose_type: Presentation purpose
        spotlight_depth: How rich the visual should be

    Returns:
        SpotlightConcept with extracted visual concept
    """
    import random

    # Get domain-specific mappings
    domain_config = DOMAIN_SUBJECT_MAPPING.get(domain, DOMAIN_SUBJECT_MAPPING["default"])

    # Select primary subject (use first if topics hint at specificity)
    primary_subjects = domain_config["primary_subjects"]
    if topics and len(topics) >= 2:
        # More topics = use more structured subject
        primary_subject = primary_subjects[min(len(topics) - 1, len(primary_subjects) - 1)]
    else:
        primary_subject = random.choice(primary_subjects)

    # Select visual elements based on spotlight depth
    all_elements = domain_config["visual_elements"]
    if spotlight_depth == SpotlightDepth.MINIMAL:
        visual_elements = []
    elif spotlight_depth == SpotlightDepth.FOCUSED:
        visual_elements = all_elements[:1]
    elif spotlight_depth == SpotlightDepth.RICH:
        visual_elements = all_elements[:2]
    else:  # LAYERED
        visual_elements = all_elements[:3]

    # Determine emotional focus from purpose
    emotional_focus = PURPOSE_EMOTIONAL_MAP.get(
        purpose_type.lower() if purpose_type else "inform",
        "professional"
    )

    # Determine abstraction level (may be overridden by audience)
    abstraction = domain_config["default_abstraction"]
    if audience_type:
        audience_lower = audience_type.lower()
        if audience_lower in ["executives", "technical", "developers"]:
            abstraction = AbstractionLevel.ABSTRACT  # Clean, minimal
        elif audience_lower in ["kids_tween", "kids_teen", "kids_young", "children"]:
            abstraction = AbstractionLevel.LITERAL  # Concrete imagery

    # Composition hint based on topic count
    composition_hint = "centered"  # Default
    if len(topics) > 3:
        composition_hint = "environmental"  # Broader scene for many topics

    return SpotlightConcept(
        primary_subject=primary_subject,
        visual_elements=visual_elements,
        composition_hint=composition_hint,
        emotional_focus=emotional_focus,
        abstraction_level=abstraction,
        spotlight_rationale=f"Rule-based extraction for {domain} domain (depth: {spotlight_depth.value})"
    )


# =============================================================================
# LLM-Based Concept Extraction
# =============================================================================

CONCEPT_EXTRACTION_PROMPT = """Extract the core visual concept for an image that represents this slide content.

NARRATIVE:
{narrative}

TOPICS:
{topics}

DOMAIN: {domain}
AUDIENCE: {audience_type}
PURPOSE: {purpose_type}
SPOTLIGHT DEPTH: {spotlight_depth}

Based on the narrative, identify:
1. PRIMARY SUBJECT: The single most important visual element that captures the main message
2. VISUAL ELEMENTS: 1-3 supporting visual elements (based on spotlight depth)
3. COMPOSITION: How elements should be arranged (centered, environmental, left-weighted, right-weighted)
4. EMOTIONAL FOCUS: The feeling the image should evoke (professional, inspiring, energetic, calm, serious, encouraging, uplifting)
5. ABSTRACTION LEVEL: How literal vs abstract (literal, metaphorical, abstract)

SPOTLIGHT DEPTH GUIDANCE:
- minimal: Single clean element, no metaphor, executives/technical audiences
- focused: Primary element + 1 supporting, professional presentations
- rich: Full concept with metaphor and mood, educational/inspiring content
- layered: Complex multi-element composition, creative/storytelling

CRITICAL REQUIREMENTS:
- Focus on WHAT to show, not HOW to show it
- Choose imagery that represents the core message, not just the topic
- For abstract concepts, use visual metaphors
- NEVER include text, words, letters, numbers in the concept
- NEVER include human faces, people, or characters in the concept
- Focus purely on objects, environments, patterns, and abstract visuals

Return ONLY valid JSON (no markdown, no explanation):
{{
    "primary_subject": "main visual element description (50-150 chars)",
    "visual_elements": ["element1", "element2"],
    "composition_hint": "centered|environmental|left-weighted|right-weighted",
    "emotional_focus": "professional|inspiring|energetic|calm|serious|encouraging|uplifting",
    "abstraction_level": "literal|metaphorical|abstract",
    "spotlight_rationale": "brief explanation (under 100 chars)"
}}
"""


async def extract_concept_llm(
    llm_service: Callable,
    narrative: str,
    topics: List[str],
    domain: str,
    audience_type: Optional[str] = None,
    purpose_type: Optional[str] = None,
    spotlight_depth: SpotlightDepth = SpotlightDepth.FOCUSED
) -> SpotlightConcept:
    """
    Extract visual concept using LLM for complex narratives.

    Args:
        llm_service: Async LLM callable that takes prompt and returns response
        narrative: Main narrative text
        topics: List of topic strings
        domain: Detected content domain
        audience_type: Target audience
        purpose_type: Presentation purpose
        spotlight_depth: How rich the visual should be

    Returns:
        SpotlightConcept with LLM-extracted visual concept
    """
    prompt = CONCEPT_EXTRACTION_PROMPT.format(
        narrative=narrative,
        topics=", ".join(topics) if topics else "General overview",
        domain=domain,
        audience_type=audience_type or "professional",
        purpose_type=purpose_type or "inform",
        spotlight_depth=spotlight_depth.value
    )

    try:
        response = await llm_service(prompt)

        # Clean response - remove markdown code blocks if present
        text = response.strip()
        if text.startswith("```"):
            # Find content between first ``` and last ```
            parts = text.split("```")
            if len(parts) >= 3:
                text = parts[1]
                if text.startswith("json"):
                    text = text[4:]
            else:
                text = parts[1] if len(parts) > 1 else text
        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        # Parse JSON response
        data = json.loads(text)

        # Parse abstraction level
        abstraction_str = data.get("abstraction_level", "abstract").lower()
        try:
            abstraction = AbstractionLevel(abstraction_str)
        except ValueError:
            abstraction = AbstractionLevel.ABSTRACT

        # Validate visual_elements length
        visual_elements = data.get("visual_elements", [])
        if isinstance(visual_elements, list):
            visual_elements = visual_elements[:3]  # Max 3
        else:
            visual_elements = []

        return SpotlightConcept(
            primary_subject=data.get("primary_subject", "abstract professional visualization")[:150],
            visual_elements=visual_elements,
            composition_hint=data.get("composition_hint", "centered"),
            emotional_focus=data.get("emotional_focus", "professional"),
            abstraction_level=abstraction,
            spotlight_rationale=data.get("spotlight_rationale", "LLM extraction")[:100]
        )

    except json.JSONDecodeError as e:
        logger.warning(f"LLM response JSON parse failed: {e}. Response: {text[:200]}...")
        # Fall back to rule-based
        return extract_concept_rule_based(
            narrative, topics, domain, audience_type, purpose_type, spotlight_depth
        )

    except Exception as e:
        logger.warning(f"LLM concept extraction failed: {e}. Falling back to rule-based.")
        return extract_concept_rule_based(
            narrative, topics, domain, audience_type, purpose_type, spotlight_depth
        )


# =============================================================================
# Main Extractor Class
# =============================================================================

class SpotlightConceptExtractor:
    """
    Hybrid concept extractor for 2-step image generation.

    Determines complexity and routes to appropriate extraction method:
    - Simple narratives: Rule-based extraction (fast, no LLM call)
    - Complex narratives: LLM-based extraction (slower, better quality)

    Usage:
        extractor = SpotlightConceptExtractor(llm_service=my_llm_func)
        concept, metadata = await extractor.extract(
            narrative="Our platform revolutionizes...",
            topics=["Speed", "Reliability", "Cost"],
            audience_type="executives",
            purpose_type="persuade"
        )
    """

    def __init__(
        self,
        llm_service: Optional[Callable] = None,
        complexity_threshold: float = 0.35
    ):
        """
        Initialize extractor.

        Args:
            llm_service: Async LLM callable (optional for rule-only mode)
            complexity_threshold: Score threshold for LLM usage (default: 0.35)
        """
        self.llm_service = llm_service
        self.complexity_threshold = complexity_threshold

        # Stats tracking
        self.total_extractions = 0
        self.llm_extractions = 0
        self.rule_extractions = 0

    async def extract(
        self,
        narrative: str,
        topics: List[str],
        audience_type: Optional[str] = None,
        purpose_type: Optional[str] = None,
        content_context: Optional[Dict[str, Any]] = None,
        force_llm: bool = False,
        force_rules: bool = False
    ) -> Tuple[SpotlightConcept, Dict[str, Any]]:
        """
        Extract visual concept using hybrid approach.

        Args:
            narrative: Main narrative text
            topics: List of topic strings
            audience_type: Target audience (from content_context if not provided)
            purpose_type: Presentation purpose (from content_context if not provided)
            content_context: Optional full ContentContext dict
            force_llm: Force LLM extraction regardless of complexity
            force_rules: Force rule-based extraction regardless of complexity

        Returns:
            Tuple of (SpotlightConcept, extraction_metadata)
        """
        self.total_extractions += 1

        # Extract context params if not provided directly
        if content_context:
            if not audience_type:
                audience_info = content_context.get("audience", {})
                audience_type = audience_info.get("audience_type")
            if not purpose_type:
                purpose_info = content_context.get("purpose", {})
                purpose_type = purpose_info.get("purpose_type")

        # Detect domain from narrative + topics
        combined_text = f"{narrative} {' '.join(topics)}".lower()
        domain = detect_domain_from_text(combined_text)

        # Import here to avoid circular import
        from app.core.iseries.context_style_mapper import get_spotlight_depth

        # Get spotlight depth based on audience/purpose
        spotlight_depth = get_spotlight_depth(
            audience_type or "professional",
            purpose_type or "inform"
        )

        # Analyze complexity
        complexity = analyze_narrative_complexity(
            narrative, topics, threshold=self.complexity_threshold
        )

        # Determine extraction method
        use_llm = False
        if force_llm and self.llm_service:
            use_llm = True
        elif force_rules:
            use_llm = False
        elif complexity.is_complex and self.llm_service:
            use_llm = True

        # Extract concept
        if use_llm:
            self.llm_extractions += 1
            concept = await extract_concept_llm(
                self.llm_service,
                narrative,
                topics,
                domain,
                audience_type,
                purpose_type,
                spotlight_depth
            )
            extraction_method = "llm"
        else:
            self.rule_extractions += 1
            concept = extract_concept_rule_based(
                narrative,
                topics,
                domain,
                audience_type,
                purpose_type,
                spotlight_depth
            )
            extraction_method = "rules"

        # Build metadata
        metadata = {
            "extraction_method": extraction_method,
            "domain": domain,
            "spotlight_depth": spotlight_depth.value,
            "complexity_score": complexity.score,
            "complexity_indicators": complexity.indicators[:5],  # Limit indicators
            "audience_type": audience_type,
            "purpose_type": purpose_type
        }

        logger.info(
            f"Spotlight concept extracted (method={extraction_method}, "
            f"domain={domain}, depth={spotlight_depth.value}, "
            f"subject='{concept.primary_subject[:50]}...')"
        )

        return concept, metadata

    def get_stats(self) -> Dict[str, Any]:
        """Get extraction statistics."""
        llm_pct = (
            self.llm_extractions / self.total_extractions * 100
            if self.total_extractions > 0 else 0
        )

        return {
            "total_extractions": self.total_extractions,
            "llm_extractions": self.llm_extractions,
            "rule_extractions": self.rule_extractions,
            "llm_percentage": f"{llm_pct:.1f}%"
        }

    def reset_stats(self):
        """Reset extraction statistics."""
        self.total_extractions = 0
        self.llm_extractions = 0
        self.rule_extractions = 0
