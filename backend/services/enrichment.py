"""
Enrichment Service - Cost-Optimized Metadata Enrichment
Tries cheap sources first, escalates only when needed
"""
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.models.preview_record_db import PreviewRecordDB
from backend.models.record_state import RecordState
from backend.db import SessionLocal

logger = logging.getLogger(__name__)


class EnrichmentService:
    """
    Enrichment Service
    
    Cost-optimized enrichment strategy:
    1. Try cache (free, instant)
    2. Try Discogs API (free, fast)
    3. Only call AI if still missing (expensive)
    """
    
    def __init__(self):
        self.cache = {}  # Simple in-memory cache (can be Redis in production)
    
    async def enrich_metadata(
        self, 
        preview_id: str,
        force_ai: bool = False
    ) -> Dict[str, Any]:
        """
        Enrich metadata for a preview record.
        
        Args:
            preview_id: Preview record ID
            force_ai: Skip cache/Discogs and go straight to AI
        
        Returns:
            {
                "preview_id": "...",
                "state": "ENRICHED",
                "enrichment_source": "cache|discogs|ai",
                "metadata": {...}
            }
        """
        db = SessionLocal()
        try:
            preview = db.query(PreviewRecordDB).filter(
                PreviewRecordDB.preview_id == preview_id
            ).first()
            
            if not preview:
                raise ValueError(f"Preview record not found: {preview_id}")
            
            if preview.state != RecordState.USER_REVIEWED:
                logger.warning(f"Preview {preview_id} not in USER_REVIEWED state: {preview.state}")
            
            # Step 1: Check cache (free, instant)
            if not force_ai:
                cache_key = self._build_cache_key(preview)
                cached = self._get_from_cache(cache_key)
                if cached:
                    logger.info(f"[ENRICHMENT] Cache hit for {preview_id}")
                    return self._apply_enrichment(preview, cached, "cache", db)
            
            # Step 2: Try Discogs API (free, fast)
            if not force_ai:
                discogs_result = await self._try_discogs(preview)
                if discogs_result:
                    logger.info(f"[ENRICHMENT] Discogs hit for {preview_id}")
                    # Cache the result
                    self._set_cache(cache_key, discogs_result)
                    return self._apply_enrichment(preview, discogs_result, "discogs", db)
            
            # Step 3: AI enrichment (expensive, last resort)
            logger.info(f"[ENRICHMENT] Escalating to AI for {preview_id}")
            ai_result = await self._ai_enrichment(preview)
            if ai_result:
                # Cache the result
                self._set_cache(cache_key, ai_result)
                return self._apply_enrichment(preview, ai_result, "ai", db)
            
            # No enrichment found
            logger.warning(f"[ENRICHMENT] No enrichment found for {preview_id}")
            preview.state = RecordState.ENRICHED
            preview.enrichment_source = "none"
            db.commit()
            
            return {
                "preview_id": preview_id,
                "state": preview.state.value,
                "enrichment_source": "none",
                "metadata": self._extract_metadata(preview)
            }
            
        except Exception as e:
            logger.error(f"Enrichment failed for {preview_id}: {e}", exc_info=True)
            raise
        finally:
            db.close()
    
    def _build_cache_key(self, preview: PreviewRecordDB) -> str:
        """Build cache key from preview metadata."""
        parts = [
            preview.artist or "",
            preview.album or preview.title or "",
            preview.label or "",
            preview.year or ""
        ]
        return "|".join(parts).lower().strip()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get enrichment from cache."""
        return self.cache.get(cache_key)
    
    def _set_cache(self, cache_key: str, data: Dict[str, Any]):
        """Store enrichment in cache."""
        self.cache[cache_key] = data
        # Simple cache eviction (keep last 1000 entries)
        if len(self.cache) > 1000:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
    
    async def _try_discogs(self, preview: PreviewRecordDB) -> Optional[Dict[str, Any]]:
        """Try Discogs API for metadata enrichment."""
        try:
            # Check if Discogs token is available
            import os
            discogs_token = os.getenv("DISCOGS_TOKEN")
            if not discogs_token:
                logger.debug("Discogs token not configured, skipping")
                return None
            
            from backend.services.vinyl_pricing_service import vinyl_pricing_service
            
            # Build search query
            query_parts = []
            if preview.artist:
                query_parts.append(preview.artist)
            if preview.album or preview.title:
                query_parts.append(preview.album or preview.title)
            
            if not query_parts:
                return None
            
            query = " ".join(query_parts)
            
            # Search Discogs
            results = vinyl_pricing_service.search_discogs(query)
            if results and len(results) > 0:
                # Use first result
                result = results[0]
                return {
                    "artist": result.get("artist") or preview.artist,
                    "album": result.get("album") or preview.album or preview.title,
                    "title": result.get("title") or preview.title,
                    "label": result.get("label") or preview.label,
                    "year": result.get("year") or preview.year,
                    "catalog_number": result.get("catalog_number") or preview.catalog_number,
                    "country": result.get("country") or preview.country,
                    "format": result.get("format") or preview.format
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"Discogs enrichment failed: {e}")
            return None
    
    async def _ai_enrichment(self, preview: PreviewRecordDB) -> Optional[Dict[str, Any]]:
        """AI-based enrichment (expensive, last resort)."""
        try:
            from backend.services.novarchive_gpt_service import novarchive_gpt_service
            
            image_path = preview.canonical_image_path
            result = novarchive_gpt_service.analyze_vinyl_record(
                file_path=image_path,
                raw_bytes=None
            )
            
            return {
                "artist": result.get("artist"),
                "album": result.get("album") or result.get("title"),
                "title": result.get("title"),
                "label": result.get("label"),
                "year": result.get("year"),
                "catalog_number": result.get("catalog_number"),
                "country": result.get("country"),
                "format": result.get("format", "LP")
            }
            
        except Exception as e:
            logger.error(f"AI enrichment failed: {e}")
            return None
    
    def _apply_enrichment(
        self,
        preview: PreviewRecordDB,
        enrichment: Dict[str, Any],
        source: str,
        db: Session
    ) -> Dict[str, Any]:
        """Apply enrichment data to preview record."""
        # Only fill missing fields
        if not preview.artist and enrichment.get("artist"):
            preview.artist = enrichment["artist"]
        if not preview.album and enrichment.get("album"):
            preview.album = enrichment["album"]
        if not preview.title and enrichment.get("title"):
            preview.title = enrichment["title"]
        if not preview.label and enrichment.get("label"):
            preview.label = enrichment["label"]
        if not preview.year and enrichment.get("year"):
            preview.year = enrichment["year"]
        if not preview.catalog_number and enrichment.get("catalog_number"):
            preview.catalog_number = enrichment["catalog_number"]
        if not preview.country and enrichment.get("country"):
            preview.country = enrichment["country"]
        if not preview.format and enrichment.get("format"):
            preview.format = enrichment["format"]
        
        preview.state = RecordState.ENRICHED
        preview.enrichment_source = source
        db.commit()
        db.refresh(preview)
        
        return {
            "preview_id": preview.preview_id,
            "state": preview.state.value,
            "enrichment_source": source,
            "metadata": self._extract_metadata(preview)
        }
    
    def _extract_metadata(self, preview: PreviewRecordDB) -> Dict[str, Any]:
        """Extract metadata dict from preview record."""
        return {
            "artist": preview.artist,
            "album": preview.album,
            "title": preview.title,
            "label": preview.label,
            "year": preview.year,
            "catalog_number": preview.catalog_number,
            "format": preview.format,
            "country": preview.country
        }


# Singleton
enrichment_service = EnrichmentService()
