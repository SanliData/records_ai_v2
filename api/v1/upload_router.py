# backend/api/v1/upload_router.py
# UTF-8, English only

from fastapi import APIRouter, UploadFile, File, Form
from backend.services.upap.engine.upap_engine import upap_engine

router = APIRouter(prefix="/upap")


@router.post("/upload")
async def upload_only(
    file: UploadFile = File(...),
    email: str = Form(...)
):
    """
    UPAP – Upload-only entry point.
    Runs:
    1) AuthStage
    2) UploadStage
    """

    # 1. AUTH
    auth_payload = {"email": email}
    user_context = upap_engine.run_stage("auth", auth_payload)

    # 2. UPLOAD
    file_bytes = await file.read()
    upload_payload = {
        "file": file_bytes,
        "user_context": user_context
    }

    upload_context = upap_engine.run_stage("upload", upload_payload)

    return {
        "status": "ok",
        "auth": user_context,
        "upload": upload_context
    }
