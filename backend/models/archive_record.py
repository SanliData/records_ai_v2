#backend/models/archive_record.py
# UTF-8, English only

from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class ArchiveRecord(BaseModel):
    """
    Fully approved archival entry. Mandatory fields must be complete,
    missing fields may be filled later by slow background enrichment.
    """

    id: str = Field(..., description="Unique ID in archive (UUID)")
    approved_at: datetime = Field(default_factory=datetime.utcnow)

    # Core metadata
    artist: Optional[str] = None
    album: Optional[str] = None
    label: Optional[str] = None
    catalog_number: Optional[str] = None
    release_year: Optional[str] = None

    # More optional enrichment fields
    tracklist: Optional[list[str]] = None
    genre: Optional[str] = None
    notes: Optional[str] = None

    # Fingerprint snapshot
    fingerprint: Optional[Dict[str, Any]] = None

    # File pointer
    file_path: str = Field(..., description="Path to archived normalized image")

    class Config:
        from_attributes = True
