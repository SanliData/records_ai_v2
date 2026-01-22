"""
UPAP Preview Router V2 - Get Preview with AI Results
Frontend calls this to get AI-analyzed preview data
"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.api.v1.auth_middleware import get_current_user
from backend.models.user import User
from backend.models.preview_record_db import PreviewRecordDB

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/upap", tags=["UPAP"])


@router.get("/preview/{preview_id}")
async def get_preview_v2(
    preview_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get preview record with AI analysis results.
    
    Returns:
        {
            "preview_id": "...",
            "state": "AI_ANALYZED",
            "confidence": 0.83,
            "artist": "...",
            "album": "...",
            "file_path": "...",
            ...
        }
    """
    preview = db.query(PreviewRecordDB).filter(
        PreviewRecordDB.preview_id == preview_id,
        PreviewRecordDB.user_id == str(current_user.id)
    ).first()
    
    if not preview:
        raise HTTPException(
            status_code=404,
            detail=f"Preview record not found: {preview_id}"
        )
    
    # Build response with all metadata
    response = {
        "preview_id": preview.preview_id,
        "record_id": preview.record_id,
        "state": preview.state.value,
        "confidence": preview.confidence,
        "model_used": preview.model_used,
        "cost_estimate": preview.cost_estimate,
        
        # Metadata
        "artist": preview.artist,
        "album": preview.album,
        "title": preview.title,
        "label": preview.label,
        "year": preview.year,
        "catalog_number": preview.catalog_number,
        "format": preview.format,
        "country": preview.country,
        
        # File paths
        "file_path": preview.file_path,
        "canonical_image_path": preview.canonical_image_path,
        "full_image_url": f"/{preview.canonical_image_path.replace('\\', '/')}",
        "label_image_url": f"/{preview.canonical_image_path.replace('\\', '/')}",
        "thumbnail_url": f"/{preview.canonical_image_path.replace('\\', '/')}",
        
        # AI results
        "ocr_text": preview.ocr_text,
        "ai_metadata": preview.ai_metadata,
        
        # Timestamps
        "created_at": preview.created_at.isoformat() if preview.created_at else None,
        "ai_analyzed_at": preview.ai_analyzed_at.isoformat() if preview.ai_analyzed_at else None,
    }
    
    logger.info(f"[PREVIEW_V2] Returning preview: preview_id={preview_id}, state={preview.state.value}, artist={preview.artist}")
    
    return response
