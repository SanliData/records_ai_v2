# File: backend/services/upap/process/ai_unit.py
# -*- coding: utf-8 -*-
"""
AIUnit
Central AI metadata extraction wrapper for UPAP ProcessStage.

Role-3 design:
- Do NOT call OpenAI directly in V1 for pipeline stability.
- Wraps the backend.services.ai_service mock.
- Ensures a consistent interface for ProcessStage and future models.
"""

from typing import Dict, Any
from backend.services.ai_service import ai_service


class AIUnit:
    """
    Provides AI-based metadata extraction.

    V1 Behavior:
        - Delegates all inference to ai_service (mock).
        - Ensures stable return format for ProcessStage.

    V2 Behavior:
        - Will route requests to OpenAI GPT models.
    """

    def run(self, text_hint: str) -> Dict[str, Any]:
        """
        Runs metadata inference on the hint text.

        :param text_hint: Combined text from filename, OCR, and other signals.
        :return: Dict in the form:
                 {
                    "metadata": {...},
                    "confidence": float,
                    "raw_text": "...",
                 }
        """

        if not text_hint:
            # Fallback for broken contexts
            return {
                "metadata": {
                    "title": None,
                    "artist": None,
                    "label": None,
                    "year": None
                },
                "confidence": 0.0,
                "raw_text": None
            }

        return ai_service.analyze_text(text_hint)
