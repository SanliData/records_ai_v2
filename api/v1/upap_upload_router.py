from fastapi import APIRouter, UploadFile, File, Form
from datetime import datetime
import uuid

router = APIRouter( tags=["UPAP"])


@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    email: str = Form(...)
):
    """
    UPAP upload endpoint (prod-stable).
    Cloud Run + curl -F uyumlu.
    """

    record_id = str(uuid.uuid4())

    content = await file.read()
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
