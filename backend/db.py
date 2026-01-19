#backend/db.py
# UTF-8
import os
import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)

# DATABASE_URL configuration
# PROD: Must be set (Cloud Run env vars)
# LOCAL: Falls back to SQLite file if not set
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Local development fallback: use SQLite file
    REPO_ROOT = Path(__file__).resolve().parent.parent
    SQLITE_PATH = REPO_ROOT / "records_ai_v2.db"
    DATABASE_URL = f"sqlite:///{SQLITE_PATH}"
    logger.warning(
        f"DATABASE_URL not set. Using local SQLite fallback: {DATABASE_URL}. "
        "Set DATABASE_URL environment variable for production."
    )
else:
    logger.info("DATABASE_URL configured from environment")

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


