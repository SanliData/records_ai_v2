# backend/api/v1/channels_publish_router.py
# UTF-8, English only
# Multi-channel publishing endpoint

from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any, Optional
from backend.services.openai_channel_orchestrator import openai_channel_orchestrator
from backend.services.channels.ebay import ebay_connector
from backend.services.channels.discogs import discogs_connector
from backend.services.channels.shopify import shopify_connector
from backend.services.channels.etsy import etsy_connector
from backend.api.v1.auth_middleware import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/channels", tags=["Multi-Channel Publishing"])


@router.post("/publish")
async def publish_to_channels(
    record: Dict[str, Any] = Body(...),
    auto_publish: bool = Body(default=False, description="Auto-publish without approval (default: False)"),
    user = Depends(get_current_user)
):
    """
    Orchestrate multi-channel publishing for archived record.
    
    Flow:
    1. Record already archived
    2. Send record to OpenAI
    3. OpenAI decides: platforms, titles, descriptions, prices
    4. System prepares publishing (requires user approval unless auto_publish=True)
    5. Return result report
    
    Args:
        record: Archived record with metadata (artist, album, label, year, etc.)
        auto_publish: If True, automatically publish to platforms (default: False)
    
    Returns:
        {
            "orchestration": {
                "platforms": [...],
                "strategy": {...}
            },
            "publishing_results": {
                "ebay": {...},
                "discogs": {...},
                ...
            },
            "summary": {
                "total_platforms": int,
                "successful": int,
                "failed": int,
                "requires_approval": bool
            }
        }
    """
    try:
        # Step 1: Orchestrate with OpenAI
        logger.info(f"Orchestrating publishing for: {record.get('artist')} - {record.get('album')}")
        orchestration = openai_channel_orchestrator.orchestrate_publishing(record)
        
        if orchestration.get("error"):
            raise HTTPException(
                status_code=500,
                detail=f"OpenAI orchestration failed: {orchestration.get('error')}"
            )
        
        platforms = orchestration.get("platforms", [])
        if not platforms:
            return JSONResponse(
                status_code=200,
                content={
                    "orchestration": orchestration,
                    "publishing_results": {},
                    "summary": {
                        "total_platforms": 0,
                        "successful": 0,
                        "failed": 0,
                        "requires_approval": True,
                        "message": "No platforms recommended by OpenAI"
                    }
                }
            )
        
        # Step 2: Prepare publishing (requires approval unless auto_publish=True)
        publishing_results = {}
        successful = 0
        failed = 0
        
        if auto_publish:
            # Auto-publish to all recommended platforms
            for platform_config in platforms:
                platform_name = platform_config.get("platform", "").lower()
                result = await _publish_to_platform(
                    platform_name,
                    platform_config,
                    record
                )
                publishing_results[platform_name] = result
                if result.get("success"):
                    successful += 1
                else:
                    failed += 1
        else:
            # Prepare but don't publish (requires user approval)
            for platform_config in platforms:
                platform_name = platform_config.get("platform", "").lower()
                publishing_results[platform_name] = {
                    "prepared": True,
                    "requires_approval": True,
                    "config": platform_config,
                    "message": "Ready for publishing - approval required"
                }
        
        # Step 3: Return result report
        summary = {
            "total_platforms": len(platforms),
            "successful": successful,
            "failed": failed,
            "requires_approval": not auto_publish,
            "message": "Publishing orchestrated successfully" if not auto_publish else f"Published to {successful} platform(s)"
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "orchestration": orchestration,
                "publishing_results": publishing_results,
                "summary": summary
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in /channels/publish: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


async def _publish_to_platform(
    platform_name: str,
    platform_config: Dict[str, Any],
    record: Dict[str, Any]
) -> Dict[str, Any]:
    """Publish to specific platform."""
    title = platform_config.get("title", "")
    description = platform_config.get("description", "")
    price = platform_config.get("price", 0.0)
    currency = platform_config.get("currency", "USD")
    category = platform_config.get("category", "")
    tags = platform_config.get("tags", [])
    
    # Get images from record if available
    images = []
    if record.get("file_path"):
        images.append(record.get("file_path"))
    if record.get("thumbnail_url"):
        images.append(record.get("thumbnail_url"))
    
    try:
        if platform_name == "ebay":
            return ebay_connector.publish_listing(
                title=title,
                description=description,
                price=price,
                currency=currency,
                category=category,
                tags=tags,
                images=images
            )
        elif platform_name == "discogs":
            return discogs_connector.publish_listing(
                title=title,
                description=description,
                price=price,
                currency=currency,
                condition=record.get("condition", "VG+"),
                images=images
            )
        elif platform_name == "shopify":
            return shopify_connector.publish_listing(
                title=title,
                description=description,
                price=price,
                currency=currency,
                category=category,
                tags=tags,
                images=images
            )
        elif platform_name == "etsy":
            return etsy_connector.publish_listing(
                title=title,
                description=description,
                price=price,
                currency=currency,
                category=category,
                tags=tags,
                images=images
            )
        else:
            return {
                "success": False,
                "error": f"Unknown platform: {platform_name}",
                "listing_id": None,
                "url": None
            }
    except Exception as e:
        logger.error(f"Failed to publish to {platform_name}: {e}")
        return {
            "success": False,
            "error": str(e),
            "listing_id": None,
            "url": None
        }
