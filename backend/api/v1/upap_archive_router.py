# -*- coding: utf-8 -*-
"""
UPAP Archive Router
HTTP contract for archive-related operations.

Note:
The core UPAPEngine currently defines stages:
- upload
- process
- publish

There is an ArchiveStage implementation under services, but
it is not registered on the engine. This router exposes
a placeholder API and returns 501 until the stage wiring
is finalized at engine level.
"""

from typing import Any, Dict

from fastapi import APIRouter, Form, HTTPException

router = APIRouter(
    prefix="/archive",
    tags=["upap-archive"],
)


@router.post(
    "",
    summary="Archive a processed record (not wired to engine yet).",
)
async def archive_record(
    record_id: str = Form(..., description="Identifier of the record to archive."),
) -> Dict[str, Any]:
    """
    Placeholder archive endpoint.

    Once ArchiveStage is registered on the engine, this will:
    - Build a payload with record_id.
    - Delegate to the archive stage.
    """
    raise HTTPException(
        status_code=501,
        detail="UPAP archive stage is not wired to the engine yet.",
    )
