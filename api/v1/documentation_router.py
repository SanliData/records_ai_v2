# File: backend/api/v1/documentation_router.py
# -*- coding: utf-8 -*-
"""
Documentation Router (Legacy Bridge)

Provides system metadata for old clients.
UPAP is now included in the service summary.

Role-3: Router returns static information only.
"""

from fastapi import APIRouter

router = APIRouter(
    prefix="/documentation",
    tags=["Documentation (Legacy Bridge)"]
)


@router.get("")
async def service_info():
    """
    Returns high-level backend information.
    Old clients expect this endpoint to exist.
    """

    return {
        "service": "Records AI Backend",
        "version": "1.0.0",
        "description": "Unified pipeline with UPAP Engine",
        "components": [
            "auth_router",
            "records_router",
            "analyze_router",
            "upload_router",
            "user_library_router",
            "search_router",
            "archive_router",
            "upap_router"
        ],
        "upap_enabled": True,
        "upap_version": "v1",
    }
