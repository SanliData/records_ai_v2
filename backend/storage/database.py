import os
from tinydb import TinyDB, Query

# Ensure storage directory exists
STORAGE_DIR = "backend/storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

DB_PATH = os.path.join(STORAGE_DIR, "records.json")

# Main TinyDB instance
db = TinyDB(DB_PATH)

# Query helper
RecordQuery = Query()
