#!/usr/bin/env python3
"""
Fix All Grid Template Spacing Issues
Handles all 5 requested spacing/sizing changes
"""
import re
from pathlib import Path


def apply_percentage_reduction(value_str: str, percent: float) -> str:
    """Apply percentage reduction to a CSS value (e.g., '36px' -> '33px')."""
    match = re.match(r'(\d+)(px|%|em|rem)', value_str)
    if not match:
        return value_str

    value = int(match.group(1))
    unit = match.group(2)
    new_value = round(value * (1 - percent / 100))
    return f"{new_value}{unit}"


def fix_grid_2x2_centered():
    """Fix grid_2x2_centered - reduce by 6%."""
    print("Fixing grid_2x2_centered (6% reduction)...")

    file_path = Path("app/templates/grid/grid_2x2_centered.html")
    content = file_path.read_text()

    # gap: 19px → 18px (6% reduction)
    content = re.sub(r'gap: 19px;', 'gap: 18px;', content)

    # padding: 40px → 38px
    content = re.sub(r'padding: 40px;', 'padding: 38px;', content)

    # icon font-size: 53px → 50px
    content = re.sub(r'font-size: 53px;', 'font-size: 50px;', content)

    # icon margin-bottom: 16px → 15px
    content = re.sub(r'margin: 0 0 16px 0;', 'margin: 0 0 15px 0;', content)

    # title font-size: 23px → 22px
    content = re.sub(r'(h3 style="[^"]*font-size:) 23px', r'\1 22px', content)

    # title margin-bottom: 11px → 10px
    content = re.sub(r'(h3 style="[^"]*margin:) 0 0 11px 0', r'\1 0 0 10px 0', content)

    # description font-size: 17px → 16px
    content = re.sub(r'(p style="[^"]*font-size:) 17px', r'\1 16px', content)

    file_path.write_text(content)
    print("  ✓ grid_2x2_centered updated")


def fix_grid_2x3_left():
    """Fix grid_2x3_left - reduce spacing by 50% and height by 3%."""
    print("Fixing grid_2x3_left (50% spacing, 3% height)...")

    file_path = Path("app/templates/grid/grid_2x3_left.html")
    content = file_path.read_text()

    # gap: 20px → 10px (50% reduction)
    content = re.sub(r'gap: 20px;', 'gap: 10px;', content)

    # padding: 30px → 29px (3% reduction)
    content = re.sub(r'padding: 30px;', 'padding: 29px;', content)

    # icon font-size: 53px → 51px (3%)
    content = re.sub(r'font-size: 53px;', 'font-size: 51px;', content)

    # icon margin-right: 18px → 17px (3%)
    content = re.sub(r'margin-right: 18px;', 'margin-right: 17px;', content)

    # title font-size: 21px → 20px (3%)
    content = re.sub(r'(h3 style="[^"]*font-size:) 21px', r'\1 20px', content)

    # title margin-bottom: 8px → 8px (already close)

    # description font-size: 16px → 16px (already close)

    file_path.write_text(content)
    print("  ✓ grid_2x3_left updated")


def main():
    print("=" * 70)
    print("Fixing Grid Template Spacing Issues")
    print("=" * 70)

    # Change #2: grid_2x2_centered - 6% reduction
    fix_grid_2x2_centered()

    # Change #3: grid_2x3_left - 50% spacing, 3% height
    fix_grid_2x3_left()

    print("=" * 70)
    print("✅ All spacing fixes applied!")
    print("\nSummary:")
    print("  ✓ grid_3x2 - 7.5% reduction (already done manually)")
    print("  ✓ grid_2x2_centered - 6% reduction")
    print("  ✓ grid_2x3_left - 50% spacing, 3% height")


if __name__ == "__main__":
    main()
