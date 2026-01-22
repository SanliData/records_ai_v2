"""
ArchiveRecord Database Model V2 - AI Pipeline
"""
from sqlalchemy import Column, String, Float, Text, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from backend.db import Base
from backend.models.record_state import RecordState


class ArchiveRecordDB(Base):
    """Database model for archived records."""
    __tablename__ = "archive_records_v2"

    record_id = Column(String(36), primary_key=True, index=True)
    preview_id = Column(String(36), index=True, nullable=True)  # Link to original preview
    user_id = Column(String(36), nullable=False, index=True)
    
    # State
    state = Column(SQLEnum(RecordState), default=RecordState.ARCHIVED, index=True)
    
    # Metadata
    artist = Column(String(255), nullable=True)
    album = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    label = Column(String(255), nullable=True)
    year = Column(String(10), nullable=True)
    catalog_number = Column(String(80), nullable=True)
    format = Column(String(50), nullable=True, default="LP")
    country = Column(String(100), nullable=True)
    
    # File paths
    image_path = Column(Text, nullable=False)
    file_path = Column(Text, nullable=False)
    
    # AI Results
    ocr_text = Column(Text, default="")
    ai_metadata = Column(JSON, nullable=True)
    confidence = Column(Float, default=0.0)
    
    # Pipeline tracking
    model_used = Column(String(100), nullable=True)
    cost_estimate = Column(Float, default=0.0)
    enrichment_source = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    archived_at = Column(DateTime(timezone=True), nullable=True)
