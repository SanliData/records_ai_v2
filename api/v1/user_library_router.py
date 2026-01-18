# UTF-8 — English only

from fastapi import APIRouter, Query
from backend.services.user_library_service import user_library_service

router = APIRouter(prefix="/user/library", tags=["User Library"])

@router.get("")
def list_user_records(user_id: int = Query(...)):
    """
    Returns all archive records for the given user.
    Includes thumbnails, confidence, title, artist, and file paths.
    """
    return {
        "status": "ok",
        "records": user_library_service.list_user_records(user_id)
    }

@router.get("/record/{archive_id}")
def get_record(archive_id: str):
    record = user_library_service.get_record(archive_id)
    if not record:
        return {"status": "error", "message": "Record not found"}
    return {"status": "ok", "record": record}

@router.delete("/record/{archive_id}")
def delete_record(archive_id: str):
    ok = user_library_service.delete_record(archive_id)
    return {"status": "ok" if ok else "error"}

@router.put("/record/{archive_id}")
def update_record(archive_id: str, payload: dict):
    updated = user_library_service.update_record(archive_id, payload)
    return {"status": "ok", "record": updated}
