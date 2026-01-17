# -*- coding: utf-8 -*-

class User:
    def __init__(self, user_id: str, email: str, created_at: str, profile: dict, token: str, is_admin: bool = False):
        self.id = user_id
        self.email = email
        self.created_at = created_at
        self.profile = profile
        self.token = token
        self.is_admin = is_admin

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "created_at": self.created_at,
            "profile": self.profile,
            "token": self.token,
            "is_admin": self.is_admin
        }
