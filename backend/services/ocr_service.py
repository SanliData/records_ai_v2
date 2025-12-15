# -*- coding: utf-8 -*-
# ======================================================
# DEPRECATED – Replaced by the UPAP pipeline
# Do NOT use. Scheduled for removal in V2 cleanup.
# ======================================================
#backend/services/ocr_service.py
# UTF-8, English only

from backend.services.ocr_engine import OCREngine


class OCRService:
    def __init__(self):
        self.engine = OCREngine()

    def extract_text(self, image_path: str):
        """
        Extracts text from an image using the OCR engine.
        The engine handles preprocessing internally.
        """
        return self.engine.extract_text_from_image(image_path)


# Singleton instance for import
ocr_service = OCRService()

