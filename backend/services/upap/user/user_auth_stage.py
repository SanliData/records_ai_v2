# backend/services/upap/user/user_auth_stage.py
# UTF-8, English only

from backend.services.user_service import user_service


class UserAuthStage:
    """UPAP stage: validate user by email."""

    def run(self, payload: dict):
        if "email" not in payload:
            raise ValueError("UserAuthStage requires 'email'")

        email = payload["email"]

        # Fetch or auto-create user
        user = user_service.get_or_create_user(email)

        return {
            "user_id": user.id,
            "email": user.email
        }
