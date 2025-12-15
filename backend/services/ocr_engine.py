#backend/services/ocr_engine.py
# UTF-8, English only
# Records_AI v2 â€” OCR Engine with legacy compatibility shim

import re
from pathlib import Path


class OCREngine:
    """
    Minimal OCR engine.
    Provides both:
      - run_ocr(path)
      - extract_text_from_image(path)  <-- legacy API compatibility
    """

    def run_ocr(self, file_path: str) -> str:
        """
        Main OCR function used by the new metadata engine.
        """
        path = Path(file_path)
        if not path.exists():
            raise RuntimeError(f"OCR engine: file not found: {path}")

        # Minimal deterministic text extraction from filename
        tokens = re.findall(r"[A-Za-z0-9]+", path.stem)
        return " ".join(tokens).strip()

    # ---------------------------------------------------------
    # LEGACY SUPPORT (for analysis_service old import)
    # ---------------------------------------------------------
    def extract_text_from_image(self, file_path: str) -> str:
        """
        Legacy wrapper for backward compatibility.
        Old code expects this function.
        """
        return self.run_ocr(file_path)


# Singleton instance
ocr_engine = OCREngine()

# Legacy-level function export (optional but safe)
extract_text_from_image = ocr_engine.extract_text_from_image
