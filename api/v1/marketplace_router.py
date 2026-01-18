# -*- coding: utf-8 -*-
"""
Marketplace Router
Endpoints for creating and managing multi-platform listings.
"""

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from typing import List, Optional
from backend.services.marketplace_service import marketplace_service
from backend.services.user_library_service import user_library_service
from backend.api.v1.auth_middleware import get_current_user

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


@router.post("/create-listings")
async def create_listings(
    archive_id: str = Body(...),
    platforms: List[str] = Body(...),
    price: float = Body(...),
    currency: str = Body("USD"),
    condition: str = Body("VG+"),
    description: Optional[str] = Body(None),
    images: Optional[List[str]] = Body(None),
    user = Depends(get_current_user)
):
    """
    Create listings on multiple platforms for an archive record.
    
    Platforms: ["discogs", "ebay", "etsy", "amazon"]
    
    One-click listing creation across all selected platforms.
    """
    try:
        # Verify record ownership
        record = user_library_service.get_record(archive_id)
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        # Verify ownership
        if (record.get("user_email") != user.email and 
            str(record.get("user_id")) != str(user.id) and
            record.get("user_id_str") != str(user.id)):
            raise HTTPException(status_code=403, detail="Not authorized to create listings for this record")
        
        # Create listings
        result = marketplace_service.create_listings(
            archive_id=archive_id,
            platforms=platforms,
            price=price,
            currency=currency,
            condition=condition,
            description=description,
            images=images
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create listings: {str(e)}")


@router.get("/listings/{archive_id}")
async def get_listings(
    archive_id: str,
    user = Depends(get_current_user)
):
    """
    Get all listings for a specific archive record.
    """
    try:
        # Verify record ownership
        record = user_library_service.get_record(archive_id)
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        # Verify ownership
        if (record.get("user_email") != user.email and 
            str(record.get("user_id")) != str(user.id) and
            record.get("user_id_str") != str(user.id)):
            raise HTTPException(status_code=403, detail="Not authorized to view listings for this record")
        
        listings = marketplace_service.get_record_listings(archive_id)
        
        return {
            "status": "ok",
            "archive_id": archive_id,
            "count": len(listings),
            "listings": listings
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get listings: {str(e)}")


@router.put("/listing/{listing_id}/status")
async def update_listing_status(
    listing_id: str,
    status: str = Body(...),
    sold_price: Optional[float] = Body(None),
    user = Depends(get_current_user)
):
    """
    Update listing status (pending, active, sold, cancelled).
    
    If status is "sold", automatically closes other listings for the same record.
    """
    try:
        listing = marketplace_service.get_listing(listing_id)
        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")
        
        # Verify ownership via archive_id
        archive_id = listing.get("archive_id")
        record = user_library_service.get_record(archive_id)
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        # Verify ownership
        if (record.get("user_email") != user.email and 
            str(record.get("user_id")) != str(user.id) and
            record.get("user_id_str") != str(user.id)):
            raise HTTPException(status_code=403, detail="Not authorized to update this listing")
        
        # Update status
        result = marketplace_service.update_listing_status(
            listing_id=listing_id,
            status=status,
            sold_price=sold_price
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update listing status: {str(e)}")


@router.post("/sync/{archive_id}")
async def sync_listings(
    archive_id: str,
    user = Depends(get_current_user)
):
    """
    Sync listing status across all platforms.
    Closes other listings if one is sold.
    """
    try:
        # Verify record ownership
        record = user_library_service.get_record(archive_id)
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        # Verify ownership
        if (record.get("user_email") != user.email and 
            str(record.get("user_id")) != str(user.id) and
            record.get("user_id_str") != str(user.id)):
            raise HTTPException(status_code=403, detail="Not authorized to sync listings for this record")
        
        result = marketplace_service.sync_listings(archive_id)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync listings: {str(e)}")


@router.post("/quick-sell")
async def quick_sell(
    archive_id: str = Body(...),
    platforms: List[str] = Body(["discogs", "ebay", "etsy", "amazon"]),
    price: Optional[float] = Body(None),
    user = Depends(get_current_user)
):
    """
    Quick sell: Create listings on all platforms with automatic price from archive.
    One-click listing creation.
    """
    try:
        # Get record
        record = user_library_service.get_record(archive_id)
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        # Verify ownership
        if (record.get("user_email") != user.email and 
            str(record.get("user_id")) != str(user.id) and
            record.get("user_id_str") != str(user.id)):
            raise HTTPException(status_code=403, detail="Not authorized to sell this record")
        
        # Determine price
        if not price:
            # Use estimated value or median price
            price = record.get("estimated_value") or record.get("price_median") or record.get("price_high") or 0
            if price == 0:
                price = 25.00  # Default price
        
        # Get condition
        condition = record.get("media_condition") or record.get("condition") or "VG+"
        
        # Get description from record metadata
        description_parts = []
        if record.get("artist"):
            description_parts.append(f"Artist: {record.get('artist')}")
        if record.get("album"):
            description_parts.append(f"Album: {record.get('album')}")
        if record.get("label"):
            description_parts.append(f"Label: {record.get('label')}")
        if record.get("year"):
            description_parts.append(f"Year: {record.get('year')}")
        
        description = "\n".join(description_parts) if description_parts else None
        
        # Get images
        images = []
        if record.get("thumbnail_url"):
            images.append(record.get("thumbnail_url"))
        if record.get("file_path"):
            images.append(record.get("file_path"))
        
        # Create listings
        result = marketplace_service.create_listings(
            archive_id=archive_id,
            platforms=platforms,
            price=price,
            condition=condition,
            description=description,
            images=images
        )
        
        return {
            "status": "ok",
            "message": f"Quick sell: Listings created on {len(platforms)} platform(s)",
            **result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to quick sell: {str(e)}")

