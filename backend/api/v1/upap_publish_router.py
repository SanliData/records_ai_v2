# -*- coding: utf-8 -*-
"""
UPAP Publish Router
HTTP contract for the publish stage.

Note:
UPAPEngine exposes a 'publish' stage, but the exact
payload contract is under design. This router keeps the
HTTP contract stable while the stage internals evolve.
"""

from typing import Any, Dict

from fastapi import APIRouter, Form, HTTPException

# from backend.services.upap.engine.upap_engine import upap_engine

router = APIRouter(
    prefix="/publish",
    tags=["upap-publish"],
)


@router.post(
    "",
    summary="Publish a record (stage contract under design).",
)
async def publish_record(
    record_id: str = Form(..., description="Identifier of the record to publish."),
) -> Dict[str, Any]:
    """
    Placeholder publish endpoint.

    When the publish stage contract is finalized, this function should:
    - Build a payload (for example {'record_id': record_id}).
    - Call upap_engine.run_stage('publish', payload).
    - Return the engine result.
    """
    raise HTTPException(
        status_code=501,
        detail="UPAP publish stage contract is not finalized yet.",
    )
