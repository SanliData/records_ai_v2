# backend/services/openai_label_service.py
# UTF-8, English only
# Core OpenAI Vision service for vinyl record label extraction

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
    logger.warning("OpenAI SDK not available - install with: pip install openai")


class OpenAILabelService:
    """
    Core OpenAI Vision service for extracting vinyl record metadata.
    This is the CENTRAL brain of the pipeline.
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            self.enabled = True
            logger.info("OpenAILabelService initialized with API key")
        else:
            self.client = None
            self.enabled = False
            if not OPENAI_AVAILABLE:
                logger.warning("OpenAI SDK not available")
            elif not self.api_key:
                logger.warning("OPENAI_API_KEY not set - service disabled")
    
    def _encode_image(self, image_bytes: bytes) -> str:
        """Encode image bytes to base64."""
        return base64.b64encode(image_bytes).decode("utf-8")
    
    def analyze_image(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """
        Analyze vinyl record image using OpenAI Vision API.
        
        Args:
            image_bytes: Raw image bytes
            mime_type: MIME type of image (image/jpeg, image/png, etc.)
        
        Returns:
            {
                "artist": str,
                "album": str,
                "label": str,
                "year": Optional[int],
                "catalog_number": Optional[str],
                "format": Optional[str],
                "confidence": float,
                "error": Optional[str]
            }
        """
        if not self.enabled:
            return {
                "error": "OpenAI service not available - check OPENAI_API_KEY",
                "artist": None,
                "album": None,
                "label": None,
                "year": None,
                "catalog_number": None,
                "format": None,
                "confidence": 0.0
            }
        
        try:
            # Encode image to base64
            base64_image = self._encode_image(image_bytes)
            
            # Prepare prompt for structured extraction
            prompt = """Analyze this vinyl record image and extract the following information in JSON format:

{
    "artist": "Artist name",
    "album": "Album/title name",
    "label": "Record label name",
    "year": 1980,
    "catalog_number": "Catalog number if visible",
    "format": "LP, 7\", 12\", etc. if visible"
}

Rules:
- Return ONLY valid JSON, no markdown, no explanations
- If a field is not visible, use null
- Year must be a number or null
- Be precise and accurate
- Focus on text visible on the label/cover"""
            
            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=500,
                timeout=30.0
            )
            
            # Parse response
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # Normalize response structure
            normalized = {
                "artist": result.get("artist"),
                "album": result.get("album"),
                "label": result.get("label"),
                "year": result.get("year"),
                "catalog_number": result.get("catalog_number"),
                "format": result.get("format", "LP"),
                "confidence": 0.9,  # High confidence for structured extraction
                "error": None
            }
            
            logger.info(f"OpenAI analysis successful: {normalized.get('artist')} - {normalized.get('album')}")
            return normalized
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI JSON response: {e}")
            return {
                "error": f"Invalid JSON response from OpenAI: {str(e)}",
                "artist": None,
                "album": None,
                "label": None,
                "year": None,
                "catalog_number": None,
                "format": None,
                "confidence": 0.0
            }
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            logger.error(f"OpenAI API error ({error_type}): {error_msg}")
            
            # Handle specific error types
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                return {
                    "error": "OpenAI API timeout (30s)",
                    "artist": None,
                    "album": None,
                    "label": None,
                    "year": None,
                    "catalog_number": None,
                    "format": None,
                    "confidence": 0.0
                }
            elif "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
                return {
                    "error": "OpenAI API rate limit/quota exceeded",
                    "artist": None,
                    "album": None,
                    "label": None,
                    "year": None,
                    "catalog_number": None,
                    "format": None,
                    "confidence": 0.0
                }
            elif "authentication" in error_msg.lower() or "api key" in error_msg.lower():
                return {
                    "error": "OpenAI API authentication failed - check OPENAI_API_KEY",
                    "artist": None,
                    "album": None,
                    "label": None,
                    "year": None,
                    "catalog_number": None,
                    "format": None,
                    "confidence": 0.0
                }
            else:
                return {
                    "error": f"OpenAI API error: {error_type} - {error_msg}",
                    "artist": None,
                    "album": None,
                    "label": None,
                    "year": None,
                    "catalog_number": None,
                    "format": None,
                    "confidence": 0.0
                }


# Singleton instance
openai_label_service = OpenAILabelService()
