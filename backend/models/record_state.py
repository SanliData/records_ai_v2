"""
Record State Machine - Production AI Pipeline
"""
from enum import Enum


class RecordState(str, Enum):
    """State machine for AI-orchestrated pipeline."""
    UPLOADED = "uploaded"
    AI_ANALYZED = "ai_analyzed"
    USER_REVIEWED = "user_reviewed"
    ENRICHED = "enriched"
    ARCHIVED = "archived"
