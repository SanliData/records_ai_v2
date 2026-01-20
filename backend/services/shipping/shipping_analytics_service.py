# backend/services/shipping/shipping_analytics_service.py
# UTF-8, English only
# Shipping analytics and dashboard metrics

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class ShippingAnalyticsService:
    """
    Shipping analytics service for dashboard metrics.
    
    Tracks:
    - In transit
    - Delivered
    - Delayed
    - Average delivery time
    - Carrier performance
    """
    
    def __init__(self):
        # In-memory storage (extend with database)
        self._shipments = []
        logger.info("ShippingAnalyticsService initialized")
    
    def record_shipment(
        self,
        order_id: str,
        tracking_number: str,
        carrier: str,
        status: str,
        estimated_delivery: Optional[str] = None
    ):
        """Record a shipment."""
        shipment = {
            "order_id": order_id,
            "tracking_number": tracking_number,
            "carrier": carrier,
            "status": status,
            "estimated_delivery": estimated_delivery,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        self._shipments.append(shipment)
        logger.info(f"Recorded shipment: {order_id} - {carrier} - {status}")
    
    def update_shipment_status(
        self,
        tracking_number: str,
        status: str,
        location: Optional[str] = None
    ):
        """Update shipment status."""
        for shipment in self._shipments:
            if shipment["tracking_number"] == tracking_number:
                shipment["status"] = status
                shipment["updated_at"] = datetime.utcnow().isoformat()
                if location:
                    shipment["current_location"] = location
                logger.info(f"Updated shipment: {tracking_number} - {status}")
                return
        
        logger.warning(f"Shipment not found: {tracking_number}")
    
    def get_dashboard_metrics(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get shipping dashboard metrics.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            {
                "in_transit": int,
                "delivered": int,
                "delayed": int,
                "average_delivery_time": float,
                "carrier_performance": Dict[str, Dict],
                "status_breakdown": Dict[str, int]
            }
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Filter recent shipments
        recent_shipments = [
            s for s in self._shipments
            if datetime.fromisoformat(s["created_at"]) >= cutoff_date
        ]
        
        # Count by status
        status_counts = defaultdict(int)
        for shipment in recent_shipments:
            status_counts[shipment["status"]] += 1
        
        # Calculate delayed shipments
        delayed = 0
        for shipment in recent_shipments:
            if shipment["status"] == "in_transit":
                if shipment.get("estimated_delivery"):
                    try:
                        eta = datetime.fromisoformat(shipment["estimated_delivery"])
                        if eta < datetime.utcnow():
                            delayed += 1
                    except Exception:
                        pass
        
        # Carrier performance
        carrier_performance = defaultdict(lambda: {"total": 0, "delivered": 0, "delayed": 0})
        for shipment in recent_shipments:
            carrier = shipment["carrier"]
            carrier_performance[carrier]["total"] += 1
            if shipment["status"] == "delivered":
                carrier_performance[carrier]["delivered"] += 1
            elif shipment["status"] == "in_transit" and shipment.get("estimated_delivery"):
                try:
                    eta = datetime.fromisoformat(shipment["estimated_delivery"])
                    if eta < datetime.utcnow():
                        carrier_performance[carrier]["delayed"] += 1
                except Exception:
                    pass
        
        # Average delivery time (simplified)
        delivered_shipments = [s for s in recent_shipments if s["status"] == "delivered"]
        average_delivery_time = 5.0  # Stub - calculate from actual data
        
        return {
            "in_transit": status_counts.get("in_transit", 0),
            "delivered": status_counts.get("delivered", 0),
            "delayed": delayed,
            "average_delivery_time": round(average_delivery_time, 1),
            "carrier_performance": dict(carrier_performance),
            "status_breakdown": dict(status_counts),
            "total_shipments": len(recent_shipments),
            "period_days": days,
            "generated_at": datetime.utcnow().isoformat()
        }


# Singleton instance
shipping_analytics_service = ShippingAnalyticsService()
