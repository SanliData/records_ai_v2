# backend/services/openai_label_service.py
# UTF-8, English only
# Core OpenAI Vision service for vinyl record label extraction
# Cost-optimized with image hash cache

import os
import json
import base64
import hashlib
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
    
    Cost optimizations:
    - Image hash cache (skip OpenAI if already processed)
    - Default: gpt-4o-mini (cheapest)
    - Escalate to gpt-4o only if confidence < 0.6
    - Short prompt, max_tokens=150, temperature=0
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
        
        # Cache setup
        self.cache_dir = Path(__file__).parent.parent.parent / "storage" / "openai_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "image_hash_cache.json"
        self._cache = self._load_cache()
        
        # Model configuration
        self.default_model = "gpt-4o-mini"  # Cheapest
        self.escalation_model = "gpt-4o"    # More expensive, only if needed
        self.confidence_threshold = 0.6       # Escalate if below this
    
    def _load_cache(self) -> Dict[str, Dict[str, Any]]:
        """Load cache from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to disk."""
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def _hash_image(self, image_bytes: bytes) -> str:
        """Generate SHA-256 hash of image bytes."""
        return hashlib.sha256(image_bytes).hexdigest()
    
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
        Uses image hash cache to avoid duplicate API calls.
        
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
                "error": Optional[str],
                "cached": bool
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
                "confidence": 0.0,
                "cached": False
            }
        
        # Check cache first
        image_hash = self._hash_image(image_bytes)
        if image_hash in self._cache:
            logger.info(f"Cache hit for image hash: {image_hash[:16]}...")
            cached_result = self._cache[image_hash].copy()
            cached_result["cached"] = True
            return cached_result
        
        # Cache miss - call OpenAI
        logger.info(f"Cache miss for image hash: {image_hash[:16]}... - calling OpenAI")
        
        try:
            # Short prompt (cost optimization)
            prompt = """Extract JSON: {"artist": "name", "album": "title", "label": "label", "year": 1980, "catalog_number": "cat#", "format": "LP"}. Return ONLY JSON, no text."""
            
            # Try with default model (cheapest)
            model = self.default_model
            result = self._call_openai(image_bytes, mime_type, prompt, model)
            
            # Check confidence - escalate if low
            confidence = result.get("confidence", 0.0)
            if confidence < self.confidence_threshold:
                logger.info(f"Low confidence ({confidence}) - escalating to {self.escalation_model}")
                result = self._call_openai(image_bytes, mime_type, prompt, self.escalation_model)
                confidence = result.get("confidence", 0.0)
            
            # Store in cache
            result["cached"] = False
            self._cache[image_hash] = result.copy()
            self._save_cache()
            
            logger.info(f"OpenAI analysis successful: {result.get('artist')} - {result.get('album')} (confidence: {confidence})")
            return result
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            logger.error(f"OpenAI API error ({error_type}): {error_msg}")
            return self._get_error_response(error_type, error_msg)
    
    def _call_openai(
        self,
        image_bytes: bytes,
        mime_type: str,
        prompt: str,
        model: str
    ) -> Dict[str, Any]:
        """Call OpenAI Vision API with optimized settings."""
        base64_image = self._encode_image(image_bytes)
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
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
            max_tokens=150,  # Cost optimization
            temperature=0,   # Deterministic, cost optimization
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
            "confidence": 0.85 if model == self.default_model else 0.95,  # Higher confidence for escalation model
            "error": None,
            "model_used": model
        }
        
        return normalized
            
    def _get_error_response(self, error_type: str, error_msg: str) -> Dict[str, Any]:
        """Generate standardized error response."""
        base_response = {
            "artist": None,
            "album": None,
            "label": None,
            "year": None,
            "catalog_number": None,
            "format": None,
            "confidence": 0.0,
            "cached": False
        }
        
        if "JSONDecodeError" in error_type or "json" in error_msg.lower():
            base_response["error"] = f"Invalid JSON response from OpenAI: {error_msg}"
        elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
            base_response["error"] = "OpenAI API timeout (30s)"
        elif "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
            base_response["error"] = "OpenAI API rate limit/quota exceeded"
        elif "authentication" in error_msg.lower() or "api key" in error_msg.lower():
            base_response["error"] = "OpenAI API authentication failed - check OPENAI_API_KEY"
        else:
            base_response["error"] = f"OpenAI API error: {error_type} - {error_msg}"
        
        return base_response


# Singleton instance
openai_label_service = OpenAILabelService()
