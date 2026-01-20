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
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    Raises 401 if authorization header is missing or invalid.
    """
    # #region agent log
    import json
    from datetime import datetime
    try:
        with open(r"c:\Users\issan\records_ai_v2\.cursor\debug.log", "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps({
                "id": f"log_auth_middleware_entry",
                "timestamp": int(datetime.now().timestamp() * 1000),
                "location": "auth_middleware.py:23",
                "message": "Auth middleware entry",
                "data": {
                    "has_authorization": authorization is not None,
                    "auth_header_length": len(authorization) if authorization else 0,
                    "starts_with_bearer": authorization.startswith("Bearer ") if authorization else False
                },
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "B"
            }) + "\n")
    except Exception:
        pass
    # #endregion
    
    if not authorization:
        # #region agent log
        try:
            with open(r"c:\Users\issan\records_ai_v2\.cursor\debug.log", "a", encoding="utf-8") as log_file:
                log_file.write(json.dumps({
                    "id": f"log_auth_missing",
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "location": "auth_middleware.py:28",
                    "message": "Auth header MISSING - rejecting",
                    "data": {},
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "B"
                }) + "\n")
        except Exception:
            pass
        # #endregion
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please provide a valid Bearer token in the Authorization header."
        )
    
    if not authorization.startswith("Bearer "):
        # #region agent log
        try:
            with open(r"c:\Users\issan\records_ai_v2\.cursor\debug.log", "a", encoding="utf-8") as log_file:
                log_file.write(json.dumps({
                    "id": f"log_auth_invalid_format",
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "location": "auth_middleware.py:41",
                    "message": "Auth header invalid format - rejecting",
                    "data": {"auth_preview": authorization[:20] if authorization else None},
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "B"
                }) + "\n")
        except Exception:
            pass
        # #endregion
        raise HTTPException(status_code=401, detail="Invalid authorization format. Use 'Bearer <token>'")
    
    token = authorization.replace("Bearer ", "").strip()
    
    auth_service = get_auth_service(db)
    payload = auth_service.decode_token(token)
    
    if not payload:
        # #region agent log
        try:
            with open(r"c:\Users\issan\records_ai_v2\.cursor\debug.log", "a", encoding="utf-8") as log_file:
                log_file.write(json.dumps({
                    "id": f"log_token_decode_failed",
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "location": "auth_middleware.py:50",
                    "message": "Token decode FAILED - rejecting",
                    "data": {},
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "B"
                }) + "\n")
        except Exception:
            pass
        # #endregion
        raise HTTPException(status_code=401, detail="Invalid or expired token. Please sign in again.")
    
    user_id = payload.get("sub")
    if not user_id:
        # #region agent log
        try:
            with open(r"c:\Users\issan\records_ai_v2\.cursor\debug.log", "a", encoding="utf-8") as log_file:
                log_file.write(json.dumps({
                    "id": f"log_token_no_sub",
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "location": "auth_middleware.py:58",
                    "message": "Token missing sub - rejecting",
                    "data": {},
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "B"
                }) + "\n")
        except Exception:
            pass
        # #endregion
        raise HTTPException(status_code=401, detail="Invalid token payload. Please sign in again.")
    
    # Log for debugging (only in debug mode to avoid log spam)
    logger.debug(f"Looking up user with id: {user_id} (type: {type(user_id)})")
    
    user = auth_service.get_user_by_id(str(user_id))
    if not user:
        # #region agent log
        try:
            with open(r"c:\Users\issan\records_ai_v2\.cursor\debug.log", "a", encoding="utf-8") as log_file:
                log_file.write(json.dumps({
                    "id": f"log_user_not_found",
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "location": "auth_middleware.py:67",
                    "message": "User NOT FOUND in DB - rejecting",
                    "data": {"user_id": str(user_id)},
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "B"
                }) + "\n")
        except Exception:
            pass
        # #endregion
        logger.warning(f"User not found in database for user_id: {user_id}. Token may be from different environment or user was deleted.")
        raise HTTPException(
            status_code=401,
            detail="User not found. Please sign in again or bootstrap user."
        )
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive.")
    
    # #region agent log
    try:
        with open(r"c:\Users\issan\records_ai_v2\.cursor\debug.log", "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps({
                "id": f"log_auth_success",
                "timestamp": int(datetime.now().timestamp() * 1000),
                "location": "auth_middleware.py:74",
                "message": "Auth SUCCESS",
                "data": {"user_id": str(user.id), "user_email": user.email},
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "B"
            }) + "\n")
    except Exception:
        pass
    # #endregion
    
    return user


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required. This action is restricted to administrators."
        )
    return user
