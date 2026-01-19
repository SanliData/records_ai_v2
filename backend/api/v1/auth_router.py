from fastapi import APIRouter, Form, Body, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.db import get_db
from backend.services.auth_service import get_auth_service
from backend.services.user_service import get_user_service
from backend.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


class GoogleTokenRequest(BaseModel):
    token: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login/google")
async def login_with_google(
    request: GoogleTokenRequest,
    db: Session = Depends(get_db)
):
    auth_service = get_auth_service(db)
    result = auth_service.verify_google_token(request.token)
    
    if result.get("status") != "ok":
        raise HTTPException(
            status_code=401,
            detail=result.get("error", "Google authentication failed")
        )
    
    email = result.get("email")
    token = result.get("token")
    user_id = result.get("user_id")
    
    user_service = get_user_service(db)
    user = user_service.get_or_create_user(email)
    
    return {
        "status": "ok",
        "token": token,
        "email": email,
        "user_id": user_id,
        "is_admin": user.is_admin,
        "message": "Login successful. User account automatically created/activated."
    }


@router.post("/login")
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    auth_service = get_auth_service(db)
    user = auth_service.authenticate_user(request.email, request.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = auth_service.create_access_token({"sub": str(user.id), "email": user.email})
    
    return {
        "status": "ok",
        "token": token,
        "email": user.email,
        "user_id": str(user.id),
        "is_admin": user.is_admin
    }


@router.post("/register")
async def register(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    auth_service = get_auth_service(db)
    try:
        user = auth_service.create_user(request.email, request.password)
        token = auth_service.create_access_token({"sub": str(user.id), "email": user.email})
        return {
            "status": "ok",
            "token": token,
            "email": user.email,
            "user_id": str(user.id),
            "is_admin": user.is_admin
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login/request")
def request_login(email: str = Form(...), db: Session = Depends(get_db)):
    raise HTTPException(status_code=410, detail="DEPRECATED: Use /auth/login or /auth/login/google instead")


@router.post("/login/verify")
def verify_login(token: str = Form(...), db: Session = Depends(get_db)):
    raise HTTPException(status_code=410, detail="DEPRECATED: Use /auth/login or /auth/login/google instead")
