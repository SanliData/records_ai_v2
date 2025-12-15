# backend/core/db.py
# UTF-8, English only

import sqlite3
from pathlib import Path

DB_PATH = Path("storage/records.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Pending records (V1 active domain)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pending_records (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT,
            title_guess TEXT,
            artist_guess TEXT,
            label_guess TEXT,
            confidence REAL,
            ocr_text TEXT,
            vision_fingerprint TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # Archive records (final records)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS archive_records (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            title TEXT,
            artist TEXT,
            label TEXT,
            confidence REAL,
            ocr_text TEXT,
            vision_fingerprint TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
