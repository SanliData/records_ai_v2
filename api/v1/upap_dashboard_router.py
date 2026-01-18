from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(
    prefix="/upap/dashboard",
    tags=["upap-dashboard"],
)

@router.get("/summary")
def dashboard_summary():
    return {
        "status": "ok",
        "scope": "system",
        "records_total": 0,
        "users_total": 0,
        "pending_recognition": 0,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }
