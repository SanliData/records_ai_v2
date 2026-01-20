# backend/services/commerce/auto_pricing_service.py
# UTF-8, English only
# OpenAI-powered auto pricing service

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
    logger.warning("OpenAI SDK not available")


class AutoPricingService:
    """
    OpenAI-powered auto pricing service.
    
    Runs nightly to optimize prices based on:
    - Competitor prices
    - Sales velocity
    - Market trends
    - Record condition/rarity
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            self.enabled = True
            logger.info("AutoPricingService initialized with API key")
        else:
            self.client = None
            self.enabled = False
        
        self.model = "gpt-4o-mini"  # Cheapest model
    
    def optimize_prices(
        self,
        records: List[Dict[str, Any]],
        competitor_prices: Optional[Dict[str, Dict[str, float]]] = None,
        sales_metrics: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Optimize prices for multiple records using OpenAI.
        
        Args:
            records: List of records with current pricing
            competitor_prices: Optional competitor price data (record_id -> platform -> price)
            sales_metrics: Optional sales metrics (views, clicks, time_on_market, etc.)
        
        Returns:
            {
                "recommendations": [
                    {
                        "record_id": str,
                        "current_price": float,
                        "recommended_price": float,
                        "reasoning": str,
                        "strategy": str
                    }
                ],
                "summary": {
                    "total_records": int,
                    "price_increases": int,
                    "price_decreases": int,
                    "no_change": int
                }
            }
        """
        if not self.enabled:
            return {
                "error": "OpenAI service not available - check OPENAI_API_KEY",
                "recommendations": [],
                "summary": {}
            }
        
        try:
            # Build prompt with record data
            prompt = self._build_pricing_prompt(records, competitor_prices, sales_metrics)
            
            # Call OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a pricing optimization expert. Return ONLY valid JSON, no markdown."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=300,  # More tokens for multiple records
                temperature=0,
                timeout=30.0
            )
            
            # Parse response
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # Normalize response
            recommendations = result.get("recommendations", [])
            summary = self._calculate_summary(recommendations)
            
            return {
                "recommendations": recommendations,
                "summary": summary,
                "generated_at": datetime.utcnow().isoformat(),
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Auto pricing optimization failed: {e}")
            return {
                "error": str(e),
                "recommendations": [],
                "summary": {}
            }
    
    def _build_pricing_prompt(
        self,
        records: List[Dict[str, Any]],
        competitor_prices: Optional[Dict[str, Dict[str, float]]],
        sales_metrics: Optional[Dict[str, Dict[str, Any]]]
    ) -> str:
        """Build pricing optimization prompt."""
        prompt = "Optimize prices for vinyl records. Return JSON:\n"
        prompt += '{"recommendations": [{"record_id": "id", "current_price": 25.00, "recommended_price": 27.50, "reasoning": "brief reason", "strategy": "increase|decrease|hold"}]}\n\n'
        prompt += "Records:\n"
        
        for record in records[:10]:  # Limit to 10 records per call
            record_id = record.get("id", "unknown")
            artist = record.get("artist", "Unknown")
            album = record.get("album", "Unknown")
            current_price = record.get("price", 0.0)
            condition = record.get("condition", "VG+")
            days_on_market = record.get("days_on_market", 0)
            views = record.get("views", 0)
            
            prompt += f"- {record_id}: {artist} - {album} (${current_price}, {condition}, {days_on_market}d, {views} views)\n"
            
            # Add competitor prices if available
            if competitor_prices and record_id in competitor_prices:
                comp_prices = competitor_prices[record_id]
                prompt += f"  Competitor prices: {comp_prices}\n"
            
            # Add sales metrics if available
            if sales_metrics and record_id in sales_metrics:
                metrics = sales_metrics[record_id]
                prompt += f"  Metrics: {metrics}\n"
        
        prompt += "\nRules:\n"
        prompt += "- Increase price if: high views, low days on market, rare item\n"
        prompt += "- Decrease price if: slow sale (>30d), low views, common item\n"
        prompt += "- Hold if: recent listing (<7d), balanced metrics\n"
        prompt += "- Return ONLY JSON"
        
        return prompt
    
    def _calculate_summary(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics."""
        total = len(recommendations)
        increases = sum(1 for r in recommendations if r.get("strategy") == "increase")
        decreases = sum(1 for r in recommendations if r.get("strategy") == "decrease")
        no_change = sum(1 for r in recommendations if r.get("strategy") == "hold")
        
        return {
            "total_records": total,
            "price_increases": increases,
            "price_decreases": decreases,
            "no_change": no_change
        }


# Singleton instance
auto_pricing_service = AutoPricingService()
