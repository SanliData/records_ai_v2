# -*- coding: utf-8 -*-
"""
Pydantic Schemas for Archive Endpoint
Input validation with constraints
"""

from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional
from datetime import datetime
import re


class ArchiveRequestSchema(BaseModel):
    """
    P2: Input Validation + XSS Safety
    
    Validates archive request with constraints:
    - String length limits
    - Year range validation
    - Type validation
    """
    
    record_id: str = Field(..., min_length=1, max_length=255, description="Record ID (UUID)")
    preview_id: Optional[str] = Field(None, max_length=255, description="Preview ID (UUID)")
    email: Optional[str] = Field(None, max_length=255, description="User email")
    
    # Metadata fields with length constraints
    artist: Optional[str] = Field(None, max_length=255, description="Artist name")
    album: Optional[str] = Field(None, max_length=255, description="Album name")
    title: Optional[str] = Field(None, max_length=255, description="Release title")
    label: Optional[str] = Field(None, max_length=255, description="Record label")
    catalog_number: Optional[str] = Field(None, max_length=80, description="Catalog number")
    format: Optional[str] = Field(None, max_length=50, description="Format (LP, EP, etc.)")
    country: Optional[str] = Field(None, max_length=100, description="Country of release")
    
    # Year validation
    year: Optional[str] = Field(None, max_length=10, description="Release year")
    
    # File paths
    file_path: Optional[str] = Field(None, max_length=500, description="File path")
    thumbnail_url: Optional[str] = Field(None, max_length=500, description="Thumbnail URL")
    canonical_image_path: Optional[str] = Field(None, max_length=500, description="Canonical image path")
    
    # Additional fields
    matrix_info: Optional[str] = Field(None, max_length=500, description="Matrix/runout info")
    side: Optional[str] = Field(None, max_length=10, description="Side indicator (A/B)")
    ocr_text: Optional[str] = Field(None, description="OCR text")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    
    # Nested record data
    record_data: Optional[dict] = Field(None, description="Nested record data")
    
    @validator('year')
    def validate_year(cls, v):
        """Validate year is in reasonable range."""
        if v is None:
            return v
        
        # Extract numeric year if string contains numbers
        year_match = re.search(r'\d{4}', str(v))
        if year_match:
            year_int = int(year_match.group())
            # Allow years from 1900 to current year + 1
            current_year = datetime.now().year
            if 1900 <= year_int <= current_year + 1:
                return str(year_int)
        
        # If year doesn't match pattern, return as-is (could be "1980s" or "Unknown")
        return v[:10]  # Truncate if too long
    
    @validator('artist', 'album', 'label', 'catalog_number')
    def sanitize_xss(cls, v):
        """P2: XSS Safety - Strip script tags and dangerous HTML."""
        if v is None:
            return v
        
        v_str = str(v)
        
        # Remove script tags
        v_str = re.sub(r'<script[^>]*>.*?</script>', '', v_str, flags=re.IGNORECASE | re.DOTALL)
        v_str = re.sub(r'<script[^>]*>', '', v_str, flags=re.IGNORECASE)
        
        # Remove other dangerous HTML
        v_str = re.sub(r'<iframe[^>]*>', '', v_str, flags=re.IGNORECASE)
        v_str = re.sub(r'<object[^>]*>', '', v_str, flags=re.IGNORECASE)
        v_str = re.sub(r'<embed[^>]*>', '', v_str, flags=re.IGNORECASE)
        
        # Remove javascript: protocol
        v_str = re.sub(r'javascript:', '', v_str, flags=re.IGNORECASE)
        
        return v_str.strip()
    
    class Config:
        # Allow extra fields for backward compatibility
        extra = "allow"
        # Validate on assignment
        validate_assignment = True
