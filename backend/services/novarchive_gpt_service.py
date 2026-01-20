# backend/services/novarchive_gpt_service.py
# UTF-8, English only
# Integration with NovArchive Vinyl Records GPT

import os
import json
import base64
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class NovArchiveGPTService:
    """
    Service that uses OpenAI Vision API to analyze vinyl record images.
    Mimics the behavior of the NovArchive Vinyl Records GPT.
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
    
    def _encode_image(self, file_path: Path | str, raw_bytes: Optional[bytes] = None) -> str:
        """Encode image to base64."""
        if raw_bytes is not None:
            data = raw_bytes
        else:
            with open(file_path, "rb") as f:
                data = f.read()
        return base64.b64encode(data).decode("utf-8")
    
    def analyze_vinyl_record(
        self, 
        file_path: Optional[Path | str] = None,
        raw_bytes: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Analyze a vinyl record image using OpenAI Vision API.
        Returns structured metadata similar to NovArchive GPT.
        """
        if not self.enabled:
            return self._get_fallback_result()
        
        try:
            image_b64 = self._encode_image(file_path, raw_bytes) if file_path or raw_bytes else None
            if not image_b64:
                return self._get_fallback_result()
            
            # Prompt optimized for vinyl record analysis (similar to NovArchive GPT)
            prompt = """You are an expert in vinyl record identification and cataloging (NovArchive specialist).

Analyze this vinyl record image and extract ALL available information:

1. READ ALL TEXT: Extract every visible text on the label, cover, or sleeve (OCR).

2. EXTRACT STRUCTURED METADATA:
   - Artist/Performer name
   - Album/Release title
   - Record label name
   - Catalog number
   - Release year (if visible)
   - Country of release (if visible)
   - Format (LP, EP, 12", 7", etc.)
   - Matrix/runout codes (if visible)
   - Side indicators (A/B, 1/2, etc.)

3. IDENTIFY VISUAL FEATURES:
   - Label design/logo
   - Color scheme
   - Any distinctive markings
   - Condition indicators (if visible)

4. PROVIDE CONFIDENCE SCORE:
   - How certain are you about each extracted field (0.0-1.0)

Return ONLY valid JSON with this structure:
{
  "ocr_text": "all visible text as string",
  "metadata": {
    "artist": "string or null",
    "album": "string or null",
    "title": "string or null",
    "label": "string or null",
    "catalog_number": "string or null",
    "year": "integer or null",
    "country": "string or null",
    "format": "string or null",
    "matrix_info": "string or null",
    "side": "string or null"
  },
  "visual_features": {
    "label_design": "description or null",
    "colors": ["color1", "color2"] or null,
    "distinctive_markings": "description or null"
  },
  "confidence": 0.0-1.0,
  "notes": "any additional observations or null"
}"""
            
            messages = [
                {
                    "role": "system",
                    "content": "You are NovArchive Vinyl Records expert. Respond ONLY with valid JSON, no markdown, no explanations."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ]
            
            # P1-2: OpenAI Timeout + Fail-Fast
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",  # Using latest vision model
                    messages=messages,
                    temperature=0.2,
                    max_tokens=1000,
                    response_format={"type": "json_object"},
                    timeout=30.0  # 30 second timeout
                )
            except Exception as openai_error:
                # Handle OpenAI errors gracefully
                error_type = type(openai_error).__name__
                error_msg = str(openai_error)
                
                # Check for specific error types
                if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                    logger.warning(f"[OpenAI] Request timeout: {error_msg}")
                    return self._get_fallback_result("OpenAI API timeout (30s)")
                elif "429" in error_msg or "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
                    logger.warning(f"[OpenAI] Rate limit/quota exceeded: {error_msg}")
                    return self._get_fallback_result("OpenAI API rate limit/quota exceeded")
                elif "401" in error_msg or "invalid" in error_msg.lower():
                    logger.error(f"[OpenAI] Invalid API key or authentication error: {error_msg}")
                    return self._get_fallback_result("OpenAI API authentication failed")
                else:
                    logger.error(f"[OpenAI] Unexpected error: {error_type} - {error_msg}")
                    return self._get_fallback_result(f"OpenAI API error: {error_type}")
            
            raw_content = response.choices[0].message.content
            
            # Parse JSON response
            try:
                data = json.loads(raw_content)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return self._get_fallback_result()
            
            # Normalize response structure
            metadata = data.get("metadata", {})
            visual_features = data.get("visual_features", {})
            
            return {
                "status": "ok",
                "ocr_text": data.get("ocr_text", ""),
                "artist": metadata.get("artist"),
                "album": metadata.get("album") or metadata.get("title"),
                "title": metadata.get("title") or metadata.get("album"),
                "label": metadata.get("label"),
                "catalog_number": metadata.get("catalog_number"),
                "year": metadata.get("year"),
                "country": metadata.get("country"),
                "format": metadata.get("format") or "LP",
                "matrix_info": metadata.get("matrix_info"),
                "side": metadata.get("side"),
                "visual_features": visual_features,
                "confidence": float(data.get("confidence", 0.75)),
                "notes": data.get("notes"),
                "source": "novarchive_gpt"
            }
            
        except Exception as e:
            # Return fallback on any error
            return self._get_fallback_result(str(e))
    
    def _get_fallback_result(self, error: Optional[str] = None) -> Dict[str, Any]:
        """Return fallback result when OpenAI is unavailable or fails."""
        return {
            "status": "ok",
            "ocr_text": "",
            "artist": None,
            "album": None,
            "title": None,
            "label": None,
            "catalog_number": None,
            "year": None,
            "country": None,
            "format": "LP",
            "matrix_info": None,
            "side": None,
            "visual_features": {},
            "confidence": 0.5,
            "notes": error or "OpenAI API not available",
            "source": "fallback"
        }


# Global instance
novarchive_gpt_service = NovArchiveGPTService()




