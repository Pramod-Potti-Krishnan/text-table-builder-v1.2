#!/usr/bin/env python3
"""
Test Phase 2.5: Light Box Fix Verification
Tests that text in light pastel boxes uses CSS variables for dark mode switching.
"""

import requests
import json
import os
import re

# Use Railway deployment
BASE_URL = "https://web-production-5daf.up.railway.app"

# Test variants that were fixed (light pastel boxes)
TEST_VARIANTS = [
    ("hybrid_left_2x2_c1", "Fix A: Hybrid with hardcoded colors"),
    ("grid_2x3_c1", "Fix B: Grid with --text-muted"),
    ("sequential_4col_c1", "Fix B: Sequential with --text-muted"),
    ("asymmetric_8_4_4section_c1", "Fix A: Asymmetric sidebar"),
]

def generate_slide(variant_id: str) -> dict:
    """Generate a slide with the given variant."""

    payload = {
        "variant_id": variant_id,
        "layout_id": "C1",
        "slide_spec": {
            "slide_title": f"Light Box Test: {variant_id}",
            "slide_purpose": "Testing CSS variable theming for dark mode",
            "key_message": "All text should switch to white in dark mode",
            "tone": "professional",
            "audience": "developers"
        },
        "presentation_spec": {
            "presentation_title": "Phase 2.5 Test",
            "presentation_type": "Test"
        },
        "theme_config": {
            "theme_id": "default",
            "theme_mode": "dark"
        }
    }

    response = requests.post(
        f"{BASE_URL}/v1.2/generate",
        json=payload,
        timeout=90
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def check_css_variables(html: str, variant_id: str) -> dict:
    """Check for CSS variable usage in HTML."""

    # Count CSS variable occurrences
    text_primary_count = len(re.findall(r'--text-primary', html))
    text_muted_count = len(re.findall(r'--text-muted', html))
    text_on_dark_count = len(re.findall(r'--text-on-dark', html))

    # Check for hardcoded colors in text (excluding backgrounds)
    # Look for color: #XXXXXX patterns NOT inside var()
    hardcoded_pattern = r'color:\s*#[0-9a-fA-F]{6}'
    var_pattern = r'color:\s*var\('

    hardcoded_colors = len(re.findall(hardcoded_pattern, html))
    var_colors = len(re.findall(var_pattern, html))

    return {
        "variant_id": variant_id,
        "--text-primary": text_primary_count,
        "--text-muted": text_muted_count,
        "--text-on-dark": text_on_dark_count,
        "hardcoded_colors": hardcoded_colors,
        "var_colors": var_colors,
        "success": text_primary_count > 0 and text_muted_count == 0
    }

def create_preview_html(slides: list, output_path: str):
    """Create a single HTML file to preview all slides with theme toggle."""

    html = """<!DOCTYPE html>
<html>
<head>
    <title>Light Box Fix Test - Phase 2.5</title>
    <style>
        :root {
            --text-primary: #1f2937;
            --text-secondary: #374151;
            --text-muted: #6b7280;
            --text-on-dark: white;
            --border-light: #e5e7eb;
            --border-default: #d1d5db;
            --box-1-bg: #dbeafe;
            --box-2-bg: #d1fae5;
            --box-3-bg: #fef3c7;
            --box-4-bg: #fce7f3;
        }

        .theme-dark {
            --text-primary: white;
            --text-secondary: rgba(255,255,255,0.9);
            --text-muted: rgba(255,255,255,0.7);
            --border-light: rgba(255,255,255,0.2);
            --border-default: rgba(255,255,255,0.3);
            --box-1-bg: rgba(219, 234, 254, 0.4);
            --box-2-bg: rgba(209, 250, 229, 0.4);
            --box-3-bg: rgba(254, 243, 199, 0.4);
            --box-4-bg: rgba(252, 231, 243, 0.4);
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f3f4f6;
        }

        .theme-dark body, body.theme-dark {
            background: #1f2937;
        }

        .controls {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        .controls button {
            padding: 10px 20px;
            margin: 5px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }

        .controls button.light { background: #f3f4f6; color: #1f2937; }
        .controls button.dark { background: #1f2937; color: white; }

        .slide-container {
            width: 960px;
            height: 540px;
            margin: 20px auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            overflow: hidden;
            position: relative;
        }

        .theme-dark .slide-container {
            background: #111827;
        }

        .slide-label {
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 12px;
            z-index: 10;
        }

        .slide-content {
            width: 100%;
            height: 100%;
            padding: 40px;
            box-sizing: border-box;
        }

        h2 {
            margin: 40px 0 20px 0;
            color: #1f2937;
        }

        .theme-dark h2 {
            color: white;
        }
    </style>
</head>
<body>
    <div class="controls">
        <strong>Theme Mode:</strong><br>
        <button class="light" onclick="setTheme('light')">1: Light</button>
        <button class="dark" onclick="setTheme('dark')">2: Dark</button>
    </div>

    <h2>Phase 2.5: Light Box Fix Verification</h2>
    <p style="color: #6b7280;">Press 1 for Light mode, 2 for Dark mode. In dark mode, ALL text should be WHITE.</p>
"""

    for i, slide in enumerate(slides):
        html += f"""
    <div class="slide-container">
        <div class="slide-label">{slide['variant_id']} - {slide['description']}</div>
        <div class="slide-content">
            {slide['html']}
        </div>
    </div>
"""

    html += """
    <script>
        function setTheme(mode) {
            if (mode === 'dark') {
                document.documentElement.classList.add('theme-dark');
                document.body.classList.add('theme-dark');
            } else {
                document.documentElement.classList.remove('theme-dark');
                document.body.classList.remove('theme-dark');
            }
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === '1') setTheme('light');
            if (e.key === '2') setTheme('dark');
        });
    </script>
</body>
</html>
"""

    with open(output_path, 'w') as f:
        f.write(html)

    return output_path

def main():
    print("=" * 60)
    print("PHASE 2.5: LIGHT BOX FIX VERIFICATION")
    print("=" * 60)

    results = []
    slides = []

    for variant_id, description in TEST_VARIANTS:
        print(f"\nTesting {variant_id}...")

        result = generate_slide(variant_id)

        if result and result.get("success"):
            html = result.get("html", "")
            check = check_css_variables(html, variant_id)
            check["description"] = description
            results.append(check)

            slides.append({
                "variant_id": variant_id,
                "description": description,
                "html": html
            })

            status = "PASS" if check["success"] else "FAIL"
            print(f"  {status}: --text-primary={check['--text-primary']}, --text-muted={check['--text-muted']}")
        else:
            print(f"  FAIL: Generation failed")
            results.append({
                "variant_id": variant_id,
                "description": description,
                "success": False,
                "error": "Generation failed"
            })

    # Summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results if r.get("success"))
    total = len(results)

    print(f"\nPassed: {passed}/{total}")

    for r in results:
        status = "PASS" if r.get("success") else "FAIL"
        print(f"  [{status}] {r['variant_id']}: {r.get('description', '')}")
        if not r.get("success") and "--text-muted" in r:
            print(f"         --text-muted found: {r['--text-muted']} occurrences")

    # Create preview HTML
    if slides:
        output_path = "tests/light_box_test_preview.html"
        create_preview_html(slides, output_path)
        print(f"\n{'=' * 60}")
        print(f"PREVIEW FILE CREATED")
        print(f"{'=' * 60}")
        print(f"Open: {output_path}")
        print(f"\nInstructions:")
        print(f"  1. Open the HTML file in a browser")
        print(f"  2. Press '1' for light mode, '2' for dark mode")
        print(f"  3. Verify ALL text turns WHITE in dark mode")

    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
