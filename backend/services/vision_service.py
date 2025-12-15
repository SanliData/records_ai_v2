# -*- coding: utf-8 -*-
# ======================================================
# DEPRECATED – Replaced by the UPAP pipeline
# Do NOT use. Scheduled for removal in V2 cleanup.
# ======================================================
#backend/services/vision_service.py
# UTF-8 (NO BOM) â€” English only

class VisionService:
    """
    Placeholder vision engine.
    Real OCR/vision models can be integrated later.
    Provides dummy outputs to keep the API functional.
    """

    def extract_text(self, file_bytes: bytes) -> str:
        """
        Fake OCR: returns a static string.
        """
        if not file_bytes:
            return ""
        return "DUMMY_OCR_RESULT"

    def external_lookup(self, text: str) -> dict:
        """
        Fake external search. Returns predictable demo metadata.
        """
        return {
            "source": "dummy_lookup",
            "artist": "Unknown Artist",
            "album": "Unknown Album",
            "confidence": 0.0,
            "query": text
        }


# Export an instance to be imported everywhere
vision_service = VisionService()

