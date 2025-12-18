# -*- coding: utf-8 -*-
"""
UPAP Archive Router
"""

from typing import Dict, Any

from fastapi import APIRouter, Form, HTTPException

from backend.services.upap.engine.upap_engine import upap_engine


router = APIRouter(
    prefix="/archive",
    tags=["upap-archive"],
)


@router.post("", summary="Archive a processed record")
async def archive_record(
    record_id: str = Form(..., description="Identifier of the record to archive."),
) -> Dict[str, Any]:
    try:
        # Load process result from state (created during process stage)
        state = upap_engine.get_stage("archive").store.load_state(record_id)

        if not state or "archive_record" not in state:
            raise HTTPException(
                status_code=400,
                detail="Record must be processed before archiving.",
            )

        process_result = state["archive_record"].get("process_result")
        if not process_result:
            # Fallback: minimal archive
            process_result = {}

        return upap_engine.run_stage(
            "archive",
            {
                "record_id": record_id,
                "process_result": process_result,
            },
        )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
