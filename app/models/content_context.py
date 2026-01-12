"""
Content Context Models for Text Service v1.3.0

Defines the four dimensions of content generation:
1. Theme (visual) - handled separately in ThemeConfig
2. Audience - who is viewing the presentation
3. Purpose - what the presentation aims to achieve
4. Time - presentation duration

Per THEME_SYSTEM_DESIGN.md Section 12.4:
- Theme is VISUAL ONLY, orthogonal to Audience/Purpose
- Defaults: audience=professional, purpose=inform, time=15min
- These affect content generation, NOT visual styling

Version: 1.3.0
"""

from enum import Enum
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, field_validator


# =============================================================================
# Audience Configuration
# =============================================================================

class AudienceType(str, Enum):
    """
    Audience types with increasing complexity.

    Per THEME_SYSTEM_DESIGN.md Section 2.3:
    - kids_young (6-10): Simple words, 3 bullets max, no jargon
    - kids_older (10-14): Simple sentences, 4 bullets max
    - high_school (14-18): Clear language, 5 bullets max
    - college (18-25): Standard complexity, 5 bullets
    - professional (default): Business language, 5 bullets
    - executive: Concise, high-level, 4 bullets max
    """
    KIDS_YOUNG = "kids_young"       # 6-10 years
    KIDS_OLDER = "kids_older"       # 10-14 years
    HIGH_SCHOOL = "high_school"     # 14-18 years
    COLLEGE = "college"             # 18-25 years
    PROFESSIONAL = "professional"   # Default
    EXECUTIVE = "executive"


class AudienceConfig(BaseModel):
    """
    Audience configuration affecting content complexity.

    Affects Phase 1 (structure) and Phase 3 (content generation):
    - complexity_level: Vocabulary and sentence structure
    - max_sentence_words: Sentence length limit
    - max_bullets: Maximum bullet points per section
    - avoid_jargon: Replace technical terms with plain language
    """
    audience_type: AudienceType = Field(
        default=AudienceType.PROFESSIONAL,
        description="Target audience type"
    )
    complexity_level: Union[int, str] = Field(
        default=3,
        description="Complexity level (1=simplest, 5=most complex) or string like 'moderate'"
    )

    @field_validator('complexity_level', mode='before')
    @classmethod
    def convert_complexity_level(cls, v):
        """Convert string complexity to int."""
        if isinstance(v, str):
            mapping = {
                'very_simple': 1, 'simple': 2, 'moderate': 3,
                'complex': 4, 'very_complex': 5
            }
            return mapping.get(v.lower(), 3)
        return v
    max_sentence_words: int = Field(
        default=15,
        ge=5,
        le=25,
        description="Maximum words per sentence"
    )
    max_bullets: int = Field(
        default=5,
        ge=3,
        le=8,
        description="Maximum bullet points per section"
    )
    avoid_jargon: bool = Field(
        default=False,
        description="Replace technical terms with plain language"
    )
    reading_level: Optional[str] = Field(
        default=None,
        description="Optional reading level (e.g., '8th grade')"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "audience_type": "professional",
                "complexity_level": 3,
                "max_sentence_words": 15,
                "max_bullets": 5,
                "avoid_jargon": False
            }
        }


# =============================================================================
# Purpose Configuration
# =============================================================================

class PurposeType(str, Enum):
    """
    Presentation purpose types.

    Per THEME_SYSTEM_DESIGN.md Section 2.4:
    - inform: Neutral language, objective facts
    - educate: Pedagogical, step-by-step, examples
    - persuade: Compelling, problem-solution, CTAs
    - entertain: Casual, engaging, varied pacing
    - inspire: Motivational, emotional, storytelling
    - report: Data-driven, analytical, metrics
    """
    INFORM = "inform"           # Default
    EDUCATE = "educate"
    PERSUADE = "persuade"
    ENTERTAIN = "entertain"
    INSPIRE = "inspire"
    REPORT = "report"


