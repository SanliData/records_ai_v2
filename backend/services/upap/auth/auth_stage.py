# -*- coding: utf-8 -*-
"""
AuthStage – resolves user identity from email.

For now this is a simple in-memory example:
in a real system this would query a User service or database.
"""

from typing import Any, Dict
import uuid

from backend.services.upap.engine.stage_interface import StageInterface


class AuthStage(StageInterface):
    name = "auth"

    def validate_input(self, payload: Dict[str, Any]) -> None:
        email = payload.get("email")
        if not email or not isinstance(email, str):
            raise ValueError("AuthStage.run() requires 'email' in context")

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        email = context["email"]

        # In a real system: lookup or create user.
        # Here we just generate a deterministic user_id for testing.
        user_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"upap-user:{email}"))

        return {
            "user_id": user_id,
            "email": email,
        }
