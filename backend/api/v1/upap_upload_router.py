# -*- coding: utf-8 -*-
"""
UPAP Upload Router
Thin HTTP layer for:
- multipart upload
- email-based auth
- delegating to UPAPEngine.run_upload_only(...)
"""

from typing import Any, Dict

import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.services.upap.engine.upap_engine import upap_engine

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/upload",
    tags=["upap-upload"],
)


@router.post(
    "",
    summary="Upload a file via UPAP (auth + upload stage).",
)
async def upload_only(
    file: UploadFile = File(...),
    email: str = Form(...),
) -> Dict[str, Any]:
    """
    UPAP entrypoint used by the client UI and CLI.

    Responsibilities (router level):
    - Validate multipart form (email + file).
    - Read file bytes into memory (demo scale).
    - Delegate to UPAPEngine.run_upload_only.
    - Map low level errors to HTTP responses.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty file payload")

    try:
        result = upap_engine.run_upload_only(
            file_bytes=file_bytes,
            email=email,
        )
    except Exception as exc:
        logger.exception(
            "UPAP upload failed",
            extra={"email": email, "filename": file.filename},
        )
        raise HTTPException(
            status_code=500,
            detail="UPAP upload failed",
        ) from exc

    return result
