"""
UPAP Upload Router V2 - AI-Orchestrated Pipeline
Backend owns everything. Frontend only receives preview_id.
"""
import uuid
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import tempfile
import shutil
import os

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.api.v1.auth_middleware import get_current_user
from backend.models.user import User
from backend.models.preview_record_db import PreviewRecordDB
from backend.models.record_state import RecordState
from backend.db import get_db
from backend.services.ai_pipeline import ai_pipeline
from backend.core.file_validation import (
    sanitize_filename,
    validate_path_stays_in_directory,
    validate_file_signature
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/upap", tags=["UPAP"])

# File size limit: 50MB
MAX_FILE_SIZE = 50 * 1024 * 1024


@router.post("/upload")
async def upload_v2(
    file: UploadFile = File(...),
    email: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI-Orchestrated Upload Endpoint V2
    
    Backend automatically:
    1. Saves file
    2. Creates preview record
    3. Enqueues AI pipeline
    4. Returns preview_id only
    
    Frontend MUST NOT:
    - Call OpenAI
    - Generate IDs
    - Enrich metadata
    - Control flow
    """
    
    # Validate email matches authenticated user
    if email != current_user.email:
        raise HTTPException(
            status_code=403,
            detail="Email does not match authenticated user"
        )
    
    # Generate IDs (backend owns this)
    preview_id = str(uuid.uuid4())
    record_id = None  # Will be generated at archive time
    
    # Validate and sanitize filename
    original_filename = file.filename or "upload.jpg"
    safe_filename = sanitize_filename(original_filename, default="upload.jpg")
    
    # Validate file signature
    first_chunk = await file.read(512)
    await file.seek(0)  # Reset for full read
    
    is_valid, detected_type, sig_error = validate_file_signature(
        first_chunk,
        file.content_type
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"File type validation failed: {sig_error}"
        )
    
    # Determine mode
    if file.content_type and file.content_type.startswith('image/'):
        mode = "cover_recognition"
    elif file.content_type and file.content_type.startswith('audio/'):
        mode = "audio_metadata"
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported content type: {file.content_type}"
        )
    
    # Save file to temp location
    temp_dir = Path("storage").resolve() / "temp" / str(current_user.id)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    temp_file = temp_dir / f"{preview_id}_{safe_filename}"
    
    # Verify path safety
    is_safe, path_error = validate_path_stays_in_directory(
        temp_dir.resolve(),
        temp_file.resolve()
    )
    if not is_safe:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid filename: {path_error}"
        )
    
    # Write file
    total_size = 0
    with open(temp_file, "wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)  # 1MB chunks
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                temp_file.unlink()
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large: {total_size} bytes"
                )
            f.write(chunk)
    
    # Convert to standard JPEG for archive
    canonical_image_path = None
    try:
        from backend.services.vision_engine import vision_engine
        
        archive_dir = Path("storage") / "archive" / str(current_user.id)
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        converted_path = vision_engine.save_as_jpeg(
            file_path=temp_file,
            target_dir=archive_dir
        )
        
        # Rename to standard format
        standard_jpeg = archive_dir / f"{preview_id}.jpg"
        if Path(converted_path).exists() and converted_path != str(standard_jpeg):
            Path(converted_path).rename(standard_jpeg)
        canonical_image_path = str(standard_jpeg)
        
    except Exception as e:
        logger.warning(f"JPEG conversion failed: {e}, using temp file")
        canonical_image_path = str(temp_file)
    
    # Create preview record in database
    preview = PreviewRecordDB(
        preview_id=preview_id,
        record_id=record_id,
        state=RecordState.UPLOADED,
        file_path=str(temp_file),
        canonical_image_path=canonical_image_path,
        user_id=str(current_user.id)
    )
    
    db.add(preview)
    db.commit()
    db.refresh(preview)
    
    # RUNTIME PROOF: Log before AI pipeline trigger
    logger.warning(f"[UPLOAD_V2] ⚡ AI PIPELINE TRIGGERED: preview_id={preview_id}")
    print(f"[UPLOAD_V2] ⚡ AI PIPELINE TRIGGERED: preview_id={preview_id}")
    
    # Enqueue AI pipeline (async, non-blocking) with error handling
    async def run_ai_with_proof(preview_id: str):
        """Wrapper to ensure AI pipeline runs and logs proof."""
        try:
            logger.warning(f"[AI_PIPELINE] 🚀 STARTING: preview_id={preview_id}")
            print(f"[AI_PIPELINE] 🚀 STARTING: preview_id={preview_id}")
            result = await ai_pipeline.run_ai_pipeline(preview_id)
            logger.warning(f"[AI_PIPELINE] ✅ COMPLETED: preview_id={preview_id}, state={result.get('state')}")
            print(f"[AI_PIPELINE] ✅ COMPLETED: preview_id={preview_id}, state={result.get('state')}")
            return result
        except Exception as e:
            logger.error(f"[AI_PIPELINE] ❌ FAILED: preview_id={preview_id}, error={e}", exc_info=True)
            print(f"[AI_PIPELINE] ❌ FAILED: preview_id={preview_id}, error={e}")
            raise
    
    # Create task and store reference for debugging
    ai_task = asyncio.create_task(run_ai_with_proof(preview_id))
    logger.warning(f"[UPLOAD_V2] 📋 AI TASK CREATED: preview_id={preview_id}, task={ai_task}")
    print(f"[UPLOAD_V2] 📋 AI TASK CREATED: preview_id={preview_id}")
    
    # Log upload
    logger.info(f"[UPLOAD_V2] File uploaded: preview_id={preview_id}, user_id={current_user.id}, size={total_size}")
    
    # Return ONLY preview_id (backend owns everything else)
    return {
        "status": "ok",
        "preview_id": preview_id,
        "message": "File uploaded. AI pipeline started automatically."
    }