class PurposeConfig(BaseModel):
    """
    Purpose configuration affecting content tone and structure.

    Affects Phase 1 (structure pattern) and Phase 3 (tone):
    - structure_pattern: How content is organized
    - include_cta: Add call-to-action on closing slides
    - emotional_tone: Overall emotional quality
    - evidence_style: How to present supporting information
    """
    purpose_type: PurposeType = Field(
        default=PurposeType.INFORM,
        description="Primary presentation purpose"
    )
    structure_pattern: str = Field(
        default="standard",
        description="Content organization pattern: standard, problem_solution, chronological, comparison"
    )
    include_cta: bool = Field(
        default=False,
        description="Include call-to-action on closing slides"
    )
    emotional_tone: str = Field(
        default="neutral",
        description="Emotional tone: neutral, enthusiastic, serious, casual, motivational"
    )
    evidence_style: str = Field(
        default="balanced",
        description="How to present evidence: data_heavy, anecdotal, balanced, visual"
    )
    language_style: Optional[str] = Field(
        default=None,
        description="Optional language style override"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "purpose_type": "persuade",
                "structure_pattern": "problem_solution",
                "include_cta": True,
                "emotional_tone": "enthusiastic",
                "evidence_style": "data_heavy"
            }
        }


# =============================================================================
# Time Configuration
# =============================================================================

class TimeConfig(BaseModel):
    """
    Presentation time configuration.

    Per THEME_SYSTEM_DESIGN.md Section 2.5:
    - 5 min: 3-5 slides, headlines only
    - 15 min (default): 8-12 slides, moderate detail
    - 30 min: 15-20 slides, full examples
    - 60+ min: 25+ slides, deep dives, exercises

    Affects Phase 1 (structure depth) and content density.
    """
    duration_minutes: int = Field(
        default=15,
        ge=5,
        le=120,
        description="Presentation duration in minutes"
    )
    target_slides: int = Field(
        default=10,
        ge=3,
        le=60,
        description="Target number of slides"
    )
    content_depth: str = Field(
        default="standard",
        description="Content depth: headline, standard, detailed, comprehensive"
    )
    pace: str = Field(
        default="moderate",
        description="Presentation pace: fast, moderate, slow"
    )
    include_examples: bool = Field(
        default=True,
        description="Include examples and illustrations"
    )
    include_exercises: bool = Field(
        default=False,
        description="Include interactive exercises (workshops)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "duration_minutes": 30,
                "target_slides": 15,
                "content_depth": "detailed",
                "pace": "moderate",
                "include_examples": True,
                "include_exercises": False
            }
        }


# =============================================================================
# Combined Content Context
# =============================================================================

