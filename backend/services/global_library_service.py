# -*- coding: utf-8 -*-
"""
Global Library Service
Central archive for all vinyl records. Every record is first added here,
then referenced by user libraries. Records persist in global archive even
if users delete them from their personal collections.
"""
import hashlib
import json
import time
from typing import Any, Dict, List, Optional


class GlobalLibraryService:
    """
    In-memory global vinyl record library.

    Goals:
    - One canonical entry per unique record (deduplicated).
    - All lookups are done here first before any external / AI calls.
    - User library entries can be linked to global entries but are not required
      for this service to function.
    """

    def __init__(self) -> None:
        # Internal storage: list of dict records
        # Each record:
        # {
        #   "id": int,
        #   "fingerprint": str,
        #   "metadata": dict,
        #   "source": str,
        #   "created_at": float
        # }
        self._records: List[Dict[str, Any]] = []
        self._next_id: int = 1

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _normalize_value(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, (int, float)):
            return str(value)
        return str(value).strip().lower()

    def _build_fingerprint(self, metadata: Dict[str, Any]) -> str:
        """
        Build a deterministic fingerprint from core vinyl fields.
        
        UNIQUENESS RULES:
        - Same artist + album + label + year + catalog_number + country + format + barcode = SAME PLAK (same fingerprint)
        - Different label, year, catalog_number, country, format, or barcode = DIFFERENT SURUM/BASKI = DIFFERENT PLAK (different fingerprint)
        
        This ensures:
        - One unique record per vinyl release in global archive (deduplication)
        - Different pressings/versions are treated as separate records
        - Same record uploaded by different users maps to the same global entry
        
        Fingerprint includes (in order):
        1. artist - Artist name
        2. album - Album/title name
        3. title - Alternative title field (fallback for album)
        4. label - Record label (different label = different pressing)
        5. year - Release year (different year = different pressing)
        6. catalog_number - Catalog number (different cat# = different pressing)
        7. catalog - Alternative catalog field
        8. barcode - Barcode (different barcode = different pressing)
        9. country - Release country (different country = different pressing)
        10. format - Record format (LP, CD, etc.) (different format = different release)
        """
        # Core fields that define uniqueness
        # Order matters: fields are processed in sequence for consistent hashing
        core_keys = [
            "artist",          # Primary identifier
            "album",           # Primary identifier
            "title",           # Fallback/alternative for album
            "label",           # Pressing identifier (different label = different pressing)
            "year",            # Pressing identifier (different year = different pressing)
            "catalog_number",  # Pressing identifier (different cat# = different pressing)
            "catalog",         # Alternative catalog field
            "barcode",         # Pressing identifier (different barcode = different pressing)
            "country",         # Pressing identifier (different country = different pressing)
            "format",          # Release identifier (different format = different release)
        ]

        pieces = []
        for key in core_keys:
            pieces.append(self._normalize_value(metadata.get(key)))

        raw = "|".join(pieces)
        # Stable SHA-256 hash for deterministic fingerprint
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _find_by_fingerprint(self, fingerprint: str) -> Optional[Dict[str, Any]]:
        for rec in self._records:
            if rec["fingerprint"] == fingerprint:
                return rec
        return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def add_or_get(
        self,
        metadata: Dict[str, Any],
        source: str = "user_upload",
        additional_fields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Insert a record into the global library if it does not exist yet.
        If an equivalent record already exists (same fingerprint), return the existing record.
        
        UNIQUENESS GUARANTEE:
        - Each unique combination of artist, album, label, year, catalog_number, 
          country, format, and barcode creates ONE global record
        - Different pressings/versions (different label, year, cat#, etc.) 
          create SEPARATE global records
        - Same pressing uploaded by different users maps to the SAME global record
        
        This function is idempotent: same metadata = same fingerprint = same global record.
        Additional fields (pricing_data, file_path, etc.) are merged into the record.
        """
        fingerprint = self._build_fingerprint(metadata)
        existing = self._find_by_fingerprint(fingerprint)

        if existing is not None:
            # Merge additional fields if provided (e.g., pricing_data, file_path)
            if additional_fields:
                existing.update(additional_fields)
            return existing

        # Create new global record
        record = {
            "id": self._next_id,
            "fingerprint": fingerprint,
            "metadata": metadata,
            "source": source,
            "created_at": time.time(),
        }

        # Add additional fields if provided
        if additional_fields:
            record.update(additional_fields)

        self._records.append(record)
        self._next_id += 1
        return record
    
    def get_by_fingerprint(self, fingerprint: str) -> Optional[Dict[str, Any]]:
        """Get global record by fingerprint."""
        return self._find_by_fingerprint(fingerprint)
    
    def get_by_global_id(self, global_id: int) -> Optional[Dict[str, Any]]:
        """Get global record by global ID."""
        return self.get_by_id(global_id)

    def get_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        for rec in self._records:
            if rec["id"] == record_id:
                return rec
        return None

    def search_text(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Very simple text search over core metadata fields.

        This is intended as a lightweight first-step lookup before any
        external API or AI calls.
        """
        q = query.strip().lower()
        if not q:
            return []

        results: List[Dict[str, Any]] = []
        for rec in self._records:
            meta = rec.get("metadata", {})
            haystack_parts = [
                self._normalize_value(meta.get("artist")),
                self._normalize_value(meta.get("album")),
                self._normalize_value(meta.get("title")),
                self._normalize_value(meta.get("label")),
                self._normalize_value(meta.get("catalog_number")),
                self._normalize_value(meta.get("barcode")),
            ]
            haystack = " ".join(haystack_parts)
            if q in haystack:
                results.append(rec)
                if len(results) >= limit:
                    break

        return results

    def search_by_metadata(
        self,
        metadata: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Metadata-based lookup (same fingerprint logic as add_or_get).
        Returns existing global record or None.
        """
        fingerprint = self._build_fingerprint(metadata)
        return self._find_by_fingerprint(fingerprint)

    def list_all(self) -> List[Dict[str, Any]]:
        """
        Return all global records (for admin / debugging).
        """
        return list(self._records)


global_library_service = GlobalLibraryService()

