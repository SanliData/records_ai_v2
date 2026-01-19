# -*- coding: utf-8 -*-

from typing import Any, Dict
from sqlalchemy.orm import Session

from backend.services.upap.engine.stage_interface import StageInterface
from backend.services.user_service import get_user_service


class AuthStage(StageInterface):
    name = "auth"

    def validate_input(self, payload: Dict[str, Any]) -> None:
        email = payload.get("email")
        if not email or not isinstance(email, str):
            raise ValueError("AuthStage.run() requires 'email' in context")
        if "db" not in payload:
            raise ValueError("AuthStage.run() requires 'db' (Session) in context")

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        email = context["email"]
        db: Session = context["db"]

        user_service = get_user_service(db)
        user = user_service.get_or_create_user(email)

        return {
            "user_id": str(user.id),
            "email": user.email,
        }
