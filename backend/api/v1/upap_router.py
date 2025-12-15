# -*- coding: utf-8 -*-
"""
UPAP Root Router

Responsibilities:
- Own the /upap prefix.
- Provide lightweight health/debug endpoints.
- Aggregate stage-specific routers (upload, process, archive, publish).
"""

from typing import Any, Dict

from fastapi import APIRouter

from backend.api.v1.upap_upload_router import router as upap_upload_router
from backend.api.v1.upap_process_router import router as upap_process_router
from backend.api.v1.upap_archive_router import router as upap_archive_router
from backend.api.v1.upap_publish_router import router as upap_publish_router

router = APIRouter(
    prefix="/upap",
    tags=["upap"],
)


@router.get(
    "",
    summary="UPAP root health.",
)
async def upap_root() -> Dict[str, Any]:
    """
    Simple health endpoint for the UPAP pipeline.
    """
    return {
        "status": "ok",
        "pipeline": "UPAP",
        "stages": ["upload", "process", "archive", "publish"],
    }


@router.get(
    "/debug/ping",
    summary="UPAP ping for smoke tests.",
)
async def upap_ping() -> Dict[str, Any]:
    """
    Very lightweight debugging endpoint.
    """
    return {"pong": "upap"}


# Aggregate sub-routers
router.include_router(upap_upload_router)
router.include_router(upap_process_router)
router.include_router(upap_archive_router)
router.include_router(upap_publish_router)
