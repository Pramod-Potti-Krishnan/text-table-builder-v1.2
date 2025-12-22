#!/usr/bin/env python3
"""
Regenerate 4 Updated Templates for Final Review
"""
import sys
import os
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core import ElementBasedContentGenerator
from app.services import create_llm_callable

LAYOUT_SERVICE_URL = "https://web-production-f0d13.up.railway.app"

VARIANTS = {
    "matrix_2x2": "Matrix 2×2 - Updated Description Font",
    "matrix_2x3": "Matrix 2×3 - Updated Title & Font",
    "metrics_2x2_grid": "Metrics 2×2 - Top Aligned with Insights Box",
    "impact_quote": "Impact Quote - Blue Border with Corner Quotes"
}

def main():
    project_id = os.getenv("GCP_PROJECT_ID", "deckster-xyz")
    print(f"Using GCP Project: {project_id}")
    
    llm_callable = create_llm_callable()
    generator = ElementBasedContentGenerator(
        llm_service=llm_callable,
        variant_specs_dir="app/variant_specs",
        templates_dir="app/templates"
    )
    
    slides = []
    
    for variant_id, description in VARIANTS.items():
        print(f"\nGenerating: {variant_id}")
        
        slide_spec = {
            "slide_title": description,
            "slide_purpose": f"Final review of {variant_id} with updated formatting",
            "key_message": "Visual validation of template updates based on user feedback",
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
                    "presentation_name": "v1.2 Final Template Review",
                    "logo": ""
                }
            }
            
            slides.append(slide)
            print(f"✓ Generated successfully")
            
        except Exception as e:
            print(f"✗ Error: {e}")
    
    # Post to layout service
    presentation = {
        "title": "v1.2 Final Template Review - 4 Updated Templates",
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
        view_url = f"{LAYOUT_SERVICE_URL}{data.get('url', f'/p/{presentation_id}')}"
        
        print("\n" + "="*80)
        print("✅ SUCCESS! Templates Ready for Final Review")
        print("="*80)
        print(f"\n🌐 VIEW URL:")
        print(f"   {view_url}")
        print("\n" + "="*80)
    else:
        print(f"\n✗ Failed: {response.status_code}")
        print(response.text[:500])

if __name__ == "__main__":
    main()
