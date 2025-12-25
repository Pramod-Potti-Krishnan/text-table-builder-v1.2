"""
Quick Test: Generate Examples of All Three Visual Styles

Generates title slides for each style to showcase the differences:
- Professional (photorealistic)
- Illustrated (Ghibli-style)
- Kids (vibrant & playful)
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.hero.title_slide_with_image_generator import TitleSlideWithImageGenerator
from app.core.hero.base_hero_generator import HeroGenerationRequest
from app.services.llm_service import get_llm_service


async def generate_style_example(visual_style: str, llm_service):
    """Generate a single title slide example for a visual style."""

    print(f"\n{'='*60}")
    print(f"Generating {visual_style.upper()} style example...")
    print(f"{'='*60}")

    generator = TitleSlideWithImageGenerator(llm_service)

    request = HeroGenerationRequest(
        slide_number=1,
        slide_type="title_slide",
        narrative="Transforming healthcare through AI-powered diagnostic accuracy",
        topics=["AI", "Healthcare", "Diagnostics", "Innovation"],
        visual_style=visual_style,
        context={
            "theme": "professional",
            "audience": "healthcare executives",
            "presentation_title": "AI in Healthcare"
        }
    )

    try:
        result = await generator.generate(request)

        # Extract metadata
        metadata = result.get("metadata", {})
        background_image = metadata.get("background_image")
        content = result["content"]

        # Create preview HTML
        preview_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{visual_style.upper()} Style Example</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: #1a1a1a;
            font-family: 'Inter', sans-serif;
            color: white;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 2.5rem;
            margin: 0 0 10px 0;
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .header p {{
            font-size: 1.2rem;
            color: #888;
            margin: 0;
        }}
        .slide-container {{
            width: 1920px;
            height: 1080px;
            max-width: 100%;
            margin: 0 auto;
            position: relative;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            background-color: #000;
            background-image: url('{background_image if background_image else ""}');
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
        .info-box {{
            max-width: 1920px;
            margin: 30px auto;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            border-left: 4px solid #00d9ff;
        }}
        .info-box h3 {{
            margin: 0 0 10px 0;
            color: #00d9ff;
        }}
        .info-box p {{
            margin: 5px 0;
            color: #ccc;
        }}
        .info-box code {{
            background: rgba(0, 0, 0, 0.3);
            padding: 2px 6px;
            border-radius: 3px;
            color: #4facfe;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{visual_style.upper()} Style</h1>
        <p>AI-Generated Background with Style-Aware Prompting</p>
    </div>

    <div class="slide-container">
        <div class="slide-label">
            {visual_style.upper()} Style
        </div>
        {content}
    </div>

    <div class="info-box">
        <h3>Style Configuration</h3>
        <p><strong>Visual Style:</strong> {visual_style}</p>
        <p><strong>Background Image:</strong> {'Generated ✓' if background_image else 'Fallback to gradient'}</p>
        <p><strong>Image Model:</strong> <code>{'imagen-3.0-generate-001' if visual_style == 'professional' else 'imagen-3.0-fast-generate-001'}</code></p>
        <p><strong>Archetype:</strong> <code>{'photorealistic' if visual_style == 'professional' else 'spot_illustration'}</code></p>
        <p><strong>Cost:</strong> {'$0.04 (~10s)' if visual_style == 'professional' else '$0.02 (~5s)'}</p>
    </div>
</body>
</html>"""

        # Save preview
        os.makedirs("test_outputs", exist_ok=True)
        preview_path = f"test_outputs/example_{visual_style}.html"
        with open(preview_path, "w") as f:
            f.write(preview_html)

        print(f"✅ Generated successfully!")
        print(f"   Background image: {'YES' if background_image else 'FALLBACK'}")
        print(f"   Preview saved: {preview_path}")

        return {
            "style": visual_style,
            "success": True,
            "has_image": bool(background_image),
            "preview": preview_path
        }

    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        return {
            "style": visual_style,
            "success": False,
            "error": str(e)
        }


async def main():
    """Generate examples of all three visual styles."""

    print("\n" + "="*60)
    print("VISUAL STYLE EXAMPLES GENERATOR")
    print("="*60)
    print("Generating title slides for all three styles...")
    print()

    llm_service = await get_llm_service()

    styles = ["professional", "illustrated", "kids"]
    results = []

    for style in styles:
        result = await generate_style_example(style, llm_service)
        results.append(result)

    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)

    for result in results:
        if result["success"]:
            print(f"✅ {result['style'].upper()}: {result['preview']}")
        else:
            print(f"❌ {result['style'].upper()}: Failed - {result.get('error', 'Unknown error')}")

    print("\nOpen the HTML files in your browser to see the results!")


if __name__ == "__main__":
    asyncio.run(main())
