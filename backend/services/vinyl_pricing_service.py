# -*- coding: utf-8 -*-
"""
Vinyl Pricing Service
Fetches market prices from Discogs and calculates condition-based values.
"""

import requests
import time
import logging
from typing import Dict, Optional, Tuple
import os

logger = logging.getLogger(__name__)

# Discogs API Token (from environment - optional, graceful degradation)
DISCOGS_TOKEN = os.getenv("DISCOGS_TOKEN")
if not DISCOGS_TOKEN:
    logger.warning(
        "DISCOGS_TOKEN not set - vinyl pricing features will be unavailable. "
        "Set it in Cloud Run environment variables or Secret Manager."
    )
DISCOGS_BASE_URL = "https://api.discogs.com"


# Goldmine Condition Multipliers
CONDITION_MULTIPLIERS = {
    "M": 1.0,      # Mint - 100%
    "NM": 0.95,    # Near Mint - 95%
    "VG+": 0.85,   # Very Good Plus - 85%
    "VG": 0.70,    # Very Good - 70%
    "G+": 0.50,    # Good Plus - 50%
    "G": 0.30,     # Good - 30%
    "P": 0.10,     # Poor - 10%
    "": 1.0,       # No condition specified - full price
    None: 1.0
}


class VinylPricingService:
    """
    Service for fetching vinyl record market prices and calculating condition-based values.
    """
    
    def __init__(self):
        self.enabled = bool(DISCOGS_TOKEN)
        if self.enabled:
            self.headers = {
                "Authorization": f"Discogs token={DISCOGS_TOKEN}",
                "User-Agent": "RecordsAI/1.0"
            }
        else:
            self.headers = {
                "User-Agent": "RecordsAI/1.0"
            }
            logger.warning("VinylPricingService initialized without DISCOGS_TOKEN - pricing features disabled")
    
    def get_market_prices(
        self, 
        artist: str, 
        album: str, 
        catalog_number: Optional[str] = None,
        label: Optional[str] = None
    ) -> Dict:
        """
        Fetch market prices from Discogs marketplace.
        
        Returns:
        {
            "price_low": float,
            "price_high": float,
            "price_median": float,
            "currency": "USD",
            "source": "discogs",
            "url": str
        }
        """
        try:
            # Search for release
            release_id = self._search_release(artist, album, catalog_number, label)
            if not release_id:
                return self._empty_pricing()
            
            # Get marketplace statistics
            stats = self._get_marketplace_stats(release_id)
            if not stats:
                return self._empty_pricing()
            
            # Extract prices from marketplace stats
            prices = stats.get("prices", [])
            
            # If no prices in stats, try to get from marketplace listings
            if not prices:
                prices = self._get_marketplace_listings(release_id)
            
            if not prices:
                # If still no prices, return release info but no pricing
                return {
                    **self._empty_pricing(),
                    "release_id": release_id,
                    "url": f"https://www.discogs.com/release/{release_id}",
                    "note": "No marketplace prices available"
                }
            
            # Convert to USD if needed and extract values
            price_values = []
            currency = "USD"
            
            for price_item in prices:
                value = price_item.get("value") if isinstance(price_item, dict) else price_item
                if value:
                    try:
                        price_value = float(value)
                        price_currency = price_item.get("currency", "USD") if isinstance(price_item, dict) else "USD"
                        
                        # Currency conversion (approximate rates)
                        if price_currency == "USD":
                            price_values.append(price_value)
                        elif price_currency == "EUR":
                            price_values.append(price_value * 1.1)
                        elif price_currency == "GBP":
                            price_values.append(price_value * 1.27)
                        elif price_currency == "JPY":
                            price_values.append(price_value * 0.0067)
                        else:
                            price_values.append(price_value)  # Assume USD
                    except (ValueError, TypeError):
                        continue
            
            if not price_values:
                return self._empty_pricing()
            
            price_low = min(price_values)
            price_high = max(price_values)
            price_median = sorted(price_values)[len(price_values) // 2]
            
            return {
                "price_low": round(price_low, 2),
                "price_high": round(price_high, 2),
                "price_median": round(price_median, 2),
                "currency": currency,
                "source": "discogs",
                "url": f"https://www.discogs.com/release/{release_id}",
                "sample_size": len(price_values)
            }
            
        except Exception as e:
            print(f"[PricingService] Error fetching prices: {e}")
            return self._empty_pricing()
    
    def _search_release(self, artist: str, album: str, catalog_number: Optional[str] = None, label: Optional[str] = None) -> Optional[str]:
        """Search Discogs for release ID with improved matching."""
        try:
            # First try: exact match with artist and album
            query = f"{artist} {album}"
            if catalog_number:
                query += f" {catalog_number}"
            
            url = f"{DISCOGS_BASE_URL}/database/search"
            params = {
                "q": query,
                "type": "release",
                "per_page": 10
            }
            
            # Add artist and title as separate params if available
            if artist and album:
                params["artist"] = artist
                params["release_title"] = album
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code != 200:
                print(f"[PricingService] Search returned status {response.status_code}")
                return None
            
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                # Try fuzzy search with just album name
                params = {
                    "q": album,
                    "type": "release",
                    "per_page": 5
                }
                time.sleep(1)  # Rate limiting
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
            
            if not results:
                return None
            
            # Return first result's ID (best match)
            return str(results[0].get("id"))
            
        except Exception as e:
            print(f"[PricingService] Search error: {e}")
            return None
    
    def _get_marketplace_stats(self, release_id: str) -> Optional[Dict]:
        """Get marketplace statistics for a release."""
        try:
            # Try marketplace stats endpoint
            url = f"{DISCOGS_BASE_URL}/marketplace/stats/{release_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            
            # Fallback: Get release details and extract price info
            release_details = self._get_release_details(release_id)
            if release_details:
                # Try to get prices from release page or estimate
                return {
                    "prices": [],
                    "release_info": release_details
                }
            
            return None
            
        except Exception as e:
            print(f"[PricingService] Marketplace stats error: {e}")
            return None
    
    def _get_release_details(self, release_id: str) -> Optional[Dict]:
        """Get detailed release information from Discogs."""
        try:
            url = f"{DISCOGS_BASE_URL}/releases/{release_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            
            return None
            
        except Exception as e:
            print(f"[PricingService] Release details error: {e}")
            return None
    
    def get_release_info(
        self,
        artist: str,
        album: str,
        catalog_number: Optional[str] = None,
        label: Optional[str] = None
    ) -> Dict:
        """
        Get comprehensive release information from Discogs.
        Includes metadata, images, tracklist, etc.
        """
        try:
            release_id = self._search_release(artist, album, catalog_number, label)
            if not release_id:
                return {"status": "not_found"}
            
            release_details = self._get_release_details(release_id)
            if not release_details:
                return {"status": "not_found"}
            
            # Extract relevant information
            return {
                "status": "ok",
                "release_id": release_id,
                "title": release_details.get("title"),
                "artist": ", ".join([a.get("name", "") for a in release_details.get("artists", [])]),
                "label": ", ".join([l.get("name", "") for l in release_details.get("labels", [])]),
                "year": release_details.get("year"),
                "country": release_details.get("country"),
                "format": release_details.get("formats", [{}])[0].get("name", ""),
                "genre": release_details.get("genres", []),
                "style": release_details.get("styles", []),
                "tracklist": release_details.get("tracklist", []),
                "images": release_details.get("images", []),
                "url": release_details.get("uri", f"https://www.discogs.com/release/{release_id}"),
                "catalog_number": release_details.get("labels", [{}])[0].get("catno", ""),
            }
            
        except Exception as e:
            print(f"[PricingService] Get release info error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_marketplace_listings(self, release_id: str) -> list:
        """Get marketplace listings for a release (alternative method)."""
        try:
            # Discogs marketplace listings endpoint
            url = f"{DISCOGS_BASE_URL}/marketplace/listings/release/{release_id}"
            params = {
                "status": "For Sale",
                "per_page": 50
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                listings = data.get("listings", [])
                prices = []
                for listing in listings:
                    price_obj = listing.get("price")
                    if price_obj:
                        prices.append(price_obj)
                return prices
            
            return []
            
        except Exception as e:
            print(f"[PricingService] Marketplace listings error: {e}")
            return []
    
    def _empty_pricing(self) -> Dict:
        """Return empty pricing structure."""
        return {
            "price_low": None,
            "price_high": None,
            "price_median": None,
            "currency": "USD",
            "source": None,
            "url": None,
            "sample_size": 0
        }
    
    def calculate_condition_price(
        self, 
        base_price: float, 
        condition: Optional[str]
    ) -> float:
        """
        Calculate price based on record condition.
        
        Args:
            base_price: Base price (usually median or high)
            condition: Condition code (M, NM, VG+, VG, G+, G, P)
        
        Returns:
            Adjusted price based on condition
        """
        if not base_price or base_price <= 0:
            return 0.0
        
        multiplier = CONDITION_MULTIPLIERS.get(condition, 1.0)
        return round(base_price * multiplier, 2)
    
    def get_estimated_value(
        self,
        market_prices: Dict,
        condition: Optional[str] = None,
        user_estimate: Optional[float] = None
    ) -> Dict:
        """
        Calculate estimated value considering market prices and condition.
        
        Args:
            market_prices: Market prices dict from get_market_prices()
            condition: Record condition code
            user_estimate: User's manual price estimate
        
        Returns:
            {
                "estimated_value": float,
                "condition_adjusted": float,
                "market_range": {"low": float, "high": float, "median": float},
                "calculation_method": str
            }
        """
        # Use user estimate if provided
        if user_estimate and user_estimate > 0:
            estimated = user_estimate
            method = "user_estimate"
        else:
            # Use median market price as base
            estimated = market_prices.get("price_median") or market_prices.get("price_low", 0)
            method = "market_median"
        
        # Apply condition adjustment
        condition_adjusted = self.calculate_condition_price(estimated, condition)
        
        return {
            "estimated_value": round(estimated, 2),
            "condition_adjusted": condition_adjusted,
            "market_range": {
                "low": market_prices.get("price_low"),
                "high": market_prices.get("price_high"),
                "median": market_prices.get("price_median")
            },
            "calculation_method": method,
            "condition": condition,
            "condition_multiplier": CONDITION_MULTIPLIERS.get(condition, 1.0)
        }


# Global instance
vinyl_pricing_service = VinylPricingService()
