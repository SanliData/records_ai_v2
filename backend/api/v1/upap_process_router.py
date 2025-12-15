# -*- coding: utf-8 -*-
"""
UPAP Process Router
Thin HTTP layer for the process stage.

Note:
ProcessStage implementation is not finalized yet.
For now this router exposes a clear HTTP contract and
can be wired to UPAPEngine.run_stage('process', ...) later.
"""

from typing import Any, Dict

from fastapi import APIRouter, Form, HTTPException

# from backend.services.upap.engine.upap_engine import upap_engine

router = APIRouter(
    prefix="/process",
    tags=["upap-process"],
)


@router.post(
    "",
    summary="Run UPAP processing on a pending record (not fully wired yet).",
)
async def run_process(
    record_id: str = Form(..., description="Identifier of the pending record."),
) -> Dict[str, Any]:
    """
    Placeholder contract for the process stage.

    Current behavior:
    - Accepts a record_id from the client.
    - Returns 501 Not Implemented to make the status explicit.

    When ProcessStage is finalized, this function should:
    - Build a payload (for example {'record_id': record_id}).
    - Call upap_engine.run_stage('process', payload).
    - Return the engine result.
    """
    raise HTTPException(
        status_code=501,
        detail="UPAP process stage is not implemented on this node yet.",
    )
