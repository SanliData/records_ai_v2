# backend/api/v1/commerce_router.py
# UTF-8, English only
# Commerce automation endpoints

from fastapi import APIRouter, HTTPException, Depends, Body, Query
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any, Optional, List
from backend.services.commerce.stock_sync_service import stock_sync_service
from backend.services.commerce.auto_pricing_service import auto_pricing_service
from backend.services.commerce.competitor_scraper import competitor_scraper
from backend.services.commerce.sales_analytics_service import sales_analytics_service
from backend.services.commerce.event_trigger_service import event_trigger_service
from backend.api.v1.auth_middleware import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/commerce", tags=["Commerce Automation"])


@router.post("/stock/sync")
async def sync_stock(
    sale_event: Dict[str, Any] = Body(...),
    user = Depends(get_current_user)
):
    """
    Handle stock sync when item is sold.
    
    Body:
        {
            "record_id": str,
            "sold_on_platform": str,
            "listing_ids": Dict[str, str]  # platform -> listing_id
        }
    """
    try:
        result = stock_sync_service.handle_sale(
            record_id=sale_event.get("record_id"),
            sold_on_platform=sale_event.get("sold_on_platform"),
            listing_ids=sale_event.get("listing_ids", {})
        )
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        logger.error(f"Stock sync failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pricing/optimize")
async def optimize_prices(
    records: List[Dict[str, Any]] = Body(...),
    competitor_prices: Optional[Dict[str, Dict[str, float]]] = Body(default=None),
    sales_metrics: Optional[Dict[str, Dict[str, Any]]] = Body(default=None),
    user = Depends(get_current_user)
):
    """
    Optimize prices using OpenAI (nightly strategy).
    
    Body:
        {
            "records": List[Dict],
            "competitor_prices": Optional[Dict],
            "sales_metrics": Optional[Dict]
        }
    """
    try:
        result = auto_pricing_service.optimize_prices(
            records=records,
            competitor_prices=competitor_prices,
            sales_metrics=sales_metrics
        )
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        logger.error(f"Price optimization failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/competitor/prices")
async def get_competitor_prices(
    artist: str = Query(...),
    album: str = Query(...),
    catalog_number: Optional[str] = Query(default=None),
    label: Optional[str] = Query(default=None),
    year: Optional[int] = Query(default=None),
    user = Depends(get_current_user)
):
    """
    Scrape competitor prices from eBay and Discogs.
    """
    try:
        result = competitor_scraper.scrape_competitor_prices(
            artist=artist,
            album=album,
            catalog_number=catalog_number,
            label=label,
            year=year
        )
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        logger.error(f"Competitor scraping failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/dashboard")
async def get_dashboard_metrics(
    days: int = Query(default=30, ge=1, le=365),
    user = Depends(get_current_user)
):
    """
    Get sales analytics dashboard metrics.
    """
    try:
        result = sales_analytics_service.get_dashboard_metrics(days=days)
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        logger.error(f"Analytics failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events/sale")
async def handle_sale_event(
    event: Dict[str, Any] = Body(...),
    user = Depends(get_current_user)
):
    """
    Handle sale event: delist on all other platforms.
    
    Body:
        {
            "record_id": str,
            "sold_on_platform": str,
            "listing_ids": Dict[str, str],
            "price": float
        }
    """
    try:
        result = event_trigger_service.handle_sale_event(
            record_id=event.get("record_id"),
            sold_on_platform=event.get("sold_on_platform"),
            listing_ids=event.get("listing_ids", {}),
            price=event.get("price", 0.0)
        )
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        logger.error(f"Sale event handling failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events/slow-sale")
async def handle_slow_sale_event(
    event: Dict[str, Any] = Body(...),
    user = Depends(get_current_user)
):
    """
    Handle slow sale event: reduce price.
    
    Body:
        {
            "record_id": str,
            "days_on_market": int,
            "current_price": float,
            "views": Optional[int]
        }
    """
    try:
        result = event_trigger_service.handle_slow_sale_event(
            record_id=event.get("record_id"),
            days_on_market=event.get("days_on_market", 0),
            current_price=event.get("current_price", 0.0),
            views=event.get("views", 0)
        )
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        logger.error(f"Slow sale event handling failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events/high-views")
async def handle_high_views_event(
    event: Dict[str, Any] = Body(...),
    user = Depends(get_current_user)
):
    """
    Handle high views event: increase price.
    
    Body:
        {
            "record_id": str,
            "views": int,
            "days_on_market": int,
            "current_price": float
        }
    """
    try:
        result = event_trigger_service.handle_high_views_event(
            record_id=event.get("record_id"),
            views=event.get("views", 0),
            days_on_market=event.get("days_on_market", 0),
            current_price=event.get("current_price", 0.0)
        )
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        logger.error(f"High views event handling failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events/nightly-optimization")
async def process_nightly_optimization(
    records: List[Dict[str, Any]] = Body(...),
    user = Depends(get_current_user)
):
    """
    Process nightly optimization for all active listings.
    
    Uses OpenAI to make intelligent pricing decisions.
    """
    try:
        result = event_trigger_service.process_nightly_optimization(records=records)
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        logger.error(f"Nightly optimization failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
