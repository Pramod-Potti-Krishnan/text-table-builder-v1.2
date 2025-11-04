#!/usr/bin/env python3
"""
Increase Character Counts by 25% for Numbered Grid Variants
"""
import json
from pathlib import Path


def increase_description_chars(spec_path: Path):
    """Increase description character counts by 25%."""
    with open(spec_path, 'r') as f:
        spec = json.load(f)

    variant_id = spec["variant_id"]
    print(f"Processing {variant_id}...")

    for element in spec["elements"]:
        char_reqs = element["character_requirements"]

        if "description" in char_reqs:
            desc = char_reqs["description"]
            current_baseline = desc["baseline"]

            # Increase by 25%
            new_baseline = int(current_baseline * 1.25)
            new_min = int(new_baseline * 0.95)
            new_max = int(new_baseline * 1.05)

            desc["baseline"] = new_baseline
            desc["min"] = new_min
            desc["max"] = new_max

            print(f"  {element['element_id']}: {current_baseline} → {new_baseline} chars")

    # Write back
    with open(spec_path, 'w') as f:
        json.dump(spec, f, indent=2)

    print(f"  ✓ {variant_id} updated\n")


def main():
    print("=" * 70)
    print("Increasing Character Counts for Numbered Variants")
    print("=" * 70)
    print()

    specs_dir = Path("app/variant_specs/grid")

    # Update both numbered variants
    numbered_variants = [
        "grid_3x2_numbered",
        "grid_2x2_numbered"
    ]

    for variant_id in numbered_variants:
        spec_path = specs_dir / f"{variant_id}.json"
        if spec_path.exists():
            increase_description_chars(spec_path)
        else:
            print(f"⚠ Not found: {variant_id}")

    print("=" * 70)
    print("✅ All numbered variants updated with 25% increase!")


if __name__ == "__main__":
    main()
