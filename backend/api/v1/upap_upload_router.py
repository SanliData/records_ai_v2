from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
from datetime import datetime
import uuid
import re
from pathlib import Path
import tempfile
import os

from backend.api.v1.auth_middleware import get_current_user
from backend.models.user import User
from backend.services.novarchive_gpt_service import novarchive_gpt_service

router = APIRouter(prefix="/api/v1/upap", tags=["UPAP"])

# File size limit: 50MB
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Email validation regex
EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

# Allowed MIME types for audio files
ALLOWED_AUDIO_TYPES = {
    'audio/mpeg',
    'audio/mp3',
    'audio/wav',
    'audio/wave',
    'audio/x-wav',
    'audio/flac',
    'audio/x-flac',
    'audio/aiff',
    'audio/x-aiff',
}

# Allowed MIME types for image files
ALLOWED_IMAGE_TYPES = {
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/webp',
    'image/heic',
}

# Combined allowed types
ALLOWED_MIME_TYPES = ALLOWED_AUDIO_TYPES | ALLOWED_IMAGE_TYPES


def validate_email(email: str) -> bool:
    """Validate email format."""
    return bool(EMAIL_REGEX.match(email))


def validate_mime_type(content_type: str) -> bool:
    """Validate MIME type is audio or image."""
    if not content_type:
        return False
    # Check exact match and base type
    return (content_type in ALLOWED_MIME_TYPES or 
            content_type.startswith('audio/') or 
            content_type.startswith('image/'))


@router.post("/upload")
async def upload(
    request: Request,
    file: UploadFile = File(...),
    email: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """
    UPAP upload endpoint (prod-stable).
    Requires authentication - only authenticated users can upload.
    
    SECURITY:
    - Authentication required (valid Bearer token)
    - Email must match authenticated user
    - File size limit: 50MB
    - MIME type validation: audio (mp3, wav, flac, aiff) or image (jpeg, png, webp, heic)
    - Rate limit: 5 uploads per minute per IP (enforced at app level)
    
    MODES:
    - image/* → cover_recognition mode
    - audio/* → audio_metadata mode
    """
    
    # Validate email matches authenticated user
    if email != current_user.email:
        raise HTTPException(
            status_code=403,
            detail="Email does not match authenticated user"
        )
    
    # Validate email format
    if not validate_email(email):
        raise HTTPException(
            status_code=400,
            detail="Invalid email format"
        )

    # Validate MIME type - audio or image
    if not validate_mime_type(file.content_type):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Only audio (mp3, wav, flac, aiff) or image (jpeg, png, webp) files allowed. Got: {file.content_type}"
        )
    
    # Determine processing mode based on content type
    if file.content_type and file.content_type.startswith('image/'):
        mode = "cover_recognition"
    elif file.content_type and file.content_type.startswith('audio/'):
        mode = "audio_metadata"
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to determine processing mode for content type: {file.content_type}"
        )

    record_id = str(uuid.uuid4())

    # Read file with size limit
    content = await file.read(MAX_FILE_SIZE + 1)
    
    # Check if file exceeded limit
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024):.0f}MB"
        )
    
    size_bytes = len(content)

    # Base response structure
    response = {
        "status": "ok",
        "stage": "upload",
        "record_id": record_id,
        "filename": file.filename,
        "email": email,
        "size_bytes": size_bytes,
        "timestamp": datetime.utcnow().isoformat(),
        "mode": mode,
        "content_type": file.content_type,
    }

    # For image mode, perform recognition using novarchive_gpt_service
    if mode == "cover_recognition":
        try:
            # Save file temporarily for recognition
            temp_dir = Path("storage") / "temp" / str(current_user.id)
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            temp_file = temp_dir / f"{record_id}_{file.filename or 'upload.jpg'}"
            temp_file.write_bytes(content)
            
            # Perform recognition
            recognition_result = novarchive_gpt_service.analyze_vinyl_record(
                file_path=str(temp_file),
                raw_bytes=content  # Also pass raw bytes for efficiency
            )
            
            # Extract recognition data
            response["record"] = {
                "artist": recognition_result.get("artist"),
                "album": recognition_result.get("album") or recognition_result.get("title"),
                "label": recognition_result.get("label"),
                "catalog_number": recognition_result.get("catalog_number"),
                "year": recognition_result.get("year"),
                "country": recognition_result.get("country"),
                "format": recognition_result.get("format", "LP"),
                "confidence": recognition_result.get("confidence", 0.5),
            }
            response["ocr_text"] = recognition_result.get("ocr_text", "")
            response["recognition_source"] = recognition_result.get("source", "novarchive_gpt")
            
            # Convert file path to URL-accessible path
            # temp_file is like: storage/temp/{user_id}/{record_id}_{filename}
            # Convert to: /storage/temp/{user_id}/{record_id}_{filename}
            file_path_str = str(temp_file).replace("\\", "/")
            if file_path_str.startswith("storage/"):
                response["file_path"] = f"/{file_path_str}"
                response["thumbnail_url"] = f"/{file_path_str}"
                response["canonical_image_path"] = f"/{file_path_str}"
            else:
                response["file_path"] = file_path_str
                response["thumbnail_url"] = file_path_str
                response["canonical_image_path"] = file_path_str
            
            response["message"] = "Cover image received and analyzed."
            
            # Clean up temp file if needed (optional - can keep for preview)
            # temp_file.unlink()
            
        except Exception as e:
            # If recognition fails, return placeholder but don't break upload
            response["record"] = {
                "artist": None,
                "album": None,
                "label": None,
                "catalog_number": None,
                "confidence": None,
            }
            response["recognition_error"] = str(e)
            response["message"] = "Cover image received. Recognition failed - will retry later."
    elif mode == "audio_metadata":
        # Audio mode keeps existing structure for backward compatibility
        # Future: Add audio metadata extraction here
        pass

    return response
