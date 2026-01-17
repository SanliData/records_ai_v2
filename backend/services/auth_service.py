# -*- coding: utf-8 -*-
# ======================================================
# DEPRECATED – Replaced by the UPAP pipeline
# Do NOT use. Scheduled for removal in V2 cleanup.
# ======================================================
# backend/services/auth_service.py
# UTF-8 â€” English only

from tinydb import where
from backend.storage.database import db
import requests


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

    # ---------------------------------------------------
    # GOOGLE OAUTH VERIFICATION
    # ---------------------------------------------------
    def verify_google_token(self, google_token: str) -> dict:
        """
        Verify Google OAuth token and extract user email.
        Returns dict with status and email.
        """
        try:
            # Verify token with Google API
            verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={google_token}"
            response = requests.get(verify_url, timeout=10)
            
            if response.status_code != 200:
                return {"status": "invalid", "error": "Token verification failed"}
            
            token_data = response.json()
            
            # Check if token is expired (optional - Google usually handles this)
            # Check if email is verified
            if not token_data.get("email_verified"):
                return {"status": "unverified", "error": "Email not verified"}
            
            email = token_data.get("email")
            if not email:
                return {"status": "invalid", "error": "No email in token"}
            
            # Generate our own token for the session
            import uuid
            session_token = str(uuid.uuid4())
            
            # Store token in auth table
            self.table.insert({
                "email": email,
                "token": session_token,
                "verified": True,
                "auth_provider": "google",
                "google_id": token_data.get("sub")
            })
            
            return {
                "status": "ok",
                "email": email,
                "token": session_token
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}


auth_service = AuthService()

