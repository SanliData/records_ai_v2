# -*- coding: utf-8 -*-
"""
UserService – UPAP Unified Version (V1 + V2 compatible)
English only – UTF-8 – No emoji
"""

import uuid
from datetime import datetime

from backend.models.user import User


class UserService:
    def __init__(self):
        self._users = {}
        self._email_to_id = {}

    # V1 behavior
    def get_or_create_user(self, email: str) -> User:
        # Exists
        if email in self._email_to_id:
            user_id = self._email_to_id[email]
            return self._users[user_id]

        # New user
        user_id = str(uuid.uuid4())

        user = User(
            user_id=user_id,
            email=email,
            created_at=datetime.utcnow().isoformat(),
            profile={},
            token=f"MAGIC-{user_id}"
        )

        self._users[user_id] = user
        self._email_to_id[email] = user_id

        return user

    # V2 behavior (redirect to V1)
    def ensure_user(self, email: str) -> User:
        return self.get_or_create_user(email)

    # Legacy V1 (keep for compatibility)
    def create_user(self, email: str) -> User:
        if email in self._email_to_id:
            raise ValueError("Email already registered")
        return self.get_or_create_user(email)

    def get_user(self, user_id: str):
        return self._users.get(user_id)


# Global instance
user_service = UserService()
