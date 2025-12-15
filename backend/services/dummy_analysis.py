# -*- coding: utf-8 -*-
# ======================================================
# DEPRECATED – Replaced by the UPAP pipeline
# Do NOT use. Scheduled for removal in V2 cleanup.
# ======================================================
def dummy_external_lookup(text: str) -> dict:
    return {
        "source": "dummy_lookup",
        "artist": "Unknown Artist",
        "album": "Unknown Album",
        "confidence": 0.0,
        "query": text
    }

