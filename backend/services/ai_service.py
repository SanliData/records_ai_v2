"""
AI Service (Mock Version)

Provides a stable interface for text analysis so that other services
(e.g., analysis_service) can call it safely.

UTF-8 (no BOM), English-only.
"""

import random
from typing import Dict


class AIService:
    """
    Lightweight mock AI engine.
    Replace this implementation with a real OpenAI client later.
    """

    def analyze_text(self, text: str) -> Dict:
        """
        Produce a deterministic metadata structure with a randomized confidence score.
        Used by analysis_service for predictable behavior during early development.

        Parameters:
            text (str): Input OCR or extracted text.

        Returns:
            Dict: A dictionary containing mock metadata analysis results.
        """
        metadata_guess = {
            "title": "Unknown Title",
            "artist": "Unknown Artist",
            "label": "Unknown Label",
            "year": None,
        }

        confidence_score = round(random.uniform(0.35, 0.88), 3)

        return {
            "metadata": metadata_guess,
            "confidence": confidence_score,
            "raw_text": text,
        }


# Global singleton instance
ai_service = AIService()
