from fastapi import APIRouter, Form
from backend.services.upap.engine.upap_engine import upap_engine


router = APIRouter(prefix="/upap", tags=["UPAP"])

@router.post("/archive")
def archive_record(record_id: str = Form(...)):
    """
    UPAP Archive Stage endpoint.
    Uses engine public method: run_archive()
    """
    return upap_engine.run_archive(record_id)