class ContentContext(BaseModel):
    """
    Complete content context combining audience, purpose, and time.

    Per THEME_SYSTEM_DESIGN.md Section 12:
    - Passed from Director to Text Service
    - Affects content generation, NOT visual styling
    - Theme (visual) is separate and orthogonal

    Usage in Multi-Step Generation:
    - Phase 1: audience.max_bullets, purpose.structure_pattern, time.content_depth
    - Phase 3: audience.complexity, purpose.emotional_tone, vocabulary
    """
    audience: AudienceConfig = Field(
        default_factory=AudienceConfig,
        description="Audience configuration"
    )
    purpose: PurposeConfig = Field(
        default_factory=PurposeConfig,
        description="Purpose configuration"
    )
    time: TimeConfig = Field(
        default_factory=TimeConfig,
        description="Time configuration"
    )

    def get_max_bullets(self) -> int:
        """Get effective max bullets based on audience and time."""
        base = self.audience.max_bullets
        if self.time.content_depth == "headline":
            return min(base, 3)
        elif self.time.content_depth == "comprehensive":
            return base + 2
        return base

    def get_complexity_descriptor(self) -> str:
        """Get human-readable complexity description for prompts."""
        level = self.audience.complexity_level
        if level == 1:
            return "very simple, suitable for young children"
        elif level == 2:
            return "simple, suitable for older children"
        elif level == 3:
            return "standard professional level"
        elif level == 4:
            return "detailed and sophisticated"
        else:
            return "highly complex and technical"

    def get_tone_instructions(self) -> str:
        """Get tone instructions for LLM prompts."""
        purpose = self.purpose.purpose_type
        tone = self.purpose.emotional_tone

        instructions = {
            PurposeType.INFORM: f"Use objective, factual language with a {tone} tone.",
            PurposeType.EDUCATE: f"Use pedagogical language with clear explanations and a {tone} tone.",
            PurposeType.PERSUADE: f"Use compelling, action-oriented language with a {tone} tone.",
            PurposeType.ENTERTAIN: f"Use engaging, varied language with a {tone} tone.",
            PurposeType.INSPIRE: f"Use motivational, emotionally resonant language with a {tone} tone.",
            PurposeType.REPORT: f"Use analytical, data-driven language with a {tone} tone.",
        }
        return instructions.get(purpose, f"Use professional language with a {tone} tone.")

    def to_prompt_context(self) -> Dict[str, Any]:
        """Convert to dictionary for LLM prompt context."""
        return {
            "audience_type": self.audience.audience_type.value,
            "complexity_level": self.audience.complexity_level,
            "max_sentence_words": self.audience.max_sentence_words,
            "max_bullets": self.get_max_bullets(),
            "avoid_jargon": self.audience.avoid_jargon,
            "purpose_type": self.purpose.purpose_type.value,
            "structure_pattern": self.purpose.structure_pattern,
            "include_cta": self.purpose.include_cta,
            "emotional_tone": self.purpose.emotional_tone,
            "duration_minutes": self.time.duration_minutes,
            "content_depth": self.time.content_depth,
            "include_examples": self.time.include_examples,
            "complexity_descriptor": self.get_complexity_descriptor(),
            "tone_instructions": self.get_tone_instructions(),
        }

    class Config:
        json_schema_extra = {
            "example": {
                "audience": {
                    "audience_type": "professional",
                    "complexity_level": 3,
                    "max_bullets": 5
                },
                "purpose": {
                    "purpose_type": "inform",
                    "structure_pattern": "standard",
                    "emotional_tone": "neutral"
                },
                "time": {
                    "duration_minutes": 15,
                    "content_depth": "standard"
                }
            }
        }


# =============================================================================
# Presets
# =============================================================================

AUDIENCE_PRESETS: Dict[str, AudienceConfig] = {
    "kids_young": AudienceConfig(
        audience_type=AudienceType.KIDS_YOUNG,
        complexity_level=1,
        max_sentence_words=8,
        max_bullets=3,
        avoid_jargon=True,
        reading_level="3rd grade"
    ),
    "kids_older": AudienceConfig(
        audience_type=AudienceType.KIDS_OLDER,
        complexity_level=2,
        max_sentence_words=12,
        max_bullets=4,
        avoid_jargon=True,
        reading_level="6th grade"
    ),
    "high_school": AudienceConfig(
        audience_type=AudienceType.HIGH_SCHOOL,
        complexity_level=3,
        max_sentence_words=15,
        max_bullets=5,
        avoid_jargon=False,
        reading_level="9th grade"
    ),
    "college": AudienceConfig(
        audience_type=AudienceType.COLLEGE,
        complexity_level=4,
        max_sentence_words=18,
        max_bullets=5,
        avoid_jargon=False,
        reading_level="college"
    ),
    "professional": AudienceConfig(
        audience_type=AudienceType.PROFESSIONAL,
        complexity_level=3,
        max_sentence_words=15,
        max_bullets=5,
        avoid_jargon=False
    ),
    "executive": AudienceConfig(
        audience_type=AudienceType.EXECUTIVE,
        complexity_level=4,
        max_sentence_words=12,
        max_bullets=4,
        avoid_jargon=False
    ),
}

