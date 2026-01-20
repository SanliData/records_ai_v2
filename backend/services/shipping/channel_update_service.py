# backend/services/shipping/channel_update_service.py
# UTF-8, English only
# Auto-update shipping status on channels (eBay, Etsy, Shopify)

import logging
from typing import Dict, Any, Optional
from backend.services.channels.ebay import ebay_connector
from backend.services.channels.etsy import etsy_connector
from backend.services.channels.shopify import shopify_connector

logger = logging.getLogger(__name__)


class ChannelUpdateService:
    """
    Auto-update shipping status on channels.
    
    Updates:
    - eBay
    - Etsy
    - Shopify
    """
    
    def __init__(self):
        self.connectors = {
            "ebay": ebay_connector,
            "etsy": etsy_connector,
            "shopify": shopify_connector
        }
        logger.info("ChannelUpdateService initialized")
    
    def update_shipping_status(
        self,
        platform: str,
        listing_id: str,
        tracking_number: str,
        carrier: str,
        status: str
    ) -> Dict[str, Any]:
        """
        Update shipping status on platform.
        
        Args:
            platform: Platform name (ebay, etsy, shopify)
            listing_id: Listing/order ID on platform
            tracking_number: Tracking number
            carrier: Carrier name
            status: Shipping status
        
        Returns:
            Update result
        """
        connector = self.connectors.get(platform.lower())
        if not connector:
            return {
                "success": False,
                "error": f"Unknown platform: {platform}",
                "platform": platform,
                "listing_id": listing_id
            }
        
        try:
            # Stub implementation - extend with actual API calls
            logger.info(f"Updating shipping status on {platform}: {listing_id} - {status}")
            
            return {
                "success": True,
                "platform": platform,
                "listing_id": listing_id,
                "tracking_number": tracking_number,
                "carrier": carrier,
                "status": status,
                "updated_at": None  # Will be set by actual API
            }
            
        except Exception as e:
            logger.error(f"Failed to update {platform}: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform": platform,
                "listing_id": listing_id
            }
    
    def update_all_channels(
        self,
        order_id: str,
        channel_listings: Dict[str, str],  # platform -> listing_id
        tracking_number: str,
        carrier: str,
        status: str
    ) -> Dict[str, Any]:
        """
        Update shipping status on all channels for an order.
        
        Args:
            order_id: Internal order ID
            channel_listings: Mapping of platform -> listing_id
            tracking_number: Tracking number
            carrier: Carrier name
            status: Shipping status
        
        Returns:
            Results for all platforms
        """
        results = {}
        
        for platform, listing_id in channel_listings.items():
            result = self.update_shipping_status(
                platform=platform,
                listing_id=listing_id,
                tracking_number=tracking_number,
                carrier=carrier,
                status=status
            )
            results[platform] = result
        
        successful = sum(1 for r in results.values() if r.get("success"))
        
        return {
            "order_id": order_id,
            "total_channels": len(channel_listings),
            "successful": successful,
            "failed": len(channel_listings) - successful,
            "results": results
        }


# Singleton instance
channel_update_service = ChannelUpdateService()
