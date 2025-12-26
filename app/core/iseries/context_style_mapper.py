"""
Context-Aware Style Mapper for I-Series Image Generation

Maps ContentContext (audience, purpose, emotional tone) to image style parameters.
Used to generate contextually relevant images instead of generic illustrations.

Usage:
    from app.core.iseries.context_style_mapper import get_image_style_params

    style_params = get_image_style_params(
        audience_type="executives",
        purpose_type="inform",
        domain="technology"
    )
    # Returns: {"style": "photo", "color_scheme": "neutral", "lighting": "professional", ...}

Version: 1.0.0 - Initial context-aware image styling
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AudienceStyleParams:
    """Style parameters derived from audience type."""
    style: str  # photo, minimal, illustration
    color_scheme: str  # neutral, cool, warm, vibrant
    lighting: str  # professional, clean, soft, bright, playful
    avoid_elements: list  # Elements to avoid for this audience


@dataclass
class PurposeStyleParams:
    """Style parameters derived from purpose type."""
    emphasis: str  # clarity, impact, emotion, accessibility, engagement
    composition: str  # structured, dynamic, aspirational, clear, playful
    mood: str  # informative, persuasive, inspiring, educational, entertaining


@dataclass
class DomainImagery:
    """Domain-specific imagery configuration."""
    elements: list  # Positive elements to include
    avoid: list  # Elements to exclude
    style_override: Optional[str]  # Override style if domain requires it


# Audience → Style mapping
# Maps audience types to appropriate visual treatment
AUDIENCE_STYLE_MAP: Dict[str, AudienceStyleParams] = {
    # Professional/Executive audiences - clean, photorealistic
    "executives": AudienceStyleParams(
        style="photo",
        color_scheme="neutral",
        lighting="professional",
        avoid_elements=["cartoon", "anime", "playful", "childish"]
    ),
    "professional": AudienceStyleParams(
        style="photo",
        color_scheme="neutral",
        lighting="professional",
        avoid_elements=["cartoon", "anime", "playful", "childish"]
    ),

    # Technical audiences - minimal, clean diagrams
    "technical": AudienceStyleParams(
        style="minimal",
        color_scheme="cool",
        lighting="clean",
        avoid_elements=["people", "faces", "cartoon characters"]
    ),
    "developers": AudienceStyleParams(
        style="minimal",
        color_scheme="cool",
        lighting="clean",
        avoid_elements=["people", "faces", "cartoon characters"]
    ),

    # General audience - accessible illustrations
    "general": AudienceStyleParams(
        style="illustration",
        color_scheme="warm",
        lighting="soft",
        avoid_elements=["complex technical diagrams", "jargon-heavy imagery"]
    ),

    # Students - engaging, educational
    "students": AudienceStyleParams(
        style="illustration",
        color_scheme="vibrant",
        lighting="bright",
        avoid_elements=["corporate stock photos", "boring office settings"]
    ),

    # Kids/Youth - playful, colorful
    "kids_tween": AudienceStyleParams(
        style="illustration",
        color_scheme="vibrant",
        lighting="playful",
        avoid_elements=["realistic faces", "corporate settings", "adult themes"]
    ),
    "kids_teen": AudienceStyleParams(
        style="illustration",
        color_scheme="vibrant",
        lighting="bright",
        avoid_elements=["childish cartoons", "corporate settings"]
    ),

    # Default fallback
    "default": AudienceStyleParams(
        style="photo",
        color_scheme="neutral",
        lighting="professional",
        avoid_elements=["cartoon", "anime"]
    )
}


# Purpose → Style mapping
# Maps presentation purpose to visual emphasis and composition
PURPOSE_STYLE_MAP: Dict[str, PurposeStyleParams] = {
    # Informative - clear, structured
    "inform": PurposeStyleParams(
        emphasis="clarity",
        composition="structured",
        mood="informative"
    ),

    # Persuasive - impactful, dynamic
    "persuade": PurposeStyleParams(
        emphasis="impact",
        composition="dynamic",
        mood="persuasive"
    ),

    # Inspiring - emotional, aspirational
    "inspire": PurposeStyleParams(
        emphasis="emotion",
        composition="aspirational",
        mood="inspiring"
    ),

    # Educational - accessible, clear
    "educate": PurposeStyleParams(
        emphasis="accessibility",
        composition="clear",
        mood="educational"
    ),

    # Entertaining - engaging, playful
    "entertain": PurposeStyleParams(
        emphasis="engagement",
        composition="playful",
        mood="entertaining"
    ),

    # Default fallback
    "default": PurposeStyleParams(
        emphasis="clarity",
        composition="structured",
        mood="professional"
    )
}


# Domain → Imagery mapping
# Provides specific visual elements and anti-patterns per domain
DOMAIN_IMAGERY_MAP: Dict[str, DomainImagery] = {
    # Technology - abstract, clean, no people
    "technology": DomainImagery(
        elements=[
            "circuit board patterns",
            "abstract data visualization",
            "network topology diagrams",
            "server infrastructure",
            "code on screens (blurred)",
            "tech workspace with monitors",
            "cloud computing abstract",
            "digital transformation visuals"
        ],
        avoid=[
            "human faces",
            "anime characters",
            "cartoon people",
            "smiling businesspeople",
            "stock photo handshakes"
        ],
        style_override="minimal"  # Tech content should be clean/minimal
    ),

    # Business/Finance - professional, corporate
    "business": DomainImagery(
        elements=[
            "abstract growth charts",
            "geometric patterns",
            "modern office architecture",
            "city skyline silhouettes",
            "professional meeting rooms",
            "abstract success imagery"
        ],
        avoid=[
            "anime style",
            "cartoon characters",
            "childish imagery",
            "casual settings"
        ],
        style_override="photo"
    ),

    # Healthcare - clean, clinical, hopeful
    "healthcare": DomainImagery(
        elements=[
            "modern medical equipment",
            "health and wellness icons",
            "abstract body systems",
            "clinical environment",
            "medical technology",
            "wellness lifestyle imagery"
        ],
        avoid=[
            "graphic medical procedures",
            "patient faces",
            "blood or surgery",
            "distressing imagery"
        ],
        style_override="realistic"
    ),

    # Education - learning, growth
    "education": DomainImagery(
        elements=[
            "modern library interior",
            "learning environment",
            "academic campus",
            "books and knowledge symbols",
            "classroom technology",
            "graduation and achievement"
        ],
        avoid=[
            "boring lecture halls",
            "generic clipart",
            "outdated imagery"
        ],
        style_override=None  # Use audience-based style
    ),

    # Science/Research - laboratory, discovery
    "science": DomainImagery(
        elements=[
            "laboratory equipment",
            "scientific experiments",
            "research facility",
            "microscopy abstract",
            "molecular structures",
            "innovation and discovery"
        ],
        avoid=[
            "mad scientist tropes",
            "dangerous experiments",
            "generic science clipart"
        ],
        style_override="realistic"
    ),

    # Nature/Environment - sustainable, green
    "nature": DomainImagery(
        elements=[
            "pristine natural landscapes",
            "sustainable ecosystems",
            "environmental conservation",
            "wildlife habitat",
            "renewable energy",
            "green technology"
        ],
        avoid=[
            "environmental damage",
            "pollution",
            "deforestation"
        ],
        style_override=None
    ),

    # Creative/Art - artistic, expressive
    "creative": DomainImagery(
        elements=[
            "artist studio",
            "creative workspace",
            "gallery environment",
            "design process",
            "artistic expression",
            "creative tools"
        ],
        avoid=[
            "corporate sterility",
            "generic stock photos"
        ],
        style_override=None
    ),

    # Default - professional setting
    "default": DomainImagery(
        elements=[
            "professional workspace",
            "modern office environment",
            "clean business setting",
            "abstract corporate imagery"
        ],
        avoid=[
            "cartoon characters",
            "anime style",
            "childish elements"
        ],
        style_override=None
    )
}


def get_audience_style(audience_type: Optional[str]) -> AudienceStyleParams:
    """
    Get style parameters based on audience type.

    Args:
        audience_type: Audience identifier (executives, technical, kids_tween, etc.)

    Returns:
        AudienceStyleParams with style, color_scheme, lighting, avoid_elements
    """
    if audience_type is None:
        return AUDIENCE_STYLE_MAP["default"]

    audience_key = audience_type.lower().replace(" ", "_")
    return AUDIENCE_STYLE_MAP.get(audience_key, AUDIENCE_STYLE_MAP["default"])


def get_purpose_style(purpose_type: Optional[str]) -> PurposeStyleParams:
    """
    Get style parameters based on purpose type.

    Args:
        purpose_type: Purpose identifier (inform, persuade, inspire, etc.)

    Returns:
        PurposeStyleParams with emphasis, composition, mood
    """
    if purpose_type is None:
        return PURPOSE_STYLE_MAP["default"]

    purpose_key = purpose_type.lower().replace(" ", "_")
    return PURPOSE_STYLE_MAP.get(purpose_key, PURPOSE_STYLE_MAP["default"])


def get_domain_imagery(domain: Optional[str]) -> DomainImagery:
    """
    Get domain-specific imagery configuration.

    Args:
        domain: Domain identifier (technology, business, healthcare, etc.)

    Returns:
        DomainImagery with elements, avoid, style_override
    """
    if domain is None:
        return DOMAIN_IMAGERY_MAP["default"]

    domain_key = domain.lower().replace(" ", "_")
    return DOMAIN_IMAGERY_MAP.get(domain_key, DOMAIN_IMAGERY_MAP["default"])


def detect_domain_from_text(text: str) -> str:
    """
    Detect domain from narrative/topics text using keyword matching.

    Args:
        text: Combined narrative and topics text (should be lowercase)

    Returns:
        Domain identifier string
    """
    text_lower = text.lower()

    # Technology keywords
    tech_keywords = [
        'tech', 'software', 'digital', 'ai', 'data', 'cloud', 'code',
        'algorithm', 'computing', 'system', 'cyber', 'machine learning',
        'automation', 'programming', 'developer', 'api', 'platform',
        'infrastructure', 'stack', 'database', 'server', 'network'
    ]
    if any(kw in text_lower for kw in tech_keywords):
        return "technology"

    # Healthcare keywords
    healthcare_keywords = [
        'health', 'medical', 'hospital', 'patient', 'diagnostic',
        'clinical', 'doctor', 'nurse', 'healthcare', 'medicine',
        'therapy', 'treatment', 'wellness', 'pharmaceutical'
    ]
    if any(kw in text_lower for kw in healthcare_keywords):
        return "healthcare"

    # Science keywords
    science_keywords = [
        'research', 'experiment', 'laboratory', 'chemistry', 'physics',
        'biology', 'scientific', 'discovery', 'hypothesis', 'analysis',
        'study', 'findings', 'methodology', 'empirical', 'scientist'
    ]
    if any(kw in text_lower for kw in science_keywords):
        return "science"

    # Education keywords
    education_keywords = [
        'school', 'university', 'student', 'learning', 'education',
        'teach', 'academic', 'classroom', 'course', 'curriculum',
        'professor', 'degree', 'graduate', 'college', 'training'
    ]
    if any(kw in text_lower for kw in education_keywords):
        return "education"

    # Nature/Environment keywords
    nature_keywords = [
        'nature', 'environment', 'climate', 'green', 'sustainable',
        'wildlife', 'forest', 'ocean', 'conservation', 'ecosystem',
        'biodiversity', 'ecological', 'renewable', 'earth', 'planet'
    ]
    if any(kw in text_lower for kw in nature_keywords):
        return "nature"

    # Creative/Art keywords
    creative_keywords = [
        'art', 'design', 'creative', 'music', 'artist', 'gallery',
        'paint', 'sculpture', 'photography', 'illustration', 'visual',
        'aesthetic', 'artistic', 'exhibition', 'performance', 'culture'
    ]
    if any(kw in text_lower for kw in creative_keywords):
        return "creative"

    # Business/Finance keywords
    business_keywords = [
        'finance', 'business', 'market', 'trading', 'investment',
        'bank', 'revenue', 'profit', 'economy', 'financial',
        'stock', 'portfolio', 'capital', 'corporate', 'enterprise',
        'strategy', 'growth', 'expansion', 'customer', 'sales'
    ]
    if any(kw in text_lower for kw in business_keywords):
        return "business"

    # Default
    return "default"


def get_image_style_params(
    audience_type: Optional[str] = None,
    purpose_type: Optional[str] = None,
    domain: Optional[str] = None,
    narrative_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get comprehensive image style parameters based on context.

    Combines audience, purpose, and domain to produce optimal image generation params.

    Args:
        audience_type: Target audience (executives, technical, kids_tween, etc.)
        purpose_type: Presentation purpose (inform, persuade, inspire, etc.)
        domain: Content domain (technology, healthcare, etc.) or None to auto-detect
        narrative_text: Optional narrative text for domain detection

    Returns:
        Dict with style, color_scheme, lighting, elements, avoid, prompt_hints
    """
    # Get base styles from audience and purpose
    audience_style = get_audience_style(audience_type)
    purpose_style = get_purpose_style(purpose_type)

    # Auto-detect domain if not provided
    if domain is None and narrative_text:
        domain = detect_domain_from_text(narrative_text)

    domain_imagery = get_domain_imagery(domain)

    # Determine final style (domain can override)
    final_style = domain_imagery.style_override or audience_style.style

    # Build avoid list combining audience and domain
    avoid_list = list(set(audience_style.avoid_elements + domain_imagery.avoid))

    # Build positive elements from domain
    positive_elements = domain_imagery.elements[:5]  # Top 5 elements

    # Build prompt hints based on purpose
    prompt_hints = []
    if purpose_style.emphasis == "clarity":
        prompt_hints.append("clear and readable composition")
    elif purpose_style.emphasis == "impact":
        prompt_hints.append("bold and impactful imagery")
    elif purpose_style.emphasis == "emotion":
        prompt_hints.append("emotionally resonant visuals")

    if purpose_style.composition == "dynamic":
        prompt_hints.append("dynamic angles and perspective")
    elif purpose_style.composition == "aspirational":
        prompt_hints.append("aspirational and uplifting mood")

    return {
        "style": final_style,
        "color_scheme": audience_style.color_scheme,
        "lighting": audience_style.lighting,
        "elements": positive_elements,
        "avoid": avoid_list,
        "prompt_hints": prompt_hints,
        "mood": purpose_style.mood,
        "domain": domain or "default"
    }


def build_context_aware_negative_prompt(
    domain: Optional[str] = None,
    audience_type: Optional[str] = None
) -> str:
    """
    Build context-aware negative prompt for image generation.

    Args:
        domain: Content domain (technology, healthcare, etc.)
        audience_type: Target audience type

    Returns:
        Comprehensive negative prompt string
    """
    # Base negative prompt - always exclude these
    base_negatives = [
        "text", "words", "letters", "numbers", "typography",
        "watermarks", "logos", "signatures", "labels", "captions"
    ]

    # Get audience-specific negatives
    audience_style = get_audience_style(audience_type)
    audience_negatives = audience_style.avoid_elements

    # Get domain-specific negatives
    domain_imagery = get_domain_imagery(domain)
    domain_negatives = domain_imagery.avoid

    # Combine and dedupe
    all_negatives = list(set(base_negatives + audience_negatives + domain_negatives))

    # Add quality negatives
    quality_negatives = [
        "low quality", "blurry", "pixelated", "noisy", "distorted"
    ]
    all_negatives.extend(quality_negatives)

    return ", ".join(all_negatives)
