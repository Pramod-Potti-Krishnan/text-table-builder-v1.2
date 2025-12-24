#!/usr/bin/env python3
"""
Create Themed Templates Script

Converts C1 templates to use CSS variables for dark/light mode support.
Creates {variant_id}_themed.html files from original {variant_id}.html files.

Usage:
    python scripts/create_themed_templates.py
"""

import os
import re
from pathlib import Path

# Base directory for templates
TEMPLATES_DIR = Path(__file__).parent.parent / "app" / "templates"

# Templates to convert (excluding those that already have themed versions)
TEMPLATES_TO_CONVERT = {
    "metrics": [
        "metrics_2x2_grid_c1",
        "metrics_3x2_grid_c1",
        "metrics_4col_c1",
    ],
    "grid": [
        "grid_2x2_left_c1",
        "grid_2x2_numbered_c1",
        "grid_2x3_c1",
        "grid_2x3_left_c1",
        "grid_2x3_numbered_c1",
        "grid_3x2_c1",
        "grid_3x2_left_c1",
        "grid_3x2_numbered_c1",
    ],
    "table": [
        "table_2col_c1",
        "table_4col_c1",
        "table_5col_c1",
    ],
    "multilateral_comparison": [
        "comparison_2col_c1",
        "comparison_4col_c1",
    ],
    "sequential": [
        "sequential_3col_c1",
        "sequential_4col_c1",
        "sequential_5col_c1",
    ],
    "single_column": [
        "single_column_3section_c1",
        "single_column_4section_c1",
        "single_column_5section_c1",
    ],
    "asymmetric": [
        "asymmetric_8_4_3section_c1",
        "asymmetric_8_4_4section_c1",
        "asymmetric_8_4_5section_c1",
    ],
    "hybrid": [
        "hybrid_left_2x2_c1",
        "hybrid_top_2x2_c1",
    ],
    "matrix": [
        "matrix_2x2_c1",
        "matrix_2x3_c1",
    ],
}

# CSS variable replacements
# Format: (pattern, replacement)
CSS_REPLACEMENTS = [
    # Text colors - primary (dark text)
    (r'color:\s*#1f2937', 'color: var(--text-primary, #1f2937)'),
    (r'color:\s*#1F2937', 'color: var(--text-primary, #1f2937)'),

    # Text colors - secondary
    (r'color:\s*#374151', 'color: var(--text-secondary, #374151)'),

    # Text colors - body
    (r'color:\s*#4b5563', 'color: var(--text-body, #4b5563)'),
    (r'color:\s*#4B5563', 'color: var(--text-body, #4b5563)'),

    # Text colors - muted
    (r'color:\s*#6b7280', 'color: var(--text-muted, #6b7280)'),
    (r'color:\s*#6B7280', 'color: var(--text-muted, #6b7280)'),

    # Text colors - white on dark backgrounds (for gradient boxes)
    # Be careful to only replace when it's clearly on a dark background
    (r'color:\s*white(?![a-zA-Z])', 'color: var(--text-on-dark, white)'),
    (r'color:\s*#fff(?![\da-fA-F])', 'color: var(--text-on-dark, #fff)'),
    (r'color:\s*#ffffff', 'color: var(--text-on-dark, #ffffff)'),
    (r'color:\s*#FFFFFF', 'color: var(--text-on-dark, #ffffff)'),

    # Background colors - box variants (pastel colors)
    (r'background(?:-color)?:\s*#dbeafe', 'background: var(--box-1-bg, #dbeafe)'),
    (r'background(?:-color)?:\s*#DBEAFE', 'background: var(--box-1-bg, #dbeafe)'),
    (r'background(?:-color)?:\s*#d1fae5', 'background: var(--box-2-bg, #d1fae5)'),
    (r'background(?:-color)?:\s*#D1FAE5', 'background: var(--box-2-bg, #d1fae5)'),
    (r'background(?:-color)?:\s*#fef3c7', 'background: var(--box-3-bg, #fef3c7)'),
    (r'background(?:-color)?:\s*#FEF3C7', 'background: var(--box-3-bg, #fef3c7)'),
    (r'background(?:-color)?:\s*#fce7f3', 'background: var(--box-4-bg, #fce7f3)'),
    (r'background(?:-color)?:\s*#FCE7F3', 'background: var(--box-4-bg, #fce7f3)'),
    (r'background(?:-color)?:\s*#ede9fe', 'background: var(--box-5-bg, #ede9fe)'),
    (r'background(?:-color)?:\s*#EDE9FE', 'background: var(--box-5-bg, #ede9fe)'),

    # Border colors
    (r'border(?:-color)?:\s*#d1d5db', 'border-color: var(--border-default, #d1d5db)'),
    (r'border(?:-color)?:\s*#D1D5DB', 'border-color: var(--border-default, #d1d5db)'),
    (r'border(?:-color)?:\s*#e5e7eb', 'border-color: var(--border-light, #e5e7eb)'),
    (r'border(?:-color)?:\s*#E5E7EB', 'border-color: var(--border-light, #e5e7eb)'),

    # Border shorthand (e.g., border: 2px solid #d1d5db)
    (r'border:\s*(\d+px)\s+solid\s+#d1d5db', r'border: \1 solid var(--border-default, #d1d5db)'),
    (r'border:\s*(\d+px)\s+solid\s+#e5e7eb', r'border: \1 solid var(--border-light, #e5e7eb)'),

    # Table row alternating background
    (r'background(?:-color)?:\s*#f9fafb', 'background: var(--table-row-alt, #f9fafb)'),
    (r'background(?:-color)?:\s*#F9FAFB', 'background: var(--table-row-alt, #f9fafb)'),
]

