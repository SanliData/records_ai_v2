# -*- coding: utf-8 -*-
# backend/services/dashboard_service.py
# English only, UTF-8

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta
from statistics import mean
from typing import Any, Dict, List, Optional

from tinydb import Query

from backend.db import db


class DashboardService:
    """
    DashboardService

    Computes per-user and global statistics for:
    - Archive records (final stored records)
    - Pipeline activity over time

    This service is READ-ONLY:
    - It never mutates the database.
    - Safe to call from routers and admin tools.
    """

    def __init__(self) -> None:
        # Main tables (TinyDB)
        self._archives = db.table("archives")
        self._pending = db.table("pending_records")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_dt(value: Any) -> Optional[datetime]:
        """
        Best effort parsing of created_at / timestamp fields.
        Supports:
        - ISO8601 strings
        - Already-datetime objects
        Returns None if parsing fails.
        """
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except Exception:
                return None
        return None

    @staticmethod
    def _safe_confidence(records: List[Dict[str, Any]]) -> Optional[float]:
        vals: List[float] = []
        for r in records:
            c = r.get("confidence")
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

    # ------------------------------------------------------------------
    # Public API – per-user
    # ------------------------------------------------------------------

    def get_user_summary(self, user_id: int) -> Dict[str, Any]:
        """
        High level summary for a given user_id.

        Returns:
            {
              "user_id": int,
              "total_archives": int,
              "first_archive_at": str | null,
              "last_archive_at": str | null,
              "avg_confidence": float | null,
              "by_file_type": { "jpg": 12, "png": 3, ... }
            }
        """
        q = Query()
        user_records: List[Dict[str, Any]] = self._archives.search(q.user_id == user_id)

        if not user_records:
            return {
                "user_id": user_id,
                "total_archives": 0,
                "first_archive_at": None,
                "last_archive_at": None,
                "avg_confidence": None,
                "by_file_type": {},
            }

        # Dates
        dates: List[datetime] = []
        for r in user_records:
            dt = self._parse_dt(r.get("created_at"))
            if dt is not None:
                dates.append(dt)

        first_at: Optional[str] = None
        last_at: Optional[str] = None
        if dates:
            first_at = min(dates).isoformat()
            last_at = max(dates).isoformat()

        # Confidence
        avg_conf = self._safe_confidence(user_records)

        # File type histogram
        file_counter: Counter[str] = Counter()
        for r in user_records:
            fp = r.get("file_path") or ""
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
        user_id: int,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Simple daily timeline for last N days.

        Returns:
            {
              "user_id": int,
              "days": int,
              "points": [
                {"date": "2025-12-01", "count": 3},
                ...
              ]
            }
        """
        if days <= 0:
            days = 30

        now = datetime.utcnow()
        since = now - timedelta(days=days)

        q = Query()
        user_records: List[Dict[str, Any]] = self._archives.search(q.user_id == user_id)

        bucket: defaultdict[str, int] = defaultdict(int)

        for r in user_records:
            dt = self._parse_dt(r.get("created_at"))
            if dt is None:
                continue
            if dt < since:
                continue
            key = dt.date().isoformat()
            bucket[key] += 1

        # Fill missing days with zero for better charts
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
        user_id: int,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Return last N archive records for the user.

        Result is meant for table views in the dashboard, NOT full export.
        """
        q = Query()
        records: List[Dict[str, Any]] = self._archives.search(q.user_id == user_id)

        # Sort by created_at desc (best effort)
        def sort_key(r: Dict[str, Any]) -> Any:
            dt = self._parse_dt(r.get("created_at"))
            if dt is None:
                return datetime.min
            return dt

        records_sorted = sorted(records, key=sort_key, reverse=True)
        limited = records_sorted[: max(0, limit)]

        # Thin projection to keep payload small
        projected: List[Dict[str, Any]] = []
        for r in limited:
            projected.append(
                {
                    "archive_id": r.get("archive_id"),
                    "created_at": r.get("created_at"),
                    "title": r.get("title"),
                    "artist": r.get("artist"),
                    "label": r.get("label"),
                    "file_path": r.get("file_path"),
                    "confidence": r.get("confidence"),
                }
            )

        return {
            "user_id": user_id,
            "limit": limit,
            "records": projected,
        }

    # ------------------------------------------------------------------
    # Global stats (optional, for admin / overview)
    # ------------------------------------------------------------------

    def get_global_summary(self) -> Dict[str, Any]:
        """
        Global summary across all users.
        """
        all_records: List[Dict[str, Any]] = self._archives.all()

        if not all_records:
            return {
                "total_archives": 0,
                "unique_users": 0,
                "avg_confidence": None,
                "by_file_type": {},
            }

        users = {r.get("user_id") for r in all_records if r.get("user_id") is not None}
        avg_conf = self._safe_confidence(all_records)

        file_counter: Counter[str] = Counter()
        for r in all_records:
            fp = r.get("file_path") or ""
            file_counter[self._file_type_from_path(fp)] += 1

        return {
            "total_archives": len(all_records),
            "unique_users": len(users),
            "avg_confidence": avg_conf,
            "by_file_type": dict(file_counter),
        }


# Global instance
dashboard_service = DashboardService()
