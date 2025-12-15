# -*- coding: utf-8 -*-
# ======================================================
# DEPRECATED – Replaced by the UPAP pipeline
# Do NOT use. Scheduled for removal in V2 cleanup.
# ======================================================
#backend/services/local_vision.py
# UTF-8, English only

from __future__ import annotations
from typing import Any, Dict, Optional
from pathlib import Path


class LocalVisionClient:
    """
    Lightweight fallback if OpenAI is not available or low confidence.
    For now it returns dummy values; later we can add Tesseract, ORB, etc.
    """

    def analyze_image(self, file_path: Path | str, raw_bytes: Optional[bytes] = None) -> Dict[str, Any]:
        # TODO: integrate real local OCR / image hashing here.
        return {
            "ocr_text": "",
            "ai_guess": {},
            "fingerprint": {},
            "confidence": 0.0,
        }

