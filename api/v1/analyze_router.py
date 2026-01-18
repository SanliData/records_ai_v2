# File: backend/api/v1/analyze_router.py
# -*- coding: utf-8 -*-
"""
DEPRECATED - V1 Analyze Router

This router is officially disabled in V1.
UPAP Pipeline (upload -> process -> archive) replaces all analysis logic.

This file remains only as a placeholder to avoid import errors.
"""

from fastapi import APIRouter

router = APIRouter(
    prefix="/analyze",
    tags=["DEPRECATED"]
)

@router.get("")
async def deprecated_notice():
    return {
        "status": "deprecated",
        "message": "This endpoint is no longer active. Use /upap/process instead."
    }
