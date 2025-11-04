#!/usr/bin/env python3
"""
Fix bullet markers: Color the bullet points (dots) to match headers, keep text black.
Using ::marker pseudo-element for proper bullet styling.
"""
from pathlib import Path

def update_comparison_2col():
    """Update comparison_2col with colored bullet markers using ::marker."""
    print("Updating comparison_2col - colored bullet markers...")

    template_path = Path("app/templates/multilateral_comparison/comparison_2col.html")

    # Use data attributes and embedded CSS for ::marker styling
    new_template = '''<style>
  .blue-bullets li::marker {
    color: #1a73e8;
  }
  .red-bullets li::marker {
    color: #ea4335;
  }
</style>

<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 38px; padding: 40px 48px; height: 100%; background: white; align-items: start;">

  <!-- Column 1: Blue bullet markers, black text -->
  <div>
    <h3 style="color: #1a73e8; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #1a73e8; padding-bottom: 14px;">{column_1_heading}</h3>
    <ul class="blue-bullets" style="padding-left: 24px; margin: 0; font-size: 23px; line-height: 1.8; color: #1f2937;">
      {column_1_items}
    </ul>
  </div>

  <!-- Column 2: Red bullet markers, black text -->
  <div>
    <h3 style="color: #ea4335; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #ea4335; padding-bottom: 14px;">{column_2_heading}</h3>
    <ul class="red-bullets" style="padding-left: 24px; margin: 0; font-size: 23px; line-height: 1.8; color: #1f2937;">
      {column_2_items}
    </ul>
  </div>

</div>
'''

    with open(template_path, 'w') as f:
        f.write(new_template)

    print(f"  ✓ Updated {template_path}")
    print(f"    - Column 1: Blue bullet markers (#1a73e8), black text (#1f2937)")
    print(f"    - Column 2: Red bullet markers (#ea4335), black text (#1f2937)")

def update_comparison_3col():
    """Update comparison_3col with colored bullet markers using ::marker."""
    print("\nUpdating comparison_3col - colored bullet markers...")

    template_path = Path("app/templates/multilateral_comparison/comparison_3col.html")

    new_template = '''<style>
  .blue-bullets li::marker {
    color: #1a73e8;
  }
  .red-bullets li::marker {
    color: #ea4335;
  }
  .green-bullets li::marker {
    color: #10b981;
  }
</style>

<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px; padding: 40px; height: 100%; background: white; align-items: start;">

  <!-- Column 1: Blue bullet markers, black text -->
  <div>
    <h3 style="color: #1a73e8; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #1a73e8; padding-bottom: 14px;">{column_1_heading}</h3>
    <ul class="blue-bullets" style="padding-left: 24px; margin: 0; font-size: 23px; line-height: 1.8; color: #1f2937;">
      {column_1_items}
    </ul>
  </div>

  <!-- Column 2: Red bullet markers, black text -->
  <div>
    <h3 style="color: #ea4335; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #ea4335; padding-bottom: 14px;">{column_2_heading}</h3>
    <ul class="red-bullets" style="padding-left: 24px; margin: 0; font-size: 23px; line-height: 1.8; color: #1f2937;">
      {column_2_items}
    </ul>
  </div>

  <!-- Column 3: Green bullet markers, black text -->
  <div>
    <h3 style="color: #10b981; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #10b981; padding-bottom: 14px;">{column_3_heading}</h3>
    <ul class="green-bullets" style="padding-left: 24px; margin: 0; font-size: 23px; line-height: 1.8; color: #1f2937;">
      {column_3_items}
    </ul>
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
    """Update comparison_4col with colored bullet markers using ::marker."""
    print("\nUpdating comparison_4col - colored bullet markers...")

    template_path = Path("app/templates/multilateral_comparison/comparison_4col.html")

    new_template = '''<style>
  .blue-bullets li::marker {
    color: #1a73e8;
  }
  .red-bullets li::marker {
    color: #ea4335;
  }
  .green-bullets li::marker {
    color: #10b981;
  }
  .purple-bullets li::marker {
    color: #9333ea;
  }
</style>

<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 36px; padding: 40px 45px; height: 100%; background: white; align-items: start;">

  <!-- Column 1: Blue bullet markers, black text -->
  <div>
    <h3 style="color: #1a73e8; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #1a73e8; padding-bottom: 14px;">{column_1_heading}</h3>
    <ul class="blue-bullets" style="padding-left: 24px; margin: 0; font-size: 23px; line-height: 1.8; color: #1f2937;">
      {column_1_items}
    </ul>
  </div>

  <!-- Column 2: Red bullet markers, black text -->
  <div>
    <h3 style="color: #ea4335; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #ea4335; padding-bottom: 14px;">{column_2_heading}</h3>
    <ul class="red-bullets" style="padding-left: 24px; margin: 0; font-size: 23px; line-height: 1.8; color: #1f2937;">
      {column_2_items}
    </ul>
  </div>

  <!-- Column 3: Green bullet markers, black text -->
  <div>
    <h3 style="color: #10b981; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #10b981; padding-bottom: 14px;">{column_3_heading}</h3>
    <ul class="green-bullets" style="padding-left: 24px; margin: 0; font-size: 23px; line-height: 1.8; color: #1f2937;">
      {column_3_items}
    </ul>
  </div>

  <!-- Column 4: Purple bullet markers, black text -->
  <div>
    <h3 style="color: #9333ea; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #9333ea; padding-bottom: 14px;">{column_4_heading}</h3>
    <ul class="purple-bullets" style="padding-left: 24px; margin: 0; font-size: 23px; line-height: 1.8; color: #1f2937;">
      {column_4_items}
    </ul>
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
    print("Using ::marker pseudo-element for proper bullet styling")
    print()

    update_comparison_2col()
    update_comparison_3col()
    update_comparison_4col()

    print()
    print("=" * 70)
    print("✅ TEMPLATES UPDATED!")
    print("=" * 70)
    print()
    print("Changes applied:")
    print("  • Bullet markers: Colored to match header (via ::marker CSS)")
    print("  • Bullet text: Black (#1f2937)")
    print("  • Works with existing HTML list structure from LLM")
    print()

if __name__ == "__main__":
    main()
