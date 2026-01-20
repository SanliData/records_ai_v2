# backend/services/commerce/sales_analytics_service.py
# UTF-8, English only
# Sales analytics and dashboard metrics service

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class SalesAnalyticsService:
    """
    Sales analytics service for dashboard metrics.
    
    Tracks:
    - Sales velocity
    - Revenue by platform
    - Conversion rates
    - Average time to sale
    - Top performing records
    """
    
    def __init__(self):
        # In-memory storage (extend with database)
        self._sales = []
        self._listings = []
        logger.info("SalesAnalyticsService initialized")
    
    def record_sale(
        self,
        record_id: str,
        platform: str,
        price: float,
        currency: str = "USD",
        listing_id: Optional[str] = None
    ):
        """Record a sale event."""
        sale = {
            "record_id": record_id,
            "platform": platform,
            "price": price,
            "currency": currency,
            "listing_id": listing_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        self._sales.append(sale)
        logger.info(f"Recorded sale: {record_id} on {platform} for ${price}")
    
    def record_listing(
        self,
        record_id: str,
        platform: str,
        listing_id: str,
        price: float,
        listed_at: Optional[datetime] = None
    ):
        """Record a listing event."""
        listing = {
            "record_id": record_id,
            "platform": platform,
            "listing_id": listing_id,
            "price": price,
            "listed_at": (listed_at or datetime.utcnow()).isoformat(),
            "status": "active"
        }
        self._listings.append(listing)
        logger.info(f"Recorded listing: {record_id} on {platform}")
    
    def get_dashboard_metrics(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get dashboard metrics for the last N days.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            {
                "total_sales": int,
                "total_revenue": float,
                "revenue_by_platform": Dict[str, float],
                "average_sale_price": float,
                "conversion_rate": float,
                "average_days_to_sale": float,
                "top_performing_records": List[Dict],
                "sales_velocity": Dict[str, int]
            }
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Filter sales and listings
        recent_sales = [
            s for s in self._sales
            if datetime.fromisoformat(s["timestamp"]) >= cutoff_date
        ]
        
        recent_listings = [
            l for l in self._listings
            if datetime.fromisoformat(l["listed_at"]) >= cutoff_date
        ]
        
        # Calculate metrics
        total_sales = len(recent_sales)
        total_revenue = sum(s["price"] for s in recent_sales)
        
        revenue_by_platform = defaultdict(float)
        for sale in recent_sales:
            revenue_by_platform[sale["platform"]] += sale["price"]
        
        average_sale_price = total_revenue / total_sales if total_sales > 0 else 0.0
        
        # Conversion rate (simplified)
        active_listings = len([l for l in recent_listings if l["status"] == "active"])
        conversion_rate = (total_sales / active_listings * 100) if active_listings > 0 else 0.0
        
        # Average days to sale (simplified)
        average_days_to_sale = 15.0  # Stub - calculate from actual data
        
        # Top performing records
        record_sales = defaultdict(lambda: {"count": 0, "revenue": 0.0})
        for sale in recent_sales:
            record_sales[sale["record_id"]]["count"] += 1
            record_sales[sale["record_id"]]["revenue"] += sale["price"]
        
        top_performing = sorted(
            [
                {"record_id": rid, "sales": data["count"], "revenue": data["revenue"]}
                for rid, data in record_sales.items()
            ],
            key=lambda x: x["revenue"],
            reverse=True
        )[:10]
        
        # Sales velocity (sales per day)
        sales_velocity = {
            "total": total_sales,
            "per_day": total_sales / days if days > 0 else 0.0,
            "trend": "up"  # Stub - calculate actual trend
        }
        
        return {
            "total_sales": total_sales,
            "total_revenue": round(total_revenue, 2),
            "revenue_by_platform": dict(revenue_by_platform),
            "average_sale_price": round(average_sale_price, 2),
            "conversion_rate": round(conversion_rate, 2),
            "average_days_to_sale": round(average_days_to_sale, 1),
            "top_performing_records": top_performing,
            "sales_velocity": sales_velocity,
            "period_days": days,
            "generated_at": datetime.utcnow().isoformat()
        }


# Singleton instance
sales_analytics_service = SalesAnalyticsService()
