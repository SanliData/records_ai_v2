###
# UTF-8

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
from backend.services.analysis_service import process_image_file, process_video_file, process_camera_frame

router = APIRouter(
    prefix="/api/v1/analyze",
    tags=["Analyze / Ingestion"],
)


# --------------------------------------------------------
# 1) SINGLE IMAGE UPLOAD
# --------------------------------------------------------
@router.post("/image")
async def analyze_single_image(
    file: UploadFile = File(...)
):
    return await process_image_file(file)


# --------------------------------------------------------
# 2) MULTIPLE IMAGES UPLOAD
# --------------------------------------------------------
@router.post("/images")
async def analyze_multiple_images(
    files: List[UploadFile] = File(...)
):
    results = []
    for f in files:
        results.append(await process_image_file(f))
    return results


# --------------------------------------------------------
# 3) VIDEO UPLOAD → auto frame extraction → analyze frames
# --------------------------------------------------------
@router.post("/video")
async def analyze_video(
    file: UploadFile = File(...)
):
    return await process_video_file(file)


# --------------------------------------------------------
# 4) CAMERA CAPTURE (single frame from mobile or belt camera)
# Input: base64 image string
# --------------------------------------------------------
@router.post("/camera")
async def analyze_camera_frame(
    frame_base64: str = Form(...)
):
    return await process_camera_frame(frame_base64)


# --------------------------------------------------------
# 5) URL INGESTION (OneDrive / Web URL)
# --------------------------------------------------------
@router.post("/from_url")
async def analyze_from_url(
    url: str = Form(...)
):
    raise HTTPException(501, "URL ingestion is coming in v2.1")
