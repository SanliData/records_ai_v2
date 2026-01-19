# api/v1/admin_stats_router.py
# UTF-8, English only
# LEGACY FILE - This file is deprecated. Use backend/api/v1/admin_stats_router.py instead.

import logging
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter

logger = logging.getLogger(__name__)

# Defensive import: tinydb is optional (legacy support)
try:
    from tinydb import where
    from backend.db import db
    TINYDB_AVAILABLE = True
except ImportError:
    TINYDB_AVAILABLE = False
    logger.warning("tinydb not available - admin_stats_router legacy endpoints disabled")
    # Create stub db object
    class TinyDBStub:
        def table(self, name):
            return TinyTableStub()
    class TinyTableStub:
        def all(self):
            return []
        def __len__(self):
            return 0
    db = TinyDBStub()

router = APIRouter(
    prefix="/admin/stats",
    tags=["admin-stats"],
)


def _count_table(table_name: str) -> int:
    """
    Safe count of all rows in a TinyDB table.
    If the table does not exist yet, TinyDB returns an empty table.
    """
    if not TINYDB_AVAILABLE:
        return 0
    try:
        table = db.table(table_name)
        return len(table.all())
    except Exception:
        return 0


def _build_auth_stats() -> Dict[str, Any]:
    """
    Aggregate simple auth statistics from TinyDB table 'auth'.
    """
    if not TINYDB_AVAILABLE:
        return {
            "total_rows": 0,
            "distinct_emails": 0,
            "verified_users": 0,
        }
    try:
        table = db.table("auth")
        rows = table.all()
    except Exception:
        return {
            "total_rows": 0,
            "distinct_emails": 0,
            "verified_users": 0,
        }

    total_rows = len(rows)
    distinct_emails = len({row.get("email") for row in rows if row.get("email")})

    verified_count = len(
        [row for row in rows if row.get("verified") is True]
    )

    return {
        "total_rows": total_rows,
        "distinct_emails": distinct_emails,
        "verified_users": verified_count,
    }


def _build_pending_stats() -> Dict[str, Any]:
    """
    Aggregate simple pending record statistics from TinyDB table 'pending_records'.
    Uses fields that exist in the current V1 JSON structure.
    """
    if not TINYDB_AVAILABLE:
        return {
            "total_pending": 0,
            "by_format": {},
        }
    try:
        table = db.table("pending_records")
        rows = table.all()
    except Exception:
        return {
            "total_pending": 0,
            "by_format": {},
        }

    total = len(rows)
    formats: Dict[str, int] = {}

    for row in rows:
        fmt = (
            row.get("normalized_format")
            or row.get("file_type")
            or "unknown"
        )
        formats[fmt] = formats.get(fmt, 0) + 1

    return {
        "total_pending": total,
        "by_format": formats,
    }


def _build_user_library_stats() -> Dict[str, Any]:
    """
    Aggregate user library statistics from TinyDB table 'user_library'.
    Structure is compatible with current UserLibraryService:
    {
        "user_id": int,
        "records": [...],
        "favorites": [...],
        "notes": {record_id: str}
    }
    """
    if not TINYDB_AVAILABLE:
        return {
            "user_rows": 0,
            "total_records_links": 0,
            "total_favorites": 0,
            "total_notes": 0,
        }
    try:
        table = db.table("user_library")
        rows = table.all()
    except Exception:
        return {
            "user_rows": 0,
            "total_records_links": 0,
            "total_favorites": 0,
            "total_notes": 0,
        }

    user_rows = len(rows)
    records_count = 0
    favorites_count = 0
    notes_count = 0

    for row in rows:
        records = row.get("records") or []
        favorites = row.get("favorites") or []
        notes = row.get("notes") or {}

        records_count += len(records)
        favorites_count += len(favorites)
        notes_count += len(notes)

    return {
        "user_rows": user_rows,
        "total_records_links": records_count,
        "total_favorites": favorites_count,
        "total_notes": notes_count,
    }


def _build_archive_stats() -> Dict[str, Any]:
    """
    Archive stats based on TinyDB table 'archive_records'.
    If V1 has not started writing archive_records yet,
    this will simply return zeros.
    """
    if not TINYDB_AVAILABLE:
        return {
            "total_archive_records": 0,
            "by_label": {},
            "by_artist": {},
        }
    try:
        table = db.table("archive_records")
        rows = table.all()
    except Exception:
        return {
            "total_archive_records": 0,
            "by_label": {},
            "by_artist": {},
        }

    total = len(rows)
    by_label: Dict[str, int] = {}
    by_artist: Dict[str, int] = {}

    for row in rows:
        label = row.get("label") or "unknown"
        artist = row.get("artist") or "unknown"

        by_label[label] = by_label.get(label, 0) + 1
        by_artist[artist] = by_artist.get(artist, 0) + 1

    return {
        "total_archive_records": total,
        "by_label": by_label,
        "by_artist": by_artist,
    }


@router.get("/summary")
def get_summary_stats() -> Dict[str, Any]:
    """
    High-level summary for admin dashboards.

    This endpoint is intentionally cheap and read-only.
    It does not mutate any data.
    """
    now = datetime.utcnow().isoformat()

    auth_stats = _build_auth_stats()
    pending_stats = _build_pending_stats()
    user_lib_stats = _build_user_library_stats()
    archive_stats = _build_archive_stats()

    return {
        "timestamp_utc": now,
        "counts": {
            "pending_records": pending_stats["total_pending"],
            "archive_records": archive_stats["total_archive_records"],
            "auth_rows": auth_stats["total_rows"],
            "auth_distinct_emails": auth_stats["distinct_emails"],
            "auth_verified_users": auth_stats["verified_users"],
            "user_library_rows": user_lib_stats["user_rows"],
        },
        "pending": pending_stats,
        "auth": auth_stats,
        "user_library": user_lib_stats,
        "archive": archive_stats,
    }


@router.get("/upap-funnel")
def get_upap_funnel() -> Dict[str, Any]:
    """
    Very simple UPAP-style funnel statistics for dashboards.

    This is only an approximation based on current V1 data:
    - upload_stage: number of pending_records + archive_records
    - process_stage: approximated by archive_records
    - archive_stage: archive_records
    - publish_stage: currently 0 in V1 (placeholder)
    """
    pending_stats = _build_pending_stats()
    archive_stats = _build_archive_stats()

    pending_count = pending_stats["total_pending"]
    archive_count = archive_stats["total_archive_records"]

    upload_stage = pending_count + archive_count
    process_stage = archive_count
    archive_stage = archive_count
    publish_stage = 0  # V1: not implemented yet

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
