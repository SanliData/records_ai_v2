# File: backend/services/upap/process/vision_unit.py
# -*- coding: utf-8 -*-
"""
VisionUnit
Lightweight image analysis module for UPAP ProcessStage.

Role-3 design:
- Keep this module fully operational without real CV dependencies.
- Returns a stable dict structure for future compatibility.
- In V2, this will wrap vision_service or other CV engines.
"""

from typing import Optional, Dict


class VisionUnit:
    """
    Provides vision fingerprinting for UPAP ProcessStage.

    V1 behavior:
        - Does NOT perform real vision analysis.
        - Returns a placeholder fingerprint dict.

    This maintains pipeline stability without requiring OpenCV,
    Pillow, or external GPU-based models.
    """

    def run(self, file_path: str) -> Optional[Dict]:
        """
        Extracts visual fingerprint of the file (placeholder in V1).

        :param file_path: Path to the stored uploaded file.
        :return: Minimal dict fingerprint or None.
        """

        if not file_path:
            return None

        # Very lightweight placeholder.
        # V2+ will extract dominant colors, edge maps, embeddings, etc.
        return {
            "fingerprint": "placeholder",
            "source": "vision_unit_v1"
        }
