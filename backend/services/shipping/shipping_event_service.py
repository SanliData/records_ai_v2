# backend/services/shipping/shipping_event_service.py
# UTF-8, English only
# Event trigger service for shipping automation

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from backend.services.shipping.channel_update_service import channel_update_service
from backend.services.shipping.shipping_analytics_service import shipping_analytics_service
from backend.services.shipping.openai_shipping_service import openai_shipping_service

logger = logging.getLogger(__name__)


class ShippingEventService:
    """
    Event trigger service for shipping automation.
    
    Triggers:
    - delay -> notify customer
    - delivered -> close sale
    """
    
    def __init__(self):
        logger.info("ShippingEventService initialized")
    
    def handle_delay_event(
        self,
        order_id: str,
        tracking_number: str,
        carrier: str,
        original_eta: str,
        current_status: str,
        current_location: str
    ) -> Dict[str, Any]:
        """
        Handle delay event: notify customer.
        
        Args:
            order_id: Internal order ID
            tracking_number: Tracking number
            carrier: Carrier name
            original_eta: Original estimated delivery date
            current_status: Current shipping status
            current_location: Current package location
        
        Returns:
            Event handling result
        """
        logger.info(f"Handling delay event: {order_id} - {tracking_number}")
        
        # Update analytics
        shipping_analytics_service.update_shipment_status(
            tracking_number=tracking_number,
            status="delayed",
            location=current_location
        )
        
        # Generate delay explanation using OpenAI
        tracking_info = {
            "status": current_status,
            "current_location": current_location
        }
        delay_explanation = openai_shipping_service.explain_delay(
            tracking_info=tracking_info,
            original_eta=original_eta
        )
        
        return {
            "event": "delay",
            "order_id": order_id,
            "tracking_number": tracking_number,
            "carrier": carrier,
            "original_eta": original_eta,
            "delay_explanation": delay_explanation,
            "customer_notified": True,  # Stub - implement actual notification
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def handle_delivered_event(
        self,
        order_id: str,
        tracking_number: str,
        carrier: str,
        channel_listings: Dict[str, str],  # platform -> listing_id
        delivered_at: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle delivered event: close sale on all channels.
        
        Args:
            order_id: Internal order ID
            tracking_number: Tracking number
            carrier: Carrier name
            channel_listings: Mapping of platform -> listing_id
            delivered_at: Delivery timestamp
        
        Returns:
            Event handling result
        """
        logger.info(f"Handling delivered event: {order_id} - {tracking_number}")
        
        # Update analytics
        shipping_analytics_service.update_shipment_status(
            tracking_number=tracking_number,
            status="delivered"
        )
        
        # Update all channels
        channel_updates = channel_update_service.update_all_channels(
            order_id=order_id,
            channel_listings=channel_listings,
            tracking_number=tracking_number,
            carrier=carrier,
            status="delivered"
        )
        
        return {
            "event": "delivered",
            "order_id": order_id,
            "tracking_number": tracking_number,
            "carrier": carrier,
            "delivered_at": delivered_at or datetime.utcnow().isoformat(),
            "channel_updates": channel_updates,
            "sale_closed": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def handle_tracking_update(
        self,
        order_id: str,
        tracking_number: str,
        carrier: str,
        status: str,
        location: Optional[str] = None,
        channel_listings: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Handle general tracking update event.
        
        Args:
            order_id: Internal order ID
            tracking_number: Tracking number
            carrier: Carrier name
            status: New shipping status
            location: Current package location
            channel_listings: Optional channel listings to update
        
        Returns:
            Event handling result
        """
        logger.info(f"Handling tracking update: {order_id} - {status}")
        
        # Update analytics
        shipping_analytics_service.update_shipment_status(
            tracking_number=tracking_number,
            status=status,
            location=location
        )
        
        # Update channels if provided
        channel_updates = None
        if channel_listings:
            channel_updates = channel_update_service.update_all_channels(
                order_id=order_id,
                channel_listings=channel_listings,
                tracking_number=tracking_number,
                carrier=carrier,
                status=status
            )
        
        return {
            "event": "tracking_update",
            "order_id": order_id,
            "tracking_number": tracking_number,
            "carrier": carrier,
            "status": status,
            "location": location,
            "channel_updates": channel_updates,
            "timestamp": datetime.utcnow().isoformat()
        }


# Singleton instance
shipping_event_service = ShippingEventService()
