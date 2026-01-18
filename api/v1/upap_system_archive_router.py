from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(
    prefix="/upap/archive/system",
    tags=["upap-archive-system"],
)

@router.post("/confirm")
def system_archive_confirm(candidate_id: str, approved: bool = True):
    if not approved:
        return {"status": "skipped", "candidate_id": candidate_id}

    return {
        "status": "archived",
        "candidate_id": candidate_id,
        "system_record_id": candidate_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
