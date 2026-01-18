from fastapi import APIRouter
from datetime import datetime, timezone
import uuid

router = APIRouter(
    prefix="/upap/recognition",
    tags=["upap-recognition"],
)

@router.post("/candidate")
def recognition_candidate(record_id: str):
    candidate_id = str(uuid.uuid4())
    return {
        "status": "ok",
        "record_id": record_id,
        "candidate_id": candidate_id,
        "source": "placeholder",
        "confidence": 0.65,
        "suggested": {
            "artist": "UNKNOWN",
            "title": "UNKNOWN",
            "label": None,
            "year": None,
        },
        "needs_user_confirmation": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
