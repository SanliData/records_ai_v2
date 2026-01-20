# -*- coding: utf-8 -*-
"""
Discogs Collection Router
Endpoints for adding records to Discogs collection.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Optional, Dict, Any
from pydantic import BaseModel
import logging

from backend.api.v1.auth_middleware import get_current_user
from backend.services.discogs_collection_service import discogs_collection_service
from backend.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/discogs", tags=["Discogs Collection"])


class AddToCollectionRequest(BaseModel):
    """Request model for adding record to Discogs collection."""
    artist: str
    album: str
    catalog_number: Optional[str] = None
    label: Optional[str] = None
    year: Optional[int] = None
    discogs_username: str
    folder_id: int = 0  # 0 = default "All" folder
    notes: Optional[str] = None


@router.post("/collection/add")
async def add_to_collection(
    request: AddToCollectionRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Add a record to user's Discogs collection.
    
    Steps:
    1. Search Discogs for the release matching artist/album
    2. Add the found release to user's Discogs collection
    
    Requires:
    - Authenticated user
    - DISCOGS_TOKEN environment variable
    - User's Discogs username
    """
    try:
        # Step 1: Search Discogs for the release
        logger.info(f"[Discogs] Searching for: {request.artist} - {request.album}")
        
        search_result = discogs_collection_service.search_release(
            artist=request.artist,
            album=request.album,
            catalog_number=request.catalog_number,
            label=request.label,
            year=request.year
        )
        
        if not search_result:
            return {
                "status": "error",
                "error": "Release not found on Discogs",
                "message": f"Could not find '{request.artist} - {request.album}' on Discogs"
            }
        
        release_id = search_result.get("release_id")
        match_score = search_result.get("match_score", 0.0)
        
        logger.info(f"[Discogs] Found release {release_id} (match score: {match_score:.2f})")
        
        # Step 2: Add to collection
        add_result = discogs_collection_service.add_to_collection(
            discogs_username=request.discogs_username,
            release_id=release_id,
            folder_id=request.folder_id,
            notes=request.notes
        )
        
        if add_result.get("status") == "error":
            return add_result
        
        # Combine results
        return {
            "status": "ok",
            "message": "Record added to Discogs collection",
            "release_id": release_id,
            "match_score": match_score,
            "discogs_url": search_result.get("url"),
            "collection_result": add_result
        }
        
    except Exception as e:
        logger.error(f"[Discogs] Error adding to collection: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add to Discogs collection: {str(e)}"
        )


@router.get("/collection/search")
async def search_discogs(
    artist: str = Query(..., description="Artist name"),
    album: str = Query(..., description="Album name"),
    catalog_number: Optional[str] = Query(None, description="Catalog number"),
    label: Optional[str] = Query(None, description="Label name"),
    year: Optional[int] = Query(None, description="Release year"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Search Discogs for a release without adding to collection.
    Useful for previewing what will be added.
    """
    try:
        search_result = discogs_collection_service.search_release(
            artist=artist,
            album=album,
            catalog_number=catalog_number,
            label=label,
            year=year
        )
        
        if not search_result:
            return {
                "status": "error",
                "error": "Release not found on Discogs",
                "message": f"Could not find '{artist} - {album}' on Discogs"
            }
        
        return {
            "status": "ok",
            "release": search_result
        }
        
    except Exception as e:
        logger.error(f"[Discogs] Search error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Discogs search failed: {str(e)}"
        )


@router.get("/collection/folders")
async def get_collection_folders(
    discogs_username: str = Query(..., description="Discogs username"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get user's Discogs collection folders.
    """
    try:
        result = discogs_collection_service.get_user_folders(discogs_username)
        return result
        
    except Exception as e:
        logger.error(f"[Discogs] Error getting folders: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get Discogs folders: {str(e)}"
        )
