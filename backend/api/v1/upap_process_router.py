# backend/api/v1/upap_process_router.py
# -*- coding: utf-8 -*-
#
# ⚠️ INTERNAL / DIAGNOSTIC ENDPOINT
# This endpoint is a placeholder for process stage testing.
# NOT for production use - process stage is integrated into preview flow.

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime, timezone

router = APIRouter(prefix="/upap", tags=["UPAP Internal"])

class ProcessRequest(BaseModel):
    record_id: str

@router.post("/process")
async def process_record(payload: ProcessRequest):
    """
    ⚠️ INTERNAL / DIAGNOSTIC ENDPOINT
    
    UPAP PROCESS STAGE (v1) - Placeholder endpoint.
    - No AI
    - No OCR
    - No external lookup
    - Contract only
    
    NOTE: Process stage is integrated into /upap/process/preview flow.
    This endpoint exists for diagnostic/testing purposes only.
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
