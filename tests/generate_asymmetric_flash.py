#!/usr/bin/env python3
"""
Generate All Asymmetric Templates - Flash Model Only
"""
import sys
import os
import requests
from pathlib import Path

# Disable model routing via environment variable
os.environ["ENABLE_MODEL_ROUTING"] = "false"

sys.path.insert(0, str(Path(__file__).parent))

from app.core import ElementBasedContentGenerator
from app.services import create_llm_callable

LAYOUT_SERVICE_URL = "https://web-production-f0d13.up.railway.app"

ASYMMETRIC_VARIANTS = {
    "asymmetric_8_4_3section": "Asymmetric 8:4 - 3 Sections + Sidebar",
    "asymmetric_8_4_4section": "Asymmetric 8:4 - 4 Sections + Sidebar",
    "asymmetric_8_4_5section": "Asymmetric 8:4 - 5 Sections + Sidebar"
}

def main():
    print("=" * 80)
    print("ASYMMETRIC TEMPLATES - Flash Model Only (Model Routing Disabled)")
    print("=" * 80)
    
    llm_callable = create_llm_callable()
    generator = ElementBasedContentGenerator(
        llm_service=llm_callable,
        variant_specs_dir="app/variant_specs",
        templates_dir="app/templates"
    )
    
    slides = []
    
    for i, (variant_id, description) in enumerate(ASYMMETRIC_VARIANTS.items(), 1):
        print(f"\n[{i}/3] Generating: {variant_id}")
        
        slide_spec = {
            "slide_title": description,
            "slide_purpose": f"Visual review of {variant_id} layout",
            "key_message": "Asymmetric layout with main sections and sidebar",
            "tone": "professional",
            "audience": "stakeholders"
        }
        
        try:
            result = generator.generate_slide_content(
                variant_id=variant_id,
                slide_spec=slide_spec
            )
            
            slide = {
                "layout": "L25",
                "content": {
                    "slide_title": description,
                    "subtitle": f"Variant: {variant_id}",
                    "rich_content": result["html"],
                    "presentation_name": "Asymmetric Templates Review",
                    "logo": ""
                }
            }
            
            slides.append(slide)
            print(f"    ✓ Generated successfully")
            
        except Exception as e:
            print(f"    ✗ Error: {str(e)[:200]}")
    
    if not slides:
        print("\n❌ No slides generated - model access issue prevents generation")
        print("⚠️  The asymmetric templates require Gemini 1.5 Pro which is not accessible")
        print("💡 Alternative: We can show you the template HTML structure and specs instead")
        return
    
    # Post to Railway
    print("\n" + "=" * 80)
    print(f"Posting {len(slides)} templates to Railway...")
    print("=" * 80)
    
    presentation = {
        "title": "Asymmetric Templates - Block by Block Review",
        "slides": slides
    }
    
    response = requests.post(
        f"{LAYOUT_SERVICE_URL}/api/presentations",
        json=presentation,
        headers={"Content-Type": "application/json"},
        timeout=60
    )
    
    if response.status_code in [200, 201]:
        data = response.json()
        presentation_id = data.get("id")
        url_path = data.get("url", f"/p/{presentation_id}")
        view_url = f"{LAYOUT_SERVICE_URL}{url_path}"
        
        print("\n" + "=" * 80)
        print("✅ SUCCESS! Asymmetric Templates Published")
        print("=" * 80)
        print(f"\n🌐 VIEW URL:")
        print(f"   {view_url}")
        print(f"\nGenerated: {len(slides)}/3 templates")
        print("\n" + "=" * 80)
    else:
        print(f"\n❌ Failed: {response.status_code}")

if __name__ == "__main__":
    main()
