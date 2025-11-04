#!/usr/bin/env python3
"""
Final proper fix: Let CSS handle bullet colors, LLM just generates content
"""
from pathlib import Path

def create_comparison_2col():
    """Create comparison_2col with proper CSS-based colored bullets."""
    template = '''<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 38px; padding: 40px 48px; height: 100%; background: white; align-items: start;">

  <!-- Column 1: Blue bullets -->
  <div class="col-blue">
    <h3 style="color: #1a73e8; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #1a73e8; padding-bottom: 14px;">{column_1_heading}</h3>
    <ul>
      {column_1_items}
    </ul>
  </div>

  <!-- Column 2: Red bullets -->
  <div class="col-red">
    <h3 style="color: #ea4335; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #ea4335; padding-bottom: 14px;">{column_2_heading}</h3>
    <ul>
      {column_2_items}
    </ul>
  </div>

</div>

<style type="text/css">
.col-blue ul ''' + '''{''' + ''' list-style: none; padding: 0; margin: 0; font-size: 23px; line-height: 1.8; color: #1f2937; ''' + '''}''' + '''
.col-blue ul li ''' + '''{''' + ''' padding-left: 20px; position: relative; ''' + '''}''' + '''
.col-blue ul li::before ''' + '''{''' + ''' content: "●"; color: #1a73e8; position: absolute; left: 0; ''' + '''}''' + '''

.col-red ul ''' + '''{''' + ''' list-style: none; padding: 0; margin: 0; font-size: 23px; line-height: 1.8; color: #1f2937; ''' + '''}''' + '''
.col-red ul li ''' + '''{''' + ''' padding-left: 20px; position: relative; ''' + '''}''' + '''
.col-red ul li::before ''' + '''{''' + ''' content: "●"; color: #ea4335; position: absolute; left: 0; ''' + '''}''' + '''
</style>'''

    template_path = Path("app/templates/multilateral_comparison/comparison_2col.html")
    template_path.write_text(template)
    print(f"✓ Created {template_path}")
    print("  - Blue bullets for column 1")
    print("  - Red bullets for column 2")
    print("  - CSS uses ::before pseudo-element")

def create_comparison_3col():
    """Create comparison_3col with proper CSS-based colored bullets."""
    template = '''<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px; padding: 40px; height: 100%; background: white; align-items: start;">

  <!-- Column 1: Blue bullets -->
  <div class="col-blue">
    <h3 style="color: #1a73e8; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #1a73e8; padding-bottom: 14px;">{column_1_heading}</h3>
    <ul>
      {column_1_items}
    </ul>
  </div>

  <!-- Column 2: Red bullets -->
  <div class="col-red">
    <h3 style="color: #ea4335; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #ea4335; padding-bottom: 14px;">{column_2_heading}</h3>
    <ul>
      {column_2_items}
    </ul>
  </div>

  <!-- Column 3: Green bullets -->
  <div class="col-green">
    <h3 style="color: #10b981; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #10b981; padding-bottom: 14px;">{column_3_heading}</h3>
    <ul>
      {column_3_items}
    </ul>
  </div>

</div>

<style type="text/css">
.col-blue ul ''' + '''{''' + ''' list-style: none; padding: 0; margin: 0; font-size: 23px; line-height: 1.8; color: #1f2937; ''' + '''}''' + '''
.col-blue ul li ''' + '''{''' + ''' padding-left: 20px; position: relative; ''' + '''}''' + '''
.col-blue ul li::before ''' + '''{''' + ''' content: "●"; color: #1a73e8; position: absolute; left: 0; ''' + '''}''' + '''

.col-red ul ''' + '''{''' + ''' list-style: none; padding: 0; margin: 0; font-size: 23px; line-height: 1.8; color: #1f2937; ''' + '''}''' + '''
.col-red ul li ''' + '''{''' + ''' padding-left: 20px; position: relative; ''' + '''}''' + '''
.col-red ul li::before ''' + '''{''' + ''' content: "●"; color: #ea4335; position: absolute; left: 0; ''' + '''}''' + '''

.col-green ul ''' + '''{''' + ''' list-style: none; padding: 0; margin: 0; font-size: 23px; line-height: 1.8; color: #1f2937; ''' + '''}''' + '''
.col-green ul li ''' + '''{''' + ''' padding-left: 20px; position: relative; ''' + '''}''' + '''
.col-green ul li::before ''' + '''{''' + ''' content: "●"; color: #10b981; position: absolute; left: 0; ''' + '''}''' + '''
</style>'''

    template_path = Path("app/templates/multilateral_comparison/comparison_3col.html")
    template_path.write_text(template)
    print(f"✓ Created {template_path}")
    print("  - Blue, red, green bullets")

