# backend/services/upap/user/user_auth_stage.py
# UTF-8, English only

from sqlalchemy.orm import Session
from backend.services.user_service import get_user_service


class UserAuthStage:
    """UPAP stage: validate user by email."""

    def __init__(self, db: Session):
        self.db = db

    def run(self, payload: dict):
        if "email" not in payload:
            raise ValueError("UserAuthStage requires 'email'")

        email = payload["email"]

        user_service = get_user_service(self.db)
        user = user_service.get_or_create_user(email)

        return {
            "user_id": str(user.id),
            "email": user.email
        }
