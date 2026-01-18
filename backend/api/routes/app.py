from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from uuid import uuid4
from typing import Optional

router = APIRouter()

# -------------------------------------------------------------------
# Simple Bearer Token Auth (ChatGPT App MVP)
# -------------------------------------------------------------------

SERVICE_TOKEN = "recordsai-chatgpt-app-token"


def require_token(authorization: Optional[str]):
    if authorization != f"Bearer {SERVICE_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")


# -------------------------------------------------------------------
# ChatGPT App Endpoints
# -------------------------------------------------------------------

@router.post("/upload")
async def app_upload(
    image: UploadFile = File(...),
    title: Optional[str] = None,
    artist: Optional[str] = None,
    email: Optional[str] = None,
    authorization: Optional[str] = Header(default=None),
):
    """
    ChatGPT App entrypoint.

    - Receives vinyl cover image + optional metadata
    - Creates a PendingRecord (future)
    - Triggers UPAP pipeline / async worker (future)
    """

    # --- Auth ---
    require_token(authorization)

    # --- Record ID (DB will become source of truth later) ---
    record_id = str(uuid4())

    # --- PLACEHOLDER PIPELINE ---
    # TODO:
    # - Save image to storage
    # - Create PendingRecord in DB
    # - Trigger UPAP async pipeline / worker

    return {
        "record_id": record_id,
        "status": "PENDING",
        "stage": "UPLOADED",
        "message": "Upload received. Processing started."
    }


@router.get("/status/{record_id}")
def app_status(
    record_id: str,
    authorization: Optional[str] = Header(default=None),
):
    """
    ChatGPT App polling endpoint.

    ChatGPT will repeatedly call this endpoint until:
    - stage == PUBLISHED
    - or stage == FAILED
    """

    # --- Auth ---
    require_token(authorization)

    if not record_id:
        raise HTTPException(status_code=400, detail="record_id is required")

    # --- PLACEHOLDER STATE ---
    # TODO:
    # - Fetch real state from DB
    # - Return final result when published

    return {
        "record_id": record_id,
        "status": "IN_PROGRESS",
        "stage": "ANALYZING",
        "progress": 0.5,
        "result": None
    }
