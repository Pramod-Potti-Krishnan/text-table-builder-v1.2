#!/usr/bin/env python3
"""
Test Symbol Font Fix - Regenerate one grid template to verify LLM generates symbols
"""
import json
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core import ElementBasedContentGenerator
from app.services import create_llm_callable


def test_symbol_font_generation():
    """Test that LLM now generates symbol fonts instead of letters."""

    print("Testing Symbol Font Fix...")
    print("=" * 60)

    # Initialize generator
    llm_callable = create_llm_callable()
    generator = ElementBasedContentGenerator(
        llm_service=llm_callable,
        variant_specs_dir="app/variant_specs",
        templates_dir="app/templates",
        enable_parallel=True,
        max_workers=5
    )

    # Test with grid_3x2_left (6 boxes with icons)
    variant_id = "grid_3x2_left"
    slide_spec = {
        "slide_title": "Digital Transformation Initiatives",
        "slide_purpose": "Discuss the six key strategic initiatives driving digital transformation in modern enterprises",
        "key_message": "Six strategic pillars enable successful digital transformation in the modern enterprise",
        "tone": "professional",
        "audience": "executive stakeholders"
    }
    presentation_spec = {
        "presentation_title": "Business Strategy Presentation",
        "presentation_type": "Strategy Presentation",
        "current_slide_number": 5,
        "total_slides": 20
    }

    print(f"\nGenerating content for: {variant_id}")
    print(f"Slide purpose: {slide_spec['slide_purpose']}")
    print("\nExpected: Icons should be symbol fonts (●, ■, ▲, ◆, ★, ✓)")
    print("NOT letters (A, B, C) or emojis (💬, 👁️, 📈)")
    print("-" * 60)

    try:
        # Generate content
        result = generator.generate_slide_content(
            variant_id=variant_id,
            slide_spec=slide_spec,
            presentation_spec=presentation_spec
        )

        print("\n✅ Generation successful!")
        print("\nGenerated content:")
        print(json.dumps(result["elements"], indent=2))

        # Check icons
        print("\n" + "=" * 60)
        print("ICON VERIFICATION:")
        print("=" * 60)

        for i in range(1, 7):
            box_id = f"box_{i}"
            if box_id in result["elements"]:
                element = result["elements"][box_id]
                icon = element.get("icon", "")
                title = element.get("title", "")[:30]

                # Check if it's a single character
                is_single_char = len(icon) == 1

                # Check if it's NOT a letter or emoji
                is_letter = icon.isalpha()
                is_emoji = len(icon.encode('utf-8')) > 3  # Emojis are typically 4 bytes

                status = "✅ GOOD" if (is_single_char and not is_letter and not is_emoji) else "❌ BAD"

                print(f"{box_id}: '{icon}' (title: {title}...) - {status}")
                print(f"  Single char: {is_single_char}, Letter: {is_letter}, Emoji: {is_emoji}")

        print("\n" + "=" * 60)

        # Save to file for visual inspection
        output_file = "test_symbol_font_output.json"
        with open(output_file, 'w') as f:
            json.dump(result["elements"], f, indent=2)

        print(f"\n💾 Full output saved to: {output_file}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_symbol_font_generation()
