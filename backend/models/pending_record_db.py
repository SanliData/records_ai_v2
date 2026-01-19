# -*- coding: utf-8 -*-

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.db import Base


class PendingRecord(Base):
    __tablename__ = "pending_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))
    title_guess = Column(String(255))
    artist_guess = Column(String(255))
    label_guess = Column(String(255))
    confidence = Column(Float)
    ocr_text = Column(Text)
    vision_fingerprint = Column(JSON)
    extra_metadata = Column(JSON)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", backref="pending_records")
