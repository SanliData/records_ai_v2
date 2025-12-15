# -*- coding: utf-8 -*-
# ======================================================
# DEPRECATED – Replaced by the UPAP pipeline
# Do NOT use. Scheduled for removal in V2 cleanup.
# ======================================================
# backend/services/auth_service.py
# UTF-8 â€” English only

from tinydb import where
from backend.storage.database import db


class AuthService:
    """
    Simplified email â†’ token login flow stored in TinyDB.
    No encryption, no JWT, only dev-mode demo auth.
    """

    def __init__(self):
        self.table = db.table("auth")

    # ---------------------------------------------------
    # REQUEST LOGIN
    # ---------------------------------------------------
    def request_login(self, email: str) -> str:
        """
        Create a login token and store it.
        """
        import uuid

        token = str(uuid.uuid4())

        # store a request record
        self.table.insert({
            "email": email,
            "token": token,
            "verified": False
        })

        return token

    # ---------------------------------------------------
    # VERIFY LOGIN
    # ---------------------------------------------------
    def verify_token(self, token: str) -> dict:
        """
        Verify a login token and activate the session.
        """
        row = self.table.get(where("token") == token)
        if not row:
            return {"status": "invalid"}

        # mark as verified
        row["verified"] = True

        # update document
        self.table.update(row, where("token") == token)

        return {
            "status": "ok",
            "email": row["email"]
        }

    # ---------------------------------------------------
    # OPTIONAL â€” Lookup verified user by token
    # ---------------------------------------------------
    def get_user_by_token(self, token: str):
        row = self.table.get((where("token") == token) & (where("verified") == True))
        return row


auth_service = AuthService()

