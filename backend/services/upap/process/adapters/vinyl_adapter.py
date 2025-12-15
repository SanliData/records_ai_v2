# File: backend/services/upap/process/adapters/vinyl_adapter.py
# -*- coding: utf-8 -*-
"""
VinylAdapter
Maps generic AI metadata, OCR text, and vision fingerprint
into a vinyl-record-specific metadata dictionary.

Role-3 notes:
- Keep implementation stable and simple for V1.
- Do NOT fetch external metadata sources yet.
- This adapter only reshapes the AI metadata into V1 vinyl structure.
"""

from typing import Dict, Any
from .domain_adapter import DomainAdapter


class VinylAdapter(DomainAdapter):
    """
    Concrete domain adapter for vinyl records.

    Responsible for transforming:
        ai_meta        → base metadata (title, artist, label, year)
        ocr_text       → additional hints (rarely used in V1)
        vision_fingerprint → future visual cues (V2+)
    """

    def map_metadata(
        self,
        ai_meta: Dict[str, Any],
        ocr_text: str | None,
        vision_fingerprint: Dict[str, Any] | None
    ) -> Dict[str, Any]:
        """
        Produce vinyl-specific metadata dictionary.

        Expected ai_meta structure:
            {
                "title": "...",
                "artist": "...",
                "label": "...",
                "year": 1983 or None
            }
        """

        return {
            "title": ai_meta.get("title"),
            "artist": ai_meta.get("artist"),
            "label": ai_meta.get("label"),
            "year": ai_meta.get("year"),
            "ocr_text": ocr_text,                     # preserved for debugging
            "vision_fingerprint": vision_fingerprint  # reserved for V2
        }
