#!/usr/bin/env python3
"""
Fix bullet markers: Color the bullet points (dots) to match headers, keep text black
"""
from pathlib import Path

def update_comparison_2col():
    """Update comparison_2col with colored bullet markers."""
    print("Updating comparison_2col - colored bullet markers...")

    template_path = Path("app/templates/multilateral_comparison/comparison_2col.html")

    # Use ::marker pseudo-element or list-style approach
    # Using custom bullets with ::before for better color control
    new_template = '''<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 38px; padding: 40px 48px; height: 100%; background: white; align-items: start;">

  <!-- Column 1: Blue -->
  <div>
    <h3 style="color: #1a73e8; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #1a73e8; padding-bottom: 14px;">{column_1_heading}</h3>
    <ul style="list-style: none; padding: 0; margin: 0; font-size: 23px; line-height: 1.8; color: #1f2937;">
      {column_1_items_with_blue_bullets}
    </ul>
  </div>

  <!-- Column 2: Red -->
  <div>
    <h3 style="color: #ea4335; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #ea4335; padding-bottom: 14px;">{column_2_heading}</h3>
    <ul style="list-style: none; padding: 0; margin: 0; font-size: 23px; line-height: 1.8; color: #1f2937;">
      {column_2_items_with_red_bullets}
    </ul>
  </div>

</div>

<style>
  /* Blue bullets for column 1 */
  ul li:has(+ li) {
    position: relative;
    padding-left: 24px;
  }
  ul li::before {
    content: "•";
    position: absolute;
    left: 0;
  }
  /* Apply via inline or embedded - we'll use inline style approach instead */
</style>
'''

    # Better approach: Use inline styles with span wrapper
    new_template = '''<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 38px; padding: 40px 48px; height: 100%; background: white; align-items: start;">

  <!-- Column 1: Blue bullets, black text -->
  <div>
    <h3 style="color: #1a73e8; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #1a73e8; padding-bottom: 14px;">{column_1_heading}</h3>
    <div style="font-size: 23px; line-height: 1.8; color: #1f2937;">
      {column_1_items}
    </div>
  </div>

  <!-- Column 2: Red bullets, black text -->
  <div>
    <h3 style="color: #ea4335; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #ea4335; padding-bottom: 14px;">{column_2_heading}</h3>
    <div style="font-size: 23px; line-height: 1.8; color: #1f2937;">
      {column_2_items}
    </div>
  </div>

</div>
'''

    with open(template_path, 'w') as f:
        f.write(new_template)

    print(f"  ✓ Updated {template_path}")
    print(f"    - Column 1: Blue bullet markers (#1a73e8), black text")
    print(f"    - Column 2: Red bullet markers (#ea4335), black text")

def update_comparison_3col():
    """Update comparison_3col with colored bullet markers."""
    print("\nUpdating comparison_3col - colored bullet markers...")

    template_path = Path("app/templates/multilateral_comparison/comparison_3col.html")

    new_template = '''<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px; padding: 40px; height: 100%; background: white; align-items: start;">

  <!-- Column 1: Blue bullets, black text -->
  <div>
    <h3 style="color: #1a73e8; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #1a73e8; padding-bottom: 14px;">{column_1_heading}</h3>
    <div style="font-size: 23px; line-height: 1.8; color: #1f2937;">
      {column_1_items}
    </div>
  </div>

  <!-- Column 2: Red bullets, black text -->
  <div>
    <h3 style="color: #ea4335; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #ea4335; padding-bottom: 14px;">{column_2_heading}</h3>
    <div style="font-size: 23px; line-height: 1.8; color: #1f2937;">
      {column_2_items}
    </div>
  </div>

  <!-- Column 3: Green bullets, black text -->
  <div>
    <h3 style="color: #10b981; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #10b981; padding-bottom: 14px;">{column_3_heading}</h3>
    <div style="font-size: 23px; line-height: 1.8; color: #1f2937;">
      {column_3_items}
    </div>
  </div>

</div>
'''

    with open(template_path, 'w') as f:
        f.write(new_template)

    print(f"  ✓ Updated {template_path}")
    print(f"    - Column 1: Blue bullet markers, black text")
    print(f"    - Column 2: Red bullet markers, black text")
    print(f"    - Column 3: Green bullet markers, black text")

def update_comparison_4col():
    """Update comparison_4col with colored bullet markers."""
    print("\nUpdating comparison_4col - colored bullet markers...")

    template_path = Path("app/templates/multilateral_comparison/comparison_4col.html")

    new_template = '''<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 36px; padding: 40px 45px; height: 100%; background: white; align-items: start;">

  <!-- Column 1: Blue bullets, black text -->
  <div>
    <h3 style="color: #1a73e8; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #1a73e8; padding-bottom: 14px;">{column_1_heading}</h3>
    <div style="font-size: 23px; line-height: 1.8; color: #1f2937;">
      {column_1_items}
    </div>
  </div>

  <!-- Column 2: Red bullets, black text -->
  <div>
    <h3 style="color: #ea4335; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #ea4335; padding-bottom: 14px;">{column_2_heading}</h3>
    <div style="font-size: 23px; line-height: 1.8; color: #1f2937;">
      {column_2_items}
    </div>
  </div>

  <!-- Column 3: Green bullets, black text -->
  <div>
    <h3 style="color: #10b981; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #10b981; padding-bottom: 14px;">{column_3_heading}</h3>
    <div style="font-size: 23px; line-height: 1.8; color: #1f2937;">
      {column_3_items}
    </div>
  </div>

  <!-- Column 4: Purple bullets, black text -->
  <div>
    <h3 style="color: #9333ea; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #9333ea; padding-bottom: 14px;">{column_4_heading}</h3>
    <div style="font-size: 23px; line-height: 1.8; color: #1f2937;">
      {column_4_items}
    </div>
  </div>

</div>
'''

    with open(template_path, 'w') as f:
        f.write(new_template)

    print(f"  ✓ Updated {template_path}")
    print(f"    - Column 1: Blue bullet markers, black text")
    print(f"    - Column 2: Red bullet markers, black text")
    print(f"    - Column 3: Green bullet markers, black text")
    print(f"    - Column 4: Purple bullet markers, black text")

def main():
    print("=" * 70)
    print("FIXING BULLET MARKERS - COLORED DOTS, BLACK TEXT")
    print("=" * 70)
    print()

    update_comparison_2col()
    update_comparison_3col()
    update_comparison_4col()

    print()
    print("=" * 70)
    print("✅ TEMPLATES UPDATED!")
    print("=" * 70)
    print()
    print("Note: The LLM will need to wrap bullets in colored spans.")
    print("Next step: Update element_prompt_builder.py to generate colored bullets")
    print()

if __name__ == "__main__":
    main()
