# backend/api/v1/upap_preview_router.py
# UTF-8, English only

from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends
from typing import List
from datetime import datetime
import uuid
import zipfile
import io
import os

# UPAP Pipeline imports
from backend.services.upap.upload.upload_stage import UploadStage
from backend.services.upap.process.process_stage import ProcessStage
from backend.services.upap.engine.upap_engine import upap_engine
from backend.services.novarchive_gpt_service import novarchive_gpt_service
from backend.services.video_processing_service import video_processing_service
from backend.services.multi_record_detection_service import multi_record_detection_service
from backend.models.preview_record import PreviewRecord
from backend.api.v1.auth_middleware import get_current_user

router = APIRouter(prefix="/upap/process", tags=["UPAP Preview"])

# Initialize UPAP stages
upload_stage = UploadStage()
process_stage = ProcessStage()


async def process_single_file(file_bytes: bytes, filename: str, user_email: str, detect_multiple: bool = True) -> dict:
    """
    UPAP V2 Compliance: Process file through Upload → Process stages.
    Authentication required - user must be logged in.
    Returns PreviewRecord (non-authoritative state).
    Stops before Archive and Publish stages.
    
    If detect_multiple=True, detects multiple records in the image using AI (Sherlock Holmes mode).
    Each detected record is processed separately.
    """
    user_id = user_email  # Use email as user_id for authenticated users
    
    try:
        # 1. UPLOAD STAGE - Save file first
        upload_context = {
            "file_bytes": file_bytes,
            "filename": filename,
            "user_id": user_id
        }
        upload_stage.validate_input(upload_context)
        upload_result = upload_stage.run(upload_context)
        saved_path = upload_result.get("saved_to")
        
        # 2. MULTI-RECORD DETECTION (Sherlock Holmes mode)
        if detect_multiple:
            detections = multi_record_detection_service.detect_records_in_image(
                image_path=saved_path,
                raw_bytes=file_bytes
            )
            
            # If multiple records detected, process each separately
            if len(detections) > 1:
                results = []
                for detection in detections:
                    crop_path = detection.get("crop_path", saved_path)
                    if crop_path != saved_path:
                        # Process cropped record
                        with open(crop_path, 'rb') as f:
                            crop_bytes = f.read()
                        crop_filename = os.path.basename(crop_path)
                        result = await process_single_file(
                            crop_bytes, 
                            crop_filename, 
                            user_email, 
                            detect_multiple=False  # Don't recurse on crops
                        )
                        result["detection_info"] = {
                            "record_index": detection.get("record_id", "unknown"),
                            "bbox": detection.get("bbox"),
                            "confidence": detection.get("confidence", 0.5),
                            "detection_method": detection.get("detection_method", "unknown")
                        }
                        results.append(result)
                    else:
                        # Use original file for single record
                        result = await process_single_file(
                            file_bytes,
                            filename,
                            user_email,
                            detect_multiple=False
                        )
                        results.append(result)
                
                # Return combined results
                return {
                    "status": "ok",
                    "type": "multiple_records",
                    "count": len(results),
                    "records": results,
                    "detection_method": "ai_vision_sherlock",
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        # Single record processing (original logic)
        record_id = str(uuid.uuid4())
        
        # 3. OCR STAGE (if enabled)
        ocr_text = ""
        if "ocr" in upap_engine.stages:
            ocr_stage = upap_engine.stages["ocr"]
            ocr_context = {
                "file_path": saved_path,
                "record_id": record_id
            }
            ocr_result = ocr_stage.run(ocr_context)
            ocr_text = ocr_result.get("ocr_text", "")
        
        # 4. PROCESS STAGE - Normalize and match
        process_context = {
            "ocr_text": ocr_text or "[No OCR text available]",
            "record_id": record_id,
            "candidate_titles": []  # Empty for preview
        }
        try:
            process_stage.validate_input(process_context)
            process_result = process_stage.run(process_context)
        except ValueError:
            # If OCR text is missing, skip process stage
            process_result = process_context
        
        # 5. NOVARCHIVE GPT ANALYSIS (Primary AI analysis)
        # Use NovArchive GPT service for enhanced vinyl record analysis
        gpt_analysis = {}
        if saved_path:
            try:
                gpt_analysis = novarchive_gpt_service.analyze_vinyl_record(file_path=saved_path)
            except Exception as e:
                # Fallback if GPT analysis fails
                gpt_analysis = {"error": str(e), "source": "error"}
        
        # 5. AI STAGE (if enabled - fallback to UPAP AI stage)
        ai_metadata = {}
        if "ai" in upap_engine.stages or "aianalysis" in upap_engine.stages:
            ai_stage_name = "ai" if "ai" in upap_engine.stages else "aianalysis"
            ai_stage = upap_engine.stages[ai_stage_name]
            ai_context = {
                "ocr_text": gpt_analysis.get("ocr_text") or ocr_text,
                "record_id": record_id,
                **process_result
            }
            ai_result = ai_stage.run(ai_context)
            ai_metadata = ai_result.get("ai_metadata", {})
        
        # Merge GPT analysis with AI metadata (GPT takes priority)
        final_metadata = {
            **ai_metadata,
            **{k: v for k, v in gpt_analysis.items() if v is not None and k != "status"}
        }
        
        # UPAP V2 Compliance: Build PreviewRecord (non-authoritative state)
        preview_id = str(uuid.uuid4())
        canonical_image_path = upload_result.get("saved_to")
        
        preview_record = PreviewRecord(
            preview_id=preview_id,
            record_id=record_id,
            canonical_image_path=canonical_image_path,
            ocr_text=gpt_analysis.get("ocr_text") or ocr_text,
            ai_metadata=final_metadata,
            process_result=process_result,
            artist=final_metadata.get("artist") or gpt_analysis.get("artist") or "Unknown Artist",
            album=final_metadata.get("album") or gpt_analysis.get("album") or "Unknown Album",
            title=final_metadata.get("title") or gpt_analysis.get("title"),
            label=final_metadata.get("label") or gpt_analysis.get("label"),
            year=final_metadata.get("year") or gpt_analysis.get("year"),
            catalog_number=final_metadata.get("catalog_number") or gpt_analysis.get("catalog_number"),
            country=final_metadata.get("country") or gpt_analysis.get("country"),
            format=final_metadata.get("format") or gpt_analysis.get("format") or "LP",
            confidence=final_metadata.get("confidence") or gpt_analysis.get("confidence") or 0.75,
            is_preview=True,
            is_archived=False,
            is_published=False
        )
        
        # Return PreviewRecord as dict for JSON serialization
        result = preview_record.model_dump()
        result["status"] = "ok"
        result["type"] = "image" if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')) else "video"
        result["filename"] = filename
        result["thumbnail_url"] = canonical_image_path
        result["file_path"] = canonical_image_path
        result["matrix_info"] = final_metadata.get("matrix_info") or gpt_analysis.get("matrix_info")
        result["side"] = final_metadata.get("side") or gpt_analysis.get("side")
        result["visual_features"] = gpt_analysis.get("visual_features", {})
        result["notes"] = gpt_analysis.get("notes")
        result["timestamp"] = datetime.utcnow().isoformat()
        
        return result
        
    except Exception as e:
        # Fallback to basic result if UPAP pipeline fails
        return {
            "status": "ok",
            "record_id": record_id,
            "filename": filename,
            "type": "image",
            "artist": "Unknown Artist",
            "album": "Unknown Album",
            "label": None,
            "year": None,
            "catalog_number": None,
            "format": "LP",
            "confidence": 0.5,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def process_video_file(file_bytes: bytes, filename: str, user_email: str) -> dict:
    """
    Extract best frame from video and process it as JPEG.
    Video is converted to JPEG (best frame) for archive storage.
    """
    try:
        # Extract best frame from video and convert to JPEG
        jpeg_path, video_metadata = video_processing_service.extract_best_frame(
            video_bytes=file_bytes,
            video_filename=filename
        )
        
        # Read JPEG file bytes
        with open(jpeg_path, 'rb') as f:
            jpeg_bytes = f.read()
        
        # Process extracted JPEG frame as image
        result = await process_single_file(jpeg_bytes, os.path.basename(jpeg_path), user_email)
        
        # Add video metadata to result
        result["video_metadata"] = video_metadata
        result["original_video_filename"] = filename
        result["video_to_jpeg_converted"] = True
        result["type"] = "video"
        
        return result
        
    except Exception as e:
        # Fallback: process video file directly if frame extraction fails
        print(f"[VideoProcessing] Frame extraction failed: {e}")
        return await process_single_file(file_bytes, filename, user_email)


async def extract_zip_files(zip_bytes: bytes, user_email: str) -> List[dict]:
    """
    Extract files from ZIP and process each image through UPAP pipeline.
    """
    results = []
    
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_ref:
            for file_info in zip_ref.filelist:
                if file_info.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    file_bytes = zip_ref.read(file_info.filename)
                    result = await process_single_file(file_bytes, file_info.filename, user_email)
                    results.append(result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ZIP extraction failed: {str(e)}")
    
    return results


@router.post("/process/preview")
async def upload_preview(
    request: Request,
    user = Depends(get_current_user)
):
    """
    UPAP V2 Compliance: Process stage preview endpoint.
    Processes files through UPAP pipeline (Upload → Process).
    Stops before Archive and Publish stages (preview mode).
    Supports multiple images, videos, and ZIP files.
    Returns preview results that can be reviewed before adding to archive.
    
    Authentication required - user must be logged in.
    """
    results = []
    user_email = user.email
    
    # Get form data
    form = await request.form()
    
    # Collect all files from form
    files_to_process = []
    for key, value in form.items():
        if isinstance(value, UploadFile):
            files_to_process.append(value)
    
    if not files_to_process:
        raise HTTPException(status_code=400, detail="No files provided")
    
    for file in files_to_process:
        if not file.filename:
            continue
            
        file_bytes = await file.read()
        filename = file.filename.lower()
        
        # Determine file type
        if filename.endswith('.zip'):
            # Process ZIP file
            zip_results = await extract_zip_files(file_bytes, user_email)
            results.extend(zip_results)
        elif file.content_type and file.content_type.startswith('video/'):
            # Process video
            result = await process_video_file(file_bytes, file.filename, user_email)
            results.append(result)
        elif file.content_type and file.content_type.startswith('image/'):
            # Process image
            result = await process_single_file(file_bytes, file.filename, user_email)
            results.append(result)
        else:
            # Unknown type, skip
            continue
    
    if not results:
        raise HTTPException(status_code=400, detail="No valid files to process")
    
    return {
        "status": "ok",
        "count": len(results),
        "results": results,
        "timestamp": datetime.utcnow().isoformat()
    }
