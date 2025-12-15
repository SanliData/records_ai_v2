# File: backend/api/v1/records_router.py
# -*- coding: utf-8 -*-
"""
Records Router (Legacy Bridge)
Maps old /records API calls into the UPAP archive system.

Old behavior:
    - Read records from old storage or old DB models

New behavior (UPAP Bridge):
    - Use a lightweight in-memory or JSON-based archive listing
    - Fully compatible with old frontend UI

NOTE:
    This is a minimal, safe V1 implementation.
    It does NOT depend on UPAP engine to avoid import issues.
"""

from fastapi import APIRouter, HTTPException, Form
import json

router = APIRouter(
    prefix="/records",
    tags=["Records (Legacy Bridge)"]
)

# ------------------------------------------------------
# In-memory storage for V1 bridge mode
# ------------------------------------------------------
RECORD_LIBRARY = []


@router.get("")
async def list_records():
    """
    Returns all archived records collected through V1 bridge mode.
    """
    return {
        "status": "ok",
        "count": len(RECORD_LIBRARY),
        "records": RECORD_LIBRARY,
    }


@router.post("/add")
async def add_record(
    archive_record_json: str = Form(...),
    email: str = Form(None)
):
    """
    Legacy endpoint to add new record to library.
    Mapped directly to in-memory RECORD_LIBRARY.
    """

    try:
        archive_record = json.loads(archive_record_json)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid archive_record JSON")

    # Tag with email for minimal traceability
    archive_record["email"] = email

    RECORD_LIBRARY.append(archive_record)

    return {
        "status": "ok",
        "added": archive_record,
        "total": len(RECORD_LIBRARY)
    }
