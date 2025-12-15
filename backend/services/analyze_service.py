# -*- coding: utf-8 -*-
# ======================================================
# DEPRECATED – Replaced by the UPAP pipeline
# Do NOT use. Scheduled for removal in V2 cleanup.
# ======================================================
#backend/services/analysis_service.py
from __future__ import annotations

import uuid
from pathlib import Path
from backend.services.ocr_engine import ocr_engine
from backend.services.vision_engine import vision_engine
from backend.services.metadata_engine import metadata_engine
from backend.models.pending_record import PendingRecord
from backend.db import get_session
from backend.core.paths import STORAGE_UPLOADS
from backend.services.openai_client import openai_client


class AnalyzeService:
    """
    High-accuracy metadata inference pipeline.
    This is the central processing unit for record recognition.
    """

    def process_upload(self, file_bytes: bytes, filename: str) -> PendingRecord:
        # 1. Save raw file
        file_id = str(uuid.uuid4())
        ext = Path(filename).suffix.lower()
        saved_path = STORAGE_UPLOADS / f"{file_id}{ext}"
        saved_path.write_bytes(file_bytes)

        # 2. Normalize image (heicÃ¢â€ â€™jpg, rotation, crop)
        normalized_img = metadata_engine.normalize_image(saved_path)
        normalized_path = STORAGE_UPLOADS / f"{file_id}_norm.jpg"
        normalized_img.save(normalized_path)

        # 3. OCR extraction
        ocr_text = ocr_engine.extract_text(normalized_path)

        # 4. Vision fingerprint
        fingerprint = vision_engine.generate_fingerprint(normalized_path)

        # 5. OpenAI metadata inference (strict-first-stage high accuracy)
        ai_guess = metadata_engine.generate_metadata_guess(
            ocr_text=ocr_text,
            fingerprint=fingerprint
        )

        # 6. Merge all info
        merged = metadata_engine.merge_all(
            ai_guess=ai_guess,
            ocr_text=ocr_text,
            fingerprint=fingerprint
        )

        # 7. Create PendingRecord
        pending = PendingRecord(
            file_id=file_id,
            file_path=str(normalized_path),
            raw_ocr=ocr_text,
            raw_fingerprint=fingerprint,
            ai_metadata=merged,
            status="pending"
        )

        with get_session() as session:
            session.add(pending)
            session.commit()
            session.refresh(pending)

        return pending


analysis_service = AnalyzeService()

