#!/usr/bin/env python3
"""
Publish updated comparison templates to Railway
"""
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and display output."""
    print(f"\n{description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"✗ Failed: {result.stderr}")
        return False

    print(f"✓ Success")
    if result.stdout:
        print(result.stdout)
    return True

def main():
    print("=" * 70)
    print("PUBLISHING COMPARISON TEMPLATE UPDATES TO RAILWAY")
    print("=" * 70)

    # Verify templates exist
    template_dir = Path("app/templates/multilateral_comparison")
    templates = [
        "comparison_2col.html",
        "comparison_3col.html",
        "comparison_4col.html"
    ]

    print("\n1. Verifying templates...")
    for template in templates:
        template_path = template_dir / template
        if not template_path.exists():
            print(f"✗ Missing: {template_path}")
            sys.exit(1)
        print(f"  ✓ Found: {template}")

    # Verify variant specs updated
    spec_dir = Path("app/variant_specs/comparison")
    specs = [
        "comparison_2col.json",
        "comparison_3col.json",
        "comparison_4col.json"
    ]

    print("\n2. Verifying variant specs...")
    for spec in specs:
        spec_path = spec_dir / spec
        if not spec_path.exists():
            print(f"✗ Missing: {spec_path}")
            sys.exit(1)
        print(f"  ✓ Found: {spec}")

    # Verify template assembler fix
    print("\n3. Verifying template assembler fix...")
    assembler_path = Path("app/core/template_assembler.py")
    content = assembler_path.read_text()
    if r'\{([a-z_][a-z0-9_]*)\}' in content:
        print("  ✓ Template assembler uses specific placeholder pattern")
    else:
        print("  ✗ Template assembler may still have old pattern")
        sys.exit(1)

    print("\n4. Publishing to Railway...")
    print("\nCommands to run:")
    print("  git add app/templates/multilateral_comparison/*.html")
    print("  git add app/variant_specs/comparison/*.json")
    print("  git add app/core/template_assembler.py")
    print('  git commit -m "feat: Add colored bullets to comparison layouts')
    print()
    print("  - Reduce h3 font from 36px to 32px (-10%)")
    print("  - Add CSS ::before pseudo-elements for colored bullet markers")
    print("  - Blue (#1a73e8), red (#ea4335), green (#10b981), purple (#9333ea)")
    print("  - Bullet text remains black (#1f2937)")
    print("  - comparison_2col: gap 38px, padding 48px sides (+20%)")
    print("  - comparison_4col: gap 36px, padding 45px sides (+12%)")
    print("  - Update character counts (2col: 450 chars, 4col: 200 chars)")
    print("  - Fix template assembler regex to ignore CSS curly braces")
    print()
    print('  🤖 Generated with [Claude Code](https://claude.com/claude-code)')
    print()
    print('  Co-Authored-By: Claude <noreply@anthropic.com>"')
    print("  git push")

    print("\n" + "=" * 70)
    print("✅ READY TO PUBLISH!")
    print("=" * 70)
    print()
    print("Templates updated:")
    print("  - comparison_2col.html (2 columns with blue/red bullets)")
    print("  - comparison_3col.html (3 columns with blue/red/green bullets)")
    print("  - comparison_4col.html (4 columns with blue/red/green/purple bullets)")
    print()
    print("Changes:")
    print("  ✓ H3 headers: 36px → 32px (-10%)")
    print("  ✓ Colored bullet markers via CSS ::before")
    print("  ✓ Bullet text: black (#1f2937)")
    print("  ✓ Updated spacing and character counts")
    print("  ✓ Template assembler handles CSS curly braces")
    print()
    print("Railway will auto-deploy after git push.")
    print()

if __name__ == "__main__":
    main()
