# -*- coding: utf-8 -*-
"""
B2B Company Model - Company information for customer pool
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.db import Base


class Company(Base):
    """Target customer company information"""
    __tablename__ = "b2b_companies"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("b2b_products.id"), nullable=True, index=True)  # Related product
    name = Column(String(255), nullable=False, index=True)
    official_name = Column(String(500))  # Official company name
    website = Column(String(500))
    industry = Column(String(255))
    company_size = Column(String(50))  # 1-10, 11-50, 51-200, etc.
    
    # Address information
    address_line1 = Column(String(500))
    address_line2 = Column(String(500))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(50))
    country = Column(String(100))
    
    # Geographic coordinates (for 10 meter accuracy)
    latitude = Column(Float)
    longitude = Column(Float)
    address_validated = Column(Boolean, default=False)
    address_validation_date = Column(DateTime)
    address_validation_source = Column(String(100))  # Google Maps, OpenStreetMap, etc.
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, default=dict)  # Additional information (SIC codes, tax number, etc.)
    
    # Relationships
    product = relationship("Product", back_populates="companies")
    personas = relationship("Persona", back_populates="company", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="company", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "name": self.name,
            "official_name": self.official_name,
            "website": self.website,
            "industry": self.industry,
            "company_size": self.company_size,
            "address": {
                "line1": self.address_line1,
                "line2": self.address_line2,
                "city": self.city,
                "state": self.state,
                "postal_code": self.postal_code,
                "country": self.country,
            },
            "location": {
                "latitude": self.latitude,
                "longitude": self.longitude,
            },
            "address_validated": self.address_validated,
            "address_validation_date": self.address_validation_date.isoformat() if self.address_validation_date else None,
            "address_validation_source": self.address_validation_source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata or {},
        }

