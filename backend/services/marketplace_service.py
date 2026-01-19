# -*- coding: utf-8 -*-
"""
Marketplace Service
Manages multi-platform listings (Discogs, eBay, Etsy, Amazon).
Handles listing creation, status tracking, and cross-platform sync.

STATUS:
- Discogs API: Ready for integration (pricing service uses Discogs API)
- eBay API: Placeholder (Phase 3)
- Etsy API: Placeholder (Phase 3)
- Amazon API: Placeholder (Phase 3)

Current implementation uses in-memory storage for testing.
Real API integrations will be added in Phase 3.
"""

from typing import Dict, Optional, List
from datetime import datetime
import uuid
import os
import logging

logger = logging.getLogger(__name__)


class MarketplaceService:
    """
    Service for managing multi-platform marketplace listings.
    Handles listing creation, status updates, and cross-platform sync.
    """
    
    def __init__(self):
        # In-memory storage for listings
        # In production, this would be a database
        self._listings = {}  # listing_id => listing_dict
        self._record_listings = {}  # archive_id => [listing_ids]
        
        # API credentials (from environment)
        self.discogs_token = os.getenv("DISCOGS_TOKEN")
        self.ebay_app_id = os.getenv("EBAY_APP_ID")
        self.etsy_api_key = os.getenv("ETSY_API_KEY")
        self.amazon_access_key = os.getenv("AMAZON_ACCESS_KEY")
        
        # Feature flags
        self.use_real_apis = os.getenv("MARKETPLACE_USE_REAL_APIS", "false").lower() == "true"
    
    def create_listings(
        self,
        archive_id: str,
        platforms: List[str],
        price: float,
        currency: str = "USD",
        condition: str = "VG+",
        description: Optional[str] = None,
        images: Optional[List[str]] = None
    ) -> Dict:
        """
        Create listings on multiple platforms for a single archive record.
        
        Platforms: ["discogs", "ebay", "etsy", "amazon"]
        
        Returns:
        {
            "status": "ok",
            "listings": [
                {"platform": "discogs", "listing_id": "...", "status": "pending"},
                ...
            ],
            "archive_id": "..."
        }
        """
        if not archive_id or not platforms:
            return {"status": "error", "message": "archive_id and platforms required"}
        
        created_listings = []
        
        for platform in platforms:
            if platform not in ["discogs", "ebay", "etsy", "amazon"]:
                continue
            
            # Create listing (real API or placeholder)
            if self.use_real_apis:
                listing_result = self._create_real_listing(
                    platform, archive_id, price, currency, condition, description, images
                )
                if listing_result:
                    created_listings.append(listing_result)
                    continue
            
            # Placeholder implementation (in-memory)
            listing_id = str(uuid.uuid4())
            listing = {
                "listing_id": listing_id,
                "archive_id": archive_id,
                "platform": platform,
                "status": "pending",  # pending, active, sold, cancelled
                "price": price,
                "currency": currency,
                "condition": condition,
                "description": description,
                "images": images or [],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "sold_at": None,
                "sold_price": None,
                "is_placeholder": True  # Mark as placeholder
            }
            
            # Store listing
            self._listings[listing_id] = listing
            
            # Track listings per archive
            if archive_id not in self._record_listings:
                self._record_listings[archive_id] = []
            self._record_listings[archive_id].append(listing_id)
            
            created_listings.append({
                "platform": platform,
                "listing_id": listing_id,
                "status": "pending",
                "url": self._get_listing_url(platform, listing_id),
                "is_placeholder": True,
                "message": f"Placeholder listing created. Set MARKETPLACE_USE_REAL_APIS=true for real API integration."
            })
        
        return {
            "status": "ok",
            "message": f"Listings created on {len(created_listings)} platform(s)",
            "listings": created_listings,
            "archive_id": archive_id
        }
    
    def update_listing_status(
        self,
        listing_id: str,
        status: str,
        sold_price: Optional[float] = None
    ) -> Dict:
        """
        Update listing status (pending -> active -> sold).
        
        If status is "sold", automatically close other listings for the same record.
        """
        if listing_id not in self._listings:
            return {"status": "error", "message": "Listing not found"}
        
        listing = self._listings[listing_id]
        old_status = listing.get("status")
        
        # Update status
        listing["status"] = status
        listing["updated_at"] = datetime.utcnow().isoformat()
        
        if status == "sold":
            listing["sold_at"] = datetime.utcnow().isoformat()
            if sold_price:
                listing["sold_price"] = sold_price
            
            # IMPORTANT: Close other listings for the same record
            archive_id = listing.get("archive_id")
            if archive_id:
                self._close_other_listings(archive_id, listing_id)
        
        return {
            "status": "ok",
            "listing_id": listing_id,
            "old_status": old_status,
            "new_status": status,
            "closed_other_listings": status == "sold"
        }
    
    def _close_other_listings(self, archive_id: str, sold_listing_id: str):
        """Close all other listings for the same record when one is sold."""
        if archive_id not in self._record_listings:
            return
        
        listing_ids = self._record_listings[archive_id]
        
        for listing_id in listing_ids:
            if listing_id != sold_listing_id:
                listing = self._listings.get(listing_id)
                if listing and listing.get("status") in ["pending", "active"]:
                    listing["status"] = "cancelled"
                    listing["updated_at"] = datetime.utcnow().isoformat()
                    listing["cancelled_reason"] = "Sold on another platform"
    
    def get_record_listings(self, archive_id: str) -> List[Dict]:
        """Get all listings for a specific archive record."""
        if archive_id not in self._record_listings:
            return []
        
        listing_ids = self._record_listings[archive_id]
        listings = []
        
        for listing_id in listing_ids:
            listing = self._listings.get(listing_id)
            if listing:
                listings.append(listing)
        
        return listings
    
    def get_listing(self, listing_id: str) -> Optional[Dict]:
        """Get a specific listing by ID."""
        return self._listings.get(listing_id)
    
    def _create_real_listing(
        self,
        platform: str,
        archive_id: str,
        price: float,
        currency: str,
        condition: str,
        description: Optional[str],
        images: Optional[List[str]]
    ) -> Optional[Dict]:
        """
        Create listing using real platform APIs.
        Returns listing dict or None if API call fails.
        
        NOTE: This is a placeholder for Phase 3 implementation.
        Real API integrations will be added here.
        """
        try:
            if platform == "discogs" and self.discogs_token:
                # TODO: Implement Discogs API listing creation
                # See: https://www.discogs.com/developers#page:marketplace,header:marketplace-listing-post
                logger.warning("Discogs API listing creation not yet implemented (Phase 3)")
                return None
            elif platform == "ebay" and self.ebay_app_id:
                # TODO: Implement eBay API listing creation
                # See: https://developer.ebay.com/api-docs/sell/inventory/overview.html
                logger.warning("eBay API listing creation not yet implemented (Phase 3)")
                return None
            elif platform == "etsy" and self.etsy_api_key:
                # TODO: Implement Etsy API listing creation
                # See: https://developers.etsy.com/documentation/reference#operation/createListing
                logger.warning("Etsy API listing creation not yet implemented (Phase 3)")
                return None
            elif platform == "amazon" and self.amazon_access_key:
                # TODO: Implement Amazon Marketplace API listing creation
                logger.warning("Amazon API listing creation not yet implemented (Phase 3)")
                return None
        except Exception as e:
            logger.error(f"Failed to create real listing on {platform}: {e}")
        
        return None
    
    def _get_listing_url(self, platform: str, listing_id: str) -> str:
        """Generate listing URL based on platform."""
        base_urls = {
            "discogs": f"https://www.discogs.com/sell/item/{listing_id}",
            "ebay": f"https://www.ebay.com/itm/{listing_id}",
            "etsy": f"https://www.etsy.com/listing/{listing_id}",
            "amazon": f"https://www.amazon.com/dp/{listing_id}"
        }
        return base_urls.get(platform, "#")
    
    def sync_listings(self, archive_id: str) -> Dict:
        """
        Sync listing status across all platforms.
        Checks for sold status and closes other listings if needed.
        """
        listings = self.get_record_listings(archive_id)
        
        # Check if any listing is sold
        sold_listing = None
        for listing in listings:
            if listing.get("status") == "sold":
                sold_listing = listing
                break
        
        if sold_listing:
            # Close other active/pending listings
            self._close_other_listings(archive_id, sold_listing.get("listing_id"))
            
            return {
                "status": "synced",
                "message": "Listings synced - record is sold, other listings closed",
                "sold_listing": sold_listing.get("listing_id"),
                "closed_listings": [
                    l.get("listing_id") for l in listings 
                    if l.get("status") == "cancelled" and l.get("listing_id") != sold_listing.get("listing_id")
                ]
            }
        
        return {
            "status": "ok",
            "message": "Listings synced - no sold listings found",
            "listings": listings
        }


# Global instance
marketplace_service = MarketplaceService()
