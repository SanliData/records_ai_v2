# File: backend/api/v1/archive_router.py
# -*- coding: utf-8 -*-
"""
Archive Router (Legacy Bridge)
Redirects old archive operations to UPAP ArchiveStage.

Old behavior:
    /archive → store final analysis record

New behavior:
    - Preserves old endpoint signature
    - Delegates logic to UPAPEngine.archive_only()
"""

from fastapi import APIRouter, HTTPException, Form
from backend.services.upap.engine.upap_engine import upap_engine
import json

router = APIRouter(
    prefix="/archive",
    tags=["Archive (Legacy Bridge)"]
)


@router.post("")
async def legacy_archive(
    process_result_json: str = Form(...),
    email: str = Form(None)
):
    """
    Legacy endpoint mapped to UPAP ArchiveStage.

    Expected input:
        process_result_json: JSON string from old frontend

    New behavior:
        - Convert JSON → dict
        - Use UPAPEngine.archive_only()
    """

    try:
        process_result = json.loads(process_result_json)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON for process_result")

    auth_payload = {"email": email}

    try:
        # Stage 0: auth
        user_ctx = upap_engine.run_auth(auth_payload)

        # Stage 3: Archive directly
        archive_record = upap_engine.run_archive_only(
            process_result=process_result,
            user_context=user_ctx
        )

        return {
            "status": "ok",
            "archive_record": archive_record
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
