#!/usr/bin/env python3
"""
Test that the template assembler fix properly handles CSS curly braces
"""
from app.core.template_assembler import TemplateAssembler

def test_comparison_2col():
    """Test that comparison_2col template can be loaded and placeholders detected."""
    assembler = TemplateAssembler()

    print("Testing comparison_2col template...")
    try:
        placeholders = assembler.get_template_placeholders("multilateral_comparison/comparison_2col.html")
        print(f"✓ Successfully detected placeholders: {sorted(placeholders)}")

        # Expected placeholders
        expected = {'column_1_heading', 'column_1_items', 'column_2_heading', 'column_2_items'}

        if placeholders == expected:
            print(f"✓ Correct placeholders detected!")
            return True
        else:
            print(f"✗ Unexpected placeholders!")
            print(f"  Expected: {sorted(expected)}")
            print(f"  Got: {sorted(placeholders)}")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_comparison_3col():
    """Test that comparison_3col template can be loaded."""
    assembler = TemplateAssembler()

    print("\nTesting comparison_3col template...")
    try:
        placeholders = assembler.get_template_placeholders("multilateral_comparison/comparison_3col.html")
        print(f"✓ Successfully detected placeholders: {sorted(placeholders)}")

        expected = {
            'column_1_heading', 'column_1_items',
            'column_2_heading', 'column_2_items',
            'column_3_heading', 'column_3_items'
        }

        if placeholders == expected:
            print(f"✓ Correct placeholders detected!")
            return True
        else:
            print(f"✗ Unexpected placeholders!")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_comparison_4col():
    """Test that comparison_4col template can be loaded."""
    assembler = TemplateAssembler()

    print("\nTesting comparison_4col template...")
    try:
        placeholders = assembler.get_template_placeholders("multilateral_comparison/comparison_4col.html")
        print(f"✓ Successfully detected placeholders: {sorted(placeholders)}")

        expected = {
            'column_1_heading', 'column_1_items',
            'column_2_heading', 'column_2_items',
            'column_3_heading', 'column_3_items',
            'column_4_heading', 'column_4_items'
        }

        if placeholders == expected:
            print(f"✓ Correct placeholders detected!")
            return True
        else:
            print(f"✗ Unexpected placeholders!")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("=" * 70)
    print("TESTING TEMPLATE ASSEMBLER FIX FOR CSS CURLY BRACES")
    print("=" * 70)
    print()

    results = []
    results.append(test_comparison_2col())
    results.append(test_comparison_3col())
    results.append(test_comparison_4col())

    print()
    print("=" * 70)
    if all(results):
        print("✅ ALL TESTS PASSED!")
        print("Template assembler can now handle CSS curly braces correctly.")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70)

if __name__ == "__main__":
    main()
