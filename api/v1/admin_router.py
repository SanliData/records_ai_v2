# File: backend/api/v1/admin_router.py
# -*- coding: utf-8 -*-
"""
Admin Router
Provides admin-only functionality for moderation and management.

Admin users: ednovitsky@archive.com, isanli058@gmail.com
All admin endpoints require admin privileges.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from backend.api.v1.auth_middleware import get_current_admin
from backend.api.v1.records_router import RECORD_LIBRARY
from backend.services.admin_service import admin_service
from backend.models.user import User

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# Simple in-memory flags for moderation state
PENDING = []
APPROVED = []
REJECTED = []


@router.get("/pending")
async def list_pending(admin: User = Depends(get_current_admin)):
    """
    Returns a list of pending records.
    Admin only - requires admin privileges.
    """
    return {
        "status": "ok",
        "count": len(PENDING),
        "pending": PENDING,
        "admin": admin.email
    }


@router.post("/queue/{archive_id}")
async def add_to_pending(archive_id: str, admin: User = Depends(get_current_admin)):
    """
    Adds a record to the pending moderation queue.
    Admin only - requires admin privileges.
    """
    record = next((r for r in RECORD_LIBRARY if r["archive_id"] == archive_id), None)
    if not record:
        raise HTTPException(status_code=404, detail="Archive record not found")

    # Avoid duplicates
    if record not in PENDING:
        PENDING.append(record)

    return {
        "status": "queued",
        "record": record,
        "admin": admin.email
    }


@router.post("/approve/{archive_id}")
async def approve_record(archive_id: str, admin: User = Depends(get_current_admin)):
    """
    Approves a record if it exists in PENDING.
    Admin only - requires admin privileges.
    """
    record = next((r for r in PENDING if r["archive_id"] == archive_id), None)
    if not record:
        raise HTTPException(status_code=404, detail="Record not pending")

    PENDING.remove(record)
    APPROVED.append(record)

    return {
        "status": "approved",
        "record": record,
        "admin": admin.email
    }


@router.post("/reject/{archive_id}")
async def reject_record(archive_id: str, admin: User = Depends(get_current_admin)):
    """
    Rejects a pending record.
    Admin only - requires admin privileges.
    """
    record = next((r for r in PENDING if r["archive_id"] == archive_id), None)
    if not record:
        raise HTTPException(status_code=404, detail="Record not pending")

    PENDING.remove(record)
    REJECTED.append(record)

    return {
        "status": "rejected",
        "record": record,
        "admin": admin.email
    }


@router.get("/stats")
async def moderation_stats(admin: User = Depends(get_current_admin)):
    """
    Returns summary of moderation states.
    Admin only - requires admin privileges.
    """
    return {
        "status": "ok",
        "pending": len(PENDING),
        "approved": len(APPROVED),
        "rejected": len(REJECTED),
        "total_archives": len(RECORD_LIBRARY),
        "admin": admin.email
    }


@router.get("/admins")
async def list_admins(admin: User = Depends(get_current_admin)):
    """
    List all admin emails.
    Admin only - requires admin privileges.
    """
    admins = admin_service.list_admins()
    return {
        "status": "ok",
        "admins": admins,
        "count": len(admins),
        "admin": admin.email
    }


@router.post("/admins/{email}")
async def add_admin(email: str, admin: User = Depends(get_current_admin)):
    """
    Add an admin email.
    Admin only - requires admin privileges.
    """
    success = admin_service.add_admin(email)
    if not success:
        raise HTTPException(status_code=400, detail="Email already exists in admin list")
    
    return {
        "status": "ok",
        "message": f"Admin {email} added successfully",
        "admins": admin_service.list_admins(),
        "admin": admin.email
    }


@router.delete("/admins/{email}")
async def remove_admin(email: str, admin: User = Depends(get_current_admin)):
    """
    Remove an admin email.
    Admin only - requires admin privileges.
    """
    success = admin_service.remove_admin(email)
    if not success:
        raise HTTPException(status_code=404, detail="Email not found in admin list")
    
    return {
        "status": "ok",
        "message": f"Admin {email} removed successfully",
        "admins": admin_service.list_admins(),
        "admin": admin.email
    }
