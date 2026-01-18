# backend/api/v1/upap_process_router.py
# -*- coding: utf-8 -*-

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime, timezone

router = APIRouter( tags=["upap"])

class ProcessRequest(BaseModel):
    record_id: str

@router.post("/process")
async def process_record(payload: ProcessRequest):
    """
    UPAP PROCESS STAGE (v1)
    - No AI
    - No OCR
    - No external lookup
    - Contract only
    """

    return {
        "status": "ok",
        "stage": "process",
        "record_id": payload.record_id,
        "archive_match": False,
        "candidates": [],
        "next": "archive",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
