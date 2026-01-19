# -*- coding: utf-8 -*-
# backend/services/dashboard_service.py
# English only, UTF-8

from __future__ import annotations

import logging
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from statistics import mean
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.models.archive_record_db import ArchiveRecord

logger = logging.getLogger(__name__)


class DashboardService:
    """
    DashboardService

    Computes per-user and global statistics for:
    - Archive records (final stored records)

    This service is READ-ONLY:
    - It never mutates the database.
    - Safe to call from routers and admin tools.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _parse_dt(value: Any) -> Optional[datetime]:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except Exception:
                return None
        return None

    @staticmethod
    def _safe_confidence(records: List[Any]) -> Optional[float]:
        vals: List[float] = []
        for r in records:
            c = r.confidence if hasattr(r, "confidence") else None
            if isinstance(c, (int, float)):
                vals.append(float(c))
        if not vals:
            return None
        return float(mean(vals))

    @staticmethod
    def _file_type_from_path(path: str) -> str:
        path = path or ""
        lower = path.lower()
        if "." in lower:
            return lower.rsplit(".", 1)[-1]
        return "unknown"

    def get_user_summary(self, user_id: str) -> Dict[str, Any]:
        user_records = self.db.query(ArchiveRecord).filter(ArchiveRecord.user_id == user_id).all()

        if not user_records:
            return {
                "user_id": user_id,
                "total_archives": 0,
                "first_archive_at": None,
                "last_archive_at": None,
                "avg_confidence": None,
                "by_file_type": {},
            }

        dates: List[datetime] = []
        for r in user_records:
            dt = self._parse_dt(r.created_at if hasattr(r, "created_at") else None)
            if dt is not None:
                dates.append(dt)

        first_at: Optional[str] = None
        last_at: Optional[str] = None
        if dates:
            first_at = min(dates).isoformat()
            last_at = max(dates).isoformat()

        avg_conf = self._safe_confidence(user_records)

        file_counter: Counter[str] = Counter()
        for r in user_records:
            fp = getattr(r, "file_path", None) or ""
            file_counter[self._file_type_from_path(fp)] += 1

        return {
            "user_id": user_id,
            "total_archives": len(user_records),
            "first_archive_at": first_at,
            "last_archive_at": last_at,
            "avg_confidence": avg_conf,
            "by_file_type": dict(file_counter),
        }

    def get_user_timeline(
        self,
        user_id: str,
        days: int = 30,
    ) -> Dict[str, Any]:
        if days <= 0:
            days = 30

        try:
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        except (ValueError, AttributeError):
            return {
                "user_id": user_id,
                "days": days,
                "points": [],
            }

        now = datetime.utcnow()
        since = now - timedelta(days=days)

        user_records = self.db.query(ArchiveRecord).filter(ArchiveRecord.user_id == user_uuid).all()

        bucket: defaultdict[str, int] = defaultdict(int)

        for r in user_records:
            if not r.created_at:
                continue
            if r.created_at < since:
                continue
            key = r.created_at.date().isoformat()
            bucket[key] += 1

        points: List[Dict[str, Any]] = []
        for i in range(days + 1):
            d = (since + timedelta(days=i)).date().isoformat()
            points.append({"date": d, "count": int(bucket.get(d, 0))})

        return {
            "user_id": user_id,
            "days": days,
            "points": points,
        }

    def get_user_recent_records(
        self,
        user_id: str,
        limit: int = 20,
    ) -> Dict[str, Any]:
        try:
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        except (ValueError, AttributeError):
            return {
                "user_id": user_id,
                "limit": limit,
                "records": [],
            }
        
        records = self.db.query(ArchiveRecord).filter(
            ArchiveRecord.user_id == user_uuid
        ).order_by(ArchiveRecord.created_at.desc()).limit(limit).all()

        projected: List[Dict[str, Any]] = []
        for r in records:
            projected.append({
                "archive_id": str(r.id),
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "title": r.title,
                "artist": r.artist,
                "label": r.label,
                "file_path": r.file_path,
                "confidence": r.confidence,
            })

        return {
            "user_id": user_id,
            "limit": limit,
            "records": projected,
        }

    def get_global_summary(self) -> Dict[str, Any]:
        all_records = self.db.query(ArchiveRecord).all()

        if not all_records:
            return {
                "total_archives": 0,
                "unique_users": 0,
                "avg_confidence": None,
                "by_file_type": {},
            }

        users = {r.user_id for r in all_records if r.user_id is not None}
        avg_conf = self._safe_confidence(all_records)

        file_counter: Counter[str] = Counter()
        for r in all_records:
            fp = r.file_path or ""
            file_counter[self._file_type_from_path(fp)] += 1

        return {
            "total_archives": len(all_records),
            "unique_users": len(users),
            "avg_confidence": avg_conf,
            "by_file_type": dict(file_counter),
        }


def get_dashboard_service(db: Session) -> DashboardService:
    return DashboardService(db)
