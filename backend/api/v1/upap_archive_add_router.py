from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.db import get_db
from backend.api.v1.auth_middleware import get_current_user
from backend.models.user import User
from backend.services.upap.engine.upap_engine import upap_engine

router = APIRouter(prefix="/api/v1/upap", tags=["UPAP"])

class ArchiveAddRequest(BaseModel):
    preview_id: str | None = None
    record_id: str | None = None
    artist: str
    album: str
    title: str | None = None
    label: str | None = None
    year: str | None = None
    catalog_number: str | None = None
    country: str | None = None
    format: str | None = None
    file_path: str | None = None
    matrix_info: str | None = None
    side: str | None = None
    ocr_text: str | None = None

@router.post("/archive/add")
async def add_to_archive(
    payload: ArchiveAddRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add record to archive using UPAP archive stage.
    Requires authentication.
    """
    # Use record_id or preview_id
    record_id = payload.record_id or payload.preview_id
    
    if not record_id:
        raise HTTPException(status_code=400, detail="record_id or preview_id is required")
    
    try:
        # Use UPAP engine to archive the record
        result = upap_engine.run_archive(record_id)
        return {
            "status": "ok",
            "message": "Record added to archive",
            "record_id": record_id,
            "archive_result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to archive record: {str(e)}")
