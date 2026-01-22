"""
UPAP Debug Router - Runtime Proof Verification
CEO-level accountability: Prove AI pipeline executed
"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pathlib import Path

from backend.db import get_db
from backend.api.v1.auth_middleware import get_current_user
from backend.models.user import User
from backend.models.preview_record_db import PreviewRecordDB
from backend.services.pipeline_logger import pipeline_logger

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/upap/debug", tags=["UPAP Debug"])


@router.get("/preview/{preview_id}/status")
async def get_preview_status(
    preview_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get preview status with runtime proof.
    CEO-level accountability endpoint.
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
    
    # Get pipeline logs
    logs = pipeline_logger.get_logs(preview_id)
    
    # Check if AI pipeline executed
    ai_logs = [log for log in logs if "AI_PIPELINE" in log.get("step", "")]
    has_ai_execution = len(ai_logs) > 0
    
    # Build proof response
    response = {
        "preview_id": preview_id,
        "state": preview.state.value,
        
        # Runtime Proof
        "runtime_proof": {
            "preview_exists": True,
            "state_in_db": preview.state.value,
            "ai_analyzed_at": preview.ai_analyzed_at.isoformat() if preview.ai_analyzed_at else None,
            "has_ai_execution_logs": has_ai_execution,
            "log_count": len(logs),
            "ai_log_count": len(ai_logs)
        },
        
        # Metadata (proof AI extracted data)
        "metadata_proof": {
            "artist": preview.artist,
            "album": preview.album,
            "label": preview.label,
            "confidence": preview.confidence,
            "model_used": preview.model_used,
            "has_metadata": bool(preview.artist or preview.album)
        },
        
        # Pipeline logs
        "logs": logs[-10:],  # Last 10 logs
        
        # File proof
        "file_proof": {
            "file_path": preview.file_path,
            "canonical_image_path": preview.canonical_image_path,
            "file_exists": Path(preview.canonical_image_path).exists() if preview.canonical_image_path else False
        }
    }
    
    return response
