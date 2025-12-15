# -*- coding: utf-8 -*-
# ======================================================
# DEPRECATED – Replaced by the UPAP pipeline
# Do NOT use. Scheduled for removal in V2 cleanup.
# ======================================================
# backend/services/analysis_service.py
# UTF-8 (NO BOM), English-only.

from typing import Dict, Any

from backend.services.ai_service import ai_service  # OpenAI wrapper
from backend.services.metadata_engine import metadata_engine
from backend.services.ocr_service import ocr_service
from backend.services.upload_service import upload_service


class AnalysisService:
    """
    High-level orchestration layer for analyzing audio / image / text
    and producing structured metadata for Records_AI.
    This version has NO DEPENDENCY on fingerprint_service.
    """

    def analyze_record(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Master pipeline:
        1. Upload â†’ get URL
        2. OCR / vision pass
        3. AI enrichment pass
        4. Metadata merge
        """
        if not file_bytes:
            return {"error": "empty_file"}

        # 1) upload
        url = upload_service.store(file_bytes, filename)

        # 2) OCR / vision
        ocr_text = ocr_service.extract_text(file_bytes)

        # 3) AI enrichment
        ai_meta = ai_service.enrich_text(ocr_text)

        # 4) Metadata merge
        final = metadata_engine.merge(
            {
                "source_url": url,
                "ocr_text": ocr_text,
                "ai_metadata": ai_meta,
            }
        )

        return final


analysis_service = AnalysisService()

