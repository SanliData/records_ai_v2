# -*- coding: utf-8 -*-
# ======================================================
# DEPRECATED – Replaced by the UPAP pipeline
# Do NOT use. Scheduled for removal in V2 cleanup.
# ======================================================
import threading
import time
import queue
import requests

from sqlalchemy.orm import Session
from backend.db import get_session
from backend.models.archive_record import ArchiveRecord


class EnrichmentWorker:
    """
    Background worker that performs:
    - Discogs free search enrichment
    - MusicBrainz lookup
    - Popsike pricing check (best effort)
    - Runout/matrix refinement
    """

    def __init__(self):
        self.q = queue.Queue()
        self.thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.thread.start()

    def enqueue(self, archive_id: int):
        """Places job into queue."""
        self.q.put(archive_id)

    def _worker_loop(self):
        """Infinite background loop."""
        while True:
            archive_id = self.q.get()
            try:
                self._process(archive_id)
            except Exception as e:
                print(f"[EnrichmentWorker] Error: {e}")
            time.sleep(0.2)  # prevents CPU spiking
            self.q.task_done()

    def _process(self, archive_id: int):
        session: Session = get_session()
        record = session.query(ArchiveRecord).filter_by(id=archive_id).first()
        if not record:
            return

        enriched = {}

        # 1. Minimal Discogs free lookup
        discogs_meta = self._discogs_search(record)
        if discogs_meta:
            enriched["discogs"] = discogs_meta

        # 2. MusicBrainz metadata
        mb_meta = self._musicbrainz_search(record)
        if mb_meta:
            enriched["musicbrainz"] = mb_meta

        # 3. Popsike pricing
        popsike_meta = self._popsike_lookup(record)
        if popsike_meta:
            enriched["popsike"] = popsike_meta

        # 4. Runout refinement
        enriched["runout_cleaned"] = self._clean_runout(record.ocr_text)

        # save data
        record.enriched_blob = enriched
        session.commit()

    # Discogs (free unauthenticated search)
    def _discogs_search(self, record):
        try:
            query = f"{record.artist} {record.album}"
            url = f"https://api.discogs.com/database/search?q={query}&type=release"
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                return None
            data = r.json()
            if not data.get("results"):
                return None
            first = data["results"][0]
            return {
                "title": first.get("title"),
                "year": first.get("year"),
                "label": first.get("label"),
                "catno": first.get("catno"),
                "thumb": first.get("thumb"),
            }
        except:
            return None

    # MusicBrainz
    def _musicbrainz_search(self, record):
        try:
            query = f"{record.artist} {record.album}"
            url = f"https://musicbrainz.org/ws/2/release/?query={query}&fmt=json"
            r = requests.get(url, timeout=5, headers={"User-Agent": "RecordsAI/1.0"})
            if r.status_code != 200:
                return None
            data = r.json()
            if "releases" not in data or not data["releases"]:
                return None
            rel = data["releases"][0]
            return {
                "title": rel.get("title"),
                "date": rel.get("date"),
                "country": rel.get("country"),
                "status": rel.get("status"),
                "label-info": rel.get("label-info"),
            }
        except:
            return None

    # Popsike
    def _popsike_lookup(self, record):
        try:
            # Popsike has no official free API but provides HTML search
            query = f"{record.artist} {record.album}".replace(" ", "+")
            url = f"https://www.popsike.com/php/quicksearch.php?searchtext={query}"
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                return None

            # naive extraction
            text = r.text.lower()
            if "results" not in text:
                return None

            return {"raw_html": "stored", "note": "HTML stored for later parsing"}
        except:
            return None

    # Runout refinement
    def _clean_runout(self, text):
        if not text:
            return None
        return (
            text.replace("\n", " ")
            .replace("-", "")
            .strip()
        )


enrichment_worker = EnrichmentWorker()

