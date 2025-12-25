#!/usr/bin/env python3
"""
Direct test of Image Builder API to see response format.
"""

import httpx
import json
import asyncio

async def test_direct():
    async with httpx.AsyncClient(timeout=120.0) as client:
        payload = {
            "prompt": "Professional presentation background, modern corporate style",
            "aspect_ratio": "16:9",
            "options": {
                "store_in_cloud": True
            }
        }

        response = await client.post(
            "https://web-production-1b5df.up.railway.app/api/v2/generate",
            json=payload
        )

        print(f"Status: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    asyncio.run(test_direct())
