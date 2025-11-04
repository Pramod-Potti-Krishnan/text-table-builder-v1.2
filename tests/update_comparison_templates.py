#!/usr/bin/env python3
"""
Update all 3 comparison templates with new specifications:
1. Reduce h3 font size by 10% (36px → 32.4px ≈ 32px)
2. Match bullet colors to h3 header colors
3. comparison_2col: increase column width and gap by 20%, increase chars to 75 avg
4. comparison_4col: increase section width by 12%, increase chars to 25 avg
"""
import json
from pathlib import Path

def update_comparison_2col():
    """Update comparison_2col template with all changes."""
    print("Updating comparison_2col template...")

    template_path = Path("app/templates/multilateral_comparison/comparison_2col.html")

    # New template with:
    # - h3: 32px (down from 36px, -10%)
    # - gap: 38px (up from 32px, +20%)
    # - padding increased by 20% on sides
    # - bullet color matches header color
    new_template = '''<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 38px; padding: 40px 48px; height: 100%; background: white; align-items: start;">

  <!-- Column 1: Blue -->
  <div>
    <h3 style="color: #1a73e8; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #1a73e8; padding-bottom: 14px;">{column_1_heading}</h3>
    <ul style="list-style: none; padding: 0; margin: 0; font-size: 23px; line-height: 1.8; color: #1a73e8;">
      {column_1_items}
    </ul>
  </div>

  <!-- Column 2: Red -->
  <div>
    <h3 style="color: #ea4335; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #ea4335; padding-bottom: 14px;">{column_2_heading}</h3>
    <ul style="list-style: none; padding: 0; margin: 0; font-size: 23px; line-height: 1.8; color: #ea4335;">
      {column_2_items}
    </ul>
  </div>

</div>
'''

    with open(template_path, 'w') as f:
        f.write(new_template)

    print(f"  ✓ Updated {template_path}")
    print(f"    - h3 font: 36px → 32px (-10%)")
    print(f"    - gap: 32px → 38px (+20%)")
    print(f"    - padding: 40px → 48px sides (+20%)")
    print(f"    - bullet colors: match headers (blue, red)")

def update_comparison_3col():
    """Update comparison_3col template with color matching."""
    print("\nUpdating comparison_3col template...")

    template_path = Path("app/templates/multilateral_comparison/comparison_3col.html")

    # New template with:
    # - h3: 32px (down from 36px, -10%)
    # - bullet color matches header color
    new_template = '''<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px; padding: 40px; height: 100%; background: white; align-items: start;">

  <!-- Column 1: Blue -->
  <div>
    <h3 style="color: #1a73e8; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #1a73e8; padding-bottom: 14px;">{column_1_heading}</h3>
    <ul style="list-style: none; padding: 0; margin: 0; font-size: 23px; line-height: 1.8; color: #1a73e8;">
      {column_1_items}
    </ul>
  </div>

  <!-- Column 2: Red -->
  <div>
    <h3 style="color: #ea4335; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #ea4335; padding-bottom: 14px;">{column_2_heading}</h3>
    <ul style="list-style: none; padding: 0; margin: 0; font-size: 23px; line-height: 1.8; color: #ea4335;">
      {column_2_items}
    </ul>
  </div>

  <!-- Column 3: Green -->
  <div>
    <h3 style="color: #10b981; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #10b981; padding-bottom: 14px;">{column_3_heading}</h3>
    <ul style="list-style: none; padding: 0; margin: 0; font-size: 23px; line-height: 1.8; color: #10b981;">
      {column_3_items}
    </ul>
  </div>

</div>
'''

    with open(template_path, 'w') as f:
        f.write(new_template)

    print(f"  ✓ Updated {template_path}")
    print(f"    - h3 font: 36px → 32px (-10%)")
    print(f"    - bullet colors: match headers (blue, red, green)")

