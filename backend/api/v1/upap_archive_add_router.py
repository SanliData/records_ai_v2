# backend/api/v1/upap_archive_add_router.py
# UTF-8, English only

from fastapi import APIRouter, Form, HTTPException, Header, Depends, Query, Body, Request
from typing import Optional
from datetime import datetime
import json
import uuid
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.db import get_db
from backend.services.user_service import get_user_service
from backend.services.user_library_service import user_library_service
from backend.services.global_library_service import global_library_service
from backend.services.upap.engine.upap_engine import upap_engine
from backend.api.v1.auth_middleware import get_current_user

# Safe import for optional services
try:
    from backend.services.vinyl_pricing_service import vinyl_pricing_service
except Exception as e:
    logger.warning(f"Failed to import vinyl_pricing_service: {e} - pricing features disabled")
    vinyl_pricing_service = None

try:
    from backend.services.lyrics_service import lyrics_service
except Exception as e:
    logger.warning(f"Failed to import lyrics_service: {e} - lyrics features disabled")
    lyrics_service = None

try:
    from backend.services.sheet_music_service import sheet_music_service
except Exception as e:
    logger.warning(f"Failed to import sheet_music_service: {e} - sheet music features disabled")
    sheet_music_service = None

from backend.api.v1.schemas.archive_schema import ArchiveRequestSchema

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upap/archive", tags=["UPAP Archive"])


# get_current_user is imported from auth_middleware


