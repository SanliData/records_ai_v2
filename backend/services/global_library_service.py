# -*- coding: utf-8 -*-
# ======================================================
# DEPRECATED – Replaced by the UPAP pipeline
# Do NOT use. Scheduled for removal in V2 cleanup.
# ======================================================
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

        This allows us to:
        - Detect duplicates
        - Return the same global record for the same vinyl, even if
          uploaded by different users.
        """
        core_keys = [
            "artist",
            "album",
            "title",           # some pipelines may use 'title' instead of 'album'
            "label",
            "year",
            "catalog_number",
            "catalog",
            "barcode",
            "country",
            "format",
        ]

        pieces = []
        for key in core_keys:
            pieces.append(self._normalize_value(metadata.get(key)))

        raw = "|".join(pieces)
        # Stable hash for fingerprint
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
    ) -> Dict[str, Any]:
        """
        Insert a record into the global library if it does not exist yet.
        If an equivalent record already exists (same fingerprint), return it.

        This function is idempotent for the same metadata.
        """
        fingerprint = self._build_fingerprint(metadata)
        existing = self._find_by_fingerprint(fingerprint)

        if existing is not None:
            return existing

        record = {
            "id": self._next_id,
            "fingerprint": fingerprint,
            "metadata": metadata,
            "source": source,
            "created_at": time.time(),
        }

        self._records.append(record)
        self._next_id += 1
        return record

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

