# -*- coding: utf-8 -*-
"""
Authentication Middleware Helper
Extracts user info from Authorization header token
"""

from fastapi import Header, HTTPException, Depends
from typing import Optional
from backend.services.auth_service import auth_service
from backend.services.user_service import user_service
from backend.models.user import User


def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    """
    Extract user from Authorization header (Bearer token).
    Returns user object if token is valid.
    No approval required - valid Google account is automatically accepted as user.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication required. Please sign in.")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format. Use 'Bearer <token>'")
    
    token = authorization.replace("Bearer ", "").strip()
    
    # Try Google token first (new flow)
    auth_result = auth_service.verify_google_token(token)
    
    # If Google token fails, try legacy token verification
    if auth_result.get("status") != "ok":
        auth_result = auth_service.verify_token(token)
        if auth_result.get("status") != "ok":
            raise HTTPException(status_code=401, detail="Invalid or expired token. Please sign in again.")
    
    email = auth_result.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Token verification failed. Please sign in again.")
    
    # Get or create user (automatically approved - no approval needed for valid Google accounts)
    user = user_service.get_or_create_user(email)
    return user


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    """
    Require admin privileges.
    Returns user if admin, raises 403 otherwise.
    """
    if not user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required. This action is restricted to administrators."
        )
    return user
