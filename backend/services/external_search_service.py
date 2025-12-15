# -*- coding: utf-8 -*-
# ======================================================
# DEPRECATED – Replaced by the UPAP pipeline
# Do NOT use. Scheduled for removal in V2 cleanup.
# ======================================================
#backend/services/external_search_service.py
# UTF-8, English only

from __future__ import annotations

from typing import Any, Dict, List


class ExternalSearchService:
    """
    Very small abstraction for external / AI marketplace search.

    Step 1 (now):
        Return a safe stub structure, so the rest of the system
        can be wired and tested without real API keys.

    Step 2 (later):
        Plug Discogs, MusicBrainz, Popsike, eBay, etc. into `search`.
    """

    def search(self, query: str) -> List[Dict[str, Any]]:
        # Placeholder implementation.
        # We intentionally *do not* call any external service here yet.
        # This way the endpoint stays deterministic and cheap while
        # architecture is being finalized.
        return [
            {
                "source": "external_stub",
                "note": "No global-library match found; external search is not configured yet.",
                "query": query,
            }
        ]


external_search_service = ExternalSearchService()