def create_comparison_4col():
    """Create comparison_4col with proper CSS-based colored bullets."""
    template = '''<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 36px; padding: 40px 45px; height: 100%; background: white; align-items: start;">

  <!-- Column 1: Blue bullets -->
  <div class="col-blue">
    <h3 style="color: #1a73e8; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #1a73e8; padding-bottom: 14px;">{column_1_heading}</h3>
    <ul>
      {column_1_items}
    </ul>
  </div>

  <!-- Column 2: Red bullets -->
  <div class="col-red">
    <h3 style="color: #ea4335; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #ea4335; padding-bottom: 14px;">{column_2_heading}</h3>
    <ul>
      {column_2_items}
    </ul>
  </div>

  <!-- Column 3: Green bullets -->
  <div class="col-green">
    <h3 style="color: #10b981; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #10b981; padding-bottom: 14px;">{column_3_heading}</h3>
    <ul>
      {column_3_items}
    </ul>
  </div>

  <!-- Column 4: Purple bullets -->
  <div class="col-purple">
    <h3 style="color: #9333ea; font-size: 32px; margin: 0 0 24px 0; font-weight: 700; border-bottom: 4px solid #9333ea; padding-bottom: 14px;">{column_4_heading}</h3>
    <ul>
      {column_4_items}
    </ul>
  </div>

</div>

<style type="text/css">
.col-blue ul ''' + '''{''' + ''' list-style: none; padding: 0; margin: 0; font-size: 23px; line-height: 1.8; color: #1f2937; ''' + '''}''' + '''
.col-blue ul li ''' + '''{''' + ''' padding-left: 20px; position: relative; ''' + '''}''' + '''
.col-blue ul li::before ''' + '''{''' + ''' content: "●"; color: #1a73e8; position: absolute; left: 0; ''' + '''}''' + '''

.col-red ul ''' + '''{''' + ''' list-style: none; padding: 0; margin: 0; font-size: 23px; line-height: 1.8; color: #1f2937; ''' + '''}''' + '''
.col-red ul li ''' + '''{''' + ''' padding-left: 20px; position: relative; ''' + '''}''' + '''
.col-red ul li::before ''' + '''{''' + ''' content: "●"; color: #ea4335; position: absolute; left: 0; ''' + '''}''' + '''

.col-green ul ''' + '''{''' + ''' list-style: none; padding: 0; margin: 0; font-size: 23px; line-height: 1.8; color: #1f2937; ''' + '''}''' + '''
.col-green ul li ''' + '''{''' + ''' padding-left: 20px; position: relative; ''' + '''}''' + '''
.col-green ul li::before ''' + '''{''' + ''' content: "●"; color: #10b981; position: absolute; left: 0; ''' + '''}''' + '''

.col-purple ul ''' + '''{''' + ''' list-style: none; padding: 0; margin: 0; font-size: 23px; line-height: 1.8; color: #1f2937; ''' + '''}''' + '''
.col-purple ul li ''' + '''{''' + ''' padding-left: 20px; position: relative; ''' + '''}''' + '''
.col-purple ul li::before ''' + '''{''' + ''' content: "●"; color: #9333ea; position: absolute; left: 0; ''' + '''}''' + '''
</style>'''

    template_path = Path("app/templates/multilateral_comparison/comparison_4col.html")
    template_path.write_text(template)
    print(f"✓ Created {template_path}")
    print("  - Blue, red, green, purple bullets")

def remove_color_instructions_from_prompt_builder():
    """Remove the color instructions we added to prompt builder since CSS now handles it."""
    print("\nRemoving color instructions from prompt builder...")

    prompt_builder_path = Path("app/core/element_prompt_builder.py")
    content = prompt_builder_path.read_text()

    # Remove the color-specific instructions we added
    old_block = '''        # For comparison columns, add color-specific instructions
        if element_type == "comparison_column":
            color_map = {
                "column_1": ("blue", "#1a73e8"),
                "column_2": ("red", "#ea4335"),
                "column_3": ("green", "#10b981"),
                "column_4": ("purple", "#9333ea")
            }
            if element_id in color_map:
                color_name, color_hex = color_map[element_id]
                element_instructions += f"\\n\\n⚠️ CRITICAL FORMATTING REQUIREMENT:\\n"
                element_instructions += f"Each <li> MUST use this EXACT format:\\n"
                element_instructions += f'<li><span style="color: {color_hex};">● </span>Your text content here</li>\\n'
                element_instructions += f"\\nDO NOT use plain <li> tags. The colored bullet is MANDATORY.\\n"
                element_instructions += f"The ● character must be inside the colored span, followed by a space, then your text."

'''

    if old_block in content:
        content = content.replace(old_block, '')
        prompt_builder_path.write_text(content)
        print("  ✓ Removed color instructions from prompt builder")
    else:
        print("  ℹ Color instructions not found (may already be removed)")

def main():
    print("=" * 70)
    print("PROPER FIX: CSS HANDLES BULLETS, LLM GENERATES CONTENT")
    print("=" * 70)
    print()

    create_comparison_2col()
    print()
    create_comparison_3col()
    print()
    create_comparison_4col()
    print()
    remove_color_instructions_from_prompt_builder()

    print()
    print("=" * 70)
    print("✅ TEMPLATES FIXED PROPERLY!")
    print("=" * 70)
    print()
    print("How it works now:")
    print("  1. HTML template has CSS classes (col-blue, col-red, etc.)")
    print("  2. CSS ::before pseudo-element adds colored bullets")
    print("  3. LLM generates plain <li>Content</li> tags")
    print("  4. No curly braces in templates (CSS built with string concat)")
    print()
    print("Next: Regenerate and publish!")
    print()

if __name__ == "__main__":
    main()
