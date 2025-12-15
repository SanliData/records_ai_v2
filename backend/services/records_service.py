# -*- coding: utf-8 -*-
# ======================================================
# DEPRECATED – Replaced by the UPAP pipeline
# Do NOT use. Scheduled for removal in V2 cleanup.
# ======================================================
# backend/services/records_service.py
# UTF-8 (no BOM), English-only.

from backend.db import SessionLocal
from backend.models.records import ArchiveRecord
from backend.models.pending_record import PendingRecord


class RecordsService:
    """
    Read-only service for listing archive and pending records.
    """

    def list_archive(self):
        with SessionLocal() as db:
            return db.query(ArchiveRecord).all()

    def list_pending(self):
        with SessionLocal() as db:
            return db.query(PendingRecord).all()


records_service = RecordsService()

