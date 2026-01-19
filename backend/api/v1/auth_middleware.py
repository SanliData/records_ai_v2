# -*- coding: utf-8 -*-

import logging
from fastapi import Header, HTTPException, Depends
from typing import Optional
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.services.auth_service import get_auth_service
from backend.models.user import User

logger = logging.getLogger(__name__)


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication required. Please sign in.")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format. Use 'Bearer <token>'")
    
    token = authorization.replace("Bearer ", "").strip()
    
    auth_service = get_auth_service(db)
    payload = auth_service.decode_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token. Please sign in again.")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload. Please sign in again.")
    
    # Log for debugging (only in debug mode to avoid log spam)
    logger.debug(f"Looking up user with id: {user_id} (type: {type(user_id)})")
    
    user = auth_service.get_user_by_id(str(user_id))
    if not user:
        logger.warning(f"User not found in database for user_id: {user_id}. Token may be from different environment or user was deleted.")
        raise HTTPException(status_code=401, detail="User not found. Please sign in again.")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive.")
    
    return user


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required. This action is restricted to administrators."
        )
    return user
