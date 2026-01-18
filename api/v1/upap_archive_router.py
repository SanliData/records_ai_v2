from fastapi import APIRouter, Form
from backend.services.upap.engine.upap_engine import upap_engine


router = APIRouter(tags=["upap-archive"])

@router.post("/archive")
def archive_record(record_id: str = Form(...)):
    return upap_engine.run_archive(record_id)