def update_comparison_4col():
    """Update comparison_4col template with all changes."""
    print("\nUpdating comparison_4col template...")

    template_path = Path("app/templates/multilateral_comparison/comparison_4col.html")

    # New template with:
    # - h3: 32px (down from 36px, -10%)
    # - gap: 36px (up from 32px, +12%)
    # - padding increased by 12%
    # - bullet color matches header color
    new_template = '''<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 36px; padding: 40px 45px; height: 100%; background: white; align-items: start;">

  <!-- Column 1: Blue -->
  <div>
    <h3 style="color: #1a73e8; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #1a73e8; padding-bottom: 14px;">{column_1_heading}</h3>
    <ul style="list-style: none; padding: 0; margin: 0; font-size: 23px; line-height: 1.8; color: #1a73e8;">
      {column_1_items}
    </ul>
  </div>

  <!-- Column 2: Red -->
  <div>
    <h3 style="color: #ea4335; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #ea4335; padding-bottom: 14px;">{column_2_heading}</h3>
    <ul style="list-style: none; padding: 0; margin: 0; font-size: 23px; line-height: 1.8; color: #ea4335;">
      {column_2_items}
    </ul>
  </div>

  <!-- Column 3: Green -->
  <div>
    <h3 style="color: #10b981; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #10b981; padding-bottom: 14px;">{column_3_heading}</h3>
    <ul style="list-style: none; padding: 0; margin: 0; font-size: 23px; line-height: 1.8; color: #10b981;">
      {column_3_items}
    </ul>
  </div>

  <!-- Column 4: Purple -->
  <div>
    <h3 style="color: #9333ea; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #9333ea; padding-bottom: 14px;">{column_4_heading}</h3>
    <ul style="list-style: none; padding: 0; margin: 0; font-size: 23px; line-height: 1.8; color: #9333ea;">
      {column_4_items}
    </ul>
  </div>

</div>
'''

    with open(template_path, 'w') as f:
        f.write(new_template)

    print(f"  ✓ Updated {template_path}")
    print(f"    - h3 font: 36px → 32px (-10%)")
    print(f"    - gap: 32px → 36px (+12%)")
    print(f"    - padding: 40px → 45px sides (+12%)")
    print(f"    - bullet colors: match headers (blue, red, green, purple)")

def update_json_specs():
    """Update JSON specs with new character requirements."""
    print("\nUpdating JSON specifications...")

    # Update comparison_2col: increase to 75 chars avg per bullet
    # Total items chars: 350 → need ~6 bullets * 75 = 450 chars
    spec_2col_path = Path("app/variant_specs/comparison/comparison_2col.json")
    with open(spec_2col_path, 'r') as f:
        spec_2col = json.load(f)

    for element in spec_2col["elements"]:
        element["character_requirements"]["items"]["baseline"] = 450
        element["character_requirements"]["items"]["min"] = 428
        element["character_requirements"]["items"]["max"] = 473

    with open(spec_2col_path, 'w') as f:
        json.dump(spec_2col, f, indent=2)

    print(f"  ✓ Updated {spec_2col_path.name}")
    print(f"    - items chars: 350 → 450 (~75 chars per bullet)")

    # Update comparison_4col: increase to 25 chars avg per bullet
    # Need ~8 bullets * 25 = 200 chars
    spec_4col_path = Path("app/variant_specs/comparison/comparison_4col.json")

    # First read to check current structure
    with open(spec_4col_path, 'r') as f:
        spec_4col = json.load(f)

    # Update character requirements for all columns
    for element in spec_4col["elements"]:
        if "items" in element["character_requirements"]:
            element["character_requirements"]["items"]["baseline"] = 200
            element["character_requirements"]["items"]["min"] = 190
            element["character_requirements"]["items"]["max"] = 210

    with open(spec_4col_path, 'w') as f:
        json.dump(spec_4col, f, indent=2)

    print(f"  ✓ Updated {spec_4col_path.name}")
    print(f"    - items chars: variable → 200 (~25 chars per bullet)")

def main():
    print("=" * 70)
    print("UPDATING COMPARISON TEMPLATES AND SPECS")
    print("=" * 70)
    print()

    # Update all templates
    update_comparison_2col()
    update_comparison_3col()
    update_comparison_4col()

    # Update JSON specs
    update_json_specs()

    print()
    print("=" * 70)
    print("✅ ALL UPDATES COMPLETE!")
    print("=" * 70)
    print()
    print("Summary of changes:")
    print("  📏 All h3 headers: 36px → 32px (-10%)")
    print("  🎨 All bullets: color matches header color")
    print("  📐 comparison_2col: gap +20%, padding +20%, chars 350→450")
    print("  📐 comparison_4col: gap +12%, padding +12%, chars →200")
    print()

if __name__ == "__main__":
    main()
