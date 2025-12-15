# -*- coding: utf-8 -*-
# ======================================================
# DEPRECATED – Replaced by the UPAP pipeline
# Do NOT use. Scheduled for removal in V2 cleanup.
# ======================================================
import uuid
from datetime import datetime
from tinydb import TinyDB, Query
from pydantic import BaseModel, Field


# -----------------------------
# Pydantic MODELs
# -----------------------------

class PendingModel(BaseModel):
    id: str
    created_at: str
    ocr_text: str
    ai_guess: dict
    confidence: float
    fingerprint: str
    source: str
    user_id: int


class ArchiveModel(BaseModel):
    id: str
    created_at: str
    ocr_text: str
    ai_guess: dict
    confidence: float
    fingerprint: str
    user_id: int


# -----------------------------
# SERVICE
# -----------------------------

class ArchiveService:

    def __init__(self):
        self.db = TinyDB("records_db.json")
        self.table_pending = self.db.table("pending")
        self.table_archive = self.db.table("archive")

    # EXACT match check
    def find_exact(self, fingerprint: str):
        q = Query()
        return self.table_archive.get(q.fingerprint == fingerprint)

    # SAVE PENDING
    def save_pending(self, ocr_text: str, ai_guess: dict,
                     confidence: float, fingerprint: str,
                     source: str, user_id: int):

        obj = PendingModel(
            id=str(uuid.uuid4()),
            created_at=datetime.utcnow().isoformat(),
            ocr_text=ocr_text,
            ai_guess=ai_guess,
            confidence=confidence,
            fingerprint=fingerprint,
            source=source,
            user_id=user_id
        )

        self.table_pending.insert(obj.model_dump())
        return obj.id

    # APPROVE â†’ ARCHIVE
    def approve(self, pending_id: str):
        q = Query()
        entry = self.table_pending.get(q.id == pending_id)
        if not entry:
            return None

        new_item = ArchiveModel(
            id=str(uuid.uuid4()),
            created_at=datetime.utcnow().isoformat(),
            ocr_text=entry["ocr_text"],
            ai_guess=entry["ai_guess"],
            confidence=entry["confidence"],
            fingerprint=entry["fingerprint"],
            user_id=entry["user_id"]
        )

        self.table_archive.insert(new_item.model_dump())
        self.table_pending.remove(q.id == pending_id)

        return new_item.model_dump()

    # LIST pending
    def list_pending(self):
        return self.table_pending.all()

    # LIST archive
    def list_archive(self):
        return self.table_archive.all()

    # SINGLE
    def get_record(self, record_id: str):
        q = Query()
        return self.table_archive.get(q.id == record_id)


# GLOBAL INSTANCE
archive_service = ArchiveService()