@router.post("/add")
async def add_to_archive(
    request: Request,
    user = Depends(get_current_user)
):
    """
    UPAP V2 Compliance: Archive stage endpoint.
    
    Requirements:
    - Authentication required (auth gating)
    - Converts PreviewRecord to ArchiveRecord
    - Attaches record to authenticated user
    - Does NOT publish (Publish is separate stage)
    
    Accepts both JSON body (preferred) and Form data (legacy support).
    """
    try:
        # P2: Input Validation - Parse and validate request
        content_type = request.headers.get("content-type", "")
        validated_data = None
        record_info = {}  # Initialize to empty dict to avoid NameError
        
        if "application/json" in content_type:
            body = await request.json()
            # Validate using Pydantic schema
            try:
                validated_data = ArchiveRequestSchema(**body)
            except Exception as validation_error:
                # Pydantic validation error - return 422 with details
                raise HTTPException(
                    status_code=422,
                    detail={
                        "error": "Validation failed",
                        "detail": str(validation_error),
                        "errors": validation_error.errors() if hasattr(validation_error, "errors") else []
                    }
                )
            
            record_id = validated_data.record_id or validated_data.preview_id
            email = validated_data.email or user.email
            record_info = validated_data.dict(exclude_none=True, exclude={"record_id", "preview_id", "email", "record_data"})
            
            # Merge nested record_data if present
            if validated_data.record_data and isinstance(validated_data.record_data, dict):
                record_info.update(validated_data.record_data)
        else:
            # Fallback to Form data (legacy support) - validate after parsing
            form = await request.form()
            form_dict = dict(form)
            record_id = form_dict.get("record_id") or form_dict.get("preview_id")
            email = form_dict.get("email") or user.email
            record_data_str = form_dict.get("record_data")
            
            # Build dict for validation
            form_data = {
                "record_id": record_id or form_dict.get("preview_id"),
                "email": email,
                **{k: v for k, v in form_dict.items() if k not in ["record_id", "preview_id", "email", "record_data"]}
            }
            
            if record_data_str:
                try:
                    record_data_dict = json.loads(record_data_str) if isinstance(record_data_str, str) else record_data_str
                    form_data.update(record_data_dict)
                except:
                    pass
            
            # Validate Form data
            try:
                validated_data = ArchiveRequestSchema(**form_data)
                record_info = validated_data.dict(exclude_none=True, exclude={"record_id", "preview_id", "email", "record_data"})
                if validated_data.record_data:
                    record_info.update(validated_data.record_data)
            except Exception as validation_error:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "error": "Validation failed",
                        "detail": str(validation_error)
                    }
                )
        
        if not record_id:
            raise HTTPException(status_code=400, detail="record_id or preview_id is required")
        
        if not email:
            email = user.email
        
        # P0-3: IDEMPOTENCY CHECK - MUST be done FIRST before any expensive operations
        # Check if record already exists in user library by record_id
        # CRITICAL: Check ALL records for matching record_id + user_id to handle concurrent requests
        all_records = list(user_library_service._records.values())
        for rec in all_records:
            # Check by record_id AND user_id to ensure user-specific idempotency
            if (rec.get("record_id") == record_id or rec.get("archive_id") == record_id) and \
               (str(rec.get("user_id")) == str(user.id) or rec.get("user_id_str") == str(user.id) or rec.get("user_email") == user.email):
                logger.info(f"[ARCHIVE] Record {record_id} already exists for user {user.id}. Returning existing record (idempotent operation).")
                rec["idempotent"] = True
                return {
                    "status": "ok",
                    "message": "Record already exists (idempotent)",
                    "record_id": record_id,
                    "idempotent": True,
                    "library_record": rec
                }
        
        # Also check by archive_id if record_id was used as archive_id
        existing_by_archive_id = user_library_service.get_record(record_id)
        if existing_by_archive_id:
            # Verify it belongs to this user
            if (str(existing_by_archive_id.get("user_id")) == str(user.id) or 
                existing_by_archive_id.get("user_id_str") == str(user.id) or
                existing_by_archive_id.get("user_email") == user.email):
                logger.info(f"[ARCHIVE] Record {record_id} already exists in user library. Returning existing record (idempotent operation).")
                existing_by_archive_id["idempotent"] = True
                return {
                    "status": "ok",
                    "message": "Record already exists (idempotent)",
                    "record_id": record_id,
                    "idempotent": True,
                    "library_record": existing_by_archive_id
                }
        
        # UPAP V2 Compliance: Verify PreviewRecord state (optional check)
        # Allow archiving even if is_preview is not explicitly set
        if record_info.get("is_preview") is False and record_info.get("is_archived") is True:
            raise HTTPException(
                status_code=400, 
                detail="UPAP V2: Record is already archived. Cannot archive again."
            )
        
        # UPAP V2: Run archive stage through UPAP engine
        try:
            archive_result = upap_engine.run_archive(record_id)
        except Exception as e:
            # If archive stage fails, continue with manual archive creation
            logger.warning(f"UPAP archive stage failed: {e}, continuing with manual archive")
            archive_result = {}
        
        # STEP 1: Add to GLOBAL ARCHIVE first (or get existing)
        # Build metadata for global archive
        metadata = {
            "artist": record_info.get("artist"),
            "album": record_info.get("album") or record_info.get("title"),
            "title": record_info.get("album") or record_info.get("title"),
            "label": record_info.get("label"),
            "year": record_info.get("year"),
            "catalog_number": record_info.get("catalog_number"),
            "format": record_info.get("format") or "LP",
            "country": record_info.get("country"),
            "barcode": record_info.get("barcode")
        }
        
        # Get file paths (handle multiple possible field names)
        # Prefer standard JPEG path if available, otherwise use original path
        standard_jpeg_path = record_info.get("standard_jpeg_path") or record_info.get("archive_image_path")
        file_path = standard_jpeg_path or record_info.get("file_path") or record_info.get("canonical_image_path") or record_info.get("thumbnail_url")
        thumbnail_url = record_info.get("thumbnail_url") or record_info.get("file_path") or record_info.get("canonical_image_path")
        canonical_image_path = file_path  # Default to file_path
        
        # If standard JPEG doesn't exist, convert original image to standard JPEG
        if not standard_jpeg_path and file_path:
            try:
                from pathlib import Path
                from backend.services.vision_engine import vision_engine
                
                # Resolve file path (remove leading slash if present)
                original_path = file_path.lstrip("/")
                original_file = Path(original_path)
                
                if original_file.exists():
                    # Create archive directory for standard JPEG storage
                    archive_dir = Path("storage") / "archive" / str(user.id)
                    archive_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Convert to standard JPEG: {record_id}.jpg
                    standard_jpeg = archive_dir / f"{record_id}.jpg"
                    
                    # Only convert if standard JPEG doesn't exist
                    if not standard_jpeg.exists():
                        converted_path = vision_engine.save_as_jpeg(
                            file_path=original_file,
                            target_dir=archive_dir
                        )
                        
                        # Rename to standard format: {record_id}.jpg
                        if Path(converted_path).exists() and converted_path != str(standard_jpeg):
                            Path(converted_path).rename(standard_jpeg)
                            converted_path = str(standard_jpeg)
                        
                        # Update file paths to use standard JPEG
                        file_path = f"/{str(standard_jpeg).replace('\\', '/')}"
                        if not file_path.startswith("/"):
                            file_path = f"/{file_path}"
                        thumbnail_url = file_path
                        canonical_image_path = file_path
                        standard_jpeg_path = file_path
                        
                        logger.info(f"[ARCHIVE] Image converted to standard JPEG: {file_path}")
                    else:
                        # Use existing standard JPEG
                        file_path = f"/{str(standard_jpeg).replace('\\', '/')}"
                        if not file_path.startswith("/"):
                            file_path = f"/{file_path}"
                        thumbnail_url = file_path
                        canonical_image_path = file_path
                        standard_jpeg_path = file_path
                        logger.info(f"[ARCHIVE] Using existing standard JPEG: {file_path}")
            except Exception as conv_error:
                # If conversion fails, use original path (fallback)
                logger.warning(f"[ARCHIVE] JPEG conversion failed: {conv_error}, using original file")
                # canonical_image_path already set to file_path
        
        # Additional fields for global archive (pricing, files, etc.)
        # canonical_image_path is set above during conversion (defaults to file_path)
        additional_fields = {
            "file_path": file_path,
            "thumbnail_url": thumbnail_url,
            "canonical_image_path": canonical_image_path,
            "standard_jpeg_path": standard_jpeg_path if standard_jpeg_path else file_path,  # Standard JPEG path for archive
            "archive_image_path": standard_jpeg_path if standard_jpeg_path else file_path,  # Alias for standard JPEG path
            "confidence": record_info.get("confidence"),
            "ocr_text": record_info.get("ocr_text"),
            "matrix_info": record_info.get("matrix_info"),
            "side": record_info.get("side"),
            "source": "user_upload",
            **{k: v for k, v in record_info.items() if k not in ["file_path", "thumbnail_url", "canonical_image_path", "standard_jpeg_path", "archive_image_path", "confidence", "ocr_text", "matrix_info", "side"]}
        }
        
        # Add to global archive (or get existing if fingerprint matches)
        global_record = global_library_service.add_or_get(
            metadata=metadata,
            source="user_upload",
            additional_fields=additional_fields
        )
        
        global_id = global_record.get("id")
        fingerprint = global_record.get("fingerprint")
        
        # STEP 2: Build user library record with reference to global archive
        archive_record = {
            "archive_id": record_id,
            "global_id": global_id,  # Reference to global archive
            "fingerprint": fingerprint,  # Global fingerprint
            "user_id": str(user.id),  # Store as string
            "user_id_str": str(user.id),  # String version
            "user_email": email,
            "record_id": record_id,
            "preview_id": record_info.get("preview_id") or record_id,
            "added_at": datetime.utcnow().isoformat(),
            "artist": record_info.get("artist"),
            "album": record_info.get("album") or record_info.get("title"),
            "title": record_info.get("album") or record_info.get("title"),
            "label": record_info.get("label"),
            "year": record_info.get("year"),
            "catalog_number": record_info.get("catalog_number"),
            "format": record_info.get("format") or "LP",
            "country": record_info.get("country"),
            "file_path": file_path,
            "thumbnail_url": thumbnail_url,
            "canonical_image_path": canonical_image_path if 'canonical_image_path' in locals() else file_path,
            "standard_jpeg_path": file_path,  # Standard JPEG path for archive
            "archive_image_path": file_path,  # Alias for standard JPEG path
            "confidence": record_info.get("confidence"),
            "ocr_text": record_info.get("ocr_text"),
            "matrix_info": record_info.get("matrix_info"),
            "side": record_info.get("side"),
            **{k: v for k, v in record_info.items() if k not in ["file_path", "thumbnail_url", "canonical_image_path", "artist", "album", "title", "label", "year", "catalog_number", "format", "country", "confidence", "ocr_text", "matrix_info", "side"]}
        }
        
        # STEP 3: AUTOMATIC PRICING: Fetch market prices from Discogs
        # Pricing is stored in both global and user records
        pricing_data = None
        artist = record_info.get("artist")
        album = record_info.get("album")
        
        if artist and album and vinyl_pricing_service:
            try:
                # Fetch market prices automatically
                market_prices = vinyl_pricing_service.get_market_prices(
                    artist=artist,
                    album=album,
                    catalog_number=record_info.get("catalog_number"),
                    label=record_info.get("label")
                )
                
                # Store pricing data
                pricing_data = {
                    "market_prices": market_prices,
                    "fetched_at": datetime.utcnow().isoformat(),
                    "price_low": market_prices.get("price_low"),
                    "price_high": market_prices.get("price_high"),
                    "price_median": market_prices.get("price_median"),
                    "currency": market_prices.get("currency", "USD"),
                    "source": market_prices.get("source"),
                    "discogs_url": market_prices.get("url")
                }
                
                # Add pricing to user record
                archive_record["pricing_data"] = pricing_data
                archive_record["price_low"] = market_prices.get("price_low")
                archive_record["price_high"] = market_prices.get("price_high")
                archive_record["price_median"] = market_prices.get("price_median")
                
                # Also update global record with pricing if not already present
                if not global_record.get("pricing_data"):
                    global_record["pricing_data"] = pricing_data
                    global_record["price_low"] = market_prices.get("price_low")
                    global_record["price_high"] = market_prices.get("price_high")
                    global_record["price_median"] = market_prices.get("price_median")
                
            except Exception as pricing_error:
                # Don't fail archive if pricing fails - just log it
                print(f"[Archive] Pricing fetch failed for {artist} - {album}: {pricing_error}")
                pricing_data = {
                    "error": str(pricing_error),
                    "fetched_at": datetime.utcnow().isoformat()
                }
                archive_record["pricing_data"] = pricing_data
        
        # STEP 4: AUTOMATIC LYRICS & SHEET MUSIC: Fetch lyrics and sheet music links
        # For album-level links (artist + album name)
        lyrics_data = None
        sheet_music_data = None
        
        if artist and lyrics_service:
            try:
                # Get album-level lyrics links (use album name as song title for search)
                song_title_for_search = album or record_info.get("title") or "Greatest Hits"
                lyrics_data = lyrics_service.get_lyrics_links(
                    artist=artist,
                    song_title=song_title_for_search,
                    album=album
                )
                
                # Store lyrics links in archive record
                if lyrics_data.get("lyrics_links"):
                    archive_record["lyrics_data"] = lyrics_data
                    # Also update global record
                    if not global_record.get("lyrics_data"):
                        global_record["lyrics_data"] = lyrics_data
                
            except Exception as lyrics_error:
                print(f"[Archive] Lyrics fetch failed for {artist} - {album}: {lyrics_error}")
                lyrics_data = {
                    "error": str(lyrics_error),
                    "fetched_at": datetime.utcnow().isoformat()
                }
            
            if sheet_music_service:
                try:
                    # Get sheet music links
                    sheet_music_data = sheet_music_service.get_sheet_music_links(
                        artist=artist,
                        song_title=album or record_info.get("title") or "Greatest Hits",
                        album=album,
                        composer=record_info.get("composer")
                    )
                    
                    # Store sheet music links in archive record
                    if sheet_music_data.get("sheet_music_links"):
                        archive_record["sheet_music_data"] = sheet_music_data
                        # Also update global record
                        if not global_record.get("sheet_music_data"):
                            global_record["sheet_music_data"] = sheet_music_data
                            
                except Exception as sheet_music_error:
                    print(f"[Archive] Sheet music fetch failed for {artist} - {album}: {sheet_music_error}")
                    sheet_music_data = {
                        "error": str(sheet_music_error),
                        "fetched_at": datetime.utcnow().isoformat()
                    }
        
        # STEP 5: Add to user library (reference to global archive)
        # P0-3: Idempotency - add_record will check for existing record
        library_record = user_library_service.add_record(archive_record)
        
        # Check if this was an idempotent operation (record already existed)
        is_idempotent = library_record.get("idempotent", False)
        
        return {
            "status": "ok",
            "message": "Record added to archive" if not is_idempotent else "Record already exists (idempotent)",
            "idempotent": is_idempotent,
            "record_id": record_id,
            "global_id": global_id,
            "fingerprint": fingerprint,
            "archive": archive_result,
            "global_record": global_record,
            "library_record": library_record
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add to archive: {str(e)}")


@router.get("/list")
async def list_archive(
    user = Depends(get_current_user)
):
    """
    List all archived records for the current user.
    Authentication required - user from token.
    """
    try:
        # Get all records and filter by user email or user_id
        all_records = list(user_library_service._records.values())
        user_records = [
            r for r in all_records 
            if (r.get("user_email") == user.email or 
                str(r.get("user_id")) == str(user.id) or 
                r.get("user_id_str") == str(user.id))
        ]
        return {
            "status": "ok",
            "count": len(user_records),
            "records": user_records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list archive: {str(e)}")


@router.put("/record/{archive_id}")
async def update_archive_record(
    archive_id: str,
    payload: dict = Body(...),
    user = Depends(get_current_user)
):
    """
    Update an archived record.
    Only the record owner can update it.
    """
    try:
        record = user_library_service.get_record(archive_id)
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        # Verify ownership
        if (record.get("user_email") != user.email and 
            str(record.get("user_id")) != str(user.id) and
            record.get("user_id_str") != str(user.id)):
            raise HTTPException(status_code=403, detail="Not authorized to update this record")
        
        updated = user_library_service.update_record(archive_id, payload)
        return {
            "status": "ok",
            "message": "Record updated",
            "record": updated
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update record: {str(e)}")


@router.delete("/record/{archive_id}")
async def delete_archive_record(
    archive_id: str,
    user = Depends(get_current_user)
):
    """
    Delete an archived record from user's library.
    NOTE: This only removes the record from the user's personal collection.
    The record remains in the global archive for other users.
    """
    try:
        record = user_library_service.get_record(archive_id)
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        # Verify ownership
        if (record.get("user_email") != user.email and 
            str(record.get("user_id")) != str(user.id) and
            record.get("user_id_str") != str(user.id)):
            raise HTTPException(status_code=403, detail="Not authorized to delete this record")
        
        # Get global_id before deletion for response
        global_id = record.get("global_id")
        fingerprint = record.get("fingerprint")
        
        # Delete from user library ONLY (global archive remains untouched)
        deleted = user_library_service.delete_record(archive_id)
        
        return {
            "status": "ok" if deleted else "error",
            "message": "Record removed from your collection. Record remains in global archive.",
            "global_id": global_id,
            "fingerprint": fingerprint,
            "deleted_from_user_library": deleted
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete record: {str(e)}")


@router.post("/add-user-photo")
async def add_user_photo_to_archive(
    record_data: str = Form(...),
    user = Depends(get_current_user)
):
    """
    Add user's own photo to their personal archive only.
    NOTE: This does NOT add to global archive (security reason).
    User photos are stored separately and not shared globally.
    
    This endpoint is for users who want to add their own photos
    to their personal collection without sharing with global archive.
    """
    try:
        # Parse record data
        record_info = {}
        if record_data:
            try:
                record_info = json.loads(record_data)
            except:
                pass
        
        # Build user library record (NO global archive reference)
        record_id = record_info.get("record_id") or str(uuid.uuid4())
        archive_record = {
            "archive_id": record_id,
            "global_id": None,  # NO global archive reference
            "fingerprint": None,  # NO global fingerprint
            "user_id": user.id,
            "user_id_str": str(user.id),
            "user_email": user.email,
            "record_id": record_id,
            "added_at": datetime.utcnow().isoformat(),
            "is_user_photo": True,  # Flag: user's own photo
            "not_in_global_archive": True,  # Security flag
            "artist": record_info.get("artist"),
            "album": record_info.get("album"),
            "title": record_info.get("album") or record_info.get("title"),
            "label": record_info.get("label"),
            "year": record_info.get("year"),
            "catalog_number": record_info.get("catalog_number"),
            "format": record_info.get("format"),
            "file_path": record_info.get("file_path"),
            "thumbnail_url": record_info.get("thumbnail_url"),
            "confidence": record_info.get("confidence"),
            **record_info  # Include all other fields
        }
        
        # Add to user library ONLY (no global archive)
        user_library_service.add_record(archive_record)
        
        return {
            "status": "ok",
            "message": "User photo added to your personal archive. Not added to global archive for security.",
            "record_id": record_id,
            "is_user_photo": True,
            "not_in_global_archive": True,
            "library_record": archive_record
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add user photo: {str(e)}")

