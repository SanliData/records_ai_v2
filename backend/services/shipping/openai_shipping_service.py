# backend/services/shipping/openai_shipping_service.py
# UTF-8, English only
# OpenAI-powered shipping communication service

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI SDK not available")


class OpenAIShippingService:
    """
    OpenAI-powered shipping communication service.
    
    Generates:
    - Customer messages
    - Delay explanations
    - ETA predictions
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            self.enabled = True
            logger.info("OpenAIShippingService initialized with API key")
        else:
            self.client = None
            self.enabled = False
        
        self.model = "gpt-4o-mini"  # Cheapest model
    
    def generate_customer_message(
        self,
        tracking_info: Dict[str, Any],
        order_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate customer-friendly shipping update message.
        
        Args:
            tracking_info: Tracking information from carrier
            order_info: Order information (record, customer, etc.)
        
        Returns:
            {
                "message": str,
                "subject": str,
                "eta": Optional[str],
                "status": str
            }
        """
        if not self.enabled:
            return {
                "error": "OpenAI service not available - check OPENAI_API_KEY",
                "message": None,
                "subject": None
            }
        
        try:
            prompt = self._build_message_prompt(tracking_info, order_info)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a friendly customer service assistant. Return ONLY valid JSON, no markdown."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=200,
                temperature=0.7,  # Slightly creative for friendly tone
                timeout=30.0
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            return {
                "message": result.get("message", ""),
                "subject": result.get("subject", "Shipping Update"),
                "eta": result.get("eta"),
                "status": tracking_info.get("status", "unknown"),
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Failed to generate customer message: {e}")
            return {
                "error": str(e),
                "message": None,
                "subject": None
            }
    
    def explain_delay(
        self,
        tracking_info: Dict[str, Any],
        original_eta: str
    ) -> Dict[str, Any]:
        """
        Generate delay explanation for customer.
        
        Args:
            tracking_info: Current tracking information
            original_eta: Original estimated delivery date
        
        Returns:
            {
                "explanation": str,
                "new_eta": Optional[str],
                "reason": str
            }
        """
        if not self.enabled:
            return {
                "error": "OpenAI service not available",
                "explanation": None
            }
        
        try:
            prompt = f"""Shipping delay detected. Original ETA: {original_eta}. Current status: {tracking_info.get('status')}. Location: {tracking_info.get('current_location', 'Unknown')}.

Generate customer-friendly delay explanation. Return JSON:
{{
  "explanation": "friendly explanation",
  "new_eta": "new estimated date",
  "reason": "brief reason"
}}

Return ONLY JSON."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful shipping assistant. Return ONLY valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=150,
                temperature=0.7,
                timeout=30.0
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            return {
                "explanation": result.get("explanation", ""),
                "new_eta": result.get("new_eta"),
                "reason": result.get("reason", ""),
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Failed to explain delay: {e}")
            return {
                "error": str(e),
                "explanation": None
            }
    
    def predict_eta(
        self,
        tracking_info: Dict[str, Any],
        order_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict ETA using OpenAI based on tracking history.
        
        Args:
            tracking_info: Current tracking information
            order_info: Order information
        
        Returns:
            {
                "predicted_eta": str,
                "confidence": float,
                "reasoning": str
            }
        """
        if not self.enabled:
            return {
                "error": "OpenAI service not available",
                "predicted_eta": None
            }
        
        try:
            prompt = f"""Predict delivery ETA. Current status: {tracking_info.get('status')}. Location: {tracking_info.get('current_location')}. Events: {len(tracking_info.get('events', []))}.

Return JSON:
{{
  "predicted_eta": "ISO date string",
  "confidence": 0.0-1.0,
  "reasoning": "brief reason"
}}

Return ONLY JSON."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a shipping logistics expert. Return ONLY valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=150,
                temperature=0,
                timeout=30.0
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            return {
                "predicted_eta": result.get("predicted_eta"),
                "confidence": result.get("confidence", 0.5),
                "reasoning": result.get("reasoning", ""),
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Failed to predict ETA: {e}")
            return {
                "error": str(e),
                "predicted_eta": None
            }
    
    def _build_message_prompt(
        self,
        tracking_info: Dict[str, Any],
        order_info: Dict[str, Any]
    ) -> str:
        """Build prompt for customer message generation."""
        status = tracking_info.get("status", "unknown")
        location = tracking_info.get("current_location", "Unknown")
        eta = tracking_info.get("estimated_delivery", "Unknown")
        record = order_info.get("record", {})
        artist = record.get("artist", "Unknown")
        album = record.get("album", "Unknown")
        
        prompt = f"""Generate friendly shipping update for customer. Order: {artist} - {album}. Status: {status}. Location: {location}. ETA: {eta}.

Return JSON:
{{
  "message": "friendly update message",
  "subject": "email subject",
  "eta": "estimated delivery date"
}}

Return ONLY JSON."""
        
        return prompt


# Singleton instance
openai_shipping_service = OpenAIShippingService()
