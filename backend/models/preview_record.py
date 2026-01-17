# backend/models/preview_record.py
# UTF-8, English only
# UPAP V2 Compliance: PreviewRecord model

from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class PreviewRecord(BaseModel):
    """
    UPAP V2 Compliance: Non-authoritative preview state.
    
    PreviewRecord represents a record that has been processed through
    Upload → Process stages but is NOT yet owned, saved, or published.
    
    Key characteristics:
    - No user ownership (no user_id)
    - Not persisted to archive
    - Not published
    - Temporary state only
    - Can be discarded without consequence
    """
    
    preview_id: str = Field(..., description="Temporary UUID for preview state")
    record_id: str = Field(..., description="UPAP record_id from upload stage")
    
    # Canonical normalized image
    canonical_image_path: str = Field(..., description="Path to normalized canonical image")
    
    # Process stage results
    ocr_text: str = Field(default="", description="OCR extracted text")
    ai_metadata: Optional[Dict[str, Any]] = Field(default=None, description="AI metadata guess")
    process_result: Optional[Dict[str, Any]] = Field(default=None, description="Process stage output")
    
    # Display metadata (for UI)
    artist: Optional[str] = None
    album: Optional[str] = None
    title: Optional[str] = None
    label: Optional[str] = None
    year: Optional[int] = None
    catalog_number: Optional[str] = None
    format: Optional[str] = None
    country: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # State indicators
    is_preview: bool = Field(default=True, description="Always True for PreviewRecord")
    is_archived: bool = Field(default=False, description="False until Archive stage")
    is_published: bool = Field(default=False, description="False until Publish stage")
    
    class Config:
        from_attributes = True




