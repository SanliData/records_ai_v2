# backend/api/v1/shipping_router.py
# UTF-8, English only
# Shipping tracking automation endpoints

from fastapi import APIRouter, HTTPException, Depends, Body, Query, Request
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any, Optional, List
from backend.services.shipping.carrier_connectors import get_carrier_connector
from backend.services.shipping.openai_shipping_service import openai_shipping_service
from backend.services.shipping.channel_update_service import channel_update_service
from backend.services.shipping.shipping_analytics_service import shipping_analytics_service
from backend.services.shipping.shipping_event_service import shipping_event_service
from backend.api.v1.auth_middleware import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/shipping", tags=["Shipping Automation"])


@router.get("/track")
async def track_package(
    tracking_number: str = Query(...),
    carrier: str = Query(..., description="ups|fedex|usps|dhl"),
    user = Depends(get_current_user)
):
    """
    Track package by tracking number and carrier.
    """
    try:
        connector = get_carrier_connector(carrier)
        if not connector:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown carrier: {carrier}. Supported: ups, fedex, usps, dhl"
            )
        
        result = connector.track(tracking_number)
        return JSONResponse(status_code=200, content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tracking failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def webhook_listener(
    request: Request,
    # No auth required for webhooks (can add webhook secret validation)
):
    """
    Webhook listener for carrier tracking events.
    
    Receives tracking updates from carriers and processes them.
    """
    try:
        payload = await request.json()
        
        # Extract tracking information
        tracking_number = payload.get("tracking_number")
        carrier = payload.get("carrier", "").lower()
        status = payload.get("status")
        location = payload.get("location")
        order_id = payload.get("order_id")
        channel_listings = payload.get("channel_listings", {})
        
        if not tracking_number or not carrier:
            raise HTTPException(
                status_code=400,
                detail="Missing tracking_number or carrier"
            )
        
        # Process tracking update
        result = shipping_event_service.handle_tracking_update(
            order_id=order_id or f"order_{tracking_number}",
            tracking_number=tracking_number,
            carrier=carrier,
            status=status or "in_transit",
            location=location,
            channel_listings=channel_listings
        )
        
        return JSONResponse(status_code=200, content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages/generate")
async def generate_customer_message(
    tracking_info: Dict[str, Any] = Body(...),
    order_info: Dict[str, Any] = Body(...),
    user = Depends(get_current_user)
):
    """
    Generate customer-friendly shipping message using OpenAI.
    """
    try:
        result = openai_shipping_service.generate_customer_message(
            tracking_info=tracking_info,
            order_info=order_info
        )
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        logger.error(f"Message generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages/delay")
async def explain_delay(
    tracking_info: Dict[str, Any] = Body(...),
    original_eta: str = Body(...),
    user = Depends(get_current_user)
):
    """
    Generate delay explanation using OpenAI.
    """
    try:
        result = openai_shipping_service.explain_delay(
            tracking_info=tracking_info,
            original_eta=original_eta
        )
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        logger.error(f"Delay explanation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages/predict-eta")
async def predict_eta(
    tracking_info: Dict[str, Any] = Body(...),
    order_info: Dict[str, Any] = Body(...),
    user = Depends(get_current_user)
):
    """
    Predict ETA using OpenAI.
    """
    try:
        result = openai_shipping_service.predict_eta(
            tracking_info=tracking_info,
            order_info=order_info
        )
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        logger.error(f"ETA prediction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/channels/update")
async def update_channel_shipping(
    platform: str = Body(...),
    listing_id: str = Body(...),
    tracking_number: str = Body(...),
    carrier: str = Body(...),
    status: str = Body(...),
    user = Depends(get_current_user)
):
    """
    Update shipping status on a specific channel.
    """
    try:
        result = channel_update_service.update_shipping_status(
            platform=platform,
            listing_id=listing_id,
            tracking_number=tracking_number,
            carrier=carrier,
            status=status
        )
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        logger.error(f"Channel update failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/dashboard")
async def get_shipping_dashboard(
    days: int = Query(default=30, ge=1, le=365),
    user = Depends(get_current_user)
):
    """
    Get shipping dashboard metrics.
    """
    try:
        result = shipping_analytics_service.get_dashboard_metrics(days=days)
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        logger.error(f"Analytics failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events/delay")
async def handle_delay_event(
    event: Dict[str, Any] = Body(...),
    user = Depends(get_current_user)
):
    """
    Handle delay event: notify customer.
    """
    try:
        result = shipping_event_service.handle_delay_event(
            order_id=event.get("order_id"),
            tracking_number=event.get("tracking_number"),
            carrier=event.get("carrier"),
            original_eta=event.get("original_eta"),
            current_status=event.get("current_status", "in_transit"),
            current_location=event.get("current_location", "Unknown")
        )
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        logger.error(f"Delay event handling failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events/delivered")
async def handle_delivered_event(
    event: Dict[str, Any] = Body(...),
    user = Depends(get_current_user)
):
    """
    Handle delivered event: close sale on all channels.
    """
    try:
        result = shipping_event_service.handle_delivered_event(
            order_id=event.get("order_id"),
            tracking_number=event.get("tracking_number"),
            carrier=event.get("carrier"),
            channel_listings=event.get("channel_listings", {}),
            delivered_at=event.get("delivered_at")
        )
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        logger.error(f"Delivered event handling failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
