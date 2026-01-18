from fastapi import APIRouter, Query
from backend.services.upap.engine.upap_engine import upap_engine

router = APIRouter(prefix="/upap", tags=["upap"])

@router.post("/publish")
def publish_record(record_id: str = Query(...)):
    return upap_engine.run_publish(record_id)
