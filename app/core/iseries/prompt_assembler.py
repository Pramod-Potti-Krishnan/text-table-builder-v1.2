"""
Prompt Assembler for I-Series Image Generation

v1.2.3: Simplified prompting system for high-quality image generation.

This module implements the Global + Local variable separation approach:
- Global Variables (Brand): Set once per deck by Director
- Local Variables (Message): Set per slide based on content

Prompt Formula:
[Visual Style] of a [Anchor Subject] [Action/Composition].
[Lighting & Mood]. [Color Palette]. [Target Demographic Keywords].

Example Output:
"Photorealistic image of glowing circuit board patterns emanating data streams.
Professional dramatic lighting, sophisticated atmosphere.
Cool blues and metallic silvers. Enterprise executives, corporate leadership aesthetic."
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class GlobalBrandVars:
    """
    Global brand variables set once per presentation by Director.

    These define the overall visual identity and audience targeting
    for all images in the presentation.
    """
    target_demographic: str = ""     # "enterprise executives, corporate leadership"
    visual_style: str = ""           # "sleek modern photorealistic"
    color_palette: str = ""          # "cool blues and metallic silvers"
    lighting_mood: str = ""          # "professional studio lighting, sophisticated atmosphere"

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "GlobalBrandVars":
        """Create GlobalBrandVars from dict (e.g., from API request)."""
        if not data:
            return cls()
        return cls(
            target_demographic=data.get("target_demographic", ""),
            visual_style=data.get("visual_style", ""),
            color_palette=data.get("color_palette", ""),
            lighting_mood=data.get("lighting_mood", "")
        )

    def has_values(self) -> bool:
        """Check if any global brand values are set."""
        return bool(
            self.target_demographic or
            self.visual_style or
            self.color_palette or
            self.lighting_mood
        )


@dataclass
class LocalMessageVars:
    """
    Local message variables extracted per slide from content.

    These are derived from the slide's narrative, topics, and content
    to create a meaningful visual representation.
    """
    content_archetype: str = ""      # "comparison", "process", "metrics"
    topic: str = ""                  # Main subject from content
    anchor_subject: str = ""         # Concrete noun (visual focus)
    action_composition: str = ""     # What the subject is doing
    semantic_link: str = ""          # Why this relates to slide message
    aspect_ratio: str = "9:16"       # From layout (9:16 for I-series)


def assemble_prompt(
    global_vars: GlobalBrandVars,
    local_vars: LocalMessageVars
) -> str:
    """
    Assemble simple, natural-language image prompt.

    Formula: [Visual Style] of a [Anchor Subject] [Action/Composition].
             [Lighting & Mood]. [Color Palette]. [Target Demographic Keywords].

    Args:
        global_vars: Brand-level variables from Director
        local_vars: Message-level variables from slide content

    Returns:
        Natural language prompt string (~30-50 words)
    """
    parts = []

    # Part 1: Visual style + anchor subject + action
    if global_vars.visual_style and local_vars.anchor_subject:
        style_subject = f"{global_vars.visual_style} image of {local_vars.anchor_subject}"
        if local_vars.action_composition:
            style_subject += f" {local_vars.action_composition}"
        parts.append(style_subject + ".")
    elif local_vars.anchor_subject:
        # Fallback: just anchor subject with action
        subject = local_vars.anchor_subject
        if local_vars.action_composition:
            subject += f" {local_vars.action_composition}"
        parts.append(f"Image of {subject}.")

    # Part 2: Lighting and mood
    if global_vars.lighting_mood:
        parts.append(global_vars.lighting_mood + ".")

    # Part 3: Color palette
    if global_vars.color_palette:
        parts.append(global_vars.color_palette + ".")

    # Part 4: Target demographic aesthetic
    if global_vars.target_demographic:
        parts.append(f"{global_vars.target_demographic} aesthetic.")

    # Join parts with space
    prompt = " ".join(parts)

    # Fallback if nothing was assembled
    if not prompt.strip():
        prompt = f"Professional illustration for {local_vars.topic or 'presentation slide'}."

    return prompt.strip()


def assemble_prompt_with_fallback(
    global_vars: Optional[GlobalBrandVars],
    local_vars: LocalMessageVars,
    fallback_style: str = "illustrated"
) -> str:
    """
    Assemble prompt with fallback for missing global brand values.

    When Director doesn't provide global_brand, uses sensible defaults
    based on the fallback_style parameter.

    Args:
        global_vars: Brand-level variables (may be None or empty)
        local_vars: Message-level variables from slide content
        fallback_style: Visual style fallback ("professional", "illustrated", "kids")

    Returns:
        Natural language prompt string
    """
    # Create fallback global vars if needed
    if global_vars is None or not global_vars.has_values():
        fallback_defaults = {
            "professional": GlobalBrandVars(
                visual_style="polished professional photorealistic",
                color_palette="cool grays and subtle blues",
                lighting_mood="professional studio lighting, sophisticated atmosphere",
                target_demographic="business professionals"
            ),
            "illustrated": GlobalBrandVars(
                visual_style="warm approachable illustrated",
                color_palette="warm earth tones and amber accents",
                lighting_mood="soft natural lighting, welcoming atmosphere",
                target_demographic="general audience"
            ),
            "kids": GlobalBrandVars(
                visual_style="bright playful illustrated cartoon",
                color_palette="bright vibrant colors and bold accents",
                lighting_mood="cheerful vibrant lighting, fun atmosphere",
                target_demographic="young children, playful learning"
            )
        }
        global_vars = fallback_defaults.get(fallback_style, fallback_defaults["illustrated"])

    return assemble_prompt(global_vars, local_vars)


# Quick test
if __name__ == "__main__":
    # Test with full global brand
    global_brand = GlobalBrandVars(
        target_demographic="enterprise executives, corporate leadership",
        visual_style="sleek modern photorealistic",
        color_palette="cool blues and metallic silvers",
        lighting_mood="professional dramatic lighting, sophisticated atmosphere"
    )

    local_message = LocalMessageVars(
        content_archetype="process",
        topic="data analytics transformation",
        anchor_subject="glowing circuit board patterns",
        action_composition="emanating data streams",
        semantic_link="representing digital transformation",
        aspect_ratio="9:16"
    )

    prompt = assemble_prompt(global_brand, local_message)
    print("Full prompt:")
    print(prompt)
    print(f"\nWord count: {len(prompt.split())}")

    # Test with fallback
    print("\n--- Fallback test ---")
    empty_global = GlobalBrandVars()
    fallback_prompt = assemble_prompt_with_fallback(empty_global, local_message, "professional")
    print(fallback_prompt)
