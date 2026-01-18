from fastapi import APIRouter

router = APIRouter()

# VERY SIMPLE SERVICE TOKEN (MVP)
SERVICE_TOKEN = "recordsai-chatgpt-app-token"


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
