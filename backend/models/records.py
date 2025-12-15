#backend/models/records.py
# UTF-8, English only

from datetime import datetime
from pydantic import BaseModel, Field


# -------------------------------
# Shared base model
# -------------------------------
class BaseRecord(BaseModel):
    record_id: str = Field(..., description="Unique identifier of the record")
    user_id: str = Field(..., description="Owner of the uploaded record")

    title: str | None = Field(default=None)
    artist: str | None = Field(default=None)
    label: str | None = Field(default=None)
    catalog_number: str | None = Field(default=None)

    image_path: str | None = Field(default=None, description="Stored original image")
    fingerprint: str | None = Field(default=None, description="VisionEngine hash")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# -------------------------------
# 1. PendingRecord
# Before user approval
# -------------------------------
class PendingRecord(BaseRecord):
    status: str = Field(default="pending")
    ai_confidence: float | None = None
    ocr_text: str | None = None
    auto_metadata: dict | None = None


class PendingRecordSchema(PendingRecord):
    model_config = {"from_attributes": True}


# -------------------------------
# 2. ArchiveRecord
# After user approves
# -------------------------------
class ArchiveRecord(BaseRecord):
    status: str = Field(default="archived")

    # User-editable fields after approval
    condition: str | None = None
    user_notes: str | None = None

    # External API enhancement results (Discogs, MusicBrainz, etc.)
    enrichment_data: dict | None = None


class ArchiveRecordSchema(ArchiveRecord):
    model_config = {"from_attributes": True}


# -------------------------------
# 3. Update Request DTO
# -------------------------------
class ApproveRecordRequest(BaseModel):
    condition: str | None = None
    user_notes: str | None = None
