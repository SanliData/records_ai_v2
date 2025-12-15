#backend/services/archive_completion_service.py
# UTF-8, English only

from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.db import SessionLocal
from backend.models.archive_record import ArchiveRecord, ArchiveRecordSchema, ArchiveRecordCreate
from backend.models.pending_record import PendingRecord


class ArchiveCompletionService:
    """
    Takes a PendingRecord that the user approved and turns it into an ArchiveRecord.

    Pipeline:
    1. Load pending by id
    2. Build archive payload from pending fields
       (later we can plug in metadata_engine enrichment here)
    3. Insert into archive_records table
    4. Mark pending as 'approved' (or delete, but for now we keep a trace)
    """

    def approve_and_complete(self, pending_id: int) -> ArchiveRecordSchema:
        db = SessionLocal()
        try:
            pending = self._get_pending(db, pending_id)
            if not pending:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Pending record {pending_id} not found",
                )

            archive_obj = self._create_archive_from_pending(db, pending)
            db.commit()
            db.refresh(archive_obj)

            return ArchiveRecordSchema.model_validate(archive_obj)

        finally:
            db.close()

    # ----- internal helpers -----

    def _get_pending(self, db: Session, pending_id: int) -> Optional[PendingRecord]:
        return (
            db.query(PendingRecord)
            .filter(PendingRecord.id == pending_id)
            .first()
        )

    def _create_archive_from_pending(
        self, db: Session, pending: PendingRecord
    ) -> ArchiveRecord:
        """
        Map fields one by one from PendingRecord to ArchiveRecord.
        No external enrichment here yet; that comes later in a
        low-priority background process.
        """

        archive = ArchiveRecord(
            pending_id=pending.id,
            user_id=pending.user_id,
            file_path=pending.storage_path or pending.original_file_path,
            thumbnail_path=pending.thumbnail_path,
            artist=pending.artist,
            album=pending.album,
            label=pending.label,
            year=pending.year,
            catalog_number=pending.catalog_number,
            barcode=pending.barcode,
            format=pending.format,
            country=pending.country,
            pressing_details=pending.pressing_details,
            side_a_runout=pending.side_a_runout,
            side_b_runout=pending.side_b_runout,
            condition=pending.condition,
            notes=pending.notes,
            fingerprint=pending.fingerprint,
        )

        db.add(archive)

        # Keep the pending row but mark as approved.
        pending.status = "approved"

        return archive


archive_completion_service = ArchiveCompletionService()
