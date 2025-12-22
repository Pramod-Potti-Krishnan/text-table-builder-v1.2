#!/usr/bin/env python3
import sys
import os
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core import ElementBasedContentGenerator
from app.services import create_llm_callable

LAYOUT_SERVICE_URL = "https://web-production-f0d13.up.railway.app"

def main():
    llm_callable = create_llm_callable()
    generator = ElementBasedContentGenerator(
        llm_service=llm_callable,
        variant_specs_dir="app/variant_specs",
        templates_dir="app/templates"
    )
    
    print("Generating Impact Quote with updated formatting...")
    
    slide_spec = {
        "slide_title": "Impact Quote - Final Version",
        "slide_purpose": "Customer success story with blue border and corner quotes",
        "key_message": "Attribution extends within border without grey box",
        "tone": "professional",
        "audience": "stakeholders"
    }
    
    result = generator.generate_slide_content(
        variant_id="impact_quote",
        slide_spec=slide_spec
    )
    
    slide = {
        "layout": "L25",
        "content": {
            "slide_title": "Impact Quote - Final Platinum Version",
            "subtitle": "Variant: impact_quote",
            "rich_content": result["html"],
            "presentation_name": "v1.2 Impact Quote - Final Review",
            "logo": ""
        }
    }
    
    presentation = {
        "title": "Impact Quote - Final Platinum Version",
        "slides": [slide]
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
        print(f"\n✅ Impact Quote Generated Successfully!")
        print(f"\n🌐 VIEW URL:")
        print(f"   {view_url}\n")
    else:
        print(f"\n✗ Failed: {response.status_code}")

if __name__ == "__main__":
    main()
