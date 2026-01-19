# backend/api/v1/upload_router.py
# UTF-8, English only
#
# ⚠️ INTERNAL / DIAGNOSTIC ENDPOINT
# This endpoint bypasses the full UPAP pipeline for testing/debugging.
# NOT for production use - use /api/v1/upap/upload instead.

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db import get_db
from backend.services.upap.engine.upap_engine import upap_engine
from backend.services.upap.auth.auth_stage import AuthStage
from backend.services.upap.upload.upload_stage import UploadStage

router = APIRouter(prefix="/upap", tags=["UPAP Internal"])


@router.post("/upload")
async def upload_only(
    file: UploadFile = File(...),
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    ⚠️ INTERNAL / DIAGNOSTIC ENDPOINT
    
    UPAP – Upload-only entry point (partial pipeline).
    Runs:
    1) AuthStage (direct instantiation)
    2) UploadStage (direct instantiation)
    
    NOTE: This endpoint uses stage instances directly, not through engine.
    This is intentional for diagnostic/testing purposes.
    
    For production use, use /api/v1/upap/upload which follows full pipeline.
    """

    # Direct stage instantiation (bypasses engine for diagnostic purposes)
    auth_stage = AuthStage()
    upload_stage = UploadStage()

    # 1. AUTH
    auth_payload = {"email": email, "db": db}
    try:
        auth_stage.validate_input(auth_payload)
        user_context = auth_stage.run(auth_payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2. UPLOAD
    file_bytes = await file.read()
    upload_payload = {
        "file_bytes": file_bytes,
        "filename": file.filename or "uploaded_file",
        "user_id": user_context.get("user_id", email)
    }
    
    try:
        upload_stage.validate_input(upload_payload)
        upload_context = upload_stage.run(upload_payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "status": "ok",
        "auth": user_context,
        "upload": upload_context
    }
