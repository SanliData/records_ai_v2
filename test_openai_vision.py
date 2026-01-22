#!/usr/bin/env python3
"""
Test OpenAI Vision Pipeline with Real Image
Simulates vision analysis and generates archive payloads
"""

import os
import json
import base64
from pathlib import Path
from datetime import datetime
import uuid

# Image path
IMAGE_PATH = r"C:\Users\issan\Downloads\Gencer Hepozden adlı kişiden iCloud Fotoğrafları (1)\Gencer Hepozden adlı kişiden iCloud Fotoğrafları\IMG_0076.JPEG"

def encode_image(image_path):
    """Encode image to base64."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def analyze_with_openai(image_path):
    """
    Real OpenAI Vision API analysis.
    NO fallback - raises exception if API fails.
    """
    from openai import OpenAI
    import logging
    
    # Read API key from environment ONLY
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set")
    
    # Verify image exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    print(f"🔑 API key found: {api_key[:10]}...")
    print(f"📸 Loading image: {image_path}")
    
    client = OpenAI(api_key=api_key)
    image_b64 = encode_image(image_path)
    
    # System prompt
    system_prompt = "You are a vinyl record archivist AI. Extract metadata."
    
    # User prompt with instructions
    user_prompt = """Analyze this vinyl record image and extract all visible metadata.

Extract:
1. ALL visible text on the label (OCR) - put in ocr_text
2. artist: Performer/band name
3. album_title: Album name
4. label: Record label/company name
5. year: Release year (if visible)
6. genre: Music genre (if visible or can be inferred)
7. catalog_number: Catalog/release number (if visible)
8. country: Country code (if visible or guess from label)
9. format: LP/EP/Single/12"/7"/other
10. cover_color: Dominant colors visible on cover/label
11. confidence: Your confidence in the extraction (0.0-1.0)

Return ONLY valid JSON with this exact structure (use null for unknown fields):
{
  "ocr_text": "all visible text",
  "artist": "artist name or null",
  "album_title": "album name or null",
  "label": "label name or null",
  "year": "year or null",
  "genre": "genre or null",
  "catalog_number": "catalog number or null",
  "country": "country code or null",
  "format": "format type or null",
  "cover_color": "color description or null",
  "confidence": 0.0
}"""
    
    print("🚀 Calling OpenAI Vision API...")
    print(f"   Model: gpt-4.1")
    print(f"   System prompt: {system_prompt}")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.2,
            max_tokens=2000,
            response_format={"type": "json_object"}  # Force JSON response
        )
        
        # Log full response
        print("\n📋 Full API Response:")
        print(f"   Model used: {response.model}")
        print(f"   Usage: {response.usage}")
        print(f"   Finish reason: {response.choices[0].finish_reason}")
        print(f"\n📄 Raw content:")
        raw_content = response.choices[0].message.content
        print(raw_content)
        print()
        
        # Parse JSON response
        result = json.loads(raw_content)
        
        # Validate required fields exist
        required_fields = [
            "artist", "album_title", "label", "year", "genre",
            "catalog_number", "country", "format", "cover_color",
            "confidence", "ocr_text"
        ]
        
        missing_fields = [f for f in required_fields if f not in result]
        if missing_fields:
            print(f"⚠️  Warning: Missing fields in response: {missing_fields}")
        
        print("✅ OpenAI Vision analysis completed successfully")
        return result
        
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse JSON from OpenAI response: {e}\nRaw response: {raw_content if 'raw_content' in locals() else 'N/A'}"
        print(f"❌ {error_msg}")
        raise RuntimeError(error_msg) from e
    except Exception as e:
        error_msg = f"OpenAI API call failed: {type(e).__name__}: {str(e)}"
        print(f"❌ {error_msg}")
        raise RuntimeError(error_msg) from e

def build_preview_payload(analysis_result, image_path):
    """Build payload for POST /archive/preview"""
    record_id = str(uuid.uuid4())
    
    payload = {
        "image_path": image_path,
        "record_id": record_id,
        "artist": analysis_result.get("artist") or "unknown",
        "album_title": analysis_result.get("album_title") or analysis_result.get("album") or "unknown",
        "label": analysis_result.get("label") or "unknown",
        "genre": analysis_result.get("genre") or "unknown",
        "year": analysis_result.get("year") or "unknown",
        "condition": analysis_result.get("condition") or "unknown",
        "confidence": float(analysis_result.get("confidence", 0.5)),
        "format": analysis_result.get("format") or "LP",
        "catalog_number": analysis_result.get("catalog_number") or "unknown",
        "country": analysis_result.get("country") or "unknown",
        "cover_color": analysis_result.get("cover_color") or "unknown",
        "ocr_text": analysis_result.get("ocr_text", ""),
    }
    
    return payload

def build_archive_add_payload(preview_payload):
    """Build payload for POST /archive/add"""
    
    # Generate a record_id if not present
    record_id = preview_payload.get("record_id") or str(uuid.uuid4())
    
    payload = {
        "record_id": record_id,
        "artist": preview_payload.get("artist", "unknown"),
        "album": preview_payload.get("album_title", "unknown"),
        "title": preview_payload.get("album_title", "unknown"),
        "label": preview_payload.get("label", "unknown"),
        "genre": preview_payload.get("genre", "unknown"),
        "year": preview_payload.get("year", "unknown"),
        "condition": preview_payload.get("condition", "unknown"),
        "format": preview_payload.get("format", "LP"),
        "catalog_number": preview_payload.get("catalog_number", "unknown"),
        "country": preview_payload.get("country", "unknown"),
        "cover_color": preview_payload.get("cover_color", "unknown"),
        "confidence": preview_payload.get("confidence", 0.5),
        "ocr_text": preview_payload.get("ocr_text", ""),
        "file_path": preview_payload.get("image_path", ""),
        "image_path": preview_payload.get("image_path", ""),
        "is_preview": False,
        "is_archived": True,
    }
    
    return payload

def main():
    import sys
    import io
    
    # Set UTF-8 encoding for stdout
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("=" * 80)
    print("OpenAI Vision Pipeline Test")
    print("=" * 80)
    print(f"Image: {IMAGE_PATH}")
    print()
    
    # Step 1: Load and analyze image
    print("Step 1: Loading image and running vision analysis...")
    try:
        analysis_result = analyze_with_openai(IMAGE_PATH)
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        sys.exit(1)
    print()
    
    # Step 2: Build preview payload
    print("Step 2: Building preview payload...")
    preview_payload = build_preview_payload(analysis_result, IMAGE_PATH)
    print()
    
    # Step 3: Build archive add payload
    print("Step 3: Building archive/add payload...")
    archive_payload = build_archive_add_payload(preview_payload)
    print()
    
    # Print both payloads
    print("=" * 80)
    print("PAYLOAD 1: POST /archive/preview")
    print("=" * 80)
    print(json.dumps(preview_payload, indent=2, ensure_ascii=False))
    print()
    
    print("=" * 80)
    print("PAYLOAD 2: POST /archive/add")
    print("=" * 80)
    print(json.dumps(archive_payload, indent=2, ensure_ascii=False))
    print()
    
    print("=" * 80)
    print("Test completed")
    print("=" * 80)

if __name__ == "__main__":
    main()
