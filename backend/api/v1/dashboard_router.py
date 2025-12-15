# -*- coding: utf-8 -*-
# backend/api/v1/dashboard_router.py
# English only, UTF-8

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query

from backend.services.dashboard_service import dashboard_service

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
)


@router.get("/user/{user_id}/summary")
def user_summary(user_id: int) -> Dict[str, Any]:
    """
    High level per-user summary used for stats cards and basic charts.
    """
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="user_id must be positive")

    summary = dashboard_service.get_user_summary(user_id=user_id)
    return {"status": "ok", "summary": summary}


@router.get("/user/{user_id}/timeline")
def user_timeline(
    user_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
) -> Dict[str, Any]:
    """
    Daily timeline of archive counts for the last N days.
    Ideal input for line charts / bar charts on the frontend.
    """
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="user_id must be positive")

    timeline = dashboard_service.get_user_timeline(user_id=user_id, days=days)
    return {"status": "ok", "timeline": timeline}


@router.get("/user/{user_id}/recent")
def user_recent(
    user_id: int,
    limit: int = Query(20, ge=1, le=200, description="Max number of records"),
) -> Dict[str, Any]:
    """
    Last N archive records for the user.
    Used for recent activity tables.
    """
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="user_id must be positive")

    data = dashboard_service.get_user_recent_records(user_id=user_id, limit=limit)
    return {"status": "ok", "data": data}


@router.get("/global/summary")
def global_summary() -> Dict[str, Any]:
    """
    Global summary across all users.
    Useful for admin dashboards.
    """
    summary = dashboard_service.get_global_summary()
    return {"status": "ok", "summary": summary}
