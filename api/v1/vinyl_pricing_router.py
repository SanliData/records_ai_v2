# -*- coding: utf-8 -*-
"""
Vinyl Pricing Router
Endpoints for fetching market prices and calculating record values.
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional
from backend.services.vinyl_pricing_service import vinyl_pricing_service
from backend.api.v1.auth_middleware import get_current_user

router = APIRouter(prefix="/vinyl/pricing", tags=["Vinyl Pricing"])


@router.get("/market-prices")
def get_market_prices(
    artist: str = Query(...),
    album: str = Query(...),
    catalog_number: Optional[str] = Query(None),
    label: Optional[str] = Query(None),
    user = Depends(get_current_user)
):
    """
    Fetch market prices for a vinyl record from Discogs.
    Authentication required.
    """
    try:
        prices = vinyl_pricing_service.get_market_prices(
            artist=artist,
            album=album,
            catalog_number=catalog_number,
            label=label
        )
        return {
            "status": "ok",
            "prices": prices
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch market prices: {str(e)}")


@router.get("/estimate-value")
def estimate_value(
    artist: str = Query(...),
    album: str = Query(...),
    condition: Optional[str] = Query(None, description="Condition code: M, NM, VG+, VG, G+, G, P"),
    user_estimate: Optional[float] = Query(None, description="User's manual price estimate"),
    catalog_number: Optional[str] = Query(None),
    label: Optional[str] = Query(None),
    user = Depends(get_current_user)
):
    """
    Calculate estimated value for a vinyl record.
    Considers market prices and condition.
    Authentication required.
    """
    try:
        # Get market prices
        market_prices = vinyl_pricing_service.get_market_prices(
            artist=artist,
            album=album,
            catalog_number=catalog_number,
            label=label
        )
        
        # Calculate estimated value
        estimate = vinyl_pricing_service.get_estimated_value(
            market_prices=market_prices,
            condition=condition,
            user_estimate=user_estimate
        )
        
        return {
            "status": "ok",
            "estimate": estimate,
            "market_prices": market_prices
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to estimate value: {str(e)}")


@router.get("/release-info")
def get_release_info(
    artist: str = Query(...),
    album: str = Query(...),
    catalog_number: Optional[str] = Query(None),
    label: Optional[str] = Query(None),
    user = Depends(get_current_user)
):
    """
    Get comprehensive release information from Discogs.
    Includes metadata, images, tracklist, etc.
    Authentication required.
    """
    try:
        info = vinyl_pricing_service.get_release_info(
            artist=artist,
            album=album,
            catalog_number=catalog_number,
            label=label
        )
        return {
            "status": "ok",
            "release_info": info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch release info: {str(e)}")


@router.get("/condition-multipliers")
def get_condition_multipliers():
    """
    Get condition multiplier reference.
    No authentication required (reference data).
    """
    from backend.services.vinyl_pricing_service import CONDITION_MULTIPLIERS
    
    return {
        "status": "ok",
        "multipliers": CONDITION_MULTIPLIERS,
        "condition_codes": {
            "M": "Mint (100%)",
            "NM": "Near Mint (95%)",
            "VG+": "Very Good Plus (85%)",
            "VG": "Very Good (70%)",
            "G+": "Good Plus (50%)",
            "G": "Good (30%)",
            "P": "Poor (10%)"
        }
    }
