# -*- coding: utf-8 -*-

from fastapi import Header, HTTPException, Depends
from typing import Optional
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.services.auth_service import get_auth_service
from backend.models.user import User


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
    
    user = auth_service.get_user_by_id(str(user_id))
    if not user:
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
