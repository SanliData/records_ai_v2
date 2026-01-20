# backend/services/commerce/event_trigger_service.py
# UTF-8, English only
# Event trigger service for autonomous commerce actions

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from backend.services.commerce.stock_sync_service import stock_sync_service
from backend.services.commerce.auto_pricing_service import auto_pricing_service
from backend.services.commerce.sales_analytics_service import sales_analytics_service

logger = logging.getLogger(__name__)


class EventTriggerService:
    """
    Event trigger service for autonomous commerce actions.
    
    Triggers:
    - sold -> delist all
    - slow sale -> reduce price
    - high views -> increase price
    """
    
    def __init__(self):
        logger.info("EventTriggerService initialized")
    
    def handle_sale_event(
        self,
        record_id: str,
        sold_on_platform: str,
        listing_ids: Dict[str, str],
        price: float
    ) -> Dict[str, Any]:
        """
        Handle sale event: delist on all other platforms.
        
        Args:
            record_id: Internal record ID
            sold_on_platform: Platform where item was sold
            listing_ids: Mapping of platform -> listing_id
            price: Sale price
        
        Returns:
            Event handling result
        """
        logger.info(f"Handling sale event: {record_id} sold on {sold_on_platform}")
        
        # Record sale in analytics
        sales_analytics_service.record_sale(
            record_id=record_id,
            platform=sold_on_platform,
            price=price
        )
        
        # Sync stock (delist on all other platforms)
        sync_result = stock_sync_service.handle_sale(
            record_id=record_id,
            sold_on_platform=sold_on_platform,
            listing_ids=listing_ids
        )
        
        return {
            "event": "sale",
            "record_id": record_id,
            "sold_on": sold_on_platform,
            "price": price,
            "stock_sync": sync_result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def handle_slow_sale_event(
        self,
        record_id: str,
        days_on_market: int,
        current_price: float,
        views: int = 0
    ) -> Dict[str, Any]:
        """
        Handle slow sale event: reduce price.
        
        Args:
            record_id: Internal record ID
            days_on_market: Days since listing
            current_price: Current listing price
            views: Number of views
        
        Returns:
            Price adjustment recommendation
        """
        if days_on_market < 30:
            return {
                "event": "slow_sale",
                "record_id": record_id,
                "action": "no_action",
                "reason": f"Only {days_on_market} days on market (threshold: 30)"
            }
        
        logger.info(f"Handling slow sale event: {record_id} ({days_on_market} days, {views} views)")
        
        # Calculate price reduction (5-10% reduction)
        reduction_percent = 0.07  # 7% reduction
        new_price = current_price * (1 - reduction_percent)
        
        return {
            "event": "slow_sale",
            "record_id": record_id,
            "action": "reduce_price",
            "current_price": current_price,
            "recommended_price": round(new_price, 2),
            "reduction_percent": reduction_percent * 100,
            "reason": f"Slow sale: {days_on_market} days on market, {views} views",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def handle_high_views_event(
        self,
        record_id: str,
        views: int,
        days_on_market: int,
        current_price: float
    ) -> Dict[str, Any]:
        """
        Handle high views event: increase price.
        
        Args:
            record_id: Internal record ID
            views: Number of views
            days_on_market: Days since listing
            current_price: Current listing price
        
        Returns:
            Price adjustment recommendation
        """
        if views < 100:
            return {
                "event": "high_views",
                "record_id": record_id,
                "action": "no_action",
                "reason": f"Only {views} views (threshold: 100)"
            }
        
        logger.info(f"Handling high views event: {record_id} ({views} views, {days_on_market} days)")
        
        # Calculate price increase (5-10% increase)
        increase_percent = 0.08  # 8% increase
        new_price = current_price * (1 + increase_percent)
        
        return {
            "event": "high_views",
            "record_id": record_id,
            "action": "increase_price",
            "current_price": current_price,
            "recommended_price": round(new_price, 2),
            "increase_percent": increase_percent * 100,
            "reason": f"High demand: {views} views in {days_on_market} days",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def process_nightly_optimization(
        self,
        records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process nightly optimization for all active listings.
        
        Uses OpenAI to make intelligent pricing decisions.
        
        Args:
            records: List of active listings with metrics
        
        Returns:
            Optimization results
        """
        logger.info(f"Processing nightly optimization for {len(records)} records")
        
        # Get competitor prices (stub - extend with actual scraping)
        competitor_prices = {}
        
        # Get sales metrics
        sales_metrics = {}
        for record in records:
            record_id = record.get("id")
            sales_metrics[record_id] = {
                "views": record.get("views", 0),
                "days_on_market": record.get("days_on_market", 0),
                "clicks": record.get("clicks", 0)
            }
        
        # Use OpenAI to optimize prices
        optimization_result = auto_pricing_service.optimize_prices(
            records=records,
            competitor_prices=competitor_prices,
            sales_metrics=sales_metrics
        )
        
        return {
            "event": "nightly_optimization",
            "records_processed": len(records),
            "optimization": optimization_result,
            "timestamp": datetime.utcnow().isoformat()
        }


# Singleton instance
event_trigger_service = EventTriggerService()
