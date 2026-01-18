from fastapi import APIRouter, Form, Body, HTTPException
from backend.services.auth_service import auth_service
from backend.services.user_service import user_service
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/auth", tags=["auth"])

class GoogleTokenRequest(BaseModel):
    token: str

@router.post("/login/google")
async def login_with_google(request: GoogleTokenRequest):
    """
    Login with Google OAuth token.
    Verifies Google ID token and returns session token.
    
    No approval required - valid Google account is automatically accepted as user.
    User is created/retrieved automatically upon login.
    """
    result = auth_service.verify_google_token(request.token)
    
    if result.get("status") != "ok":
        raise HTTPException(
            status_code=401,
            detail=result.get("error", "Google authentication failed")
        )
    
    email = result.get("email")
    token = result.get("token")
    
    # Automatically get or create user (no approval needed)
    user = user_service.get_or_create_user(email)
    
    return {
        "status": "ok",
        "token": token,
        "email": email,
        "user_id": user.id,
        "is_admin": user.is_admin,
        "message": "Login successful. User account automatically created/activated."
    }

@router.post("/login/request")
def request_login(email: str = Form(...)):
    """DEPRECATED: Use Google OAuth instead"""
    token = auth_service.request_login(email)
    return {"status": "token_generated", "token": token}

@router.post("/login/verify")
def verify_login(token: str = Form(...)):
    """DEPRECATED: Use Google OAuth instead"""
    return auth_service.verify_token(token)
