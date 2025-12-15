from fastapi import APIRouter, Form
from backend.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login/request")
def request_login(email: str = Form(...)):
    token = auth_service.request_login(email)
    return {"status": "token_generated", "token": token}

@router.post("/login/verify")
def verify_login(token: str = Form(...)):
    return auth_service.verify_token(token)
