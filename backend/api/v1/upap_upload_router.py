from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
from datetime import datetime
import uuid
import re
from pathlib import Path
import tempfile
import os
import logging

from backend.api.v1.auth_middleware import get_current_user
from backend.models.user import User
from backend.services.novarchive_gpt_service import novarchive_gpt_service
from backend.services.image_enhancement_service import image_enhancement_service
from backend.core.file_validation import (
    sanitize_filename,
    validate_path_stays_in_directory,
    validate_file_signature
)

logger = logging.getLogger(__name__)

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
    """
    # #region agent log - Entry point
    import json
    import os
    try:
        log_dir = r"c:\Users\issan\records_ai_v2\.cursor"
        log_path = os.path.join(log_dir, "debug.log")
        os.makedirs(log_dir, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps({
                "id": "log_upload_endpoint_entry",
                "timestamp": int(datetime.now().timestamp() * 1000),
                "location": "upap_upload_router.py:71",
                "message": "Upload endpoint ENTRY - BEFORE auth dependency",
                "data": {
                    "endpoint": "/api/v1/upap/upload",
                    "filename": file.filename,
                    "email": email
                },
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "ENTRY"
            }) + "\n")
    except Exception as e:
        logger.error(f"Failed to write entry log: {e}", exc_info=True)
    # #endregion
    
    """
    
    SECURITY:
    - Authentication required (valid Bearer token)
    - Email must match authenticated user
    - File size limit: 50MB
    - MIME type validation: audio (mp3, wav, flac, aiff) or image (jpeg, png, webp, heic)
    - Magic bytes validation: File signature must match declared type
    - Filename sanitization: Path traversal protection
    - Rate limit: 20 uploads per minute per IP (enforced at app level)
    
    MODES:
    - image/* → cover_recognition mode
    - audio/* → audio_metadata mode
    """
    # #region agent log
    import json
    import os
    try:
        with open(r"c:\Users\issan\records_ai_v2\.cursor\debug.log", "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps({
                "id": f"log_upload_entry",
                "timestamp": int(datetime.now().timestamp() * 1000),
                "location": "upap_upload_router.py:95",
                "message": "Upload endpoint entry",
                "data": {
                    "has_auth": current_user is not None,
                    "user_email": current_user.email if current_user else None,
                    "form_email": email,
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "emails_match": current_user.email == email if current_user else False
                },
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "A"
            }) + "\n")
    except Exception:
        pass
    # #endregion
    
    # P1-3: Rate limiting handled at app level via slowapi decorator or middleware
    # Individual endpoint doesn't need explicit check if decorator/middleware is applied
    
    # P0-1: CRITICAL - Validate filename FIRST (before auth checks to prevent attacks even if auth bypassed)
    # This MUST happen first to prevent path traversal attacks
    original_filename = file.filename or "upload.jpg"
    
    # #region agent log
    try:
        with open(r"c:\Users\issan\records_ai_v2\.cursor\debug.log", "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps({
                "id": f"log_filename_check",
                "timestamp": int(datetime.now().timestamp() * 1000),
                "location": "upap_upload_router.py:104",
                "message": "Checking filename for path traversal",
                "data": {
                    "original_filename": original_filename,
                    "has_dotdot": ".." in original_filename,
                    "starts_with_slash": original_filename.startswith("/") or original_filename.startswith("\\"),
                    "has_backslash": "\\" in original_filename
                },
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "D"
            }) + "\n")
    except Exception:
        pass
    # #endregion
    
    # Check for path traversal patterns BEFORE any processing
    if ".." in original_filename or original_filename.startswith("/") or original_filename.startswith("\\") or "\\" in original_filename:
        logger.error(f"[UPLOAD] CRITICAL: Path traversal detected in filename: {original_filename}")
        # #region agent log
        try:
            with open(r"c:\Users\issan\records_ai_v2\.cursor\debug.log", "a", encoding="utf-8") as log_file:
                log_file.write(json.dumps({
                    "id": f"log_path_traversal_blocked",
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "location": "upap_upload_router.py:118",
                    "message": "Path traversal BLOCKED",
                    "data": {
                        "filename": original_filename
                    },
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "D"
                }) + "\n")
        except Exception:
            pass
        # #endregion
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid filename",
                "detail": "Path traversal detected in filename",
                "filename": original_filename,
                "message": "Filename contains path traversal sequences (../ or leading slashes)."
            }
        )
    
    # Check filename length BEFORE processing
    if len(original_filename) > 255:  # Filesystem limit is usually 255 chars
        logger.error(f"[UPLOAD] CRITICAL: Filename too long: {len(original_filename)} chars")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Filename too long",
                "detail": f"Filename length {len(original_filename)} exceeds maximum 255 characters",
                "filename_length": len(original_filename),
                "max_length": 255
            }
        )
    
    # Sanitize filename BEFORE using it
    safe_filename = sanitize_filename(original_filename, default="upload.jpg")
    
    # Double-check sanitized filename is safe
    if ".." in safe_filename or "/" in safe_filename or "\\" in safe_filename:
        logger.error(f"[UPLOAD] CRITICAL: Filename sanitization failed: {original_filename} -> {safe_filename}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid filename after sanitization",
                "detail": "Filename still contains dangerous characters after sanitization",
                "original_filename": original_filename,
                "sanitized_filename": safe_filename
            }
        )
    
    # Validate email matches authenticated user
    if email != current_user.email:
        # #region agent log
        try:
            with open(r"c:\Users\issan\records_ai_v2\.cursor\debug.log", "a", encoding="utf-8") as log_file:
                log_file.write(json.dumps({
                    "id": f"log_email_mismatch",
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "location": "upap_upload_router.py:148",
                    "message": "Email mismatch - rejecting",
                    "data": {
                        "user_email": current_user.email,
                        "form_email": email
                    },
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "A"
                }) + "\n")
        except Exception:
            pass
        # #endregion
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

    # P1-1: Memory Exhaustion Protection - Stream directly to temp file
    # Read file in chunks and write directly to disk to avoid loading entire file into memory
    # BUT: Validate signature from first chunk BEFORE writing full file
    import tempfile
    import shutil
    CHUNK_SIZE = 1024 * 1024  # 1MB chunks
    temp_file = None
    temp_file_path = None
    signature_bytes = None
    content = None
    total_size = 0
    first_chunk = None
    
    try:
        # Read first chunk to validate signature BEFORE writing to disk
        first_chunk = await file.read(512)  # Read first 512 bytes for signature validation
        if not first_chunk or len(first_chunk) < 4:
            raise HTTPException(
                status_code=400,
                detail="File too small to validate"
            )
        
        # P0-2: CRITICAL - Validate file signature BEFORE writing to disk
        validation_content = first_chunk
        is_valid, detected_type, sig_error = validate_file_signature(validation_content, file.content_type)
        
        if not is_valid:
            logger.error(
                f"[UPLOAD] CRITICAL: MIME type mismatch - declared={file.content_type}, "
                f"detected={detected_type}, error={sig_error}"
            )
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "File type validation failed",
                    "detail": sig_error,
                    "declared_type": file.content_type,
                    "detected_type": detected_type,
                    "expected": ["image/jpeg", "image/png", "image/webp", "image/heic",
                               "audio/mpeg", "audio/wav", "audio/flac", "audio/aiff"],
                    "message": "File signature does not match declared type. Possible MIME spoofing attack."
                }
            )
        
        # Signature validated - now create temp file and write
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".tmp")
        temp_file_path = temp_file.name
        
        # Write first chunk
        temp_file.write(first_chunk)
        total_size = len(first_chunk)
        signature_bytes = first_chunk
        
        try:
            # Continue reading and writing remaining chunks
            while True:
                chunk = await file.read(CHUNK_SIZE)
                if not chunk:
                    break
                
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE:
                    # Clean up temp file
                    temp_file.close()
                    try:
                        os.unlink(temp_file_path)
                    except:
                        pass
                    raise HTTPException(
                        status_code=413,
                        detail={
                            "error": "File too large",
                            "max_size_mb": MAX_FILE_SIZE / (1024*1024),
                            "received_size_mb": total_size / (1024*1024)
                        }
                    )
                
                # Write chunk directly to disk
                temp_file.write(chunk)
        finally:
            temp_file.close()
        
        # Read full content for processing (but validation already happened)
        with open(temp_file_path, "rb") as f:
            content = f.read()
        
        size_bytes = len(content)
        
    except HTTPException:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass
        raise
    except Exception as e:
        logger.error(f"[UPLOAD] Error reading file: {e}", exc_info=True)
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass
        raise HTTPException(
            status_code=400,
            detail="Error reading uploaded file"
        )
    
    # File signature already validated above (before writing to disk)

    # Base response structure
    response = {
        "status": "ok",
        "stage": "upload",
        "record_id": record_id,
        "filename": safe_filename,  # Use sanitized filename, not original
        "email": email,
        "size_bytes": size_bytes,
        "timestamp": datetime.utcnow().isoformat(),
        "mode": mode,
        "content_type": file.content_type,
    }

    # For image mode, perform recognition using novarchive_gpt_service
    # Filename already validated and sanitized above
    if mode == "cover_recognition":
        try:
            
            # Step 4: Create temp directory (use absolute path)
            temp_dir = Path("storage").resolve() / "temp" / str(current_user.id)
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Step 5: Create target path with sanitized filename
            temp_file = temp_dir / f"{record_id}_{safe_filename}"
            
            # Step 6: Verify path stays within temp_dir (final check before writing)
            is_safe, path_error = validate_path_stays_in_directory(temp_dir.resolve(), temp_file.resolve())
            if not is_safe:
                logger.error(f"[UPLOAD] Path traversal detected after sanitization: {path_error}")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid filename: path traversal detected"
                )
            
            # Step 7: Use the already-written temp file, or copy content to final location
            # Move temp file to final location if it exists, otherwise write content
            if temp_file_path and os.path.exists(temp_file_path):
                shutil.move(temp_file_path, temp_file)
                # Re-read for processing (but file is already on disk)
                content = temp_file.read_bytes()
            else:
                # If temp file doesn't exist (shouldn't happen), write content directly
                temp_file.write_bytes(content)
                # Clean up original temp file if it exists
                if temp_file_path and os.path.exists(temp_file_path):
                    try:
                        os.unlink(temp_file_path)
                    except:
                        pass
            
            logger.info(f"[UPLOAD] Processing image: {temp_file}, user_id: {current_user.id}, record_id: {record_id}")
            
            # Convert to standard JPEG format for archive
            standard_jpeg_path = None
            try:
                from backend.services.vision_engine import vision_engine
                
                # Create archive directory for standard JPEG storage
                archive_dir = Path("storage") / "archive" / str(current_user.id)
                archive_dir.mkdir(parents=True, exist_ok=True)
                
                # Convert to standard JPEG: {record_id}.jpg
                # First convert to JPEG, then rename to standard format
                converted_path = vision_engine.save_as_jpeg(
                    file_path=temp_file,
                    target_dir=archive_dir
                )
                
                # Rename to standard format: {record_id}.jpg
                standard_jpeg = archive_dir / f"{record_id}.jpg"
                if Path(converted_path).exists() and converted_path != str(standard_jpeg):
                    Path(converted_path).rename(standard_jpeg)
                    standard_jpeg_path = str(standard_jpeg)
                else:
                    standard_jpeg_path = converted_path
                
                logger.info(f"[UPLOAD] Image converted to standard JPEG: {standard_jpeg_path}")
            except Exception as conv_error:
                # If conversion fails, use temp file (fallback)
                logger.warning(f"[UPLOAD] JPEG conversion failed: {conv_error}, using temp file")
                standard_jpeg_path = None
            
            # Step 3: Perform recognition using enhanced image if available, otherwise use standard JPEG or original
            recognition_image_path = enhanced_image_path if enhanced_image_path and Path(enhanced_image_path).exists() else (
                standard_jpeg_path if standard_jpeg_path and Path(standard_jpeg_path).exists() else str(temp_file)
            )
            
            # Use enhanced image bytes if available for recognition
            recognition_bytes = enhancement_result.get("enhanced_image_bytes") if enhancement_result and enhancement_result.get("enhanced") else content
            
            recognition_result = novarchive_gpt_service.analyze_vinyl_record(
                file_path=recognition_image_path,
                raw_bytes=recognition_bytes
            )
            
            logger.info(f"[UPLOAD] Recognition result: artist={recognition_result.get('artist')}, album={recognition_result.get('album')}, confidence={recognition_result.get('confidence')}")
            
            # FLATTEN RESPONSE: Merge record fields to top level for frontend compatibility
            # Extract recognition data - put in nested "record" AND top level for compatibility
            record_data = {
                "artist": recognition_result.get("artist"),
                "album": recognition_result.get("album") or recognition_result.get("title"),
                "label": recognition_result.get("label"),
                "catalog_number": recognition_result.get("catalog_number"),
                "year": recognition_result.get("year"),
                "country": recognition_result.get("country"),
                "format": recognition_result.get("format", "LP"),
                "confidence": recognition_result.get("confidence", 0.5),
            }
            
            # Keep nested record for backward compatibility
            response["record"] = record_data
            
            # ALSO flatten to top level so frontend can access directly
            response.update(record_data)
            
            response["ocr_text"] = recognition_result.get("ocr_text", "")
            response["recognition_source"] = recognition_result.get("source", "novarchive_gpt")
            
            # Add enhancement info to response
            if enhancement_result:
                response["enhancement"] = {
                    "enhanced": enhancement_result.get("enhanced", False),
                    "quality_score": enhancement_result.get("quality_info", {}).get("quality_score", 0.0),
                    "quality_improvement": enhancement_result.get("quality_improvement", 0.0),
                    "enhancement_time": enhancement_result.get("enhancement_time", 0.0),
                    "original_quality": enhancement_result.get("quality_info", {}).get("quality_score", 0.0),
                    "enhanced_quality": enhancement_result.get("enhanced_quality_info", {}).get("quality_score", 0.0) if enhancement_result.get("enhanced") else None
                }
                
                if enhanced_image_path:
                    enhanced_url = f"/{str(enhanced_image_path).replace('\\', '/')}"
                    if not enhanced_url.startswith("/"):
                        enhanced_url = f"/{enhanced_url}"
                    response["enhanced_image_url"] = enhanced_url
                    response["enhancement"]["enhanced_image_path"] = enhanced_url
            
            # Convert file path to URL-accessible path
            # Use standard JPEG if available, otherwise use temp file
            canonical_path = standard_jpeg_path if standard_jpeg_path and Path(standard_jpeg_path).exists() else str(temp_file)
            
            # URL-accessible path for standard JPEG: /storage/archive/{user_id}/{record_id}.jpg
            # or temp file: /storage/temp/{user_id}/{record_id}_{filename}
            file_path_str = canonical_path.replace("\\", "/")
            if file_path_str.startswith("storage/"):
                image_url = f"/{file_path_str}"
            else:
                image_url = f"/{file_path_str}"
            
            response["file_path"] = image_url
            response["thumbnail_url"] = image_url
            response["canonical_image_path"] = image_url
            
            # Standard JPEG path for archive (for future reference)
            if standard_jpeg_path and Path(standard_jpeg_path).exists():
                standard_jpeg_url = f"/{str(standard_jpeg_path).replace('\\', '/')}"
                if not standard_jpeg_url.startswith("/"):
                    standard_jpeg_url = f"/{standard_jpeg_url}"
                response["standard_jpeg_path"] = standard_jpeg_url
                response["archive_image_path"] = standard_jpeg_url
            
            # Also add full_image_url and label_image_url for frontend
            response["full_image_url"] = image_url
            response["label_image_url"] = image_url
            
            # Add original image URL
            if original_image_path:
                original_url = f"/{str(original_image_path).replace('\\', '/')}"
                if not original_url.startswith("/"):
                    original_url = f"/{original_url}"
                response["original_image_url"] = original_url
            
            response["message"] = "Cover image received and analyzed."
            
            logger.info(f"[UPLOAD] Response prepared: artist={response.get('artist')}, file_path={image_url}")
            
            # Clean up temp file if needed (optional - can keep for preview)
            # temp_file.unlink()
            
        except Exception as e:
            logger.error(f"[UPLOAD] Recognition failed: {e}", exc_info=True)
            # If recognition fails, return placeholder but don't break upload
            response["record"] = {
                "artist": None,
                "album": None,
                "label": None,
                "catalog_number": None,
                "confidence": None,
            }
            # Also flatten empty values
            response["artist"] = None
            response["album"] = None
            response["label"] = None
            response["catalog_number"] = None
            response["confidence"] = None
            
            response["recognition_error"] = str(e)
            response["message"] = "Cover image received. Recognition failed - will retry later."
    elif mode == "audio_metadata":
        # Audio mode keeps existing structure for backward compatibility
        # Future: Add audio metadata extraction here
        pass

    return response
