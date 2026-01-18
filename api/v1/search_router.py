# File: backend/api/v1/search_router.py
# -*- coding: utf-8 -*-
"""
Search Router (Legacy Bridge)

Old behavior:
    /search → search vinyl metadata

UPAP Bridge behavior:
    - Searches across RECORD_LIBRARY (which holds archive records)
    - Keeps old API signature intact
"""

from fastapi import APIRouter, Form
from backend.api.v1.records_router import RECORD_LIBRARY

router = APIRouter(
    prefix="/search",
    tags=["Search (Legacy Bridge)"]
)


def safe_lower(x):
    """Utility for case-insensitive comparison."""
    return x.lower() if isinstance(x, str) else ""


@router.post("")
async def legacy_search(query: str = Form(...)):
    """
    Performs basic text search in archive metadata.

    Matches on:
        - title
        - artist
        - label
        - ocr_text (if exists)
    """

    q = safe_lower(query)

    results = []
    for record in RECORD_LIBRARY:
        title = safe_lower(record.get("title"))
        artist = safe_lower(record.get("artist"))
        label = safe_lower(record.get("label"))
        ocr = safe_lower(record.get("ocr_text"))

        if q in title or q in artist or q in label or q in ocr:
            results.append(record)

    return {
        "status": "ok",
        "query": query,
        "count": len(results),
        "results": results
    }
