# backend/api/v1/admin_stats_router.py
# UTF-8, English only

import logging
from datetime import datetime
from typing import Any, Dict
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends
from backend.db import get_db
from backend.models.user import User
from backend.models.archive_record_db import ArchiveRecord
from backend.models.pending_record_db import PendingRecord

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin/stats",
    tags=["admin-stats"],
)


@router.get("/summary")
def get_summary_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    now = datetime.utcnow().isoformat()

    user_count = db.query(User).count()
    active_user_count = db.query(User).filter(User.is_active == True).count()
    admin_count = db.query(User).filter(User.role == "admin").count()

    pending_count = db.query(PendingRecord).count()
    archive_count = db.query(ArchiveRecord).count()

    return {
        "timestamp_utc": now,
        "counts": {
            "pending_records": pending_count,
            "archive_records": archive_count,
            "users": user_count,
            "active_users": active_user_count,
            "admins": admin_count,
        },
    }


@router.get("/upap-funnel")
def get_upap_funnel(db: Session = Depends(get_db)) -> Dict[str, Any]:
    pending_count = db.query(PendingRecord).count()
    archive_count = db.query(ArchiveRecord).count()

    upload_stage = pending_count + archive_count
    process_stage = archive_count
    archive_stage = archive_count
    publish_stage = 0

    return {
        "timestamp_utc": datetime.utcnow().isoformat(),
        "stages": {
            "upload": upload_stage,
            "process": process_stage,
            "archive": archive_stage,
            "publish": publish_stage,
        },
        "raw": {
            "pending_records": pending_count,
            "archive_records": archive_count,
        },
    }
