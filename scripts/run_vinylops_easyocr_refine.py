import os
import time
import json
import requests
import pandas as pd
from difflib import SequenceMatcher

# ====================================================
# VinylOps - EasyOCR Refinement with Discogs Matching
# ====================================================

# Discogs API Token (from environment - REQUIRED)
import os
DISCOGS_TOKEN = os.getenv("DISCOGS_TOKEN")
if not DISCOGS_TOKEN:
    raise RuntimeError(
        "DISCOGS_TOKEN environment variable is required. "
        "Set it with: export DISCOGS_TOKEN=your_token_here"
    )

BASE_URL = "https://api.discogs.com/database/search"
HEADERS = {
    "Authorization": f"Discogs token={DISCOGS_TOKEN}",
    "User-Agent": "VinylOps/1.0"
}

INPUT_FILE = "canonical/inventory_easyocr.parquet"
OUTPUT_FILE = "canonical/inventory_easyocr_refined.parquet"


def discogs_search(artist: str, title: str):
    """Try direct Discogs search first, then fuzzy fallback."""
    params = {"artist": artist, "release_title": title, "type": "release", "per_page": 5}
    r = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=25)
    data = r.json().get("results", [])

    if not data:
        # Fuzzy fallback
        query = f"{artist} {title}"
        params = {"q": query, "type": "release", "per_page": 5}
        time.sleep(1)
        r = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=25)
        data = r.json().get("results", [])
        print(f"[INFO] Fuzzy search fallback for: {query}")

    return data


def best_fuzzy_match(sig, data):
    """Find the best fuzzy match from Discogs results."""
    best_match = None
    best_score = 0.0

    for item in data:
        title_candidate = item.get("title", "")
        score = SequenceMatcher(
            None, sig.get("title", "").lower(), title_candidate.lower()
        ).ratio()
        if score > best_score:
            best_score = score
            best_match = item

    if best_match:
        print(f"[MATCH] Best fuzzy: {best_match.get('title','N/A')} (score={best_score:.2f})")
        return {
            "artist_refined": sig.get("artist", ""),
            "title_refined": best_match.get("title", ""),
            "match_confidence": round(best_score, 2)
        }

    print(f"[WARN] No match found for: {sig.get('artist','')} - {sig.get('title','')}")
    return {
        "artist_refined": sig.get("artist", ""),
        "title_refined": sig.get("title", ""),
        "match_confidence": 0.0
    }


def main():
    print("🔍 Refining OCR results with Discogs fuzzy matching...")

    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] Input file not found: {INPUT_FILE}")
        return

    df = pd.read_parquet(INPUT_FILE)
    print(f"🧠 Processing {len(df)} entries...")

    refined_rows = []
    for _, row in df.iterrows():
        artist = str(row.get("artist", "")).strip()
        title = str(row.get("title", "")).strip()
        data = discogs_search(artist, title)
        refined = best_fuzzy_match(row, data)
        row.update(refined)
        refined_rows.append(row)

        time.sleep(1.2)  # respect Discogs rate limits

    refined_df = pd.DataFrame(refined_rows)
    refined_df.to_parquet(OUTPUT_FILE, index=False)
    print(f"✅ Created: {OUTPUT_FILE} with {len(refined_df)} entries")


if __name__ == "__main__":
    main()
