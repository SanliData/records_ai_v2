# File: backend/services/upap/process/adapters/domain_adapter.py
# -*- coding: utf-8 -*-
"""
DomainAdapter
Abstract base class for mapping generic AI metadata
into domain-specific structured metadata.

Role-3 design:
- Each domain (vinyl, book, game, etc.) implements its own adapter.
- Prevents embedding domain-specific logic directly into stages.
- Guarantees consistent interface for metadata mapping.
"""

from typing import Dict, Any


class DomainAdapter:
    """
    Base adapter used for transforming AI metadata + OCR text + vision features
    into a structured domain-specific metadata dictionary.

    Example domain outputs:
    - Vinyl metadata
    - Book metadata
    - NFT metadata
    - Game metadata

    The UPAP ProcessStage will call:
        adapter.map_metadata(ai_meta, ocr_text, vision_fingerprint)
    """

    def map_metadata(
        self,
        ai_meta: Dict[str, Any],
        ocr_text: str | None,
        vision_fingerprint: Dict[str, Any] | None
    ) -> Dict[str, Any]:
        """
        Override this method to implement domain-specific metadata
        transformation.

        Expected output:
            { ... domain fields ... }
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.map_metadata() must be implemented"
        )
