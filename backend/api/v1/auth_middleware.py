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
    import os
    from datetime import datetime
    try:
        log_dir = r"c:\Users\issan\records_ai_v2\.cursor"
        log_path = os.path.join(log_dir, "debug.log")
        os.makedirs(log_dir, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as log_file:
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
        import os
        try:
            log_dir = r"c:\Users\issan\records_ai_v2\.cursor"
            log_path = os.path.join(log_dir, "debug.log")
            os.makedirs(log_dir, exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as log_file:
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
        import os
        try:
            log_dir = r"c:\Users\issan\records_ai_v2\.cursor"
            log_path = os.path.join(log_dir, "debug.log")
            os.makedirs(log_dir, exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as log_file:
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
    
    # #region agent log
    import os
    try:
        log_dir = r"c:\Users\issan\records_ai_v2\.cursor"
        log_path = os.path.join(log_dir, "debug.log")
        os.makedirs(log_dir, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps({
                "id": f"log_token_decode_result",
                "timestamp": int(datetime.now().timestamp() * 1000),
                "location": "auth_middleware.py:104",
                "message": "Token decode result",
                "data": {
                    "payload_exists": payload is not None,
                    "payload_sub": payload.get("sub") if payload else None,
                    "payload_email": payload.get("email") if payload else None,
                    "payload_keys": list(payload.keys()) if payload else [],
                    "token_preview": token[:20] + "..." if len(token) > 20 else token
                },
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "B"
            }) + "\n")
    except Exception as e:
        logger.error(f"Failed to write token decode log: {e}", exc_info=True)
    # #endregion
    
    if not payload:
        # #region agent log
        import os
        try:
            log_dir = r"c:\Users\issan\records_ai_v2\.cursor"
            log_path = os.path.join(log_dir, "debug.log")
            os.makedirs(log_dir, exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as log_file:
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
    user_email = payload.get("email")
    
    # Log token contents to console logger for debugging
    logger.warning(f"[AUTH DEBUG] Token decoded - user_id: {user_id}, email: {user_email}, all_keys: {list(payload.keys()) if payload else 'None'}")
    
    if not user_id:
        # #region agent log
        import os
        try:
            log_dir = r"c:\Users\issan\records_ai_v2\.cursor"
            log_path = os.path.join(log_dir, "debug.log")
            os.makedirs(log_dir, exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as log_file:
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
    
    # #region agent log
    import os
    try:
        log_dir = r"c:\Users\issan\records_ai_v2\.cursor"
        log_path = os.path.join(log_dir, "debug.log")
        os.makedirs(log_dir, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps({
                "id": f"log_before_user_lookup",
                "timestamp": int(datetime.now().timestamp() * 1000),
                "location": "auth_middleware.py:132",
                "message": "Before user lookup",
                "data": {
                    "user_id_from_token": str(user_id),
                    "user_email_from_token": user_email,
                    "user_id_type": str(type(user_id)),
                    "user_id_repr": repr(user_id)
                },
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "A"
            }) + "\n")
    except Exception as e:
        logger.error(f"Failed to write debug log: {e}", exc_info=True)
    # #endregion
    
    # Try to find user by ID first
    user = auth_service.get_user_by_id(str(user_id))
    logger.warning(f"[AUTH DEBUG] User lookup by ID {user_id}: {'FOUND' if user else 'NOT FOUND'}")
    
    # If user not found by ID, try to find or create by email (fallback for database reset scenarios)
    if not user:
        # #region agent log - User not found by ID
        import os
        try:
            log_dir = r"c:\Users\issan\records_ai_v2\.cursor"
            log_path = os.path.join(log_dir, "debug.log")
            os.makedirs(log_dir, exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write(json.dumps({
                    "id": "log_user_not_found_by_id",
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "location": "auth_middleware.py:207",
                    "message": "User NOT found by ID - checking email fallback",
                    "data": {
                        "user_id_from_token": str(user_id),
                        "user_email_from_token": user_email,
                        "has_email": user_email is not None
                    },
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "A"
                }) + "\n")
        except Exception as e:
            logger.error(f"Failed to write debug log: {e}", exc_info=True)
        # #endregion
        
        if user_email:
            logger.warning(f"[AUTH DEBUG] User not found by ID {user_id}, attempting lookup/create by email {user_email}")
            try:
                from backend.services.user_service import get_user_service
                user_service = get_user_service(db)
                # Use get_or_create_user to handle database reset scenarios
                # This matches the behavior of login endpoints
                # get_or_create_user should never return None - it either returns existing or creates new user
                user = user_service.get_or_create_user(user_email)
                logger.warning(f"[AUTH DEBUG] get_or_create_user result: {'SUCCESS' if user else 'FAILED'}, user_id={user.id if user else 'None'}")
                if user:
                    logger.info(f"[AUTH DEBUG] User found/created by email fallback. Token user_id={user_id}, DB user_id={user.id}, email={user_email}")
                    # #region agent log
                    try:
                        log_dir = r"c:\Users\issan\records_ai_v2\.cursor"
                        log_path = os.path.join(log_dir, "debug.log")
                        os.makedirs(log_dir, exist_ok=True)
                        with open(log_path, "a", encoding="utf-8") as log_file:
                            log_file.write(json.dumps({
                                "id": f"log_user_found_by_email_fallback",
                                "timestamp": int(datetime.now().timestamp() * 1000),
                                "location": "auth_middleware.py:240",
                                "message": "User found/created by email fallback",
                                "data": {
                                    "token_user_id": str(user_id),
                                    "db_user_id": str(user.id),
                                    "email": user_email,
                                    "user_was_created": str(user.id) != str(user_id)
                                },
                                "sessionId": "debug-session",
                                "runId": "run1",
                                "hypothesisId": "A"
                            }) + "\n")
                    except Exception as e:
                        logger.error(f"Failed to write debug log: {e}", exc_info=True)
                    # #endregion
                else:
                    # This should never happen - get_or_create_user always returns a user
                    logger.error(f"get_or_create_user returned None for email {user_email} - this should not happen!")
            except Exception as e:
                logger.error(f"Error in email fallback lookup/create: {e}", exc_info=True)
                # Continue to raise the original error below
        else:
            # No email in token - this should not happen for valid tokens
            # But let's try to query all users with this ID to see if there's a UUID format issue
            logger.error(f"[AUTH DEBUG] User not found by ID {user_id} and token has no email field for fallback lookup")
            logger.error(f"[AUTH DEBUG] Token payload keys: {list(payload.keys()) if payload else 'None'}")
            
            # #region agent log - No email in token
            import os
            try:
                log_dir = r"c:\Users\issan\records_ai_v2\.cursor"
                log_path = os.path.join(log_dir, "debug.log")
                os.makedirs(log_dir, exist_ok=True)
                with open(log_path, "a", encoding="utf-8") as log_file:
                    log_file.write(json.dumps({
                        "id": "log_no_email_in_token",
                        "timestamp": int(datetime.now().timestamp() * 1000),
                        "location": "auth_middleware.py:298",
                        "message": "User not found by ID AND no email in token - cannot use fallback",
                        "data": {
                            "user_id_from_token": str(user_id),
                            "token_payload_keys": list(payload.keys()) if payload else [],
                            "token_payload_full": dict(payload) if payload else None
                        },
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "A"
                    }) + "\n")
            except Exception as e:
                logger.error(f"Failed to write debug log: {e}", exc_info=True)
            # #endregion
    
    # #region agent log
    import os
    try:
        log_dir = r"c:\Users\issan\records_ai_v2\.cursor"
        log_path = os.path.join(log_dir, "debug.log")
        os.makedirs(log_dir, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps({
                "id": f"log_after_user_lookup",
                "timestamp": int(datetime.now().timestamp() * 1000),
                "location": "auth_middleware.py:147",
                "message": "After user lookup",
                "data": {
                    "user_id": str(user_id),
                    "user_found": user is not None,
                    "user_email": user.email if user else None,
                    "user_id_from_db": str(user.id) if user else None,
                    "used_email_fallback": user_email is not None and user is not None
                },
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "A"
            }) + "\n")
    except Exception as e:
        logger.error(f"Failed to write debug log: {e}", exc_info=True)
    # #endregion
    
    if not user:
        # #region agent log
        import os
        try:
            log_dir = r"c:\Users\issan\records_ai_v2\.cursor"
            log_path = os.path.join(log_dir, "debug.log")
            os.makedirs(log_dir, exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as log_file:
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
        # Final check - if we still don't have a user, provide detailed error
        error_detail = f"User not found. Please sign in again."
        if user_email:
            error_detail += f" Token email: {user_email}, Token user_id: {user_id}. Database may have been reset."
        else:
            error_detail += f" Token user_id: {user_id}, but no email in token. Please re-login to get a new token."
        
        logger.error(f"User not found in database for user_id: {user_id}, email: {user_email}. Token may be from different environment or user was deleted.")
        raise HTTPException(
            status_code=401,
            detail=error_detail
        )
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive.")
    
    # #region agent log
    import os
    try:
        log_dir = r"c:\Users\issan\records_ai_v2\.cursor"
        log_path = os.path.join(log_dir, "debug.log")
        os.makedirs(log_dir, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as log_file:
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
    except Exception as e:
        logger.error(f"Failed to write debug log: {e}", exc_info=True)
    # #endregion
    
    return user


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required. This action is restricted to administrators."
        )
    return user
