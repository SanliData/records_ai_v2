from fastapi import APIRouter, UploadFile, File, HTTPException
from uuid import uuid4
from typing import Optional

router = APIRouter()


@router.post("/upload")
async def app_upload(
    image: UploadFile = File(...),
    title: Optional[str] = None,
    artist: Optional[str] = None,
    email: Optional[str] = None,
):
    """
    ChatGPT App entrypoint.
    Receives an image and optional metadata.
    Starts async processing via UPAP pipeline (placeholder).
    """

    # 1. Generate record ID (source of truth will be DB later)
    record_id = str(uuid4())

    # 2. (Placeholder) Here you will:
    # - Save image
    # - Create PendingRecord
    # - Trigger UPAP pipeline / worker

    return {
        "record_id": record_id,
        "status": "PENDING",
        "stage": "UPLOADED",
        "message": "Upload received. Processing started."
    }


@router.get("/status/{record_id}")
def app_status(record_id: str):
    """
    ChatGPT App polling endpoint.
    ChatGPT will repeatedly call this endpoint
    until stage == PUBLISHED or FAILED.
    """

    # 1. (Placeholder) Fetch record state from DB
    # For now we return a deterministic mock response

    if not record_id:
        raise HTTPException(status_code=400, detail="record_id is required")

    return {
        "record_id": record_id,
        "status": "IN_PROGRESS",
        "stage": "ANALYZING",
        "progress": 0.5,
        "result": None
    }
