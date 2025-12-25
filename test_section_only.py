#!/usr/bin/env python3
"""
Test only the improved section divider slide.
"""

import httpx
import json
import asyncio
from pathlib import Path

BASE_URL = "http://localhost:8100"
OUTPUT_DIR = Path("test_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


async def test_section_slide():
    """Test improved section divider with smart prompts and modern design."""
    print("\n" + "=" * 80)
    print("Testing IMPROVED Section Divider")
    print("=" * 80)

    payload = {
        "slide_number": 5,
        "slide_type": "section_divider",
        "narrative": "Implementation strategy for AI-powered diagnostic systems in clinical settings",
        "topics": ["Implementation", "Deployment", "Integration", "Training"],
        "context": {
            "theme": "professional",
            "audience": "healthcare IT executives"
        }
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/v1.2/hero/section-with-image",
            json=payload
        )

        result = response.json()

        # Save response
        with open(OUTPUT_DIR / "section_improved_response.json", "w") as f:
            json.dump(result, f, indent=2)

        # Save HTML
        if "content" in result:
            with open(OUTPUT_DIR / "section_improved.html", "w") as f:
                f.write(result["content"])

        # Print summary
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Slide Type: {result.get('metadata', {}).get('slide_type')}")
        print(f"✓ Background Image: {result.get('metadata', {}).get('background_image')}")
        print(f"✓ Fallback to Gradient: {result.get('metadata', {}).get('fallback_to_gradient')}")
        print(f"✓ Image Gen Time: {result.get('metadata', {}).get('image_generation_time_ms')}ms")
        print(f"✓ HTML Length: {len(result.get('content', ''))} chars")
        print(f"\n✓ Files saved:")
        print(f"  - {OUTPUT_DIR}/section_improved_response.json")
        print(f"  - {OUTPUT_DIR}/section_improved.html")

        if result.get('metadata', {}).get('background_image'):
            print(f"\n✓ Background Image URL:")
            print(f"  {result['metadata']['background_image']}")

        return result


async def create_preview_html():
    """Create a simple preview HTML."""
    print("\n" + "=" * 80)
    print("Creating Preview HTML")
    print("=" * 80)

    # Read the generated HTML
    section_html = (OUTPUT_DIR / "section_improved.html").read_text()

    # Read the JSON response to get background image
    with open(OUTPUT_DIR / "section_improved_response.json") as f:
        section_data = json.load(f)

    section_bg = section_data.get('metadata', {}).get('background_image')

    # Create preview page
    preview_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Improved Section Divider Preview</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: #1a1a1a;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: 'Inter', sans-serif;
        }}
        .slide-container {{
            width: 1920px;
            height: 1080px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            background-color: #000;
            background-image: url('{section_bg}');
            background-size: cover;
            background-position: center;
        }}
        .slide-label {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(102, 110, 234, 0.9);
            color: white;
            padding: 10px 20px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            z-index: 1000;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="slide-label">
            {'AI Background ✓ | Standard Model' if section_bg else 'Gradient Fallback'}
        </div>
        {section_html}
    </div>
</body>
</html>
"""

    # Save preview HTML
    preview_path = OUTPUT_DIR / "section_improved_preview.html"
    preview_path.write_text(preview_html)

    print(f"✓ Preview HTML created: {preview_path}")
    print(f"\nOpen in browser: file://{preview_path.absolute()}")

    return preview_path


async def main():
    """Run test."""
    print("\n" + "=" * 80)
    print("IMPROVED SECTION DIVIDER - LOCAL TESTING")
    print("=" * 80)

    try:
        # Test section slide
        await test_section_slide()

        # Create preview page
        preview_path = await create_preview_html()

        print("\n" + "=" * 80)
        print("✅ TEST COMPLETE!")
        print("=" * 80)
        print(f"\nOpen the preview: file://{preview_path.absolute()}")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())
