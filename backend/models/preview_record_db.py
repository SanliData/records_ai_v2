"""
PreviewRecord Database Model - AI Pipeline State Management
"""
from sqlalchemy import Column, String, Float, Text, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from backend.db import Base
from backend.models.record_state import RecordState


class PreviewRecordDB(Base):
    """Database model for preview records with state machine."""
    __tablename__ = "preview_records"

    preview_id = Column(String(36), primary_key=True, index=True)
    record_id = Column(String(36), index=True, nullable=True)  # Generated at archive
    
    # State machine
    state = Column(SQLEnum(RecordState), default=RecordState.UPLOADED, index=True)
    
    # File paths
    file_path = Column(Text, nullable=False)
    canonical_image_path = Column(Text, nullable=False)
    
    # User
    user_id = Column(String(36), nullable=False, index=True)
    
    # AI Results
    ocr_text = Column(Text, default="")
    ai_metadata = Column(JSON, nullable=True)
    confidence = Column(Float, default=0.0)
    
    # Extracted metadata
    artist = Column(String(255), nullable=True)
    album = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    label = Column(String(255), nullable=True)
    year = Column(String(10), nullable=True)
    catalog_number = Column(String(80), nullable=True)
    format = Column(String(50), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Pipeline tracking
    model_used = Column(String(100), nullable=True)  # e.g., "vision-mini", "gpt-4-vision"
    cost_estimate = Column(Float, default=0.0)
    enrichment_source = Column(String(100), nullable=True)  # e.g., "cache", "discogs", "ai"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    ai_analyzed_at = Column(DateTime(timezone=True), nullable=True)
    user_reviewed_at = Column(DateTime(timezone=True), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)
