# File: backend/api/v1/admin_router.py
# -*- coding: utf-8 -*-
"""
Admin Router (Legacy Bridge)
Provides a very lightweight moderation system for UPAP.

Old behavior:
    - Admins could list pending records, approve, reject.

UPAP Bridge behavior:
    - We now operate directly on RECORD_LIBRARY
    - Pending/approved states are simulated for compatibility
"""

from fastapi import APIRouter, HTTPException
from backend.api.v1.records_router import RECORD_LIBRARY

router = APIRouter(
    prefix="/admin",
    tags=["Admin (Legacy Bridge)"]
)


# Simple in-memory flags for moderation state
PENDING = []
APPROVED = []
REJECTED = []


@router.get("/pending")
async def list_pending():
    """
    Returns a list of pending records.
    Uses in-memory PENDING queue for V1.
    """

    return {
        "status": "ok",
        "count": len(PENDING),
        "pending": PENDING
    }


@router.post("/queue/{archive_id}")
async def add_to_pending(archive_id: str):
    """
    Adds a record to the pending moderation queue.
    Mirrors old behavior.
    """

    record = next((r for r in RECORD_LIBRARY if r["archive_id"] == archive_id), None)
    if not record:
        raise HTTPException(status_code=404, detail="Archive record not found")

    # Avoid duplicates
    if record not in PENDING:
        PENDING.append(record)

    return {"status": "queued", "record": record}


@router.post("/approve/{archive_id}")
async def approve_record(archive_id: str):
    """
    Approves a record if it exists in PENDING.
    """

    record = next((r for r in PENDING if r["archive_id"] == archive_id), None)
    if not record:
        raise HTTPException(status_code=404, detail="Record not pending")

    PENDING.remove(record)
    APPROVED.append(record)

    return {"status": "approved", "record": record}


@router.post("/reject/{archive_id}")
async def reject_record(archive_id: str):
    """
    Rejects a pending record.
    """

    record = next((r for r in PENDING if r["archive_id"] == archive_id), None)
    if not record:
        raise HTTPException(status_code=404, detail="Record not pending")

    PENDING.remove(record)
    REJECTED.append(record)

    return {"status": "rejected", "record": record}


@router.get("/stats")
async def moderation_stats():
    """
    Returns summary of moderation states.
    """

    return {
        "pending": len(PENDING),
        "approved": len(APPROVED),
        "rejected": len(REJECTED),
        "total_archives": len(RECORD_LIBRARY)
    }
