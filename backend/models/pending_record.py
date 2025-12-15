#backend/models/pending_record.py
# UTF-8, English only

from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class PendingRecord(BaseModel):
    """
    Persistent object representing an image that has been processed
    by the analysis pipeline but not yet approved by the user.

    This object must be serializable and safely stored either in DB
    or lightweight JSON-store depending on your backend strategy.
    """

    pending_id: str = Field(..., description="UUID generated at upload stage")
    file_path: str = Field(..., description="Filesystem path pointing to normalized JPEG")
    original_filename: str = Field(..., description="Name of the file uploaded by the user")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    # OCR result (may be empty but always present)
    ocr_text: str = Field("", description="OCR extracted from the label area")

    # Fingerprint data extracted by VisionEngine
    fingerprint: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Vision-based runout matrix, label signature, contour hash, etc.",
    )

    # AI metadata guess — high recall, low precision allowed
    ai_guess: Optional[Dict[str, Any]] = Field(
        default=None,
        description="AI-based metadata guess (artist, album, label, year)",
    )

    # Normalization
    normalized_format: str = Field("jpeg")
    normalized_path: str = Field(..., description="Final normalized JPEG path")

    class Config:
        from_attributes = True  # replaces orm_mode
