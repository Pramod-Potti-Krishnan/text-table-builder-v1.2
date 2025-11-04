#!/usr/bin/env python3
"""
Final fix for colored bullet markers:
1. Add column_color metadata to JSON specs
2. Update prompt builder to use column_color in instructions
"""
import json
from pathlib import Path

def update_comparison_specs():
    """Add column_color to all comparison variant specs."""
    print("Adding column_color metadata to comparison specs...")

    # Color mapping
    colors = {
        1: {"name": "blue", "hex": "#1a73e8"},
        2: {"name": "red", "hex": "#ea4335"},
        3: {"name": "green", "hex": "#10b981"},
        4: {"name": "purple", "hex": "#9333ea"}
    }

    specs_dir = Path("app/variant_specs/comparison")

    for spec_file in specs_dir.glob("*.json"):
        with open(spec_file, 'r') as f:
            spec = json.load(f)

        # Add column_color to each element
        for idx, element in enumerate(spec["elements"], start=1):
            if element["element_type"] == "comparison_column":
                element["column_color"] = colors[idx]["hex"]

        with open(spec_file, 'w') as f:
            json.dump(spec, f, indent=2)

        print(f"  ✓ Updated {spec_file.name}")

def update_prompt_builder():
    """Update element_prompt_builder.py to use column_color in prompts."""
    print("\nUpdating element_prompt_builder.py...")

    prompt_builder_path = Path("app/core/element_prompt_builder.py")
    content = prompt_builder_path.read_text()

    # Find the comparison_column instruction and update it
    old_instruction = '''            "comparison_column": (
                "- Heading should clearly identify what's being compared\\n"
                "- Items should be returned as HTML <ul> list with <li> tags\\n"
                "- IMPORTANT: Each <li> must start with a colored bullet character followed by black text\\n"
                "- Use HTML format: <li><span style='color: [HEADER_COLOR];'>● </span>Rest of text in black</li>\\n"
                "- Column 1 bullets: blue (#1a73e8), Column 2: red (#ea4335), Column 3: green (#10b981), Column 4: purple (#9333ea)\\n"
                "- Focus on distinct, comparable points\\n"
                "- Use parallel structure for easy comparison"
            ),'''

    new_instruction = '''            "comparison_column": (
                "- Heading should clearly identify what's being compared\\n"
                "- Items should be returned as HTML <ul> list with <li> tags\\n"
                "- Focus on distinct, comparable points\\n"
                "- Use parallel structure for easy comparison"
            ),'''

    if old_instruction in content:
        content = content.replace(old_instruction, new_instruction)
        prompt_builder_path.write_text(content)
        print("  ✓ Updated comparison_column instruction")
    else:
        print("  ℹ comparison_column instruction not found or already updated")

def main():
    print("=" * 70)
    print("ADDING COLORED BULLET SUPPORT TO COMPARISON LAYOUTS")
    print("=" * 70)
    print()

    update_comparison_specs()
    update_prompt_builder()

    print()
    print("=" * 70)
    print("✅ UPDATES COMPLETE!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Regenerate comparison templates")
    print("  2. Publish to Railway")
    print()

if __name__ == "__main__":
    main()
