# backend/services/commerce/stock_sync_service.py
# UTF-8, English only
# Stock synchronization service for multi-channel commerce

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from backend.services.channels.ebay import ebay_connector
from backend.services.channels.discogs import discogs_connector
from backend.services.channels.shopify import shopify_connector
from backend.services.channels.etsy import etsy_connector

logger = logging.getLogger(__name__)


class StockSyncService:
    """
    Stock synchronization service.
    
    Rules:
    - If sold on any channel -> auto delist on all others
    - Maintains single source of truth for inventory
    """
    
    def __init__(self):
        self.connectors = {
            "ebay": ebay_connector,
            "discogs": discogs_connector,
            "shopify": shopify_connector,
            "etsy": etsy_connector
        }
        logger.info("StockSyncService initialized")
    
    def handle_sale(
        self,
        record_id: str,
        sold_on_platform: str,
        listing_ids: Dict[str, str]  # platform -> listing_id mapping
    ) -> Dict[str, Any]:
        """
        Handle sale event: delist on all other platforms.
        
        Args:
            record_id: Internal record ID
            sold_on_platform: Platform where item was sold
            listing_ids: Mapping of platform -> listing_id for all active listings
        
        Returns:
            {
                "record_id": str,
                "sold_on": str,
                "delisted_platforms": List[str],
                "results": Dict[str, Dict],
                "success": bool
            }
        """
        logger.info(f"Handling sale for record {record_id} on {sold_on_platform}")
        
        delisted_platforms = []
        results = {}
        
        # Delist on all platforms except the one where it was sold
        for platform, listing_id in listing_ids.items():
            if platform == sold_on_platform:
                continue  # Skip the platform where it was sold
            
            if not listing_id:
                continue
            
            try:
                result = self._delist_item(platform, listing_id)
                results[platform] = result
                
                if result.get("success"):
                    delisted_platforms.append(platform)
                    logger.info(f"Delisted {record_id} from {platform}")
                else:
                    logger.warning(f"Failed to delist {record_id} from {platform}: {result.get('error')}")
            except Exception as e:
                logger.error(f"Error delisting from {platform}: {e}")
                results[platform] = {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "record_id": record_id,
            "sold_on": sold_on_platform,
            "delisted_platforms": delisted_platforms,
            "results": results,
            "success": len(delisted_platforms) == len(listing_ids) - 1,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _delist_item(self, platform: str, listing_id: str) -> Dict[str, Any]:
        """Delist item from specific platform."""
        connector = self.connectors.get(platform.lower())
        if not connector:
            return {
                "success": False,
                "error": f"Unknown platform: {platform}"
            }
        
        # Stub implementation - extend with actual API calls
        logger.info(f"Delisting {listing_id} from {platform}")
        return {
            "success": True,
            "listing_id": listing_id,
            "platform": platform,
            "message": f"Delisted from {platform}"
        }


# Singleton instance
stock_sync_service = StockSyncService()
