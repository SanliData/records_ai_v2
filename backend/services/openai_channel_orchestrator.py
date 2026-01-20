# backend/services/openai_channel_orchestrator.py
# UTF-8, English only
# OpenAI-powered multi-channel sales publishing orchestrator

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI SDK not available - install with: pip install openai")


class OpenAIChannelOrchestrator:
    """
    OpenAI-powered orchestrator for multi-channel sales publishing.
    
    Flow:
    1. Record already archived
    2. Send record to OpenAI
    3. OpenAI decides: platforms, titles, descriptions, prices
    4. System prepares publishing (requires user approval)
    5. Return result report
    
    Cost optimizations:
    - Uses gpt-4o-mini (cheapest)
    - Short prompt
    - max_tokens <= 150
    - temperature = 0
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            self.enabled = True
            logger.info("OpenAIChannelOrchestrator initialized with API key")
        else:
            self.client = None
            self.enabled = False
            if not OPENAI_AVAILABLE:
                logger.warning("OpenAI SDK not available")
            elif not self.api_key:
                logger.warning("OPENAI_API_KEY not set - service disabled")
        
        # Model configuration
        self.model = "gpt-4o-mini"  # Cheapest model
    
    def orchestrate_publishing(
        self,
        record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use OpenAI to decide publishing strategy for archived record.
        
        Args:
            record: Archived record with metadata (artist, album, label, year, etc.)
        
        Returns:
            {
                "platforms": [
                    {
                        "platform": "ebay|discogs|shopify|etsy",
                        "title": str,
                        "description": str,
                        "price": float,
                        "currency": "USD",
                        "category": str,
                        "tags": List[str],
                        "recommended": bool
                    }
                ],
                "strategy": {
                    "primary_platform": str,
                    "pricing_strategy": str,
                    "reasoning": str
                },
                "error": Optional[str]
            }
        """
        if not self.enabled:
            return {
                "error": "OpenAI service not available - check OPENAI_API_KEY",
                "platforms": [],
                "strategy": {}
            }
        
        try:
            # Prepare short prompt (cost optimization)
            prompt = self._build_prompt(record)
            
            # Call OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a vinyl record sales expert. Return ONLY valid JSON, no markdown."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=150,  # Cost optimization
                temperature=0,   # Deterministic
                timeout=30.0
            )
            
            # Parse response
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # Normalize response
            normalized = {
                "platforms": result.get("platforms", []),
                "strategy": result.get("strategy", {}),
                "error": None,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"OpenAI orchestration successful for: {record.get('artist')} - {record.get('album')}")
            return normalized
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI JSON response: {e}")
            return {
                "error": f"Invalid JSON response from OpenAI: {str(e)}",
                "platforms": [],
                "strategy": {}
            }
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            logger.error(f"OpenAI API error ({error_type}): {error_msg}")
            return {
                "error": f"OpenAI API error: {error_type} - {error_msg}",
                "platforms": [],
                "strategy": {}
            }
    
    def _build_prompt(self, record: Dict[str, Any]) -> str:
        """Build short prompt for OpenAI (cost optimization)."""
        artist = record.get("artist", "Unknown")
        album = record.get("album") or record.get("title", "Unknown")
        label = record.get("label", "Unknown")
        year = record.get("year") or record.get("release_year")
        catalog_number = record.get("catalog_number")
        condition = record.get("condition", "VG+")
        
        prompt = f"""Vinyl record: {artist} - {album} ({label}, {year or 'Unknown'}, {catalog_number or 'N/A'}), Condition: {condition}

Decide publishing strategy. Return JSON:
{{
  "platforms": [
    {{"platform": "ebay|discogs|shopify|etsy", "title": "optimized title", "description": "short description", "price": 25.00, "currency": "USD", "category": "Vinyl", "tags": ["tag1", "tag2"], "recommended": true}}
  ],
  "strategy": {{"primary_platform": "platform", "pricing_strategy": "strategy", "reasoning": "brief reason"}}
}}

Rules:
- Choose 1-4 platforms based on record value/rarity
- Optimize titles per platform (eBay: SEO, Discogs: accurate, Shopify: brand, Etsy: vintage)
- Price competitively
- Return ONLY JSON"""
        
        return prompt


# Singleton instance
openai_channel_orchestrator = OpenAIChannelOrchestrator()
