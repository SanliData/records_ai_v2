# File: backend/api/v1/admin_router.py
# -*- coding: utf-8 -*-
"""
Admin Router
Provides admin-only functionality for moderation and management.

Admin users: ednovitsky@novitskyarchive.com, isanli058@gmail.com
All admin endpoints require admin privileges.
"""

import logging
import re
import uuid
from fastapi import APIRouter, HTTPException, Depends, Body, Request
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.api.v1.auth_middleware import get_current_admin
from backend.api.v1.records_router import RECORD_LIBRARY
from backend.services.admin_service import admin_service
from backend.services.user_service import get_user_service
from backend.models.user import User

logger = logging.getLogger(__name__)

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


class BootstrapUserRequest(BaseModel):
    """Request model for bootstrap-user endpoint."""
    email: EmailStr = Field(..., description="User email address", max_length=255)
    is_admin: bool = Field(default=False, description="Whether to create user as admin")
    
    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Normalize email to lowercase."""
        return v.lower().strip()


@router.post("/bootstrap-user")
async def bootstrap_user(
    request: Request,
    payload: BootstrapUserRequest = Body(...),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Bootstrap a user account (admin-only).
    
    Creates a user if they don't exist, or returns existing user.
    Used for provisioning test users and initial setup.
    
    Behavior:
    - If user exists -> return {status:"ok", existed:true, user_id:...}
    - Else create user -> {status:"ok", existed:false, user_id:...}
    - Validates email format, max length, lowercase normalization
    - Logs request_id for audit
    
    Args:
        payload: BootstrapUserRequest with email and optional is_admin flag
        admin: Current admin user (from dependency)
        db: Database session
        
    Returns:
        {
            "status": "ok",
            "existed": bool,
            "user_id": str,
            "email": str,
            "is_admin": bool,
            "request_id": str
        }
    """
    import re
    request_id = str(uuid.uuid4())
    email = payload.email.lower().strip()
    
    logger.info(f"[BOOTSTRAP] Request {request_id}: Admin {admin.email} bootstrapping user {email}")
    
    # Validate email format (Pydantic EmailStr already validates, but add extra checks)
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if not email_pattern.match(email):
        logger.warning(f"[BOOTSTRAP] Request {request_id}: Invalid email format: {email}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid email format: {email}"
        )
    
    # Validate email length
    if len(email) > 255:
        logger.warning(f"[BOOTSTRAP] Request {request_id}: Email too long: {len(email)} chars")
        raise HTTPException(
            status_code=400,
            detail=f"Email too long: maximum 255 characters, got {len(email)}"
        )
    
    # Check if user exists
    user_service = get_user_service(db)
    existing_user = user_service.get_user_by_email(email)
    
    if existing_user:
        logger.info(f"[BOOTSTRAP] Request {request_id}: User {email} already exists (id: {existing_user.id})")
        return {
            "status": "ok",
            "existed": True,
            "user_id": str(existing_user.id),
            "email": existing_user.email,
            "is_admin": existing_user.is_admin,
            "request_id": request_id
        }
    
    # Create new user
    try:
        # Determine admin status: use payload.is_admin OR check admin_service
        should_be_admin = payload.is_admin or admin_service.is_admin(email)
        
        new_user = user_service.get_or_create_user(email)
        
        # Update admin status if needed
        if should_be_admin and not new_user.is_admin:
            new_user.role = "admin"
            new_user.is_admin = True
            db.commit()
            db.refresh(new_user)
        elif not should_be_admin and new_user.is_admin and not admin_service.is_admin(email):
            # Only downgrade if not in admin_service list
            new_user.role = "user"
            new_user.is_admin = False
            db.commit()
            db.refresh(new_user)
        
        logger.info(f"[BOOTSTRAP] Request {request_id}: Created user {email} (id: {new_user.id}, admin: {new_user.is_admin})")
        
        return {
            "status": "ok",
            "existed": False,
            "user_id": str(new_user.id),
            "email": new_user.email,
            "is_admin": new_user.is_admin,
            "request_id": request_id
        }
    except Exception as e:
        logger.error(f"[BOOTSTRAP] Request {request_id}: Failed to create user {email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to bootstrap user: {str(e)}"
        )
