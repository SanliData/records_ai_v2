# backend/storage/user_store.py
# UTF-8, English only

"""
Temporary user storage for UPAP AuthStage.

This is a minimal, in-memory implementation to satisfy
AuthStage imports and enable pipeline testing.

It MUST be replaced by a real persistence layer later
(DB, external auth service, etc.).
"""

_FAKE_USERS = {
    # Example token for local testing
    "test-token": {
        "id": "user-test-1",
        "email": "test@example.com",
        "email_verified": False,
    }
}


def get_user_by_token(token: str):
    """
    Resolve a user by access token.

    Temporary behavior:
    - Returns user dict if token exists
    - Returns None if token is unknown
    """
    return _FAKE_USERS.get(token)
