"""
Visual Style Configuration for Hero Slides with AI-Generated Backgrounds

Defines three visual style options for image generation:
1. PROFESSIONAL - Photorealistic, modern, clean (current default)
2. ILLUSTRATED - Ghibli-style, professional cartoon, hand-painted aesthetic
3. KIDS - Vibrant, playful, exciting, kid-friendly

Each style has:
- Image API archetype (photorealistic vs spot_illustration)
- Prompt style descriptors
- Domain-specific theme modifiers
- Model selection logic (standard vs fast)

Model Selection Strategy:
- Title + Professional → imagen-3.0-generate-001 (standard, $0.04, ~10s)
- Title + Illustrated/Kids → imagen-3.0-fast-generate-001 (fast, $0.02, ~5s)
- Section/Closing + Any style → imagen-3.0-fast-generate-001 (always fast)
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Tuple


class VisualStyle(str, Enum):
    """Visual style options for hero slide backgrounds."""
    PROFESSIONAL = "professional"
    ILLUSTRATED = "illustrated"
    KIDS = "kids"


class SlideType(str, Enum):
    """Hero slide types."""
    TITLE = "title_slide"
    SECTION = "section_divider"
    CLOSING = "closing_slide"


@dataclass
class StyleConfig:
    """
    Configuration for a visual style.

    Attributes:
        archetype: Image API archetype (photorealistic, spot_illustration, minimalist_vector_art)
        prompt_style: Base style descriptor for image prompts
        healthcare_theme: Healthcare-specific imagery descriptors
        tech_theme: Technology-specific imagery descriptors
        finance_theme: Finance/business-specific imagery descriptors
        religious_theme: Religious/spiritual imagery descriptors
        education_theme: Education/academic imagery descriptors
        nature_theme: Nature/environment imagery descriptors
        science_theme: Science/research imagery descriptors
        creative_theme: Art/creative imagery descriptors
        default_theme: Fallback theme for other domains
    """
    archetype: str
    prompt_style: str
    healthcare_theme: str
    tech_theme: str
    finance_theme: str
    religious_theme: str
    education_theme: str
    nature_theme: str
    science_theme: str
    creative_theme: str
    default_theme: str


# Style configurations
STYLE_CONFIGS: Dict[VisualStyle, StyleConfig] = {
    VisualStyle.PROFESSIONAL: StyleConfig(
        archetype="photorealistic",
        prompt_style="photorealistic, modern, clean, professional, subtle",
        healthcare_theme="modern hospital technology, medical imaging equipment, healthcare innovation, clinical environment",
        tech_theme="modern technology workspace, sleek displays, digital innovation, abstract tech patterns",
        finance_theme="modern business office, city skyline, professional workspace, financial district",
        religious_theme="sacred temple architecture, spiritual sanctuary, ornate religious symbols, devotional atmosphere, traditional ceremonial setting",
        education_theme="modern university campus, academic library, learning environment, educational institution, scholarly atmosphere",
        nature_theme="pristine natural landscape, environmental conservation, sustainable ecosystem, wildlife habitat, natural beauty",
        science_theme="modern research laboratory, scientific equipment, experimental facility, discovery and innovation, academic research",
        creative_theme="artistic studio, gallery space, creative workshop, design environment, artistic expression",
        default_theme="professional workspace, modern environment, clean business setting"
    ),

    VisualStyle.ILLUSTRATED: StyleConfig(
        archetype="spot_illustration",
        prompt_style="Studio Ghibli style, anime illustration, hand-painted aesthetic, soft colors, whimsical, professional cartoon, artistic",
        healthcare_theme="illustrated healthcare scene, cartoon medical facility, artistic hospital environment, whimsical clinical setting",
        tech_theme="illustrated technology workspace, cartoon tech environment, artistic digital innovation, playful tech patterns",
        finance_theme="illustrated business office, cartoon city skyline, artistic workspace, whimsical financial district",
        religious_theme="illustrated sacred temple, artistic spiritual scene, whimsical religious architecture, hand-painted devotional setting, cartoon ceremonial atmosphere",
        education_theme="illustrated campus scene, cartoon library, artistic classroom, whimsical learning environment, hand-painted academic setting",
        nature_theme="illustrated natural landscape, cartoon wildlife scene, artistic environmental setting, whimsical nature, hand-painted ecosystem",
        science_theme="illustrated laboratory, cartoon scientific discovery, artistic research scene, whimsical experiments, hand-painted innovation",
        creative_theme="illustrated art studio, cartoon gallery scene, artistic creative space, whimsical design workshop, hand-painted artistic environment",
        default_theme="illustrated professional workspace, cartoon environment, artistic business setting"
    ),

    VisualStyle.KIDS: StyleConfig(
        archetype="spot_illustration",
        prompt_style="bright vibrant colors, playful, fun, exciting, cartoon illustration, kid-friendly, energetic, colorful",
        healthcare_theme="colorful hospital adventure, fun medical scene, exciting healthcare setting, playful clinical environment",
        tech_theme="fun tech playground, colorful digital world, exciting technology adventure, playful innovation",
        finance_theme="exciting business world, colorful office adventure, fun workspace, vibrant professional setting",
        religious_theme="colorful temple adventure, fun spiritual journey, exciting ceremonial celebration, playful sacred scene, vibrant religious festival",
        education_theme="colorful school adventure, fun classroom scene, exciting learning journey, playful library, vibrant campus life",
        nature_theme="colorful nature adventure, fun wildlife encounter, exciting forest exploration, playful ocean scene, vibrant outdoor journey",
        science_theme="colorful lab adventure, fun experiment scene, exciting scientific discovery, playful research journey, vibrant innovation",
        creative_theme="colorful art adventure, fun creative journey, exciting artistic exploration, playful design workshop, vibrant artistic expression",
        default_theme="colorful workspace adventure, fun environment, exciting setting"
    )
}


def get_style_config(visual_style: str) -> StyleConfig:
    """
    Get style configuration for a visual style.

    Args:
        visual_style: Visual style identifier (professional, illustrated, kids)

    Returns:
        StyleConfig with archetype and prompt descriptors

    Raises:
        ValueError: If visual_style is not recognized
    """
    try:
        style_enum = VisualStyle(visual_style.lower())
        return STYLE_CONFIGS[style_enum]
    except (ValueError, KeyError):
        # Default to professional if invalid style provided
        return STYLE_CONFIGS[VisualStyle.PROFESSIONAL]


def get_domain_theme(
    style_config: StyleConfig,
    combined_text: str
) -> str:
    """
    Get domain-specific theme descriptors based on text analysis.

    Args:
        style_config: StyleConfig for the current visual style
        combined_text: Combined narrative and topics text (lowercase)

    Returns:
        Domain-specific theme descriptor string
    """
    # Religious/Spiritual detection (check first - more specific)
    if any(word in combined_text for word in [
        'shiva', 'hindu', 'temple', 'prayer', 'spiritual', 'sacred',
        'meditation', 'worship', 'divine', 'god', 'goddess', 'religious',
        'ceremony', 'ritual', 'faith', 'church', 'mosque', 'synagogue',
        'buddha', 'buddhist', 'christian', 'islam', 'jewish', 'dharma',
        'karma', 'mantra', 'yoga', 'enlightenment', 'devotion', 'pilgrimage',
        'lingam', 'puja', 'aarti', 'vedic', 'scripture', 'blessing'
    ]):
        return style_config.religious_theme

    # Healthcare detection
    elif any(word in combined_text for word in [
        'health', 'medical', 'hospital', 'patient', 'diagnostic',
        'clinical', 'doctor', 'nurse', 'healthcare', 'medicine',
        'therapy', 'treatment', 'wellness', 'pharmaceutical'
    ]):
        return style_config.healthcare_theme

    # Tech detection
    elif any(word in combined_text for word in [
        'tech', 'software', 'digital', 'ai', 'data', 'cloud',
        'code', 'algorithm', 'computing', 'system', 'cyber',
        'machine learning', 'automation', 'programming', 'developer'
    ]):
        return style_config.tech_theme

    # Science/Research detection
    elif any(word in combined_text for word in [
        'research', 'experiment', 'laboratory', 'chemistry', 'physics',
        'biology', 'scientific', 'discovery', 'hypothesis', 'analysis',
        'study', 'findings', 'methodology', 'empirical', 'scientist'
    ]):
        return style_config.science_theme

    # Education detection
    elif any(word in combined_text for word in [
        'school', 'university', 'student', 'learning', 'education',
        'teach', 'academic', 'classroom', 'course', 'curriculum',
        'professor', 'degree', 'graduate', 'college', 'training'
    ]):
        return style_config.education_theme

    # Nature/Environment detection
    elif any(word in combined_text for word in [
        'nature', 'environment', 'climate', 'green', 'sustainable',
        'wildlife', 'forest', 'ocean', 'conservation', 'ecosystem',
        'biodiversity', 'ecological', 'renewable', 'earth', 'planet'
    ]):
        return style_config.nature_theme

    # Creative/Art detection
    elif any(word in combined_text for word in [
        'art', 'design', 'creative', 'music', 'artist', 'gallery',
        'paint', 'sculpture', 'photography', 'illustration', 'visual',
        'aesthetic', 'artistic', 'exhibition', 'performance', 'culture'
    ]):
        return style_config.creative_theme

    # Finance detection
    elif any(word in combined_text for word in [
        'finance', 'business', 'market', 'trading', 'investment',
        'bank', 'revenue', 'profit', 'economy', 'financial',
        'stock', 'portfolio', 'capital', 'corporate', 'enterprise'
    ]):
        return style_config.finance_theme

    # Default theme
    else:
        return style_config.default_theme


def get_image_model(
    slide_type: str,
    visual_style: str
) -> str:
    """
    Get Imagen model based on slide type and visual style.

    Model Selection Strategy:
    - Title + Professional → imagen-3.0-generate-001 (standard quality)
    - Title + Illustrated/Kids → imagen-3.0-fast-generate-001 (fast/cheap)
    - Section/Closing + Any style → imagen-3.0-fast-generate-001 (always fast)

    Args:
        slide_type: Slide type (title_slide, section_divider, closing_slide)
        visual_style: Visual style (professional, illustrated, kids)

    Returns:
        Imagen model identifier string
    """
    # Normalize inputs
    slide_type_lower = slide_type.lower()
    visual_style_lower = visual_style.lower()

    # Title slide with professional style uses standard quality
    if slide_type_lower == "title_slide" and visual_style_lower == "professional":
        return "imagen-3.0-generate-001"  # Standard quality (~10s, $0.04)

    # All other combinations use fast model
    return "imagen-3.0-fast-generate-001"  # Fast/cheap (~5s, $0.02)


def build_style_aware_prompt(
    visual_style: str,
    narrative: str,
    topics: list,
    theme: str = "professional"
) -> Tuple[str, str]:
    """
    Build style-aware image generation prompt.

    Args:
        visual_style: Visual style (professional, illustrated, kids)
        narrative: Slide narrative
        topics: List of key topics
        theme: Presentation theme (currently unused, for future)

    Returns:
        Tuple of (image_prompt, archetype)
    """
    # Get style configuration
    style_config = get_style_config(visual_style)

    # Detect domain from narrative + topics
    combined_text = f"{narrative} {' '.join(topics) if topics else ''}".lower()
    domain_imagery = get_domain_theme(style_config, combined_text)

    # Build high-quality image prompt with style-specific descriptors
    prompt = f"""High-quality professional background image: {domain_imagery}.

Style: {style_config.prompt_style}
Composition: Clean and minimal, suitable for text overlay
Mood: Professional, {visual_style}, appropriate for presentation
Focus on: {', '.join(topics[:2]) if topics else 'professional setting'}

CRITICAL: Absolutely NO text, words, letters, numbers, or typography of any kind in the image."""

    return prompt, style_config.archetype
