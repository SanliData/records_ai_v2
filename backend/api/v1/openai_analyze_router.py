# backend/api/v1/openai_analyze_router.py
# UTF-8, English only
# OpenAI Vision analysis endpoint

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import logging
from backend.services.openai_label_service import openai_label_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/openai", tags=["OpenAI Analysis"])


@router.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze vinyl record image using OpenAI Vision API.
    
    This is the CORE brain of the pipeline.
    
    Flow:
    1. User uploads image
    2. Backend sends to OpenAI Vision
    3. OpenAI extracts: artist, album, label, year
    4. Return structured JSON
    5. Show preview to user
    6. User confirms
    7. Save to archive
    
    Returns:
        {
            "artist": str,
            "album": str,
            "label": str,
            "year": Optional[int],
            "catalog_number": Optional[str],
            "format": Optional[str],
            "confidence": float,
            "error": Optional[str]
        }
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.content_type}. Expected image/*"
            )
        
        # Read image bytes
        image_bytes = await file.read()
        
        if len(image_bytes) == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty file uploaded"
            )
        
        # Validate file size (max 20MB for OpenAI)
        max_size = 20 * 1024 * 1024  # 20MB
        if len(image_bytes) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large: {len(image_bytes)} bytes. Maximum: {max_size} bytes"
            )
        
        # Analyze with OpenAI
        result = openai_label_service.analyze_image(
            image_bytes=image_bytes,
            mime_type=file.content_type or "image/jpeg"
        )
        
        # Check for errors
        if result.get("error"):
            logger.warning(f"OpenAI analysis error: {result.get('error')}")
            return JSONResponse(
                status_code=200,  # Still 200, but error in response
                content=result
            )
        
        # Return successful result
        logger.info(f"OpenAI analysis successful: {result.get('artist')} - {result.get('album')}")
        return JSONResponse(
            status_code=200,
            content=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in /openai/analyze: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
