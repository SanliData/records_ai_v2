from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
from datetime import datetime
import uuid
import re

from backend.api.v1.auth_middleware import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/api/v1/upap", tags=["UPAP"])

# File size limit: 50MB
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Email validation regex
EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

# Allowed MIME types for audio files
ALLOWED_MIME_TYPES = {
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


def validate_email(email: str) -> bool:
    """Validate email format."""
    return bool(EMAIL_REGEX.match(email))


def validate_mime_type(content_type: str) -> bool:
    """Validate MIME type is audio."""
    if not content_type:
        return False
    # Check exact match and base type
    return content_type in ALLOWED_MIME_TYPES or content_type.startswith('audio/')


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
    - MIME type validation: audio only (mp3, wav, flac, aiff)
    - Rate limit: 5 uploads per minute per IP (enforced at app level)
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

    # Validate MIME type - audio only
    if not validate_mime_type(file.content_type):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Only audio files allowed (mp3, wav, flac, aiff). Got: {file.content_type}"
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

    return {
        "status": "ok",
        "stage": "upload",
        "record_id": record_id,
        "filename": file.filename,
        "email": email,
        "size_bytes": size_bytes,
        "timestamp": datetime.utcnow().isoformat(),
    }
