#backend/db.py
# UTF-8
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# DATABASE_URL is REQUIRED - no SQLite fallback
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is required. "
        "Set Cloud SQL connection string in Cloud Run environment variables. "
        "Example: postgresql://user:pass@host/dbname"
    )

# Connection args based on database type
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency to get a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Import models and create tables.
    Called once at app startup.
    """
    from backend import models  # noqa: F401  (ensures models are imported)
    Base.metadata.create_all(bind=engine)


# TinyDB instance for legacy services
# Used by auth_service, dashboard_service, admin_stats_router
from tinydb import TinyDB

# Ensure storage directory exists
REPO_ROOT = Path(__file__).resolve().parent.parent
STORAGE_DIR = REPO_ROOT / "backend" / "storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# TinyDB JSON file path
TINYDB_PATH = STORAGE_DIR / "records.json"

# Global TinyDB instance
db = TinyDB(str(TINYDB_PATH))
