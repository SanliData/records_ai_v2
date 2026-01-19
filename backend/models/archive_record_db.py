# -*- coding: utf-8 -*-

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.db import Base


class ArchiveRecord(Base):
    __tablename__ = "archive_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    title = Column(String(255))
    artist = Column(String(255))
    album = Column(String(255))
    label = Column(String(255))
    catalog_number = Column(String(100))
    year = Column(String(10))
    format = Column(String(50))
    condition = Column(String(50))
    confidence = Column(Float)
    ocr_text = Column(Text)
    fingerprint = Column(JSON)
    extra_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", backref="archive_records")