PURPOSE_PRESETS: Dict[str, PurposeConfig] = {
    "inform": PurposeConfig(
        purpose_type=PurposeType.INFORM,
        structure_pattern="standard",
        include_cta=False,
        emotional_tone="neutral",
        evidence_style="balanced"
    ),
    "educate": PurposeConfig(
        purpose_type=PurposeType.EDUCATE,
        structure_pattern="chronological",
        include_cta=False,
        emotional_tone="encouraging",
        evidence_style="balanced"
    ),
    "persuade": PurposeConfig(
        purpose_type=PurposeType.PERSUADE,
        structure_pattern="problem_solution",
        include_cta=True,
        emotional_tone="enthusiastic",
        evidence_style="data_heavy"
    ),
    "entertain": PurposeConfig(
        purpose_type=PurposeType.ENTERTAIN,
        structure_pattern="standard",
        include_cta=False,
        emotional_tone="casual",
        evidence_style="anecdotal"
    ),
    "inspire": PurposeConfig(
        purpose_type=PurposeType.INSPIRE,
        structure_pattern="standard",
        include_cta=True,
        emotional_tone="motivational",
        evidence_style="anecdotal"
    ),
    "report": PurposeConfig(
        purpose_type=PurposeType.REPORT,
        structure_pattern="standard",
        include_cta=False,
        emotional_tone="serious",
        evidence_style="data_heavy"
    ),
}

TIME_PRESETS: Dict[str, TimeConfig] = {
    "lightning": TimeConfig(
        duration_minutes=5,
        target_slides=5,
        content_depth="headline",
        pace="fast",
        include_examples=False,
        include_exercises=False
    ),
    "standard": TimeConfig(
        duration_minutes=15,
        target_slides=10,
        content_depth="standard",
        pace="moderate",
        include_examples=True,
        include_exercises=False
    ),
    "detailed": TimeConfig(
        duration_minutes=30,
        target_slides=18,
        content_depth="detailed",
        pace="moderate",
        include_examples=True,
        include_exercises=False
    ),
    "workshop": TimeConfig(
        duration_minutes=60,
        target_slides=25,
        content_depth="comprehensive",
        pace="slow",
        include_examples=True,
        include_exercises=True
    ),
}


def get_default_content_context() -> ContentContext:
    """Get default content context (professional, inform, 15min)."""
    return ContentContext(
        audience=AUDIENCE_PRESETS["professional"],
        purpose=PURPOSE_PRESETS["inform"],
        time=TIME_PRESETS["standard"]
    )


def build_content_context(
    audience_type: str = "professional",
    purpose_type: str = "inform",
    duration_minutes: int = 15
) -> ContentContext:
    """
    Build ContentContext from simple parameters.

    Args:
        audience_type: Audience preset name
        purpose_type: Purpose preset name
        duration_minutes: Presentation duration

    Returns:
        ContentContext with appropriate presets
    """
    audience = AUDIENCE_PRESETS.get(audience_type, AUDIENCE_PRESETS["professional"])
    purpose = PURPOSE_PRESETS.get(purpose_type, PURPOSE_PRESETS["inform"])

    # Find closest time preset
    if duration_minutes <= 10:
        time = TIME_PRESETS["lightning"]
    elif duration_minutes <= 20:
        time = TIME_PRESETS["standard"]
    elif duration_minutes <= 45:
        time = TIME_PRESETS["detailed"]
    else:
        time = TIME_PRESETS["workshop"]

    # Override duration with actual value
    time = TimeConfig(
        duration_minutes=duration_minutes,
        target_slides=time.target_slides,
        content_depth=time.content_depth,
        pace=time.pace,
        include_examples=time.include_examples,
        include_exercises=time.include_exercises
    )

    return ContentContext(audience=audience, purpose=purpose, time=time)
