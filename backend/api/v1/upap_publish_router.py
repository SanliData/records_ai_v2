from fastapi import APIRouter, Query
from backend.services.upap.engine.upap_engine import upap_engine

router = APIRouter(prefix="/upap", tags=["UPAP"])

@router.post("/publish")
def publish_record(record_id: str = Query(...)):
    """
    UPAP Publish Stage endpoint.
    Uses engine public method: run_publish()
    """
    return upap_engine.run_publish(record_id)
