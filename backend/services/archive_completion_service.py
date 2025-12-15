# -*- coding: utf-8 -*-
# ======================================================
# DEPRECATED – Replaced by the UPAP pipeline
# Do NOT use. Scheduled for removal in V2 cleanup.
# ======================================================
import time
import random
from typing import Optional

from backend.db import db
from backend.models.archive_record import ArchiveRecord, ArchiveRecordSchema
from backend.models.pending_record import PendingRecordSchema


class ArchiveCompletionService:
    """
    Slow background metadata completion engine.
    Works after user approves a PendingRecord.
    Uses:
        - Free APIs (Discogs, MusicBrainz)
        - Smart fuzzy matching
        - AI fallback (optional, low-cost)
    """

    def __init__(self):
        pass

    # --------------------------------------------------------
    # SIMULATED EXTERNAL LOOKUPS (mock)
    # --------------------------------------------------------

    def discogs_lookup(self, title, artist):
        """
        Mock Discogs query: In production this calls real Discogs API.
        Returns enriched metadata.
        """
        if not title or not artist:
            return {}

        # mock realistic completion
        return {
            "year": 1979 if "wall" in title.lower() else None,
            "country": "UK",
            "label": "Harvest Records",
            "catalog_number": "SHDW 411",
            "format": "LP"
        }

    def musicbrainz_lookup(self, title, artist):
        """
        Mock MusicBrainz query:
        """
        if not title or not artist:
            return {}

        return {
            "mbid": "mock-musicbrainz-id",
            "extra_notes": "Matched via MusicBrainz fuzzy search"
        }

    # --------------------------------------------------------
    # MAIN COMPLETION PIPELINE
    # --------------------------------------------------------

    def complete_metadata(self, pending: PendingRecordSchema) -> ArchiveRecordSchema:
        """
        Combine:
            1. AI-Vision first pass
            2. Discogs metadata
            3. MusicBrainz metadata
            4. Merge & fix missing fields
        """

        ai = pending.raw_ai_data or {}
        discogs = self.discogs_lookup(pending.title, pending.artist)
        mb = self.musicbrainz_lookup(pending.title, pending.artist)

        # merge fields smartly
        def pick(*values):
            """First non-null wins."""
            for v in values:
                if v not in [None, "", "unknown"]:
                    return v
            return None

        archive = ArchiveRecord(
            title=pick(ai.get("title"), pending.title),
            artist=pick(ai.get("artist"), pending.artist),
            label=pick(ai.get("label"), discogs.get("label")),
            catalog_number=pick(ai.get("catalog_number"), discogs.get("catalog_number")),
            year=pick(ai.get("year"), discogs.get("year")),
            country=pick(ai.get("country"), discogs.get("country")),
            format=pick(ai.get("format"), discogs.get("format")),
            matrix_info=pick(pending.matrix_info),
            mbid=mb.get("mbid"),
            extra_notes=mb.get("extra_notes"),
        )

        db["archive"].append(archive.to_dict())

        # remove from pending queue
        db["pending_records"] = [
            p for p in db["pending_records"] 
            if p["id"] != pending.id
        ]

        return ArchiveRecordSchema(**archive.to_dict())

    # --------------------------------------------------------
    # ENTRYPOINT CALLED BY API
    # --------------------------------------------------------

    def approve_and_complete(self, pending_id: str) -> ArchiveRecordSchema:
        """
        Called when user approves a pending record.
        """
        record_data = next((r for r in db["pending_records"] if r["id"] == pending_id), None)
        if not record_data:
            raise ValueError("Pending record not found.")

        pending = PendingRecordSchema(**record_data)

        return self.complete_metadata(pending)


archive_completion_service = ArchiveCompletionService()

