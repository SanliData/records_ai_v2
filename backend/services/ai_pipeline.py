"""
AI Pipeline Orchestrator - Production AI Pipeline
Cost-optimized, auditable, production-safe
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from sqlalchemy.orm import Session
from backend.models.preview_record_db import PreviewRecordDB
from backend.models.record_state import RecordState
from backend.db import SessionLocal
from backend.services.pipeline_logger import pipeline_logger

logger = logging.getLogger(__name__)


class AIPipeline:
    """
    AI Pipeline Orchestrator
    
    Implements cost-optimized model routing:
    - Level 1: OCR + text (cheap)
    - Level 2: Discogs / cache (free)
    - Level 3: Advanced vision (expensive)
    
    Never calls expensive model first.
    """
    
    # Confidence thresholds
    HIGH_CONFIDENCE = 0.75
    AUTO_ARCHIVE_THRESHOLD = 0.9
    
    def __init__(self):
        self.log_entries = []
    
    async def run_ai_pipeline(self, preview_id: str) -> Dict[str, Any]:
        """
        Execute full AI pipeline for a preview record.
        
        Steps:
        1. Vision extraction (OCR + text)
        2. Metadata parsing
        3. Confidence scoring
        4. Escalation logic (if needed)
        5. Save results
        
        Returns:
            {
                "preview_id": "...",
                "state": "AI_ANALYZED",
                "confidence": 0.83,
                "model_used": "vision-mini",
                "cost_estimate": 0.002,
                "metadata": {...}
            }
        """
        # RUNTIME PROOF: Log entry point
        logger.warning(f"[AI_PIPELINE] 🎯 ENTRY: run_ai_pipeline called with preview_id={preview_id}")
        print(f"[AI_PIPELINE] 🎯 ENTRY: run_ai_pipeline called with preview_id={preview_id}")
        
        db = SessionLocal()
        try:
            # Load preview record
            preview = db.query(PreviewRecordDB).filter(
                PreviewRecordDB.preview_id == preview_id
            ).first()
            
            if not preview:
                logger.error(f"[AI_PIPELINE] ❌ Preview record not found: {preview_id}")
                print(f"[AI_PIPELINE] ❌ Preview record not found: {preview_id}")
                raise ValueError(f"Preview record not found: {preview_id}")
            
            logger.warning(f"[AI_PIPELINE] 📥 Preview loaded: preview_id={preview_id}, state={preview.state}, file={preview.canonical_image_path}")
            print(f"[AI_PIPELINE] 📥 Preview loaded: preview_id={preview_id}, state={preview.state}")
            
            if preview.state != RecordState.UPLOADED:
                logger.warning(f"Preview {preview_id} already processed, state: {preview.state}")
                return self._build_response(preview)
            
            # Step 1: Level 1 - OCR + Text Extraction (cheap)
            logger.warning(f"[AI_PIPELINE] 🔍 LEVEL_1_START: preview_id={preview_id}")
            print(f"[AI_PIPELINE] 🔍 LEVEL_1_START: preview_id={preview_id}")
            self._log_step(preview_id, "LEVEL_1_START", {"model": "ocr+text"})
            pipeline_logger.log_step(preview_id, "UPLOADED", "LEVEL_1_START", {"model": "ocr+text"})
            ocr_result = await self._extract_ocr_and_text(preview)
            logger.warning(f"[AI_PIPELINE] 📝 OCR extracted: preview_id={preview_id}, text_length={len(ocr_result.get('text', ''))}")
            print(f"[AI_PIPELINE] 📝 OCR extracted: preview_id={preview_id}, text_length={len(ocr_result.get('text', ''))}")
            
            # Step 2: Parse metadata from OCR
            metadata = await self._parse_metadata(ocr_result)
            confidence = self._calculate_confidence(metadata)
            
            # Step 3: Cost-optimized routing
            if confidence >= self.HIGH_CONFIDENCE:
                # Skip expensive models
                self._log_step(preview_id, "SKIP_EXPENSIVE", {
                    "reason": f"confidence {confidence} >= {self.HIGH_CONFIDENCE}",
                    "model_used": "ocr+text"
                })
                model_used = "ocr+text"
                cost_estimate = 0.001  # Very cheap
            else:
                # Escalate to Level 3 - Advanced vision
                self._log_step(preview_id, "ESCALATE_LEVEL_3", {
                    "reason": f"confidence {confidence} < {self.HIGH_CONFIDENCE}",
                    "model": "gpt-4-vision"
                })
                vision_result = await self._advanced_vision_analysis(preview)
                metadata = self._merge_metadata(metadata, vision_result)
                confidence = self._calculate_confidence(metadata)
                model_used = "gpt-4-vision"
                cost_estimate = 0.01  # More expensive
            
            # Step 4: Update preview record
            logger.warning(f"[AI_PIPELINE] 💾 Updating DB: preview_id={preview_id}, confidence={confidence}, artist={metadata.get('artist')}")
            print(f"[AI_PIPELINE] 💾 Updating DB: preview_id={preview_id}, confidence={confidence}, artist={metadata.get('artist')}")
            
            preview.state = RecordState.AI_ANALYZED
            preview.ocr_text = ocr_result.get("text", "")
            preview.ai_metadata = metadata
            preview.confidence = confidence
            preview.model_used = model_used
            preview.cost_estimate = cost_estimate
            preview.ai_analyzed_at = datetime.utcnow()
            
            # Extract fields for quick access
            preview.artist = metadata.get("artist")
            preview.album = metadata.get("album") or metadata.get("title")
            preview.title = metadata.get("title")
            preview.label = metadata.get("label")
            preview.year = metadata.get("year")
            preview.catalog_number = metadata.get("catalog_number")
            preview.format = metadata.get("format", "LP")
            preview.country = metadata.get("country")
            
            db.commit()
            db.refresh(preview)
            
            # RUNTIME PROOF: Verify database update
            logger.warning(f"[AI_PIPELINE] ✅ DB UPDATED: preview_id={preview_id}, state={preview.state}, artist={preview.artist}, album={preview.album}")
            print(f"[AI_PIPELINE] ✅ DB UPDATED: preview_id={preview_id}, state={preview.state}, artist={preview.artist}, album={preview.album}")
            
            # Step 5: Auto-archive if confidence is very high
            if confidence >= self.AUTO_ARCHIVE_THRESHOLD:
                self._log_step(preview_id, "AUTO_ARCHIVE_TRIGGER", {
                    "confidence": confidence,
                    "threshold": self.AUTO_ARCHIVE_THRESHOLD
                })
                # Note: Archive will be handled by archive endpoint
            
            self._log_step(preview_id, "AI_PIPELINE_COMPLETE", {
                "state": preview.state.value,
                "confidence": confidence,
                "model_used": model_used,
                "cost_estimate": cost_estimate
            })
            pipeline_logger.log_step(preview_id, preview.state.value, "AI_PIPELINE_COMPLETE", {
                "confidence": confidence,
                "model_used": model_used,
                "cost_estimate": cost_estimate,
                "artist": preview.artist,
                "album": preview.album
            })
            
            return self._build_response(preview)
            
        except Exception as e:
            logger.error(f"AI pipeline failed for {preview_id}: {e}", exc_info=True)
            self._log_step(preview_id, "AI_PIPELINE_ERROR", {"error": str(e)})
            raise
        finally:
            db.close()
    
    async def _extract_ocr_and_text(self, preview: PreviewRecordDB) -> Dict[str, Any]:
        """Level 1: OCR + text extraction (cheap)."""
        try:
            from backend.services.vision_engine import vision_engine
            from backend.services.ocr_engine import ocr_engine
            
            image_path = Path(preview.canonical_image_path)
            if not image_path.exists():
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            # OCR extraction
            ocr_text = ocr_engine.run_ocr(str(image_path))
            
            # Basic text detection (vision_engine doesn't have detect_text_regions, skip for now)
            text_regions = []
            
            return {
                "text": ocr_text,
                "text_regions": text_regions,
                "model": "ocr+text"
            }
        except Exception as e:
            logger.warning(f"OCR extraction failed: {e}")
            return {"text": "", "text_regions": [], "model": "ocr+text", "error": str(e)}
    
    async def _parse_metadata(self, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse metadata from OCR text using simple heuristics."""
        text = ocr_result.get("text", "").upper()
        
        metadata = {}
        
        # Simple pattern matching (can be enhanced)
        # This is Level 1 - cheap parsing
        lines = text.split("\n")
        if lines:
            # First line often contains artist/album
            first_line = lines[0].strip()
            if first_line:
                parts = first_line.split("-", 1)
                if len(parts) == 2:
                    metadata["artist"] = parts[0].strip()
                    metadata["album"] = parts[1].strip()
        
        # Look for year (4 digits)
        import re
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        if year_match:
            metadata["year"] = year_match.group()
        
        # Look for catalog number patterns
        catalog_match = re.search(r'\b[A-Z]{1,3}\d{3,6}\b', text)
        if catalog_match:
            metadata["catalog_number"] = catalog_match.group()
        
        return metadata
    
    def _calculate_confidence(self, metadata: Dict[str, Any]) -> float:
        """Calculate confidence score based on extracted fields."""
        score = 0.0
        
        if metadata.get("artist"):
            score += 0.3
        if metadata.get("album") or metadata.get("title"):
            score += 0.3
        if metadata.get("label"):
            score += 0.2
        if metadata.get("year"):
            score += 0.1
        if metadata.get("catalog_number"):
            score += 0.1
        
        return min(score, 1.0)
    
    async def _advanced_vision_analysis(self, preview: PreviewRecordDB) -> Dict[str, Any]:
        """Level 3: Advanced vision analysis (expensive)."""
        try:
            from backend.services.novarchive_gpt_service import novarchive_gpt_service
            
            image_path = preview.canonical_image_path
            result = novarchive_gpt_service.analyze_vinyl_record(
                file_path=image_path,
                raw_bytes=None  # Will read from file
            )
            
            return {
                "artist": result.get("artist"),
                "album": result.get("album") or result.get("title"),
                "title": result.get("title"),
                "label": result.get("label"),
                "year": result.get("year"),
                "catalog_number": result.get("catalog_number"),
                "country": result.get("country"),
                "format": result.get("format", "LP"),
                "confidence": result.get("confidence", 0.5),
                "model": "gpt-4-vision"
            }
        except Exception as e:
            logger.error(f"Advanced vision analysis failed: {e}")
            return {}
    
    def _merge_metadata(self, base: Dict[str, Any], enhancement: Dict[str, Any]) -> Dict[str, Any]:
        """Merge metadata, preferring enhancement values."""
        merged = base.copy()
        for key, value in enhancement.items():
            if value and (not merged.get(key) or key == "confidence"):
                merged[key] = value
        return merged
    
    def _build_response(self, preview: PreviewRecordDB) -> Dict[str, Any]:
        """Build API response from preview record."""
        return {
            "preview_id": preview.preview_id,
            "state": preview.state.value,
            "confidence": preview.confidence,
            "model_used": preview.model_used,
            "cost_estimate": preview.cost_estimate,
            "metadata": {
                "artist": preview.artist,
                "album": preview.album,
                "title": preview.title,
                "label": preview.label,
                "year": preview.year,
                "catalog_number": preview.catalog_number,
                "format": preview.format,
                "country": preview.country
            },
            "ocr_text": preview.ocr_text
        }
    
    def _log_step(self, preview_id: str, step: str, data: Dict[str, Any]):
        """Log pipeline step for audit trail."""
        log_entry = {
            "preview_id": preview_id,
            "step": step,
            "timestamp": datetime.utcnow().isoformat(),
            **data
        }
        self.log_entries.append(log_entry)
        logger.info(f"[AI_PIPELINE] {step}: {log_entry}")


# Singleton
ai_pipeline = AIPipeline()
