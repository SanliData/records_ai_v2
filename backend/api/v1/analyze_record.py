# backend/api/v1/analyze_record.py
# UTF-8, English only

from fastapi import APIRouter, UploadFile, File
from backend.services.analysis_service import analysis_service

router = APIRouter(prefix="/api/v1/analyze", tags=["Analyze Record"])

@router.post("/upload")
async def analyze_record(file: UploadFile = File(...)):
    """
    Upload → OCR → AI guess → Archive check → Pending admin
    """
    file_bytes = await file.read()
    result = analysis_service.process_upload(file_bytes=file_bytes)
    return result
