#!/usr/bin/env python3
"""
Update Icon Instructions - Use Meaningful Professional Icons
"""
import json
from pathlib import Path

def update_icon_instruction(spec_path: Path):
    """Update a single variant spec with new icon instruction."""
    with open(spec_path, 'r') as f:
        spec = json.load(f)

    # Update all elements that have icons
    for element in spec["elements"]:
        char_reqs = element["character_requirements"]

        if "icon" in char_reqs:
            # Update to use meaningful, professional icons
            char_reqs["icon"] = {
                "baseline": 1,
                "min": 1,
                "max": 2,  # Allow 2 chars for some emojis
                "format": "professional_icon",
                "instruction": "Use a single professional icon character that semantically represents the card's topic. Choose from business/tech icons like: 💬 (communication), 👁️ (vision/monitoring), 📊 (analytics/data), ⚙️ (automation/settings), 🔌 (integration/API), 📈 (growth/metrics), 🎯 (goals/targeting), 🔒 (security), ☁️ (cloud), 🤖 (AI/automation), 📱 (mobile/digital), 🌐 (global/web), ⚡ (performance/speed), 🔍 (search/discovery). The icon MUST be relevant to the card title and maintain a professional appearance."
            }

    # Write back
    with open(spec_path, 'w') as f:
        json.dump(spec, f, indent=2)

    print(f"✓ Updated {spec_path.name}")


def main():
    print("Updating Icon Instructions for Professional Meaningful Icons...")
    print("=" * 70)

    # Update all icon-based grid variants
    icon_variants = [
        "grid_2x3",
        "grid_3x2",
        "grid_2x2_centered",
        "grid_2x3_left",
        "grid_3x2_left",
        "grid_2x2_left"
    ]

    specs_dir = Path("app/variant_specs/grid")

    for variant_id in icon_variants:
        spec_path = specs_dir / f"{variant_id}.json"
        if spec_path.exists():
            update_icon_instruction(spec_path)
        else:
            print(f"⚠ Not found: {variant_id}")

    print("=" * 70)
    print("✅ All icon variants updated!")
    print("\nNew instruction:")
    print("  - Icons will be professional and semantically meaningful")
    print("  - Icons will represent the card's topic/title")
    print("  - Examples: 💬 communication, 📊 analytics, ⚙️ automation, etc.")


if __name__ == "__main__":
    main()
