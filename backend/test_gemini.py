#!/usr/bin/env python3
"""Test script to verify Gemini API is working"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import asyncio
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def test_gemini():
    print("="*60)
    print("Testing Gemini API Connection")
    print("="*60)

    # Check API key
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not found in environment")
        print("   Please set it in backend/.env")
        return False

    print(f"✓ API Key found: {GEMINI_API_KEY[:10]}...")

    # Configure Gemini
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("✓ Gemini configured successfully")
    except Exception as e:
        print(f"❌ Failed to configure Gemini: {e}")
        return False

    # List available models
    try:
        print("\nAvailable models:")
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"  - {model.name}")
    except Exception as e:
        print(f"❌ Failed to list models: {e}")

    # Try generating content
    try:
        print("\nTesting content generation...")
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = """You are a HAZOP analyst. For a centrifugal pump with deviation "No Flow",
        suggest 3 possible causes. Return as JSON array:
        [{"text": "cause description", "confidence": 85}]"""

        response = model.generate_content(prompt)
        print("✓ Response received:")
        print(f"  {response.text[:200]}...")

        return True

    except Exception as e:
        print(f"❌ Failed to generate content: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_gemini())
    sys.exit(0 if success else 1)
