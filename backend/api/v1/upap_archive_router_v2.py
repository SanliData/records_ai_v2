"""
UPAP Archive Router V2 - AI-Orchestrated Pipeline
Backend generates record_id, validates, and archives.
Frontend sends ONLY preview_id.
"""
import uuid
import logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.api.v1.auth_middleware import get_current_user
from backend.models.user import User
from backend.models.preview_record_db import PreviewRecordDB
from backend.models.record_state import RecordState
from backend.models.archive_record_db_v2 import ArchiveRecordDB

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/upap", tags=["UPAP"])


class ArchiveRequest(BaseModel):
    """Frontend sends ONLY preview_id. Backend owns everything else."""
    preview_id: str


@router.post("/archive")
async def archive_v2(
    payload: ArchiveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Archive Endpoint V2 - AI-Orchestrated
    
    Backend must:
    1. Load preview record
    2. Generate record_id
    3. Validate fields
    4. Insert into archive table
    5. Delete temp preview record
    6. Return record_id
    
    Frontend MUST NOT send metadata.
    """
    
    preview_id = payload.preview_id
    
    # Load preview record
    preview = db.query(PreviewRecordDB).filter(
        PreviewRecordDB.preview_id == preview_id,
        PreviewRecordDB.user_id == str(current_user.id)
    ).first()
    
    if not preview:
        raise HTTPException(
            status_code=404,
            detail=f"Preview record not found: {preview_id}"
        )
    
    # Validate state
    if preview.state not in [RecordState.AI_ANALYZED, RecordState.USER_REVIEWED, RecordState.ENRICHED]:
        raise HTTPException(
            status_code=400,
            detail=f"Preview not ready for archive. Current state: {preview.state.value}"
        )
    
    # Generate record_id (backend owns this)
    record_id = str(uuid.uuid4())
    
    # Validate required fields
    if not preview.artist and not preview.album:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields: artist or album must be present"
        )
    
    # Create archive record
    archive_record = ArchiveRecordDB(
        record_id=record_id,
        user_id=str(current_user.id),
        preview_id=preview_id,
        
        # Metadata from preview
        artist=preview.artist,
        album=preview.album,
        title=preview.title,
        label=preview.label,
        year=preview.year,
        catalog_number=preview.catalog_number,
        format=preview.format or "LP",
        country=preview.country,
        
        # File paths
        image_path=preview.canonical_image_path,
        file_path=preview.file_path,
        
        # AI results
        ocr_text=preview.ocr_text,
        ai_metadata=preview.ai_metadata,
        confidence=preview.confidence,
        
        # Pipeline tracking
        model_used=preview.model_used,
        cost_estimate=preview.cost_estimate,
        enrichment_source=preview.enrichment_source,
        
        # State
        state=RecordState.ARCHIVED,
        archived_at=datetime.utcnow()
    )
    
    db.add(archive_record)
    
    # Delete preview record (temp state, no longer needed)
    db.delete(preview)
    
    db.commit()
    
    # Log archive
    logger.info(f"[ARCHIVE_V2] Record archived: record_id={record_id}, preview_id={preview_id}, user_id={current_user.id}")
    
    return {
        "status": "ok",
        "record_id": record_id,
        "message": "Record archived successfully"
    }
