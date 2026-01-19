from fastapi import APIRouter
import os

router = APIRouter()

# Service token for ChatGPT App integration (from environment)
SERVICE_TOKEN = os.getenv("SERVICE_TOKEN")
if not SERVICE_TOKEN:
    raise RuntimeError(
        "SERVICE_TOKEN environment variable is required for ChatGPT App integration. "
        "Set it in Cloud Run environment variables or Secret Manager."
    )


@router.post("/token")
def issue_token():
    """
    OAuth-like token endpoint for ChatGPT App.
    ChatGPT will call this to obtain an access token.
    """
    return {
        "access_token": SERVICE_TOKEN,
        "token_type": "bearer",
        "expires_in": 3600
    }
