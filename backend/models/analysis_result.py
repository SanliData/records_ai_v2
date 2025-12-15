#backend/models/analysis_result.py
# UTF-8
from pydantic import BaseModel
from typing import Optional, Dict, List


class AnalysisResult(BaseModel):
    """The AI summary produced during upload analysis."""

    file_path: str
    title_guess: Optional[str] = None
    artist_guess: Optional[str] = None
    label_guess: Optional[str] = None

    ocr_text: Optional[str] = None
    vision_fingerprint: Optional[Dict] = None

    confidence: float = 0.0
    warnings: List[str] = []
