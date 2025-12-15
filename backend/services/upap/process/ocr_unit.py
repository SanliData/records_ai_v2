# File: backend/services/upap/process/ocr_unit.py
# -*- coding: utf-8 -*-
"""
OCRUnit
Lightweight OCR module for UPAP ProcessStage.

Role-3 design:
- This is a minimal, safe implementation for V1.
- It does NOT call external OCR engines yet.
- It returns a stable, predictable output to avoid breaking imports.
- In V2, this class will wrap ocr_service or a real OCR backend.
"""

from typing import Optional


class OCRUnit:
    """
    Provides OCR text extraction for UPAP ProcessStage.

    In V1:
        - No real OCR is performed.
        - Returns None or a small placeholder string.

    In V2:
        - Connect to backend.services.ocr_service.ocr_service.extract_text()
        - Or integrate a real OCR library.
    """

    def run(self, file_path: str) -> Optional[str]:
        """
        Extracts text from a file (placeholder in V1).

        :param file_path: Path to the stored file.
        :return: OCR text or None.
        """

        if not file_path:
            return None

        # V1-safe behavior: no actual OCR
        return None
