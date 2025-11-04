#!/usr/bin/env python3
"""
Update Grid Specs - Fix Icon Format and Character Counts
"""
import json
from pathlib import Path

# Character count adjustments per slide (percentage increase from baseline 80)
CHARACTER_INCREASES = {
    "grid_2x3": 1.50,           # Slide 1: 50% increase -> 120 chars
    "grid_3x2": 1.20,           # Slide 2: 20% increase -> 96 chars
    "grid_2x2_centered": 1.20,  # Slide 3: 20% increase -> 163 chars (from 136)
    "grid_2x3_left": 1.50,      # Slide 4: 50% increase -> 204 chars (from 136)
    "grid_3x2_left": 1.60,      # Slide 5: 60% increase -> 218 chars (from 136)
    "grid_2x2_left": 1.50,      # Slide 6: 50% increase -> 204 chars (from 136)
    "grid_2x3_numbered": 1.30,  # Slide 7: 30% increase -> 177 chars (from 136)
    "grid_3x2_numbered": 1.0,   # No change
    "grid_2x2_numbered": 1.0    # No change
}

def update_spec(variant_id: str, base_description_chars: int):
    """Update a single variant spec."""
    spec_path = Path(f"app/variant_specs/grid/{variant_id}.json")

    with open(spec_path, 'r') as f:
        spec = json.load(f)

    # Calculate new character count
    multiplier = CHARACTER_INCREASES.get(variant_id, 1.0)
    new_baseline = int(base_description_chars * multiplier)
    new_min = int(new_baseline * 0.95)
    new_max = int(new_baseline * 1.05)

    # Update all elements
    for element in spec["elements"]:
        char_reqs = element["character_requirements"]

        # Update icon format if it exists
        if "icon" in char_reqs:
            char_reqs["icon"] = {
                "baseline": 1,
                "min": 1,
                "max": 1,
                "format": "symbol_font",
                "instruction": "Use a single Unicode symbol character from standard symbol fonts (e.g., ●, ■, ▲, ◆, ★, ✓, ➜, ⬆, ⚙, ⚡, etc.) - NOT emojis"
            }

        # Update description character counts
        if "description" in char_reqs:
            char_reqs["description"] = {
                "baseline": new_baseline,
                "min": new_min,
                "max": new_max
            }

    # Write back
    with open(spec_path, 'w') as f:
        json.dump(spec, f, indent=2)

    print(f"✓ Updated {variant_id}: description={new_baseline} chars (was {base_description_chars})")

def main():
    print("Updating Grid Variant Specs...")
    print("=" * 60)

    # Centered variants (baseline 80 chars)
    update_spec("grid_2x3", 80)
    update_spec("grid_3x2", 80)

    # Centered 2x2 (baseline 136 chars - 70% extended)
    update_spec("grid_2x2_centered", 136)

    # Left-aligned variants (baseline 136 chars - 70% extended)
    update_spec("grid_2x3_left", 136)
    update_spec("grid_3x2_left", 136)
    update_spec("grid_2x2_left", 136)

    # Numbered variants (baseline 136 chars - 70% extended)
    update_spec("grid_2x3_numbered", 136)
    update_spec("grid_3x2_numbered", 136)
    update_spec("grid_2x2_numbered", 136)

    print("=" * 60)
    print("✅ All specs updated!")

if __name__ == "__main__":
    main()
