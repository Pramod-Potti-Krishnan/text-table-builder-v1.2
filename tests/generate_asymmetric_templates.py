#!/usr/bin/env python3
"""
Generate All Asymmetric Templates for Review
"""
import sys
import os
import requests
from pathlib import Path

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
    print("ASYMMETRIC TEMPLATES - Block by Block Review")
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
            "slide_purpose": f"Visual review of {variant_id} layout and content",
            "key_message": "Asymmetric layout with main content sections and sidebar",
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
                    "company_logo": ""
                }
            }
            
            slides.append(slide)
            print(f"    ✓ Generated successfully ({len(result['html'])} chars)")
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    if not slides:
        print("\n❌ No slides generated")
        return
    
    # Post to Railway
    print("\n" + "=" * 80)
    print(f"Posting {len(slides)} Asymmetric Templates to Railway...")
    print("=" * 80)
    
    presentation = {
        "title": "Asymmetric Templates - Block by Block Review",
        "slides": slides
    }
    
    response = requests.post(
        f"{LAYOUT_SERVICE_URL}/api/presentations",
        json=presentation,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if response.status_code in [200, 201]:
        data = response.json()
        presentation_id = data.get("id")
        url_path = data.get("url", f"/p/{presentation_id}")
        view_url = f"{LAYOUT_SERVICE_URL}{url_path}"
        
        print("\n" + "=" * 80)
        print("✅ SUCCESS! Asymmetric Templates Published")
        print("=" * 80)
        print(f"\nPresentation ID: {presentation_id}")
        print(f"Templates Generated: {len(slides)}/3")
        print(f"\n🌐 VIEW URL:")
        print(f"   {view_url}")
        print("\n" + "=" * 80)
        print("\n📋 Review Instructions:")
        print("   1. Navigate through all 3 asymmetric layouts")
        print("   2. Check section content meets character counts")
        print("   3. Verify sidebar content is appropriate")
        print("   4. Review visual balance and formatting")
        print("   5. Provide feedback for any needed adjustments")
        print("\n" + "=" * 80)
    else:
        print(f"\n❌ Failed to publish: {response.status_code}")
        print(f"Response: {response.text[:500]}")

if __name__ == "__main__":
    main()