# Header comment for themed templates
THEMED_HEADER = """<!--
  Themed Template: {variant_id}
  Uses CSS variables for dark/light mode support.
  Requires: theme-variables.css loaded in parent document.
-->
"""


def apply_css_replacements(content: str) -> str:
    """Apply all CSS variable replacements to the content."""
    for pattern, replacement in CSS_REPLACEMENTS:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    return content


def create_themed_template(category: str, variant_id: str) -> bool:
    """
    Create a themed version of a template.

    Args:
        category: Template category (e.g., "metrics", "grid")
        variant_id: Variant identifier (e.g., "metrics_2x2_grid_c1")

    Returns:
        True if successful, False otherwise
    """
    # Build file paths
    category_dir = TEMPLATES_DIR / category
    original_file = category_dir / f"{variant_id}.html"
    themed_file = category_dir / f"{variant_id}_themed.html"

    # Check if original exists
    if not original_file.exists():
        print(f"  ❌ Original not found: {original_file}")
        return False

    # Check if themed already exists
    if themed_file.exists():
        print(f"  ⚠️  Themed already exists: {themed_file.name}")
        return True  # Not an error, just skip

    # Read original content
    with open(original_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply CSS variable replacements
    themed_content = apply_css_replacements(content)

    # Add header comment
    header = THEMED_HEADER.format(variant_id=variant_id)
    themed_content = header + themed_content

    # Write themed file
    with open(themed_file, 'w', encoding='utf-8') as f:
        f.write(themed_content)

    print(f"  ✅ Created: {themed_file.name}")
    return True


def main():
    """Create all themed templates."""
    print("=" * 60)
    print("Creating Themed Templates for CSS Variable Support")
    print("=" * 60)
    print(f"\nTemplates directory: {TEMPLATES_DIR}")

    total = 0
    success = 0

    for category, variants in TEMPLATES_TO_CONVERT.items():
        print(f"\n📁 {category.upper()} ({len(variants)} templates)")

        for variant_id in variants:
            total += 1
            if create_themed_template(category, variant_id):
                success += 1

    print("\n" + "=" * 60)
    print(f"Summary: {success}/{total} templates created")
    print("=" * 60)

    if success == total:
        print("\n✅ All themed templates created successfully!")
        print("\nNext steps:")
        print("1. Review the generated files")
        print("2. Update CSS_VARIABLE_TEMPLATES env var on Railway")
        print("3. Deploy Text Service")
    else:
        print(f"\n⚠️  {total - success} templates failed. Check errors above.")


if __name__ == "__main__":
    main()
