# UTF-8 — English only

import uuid
import threading

class UserLibraryService:

    def __init__(self):
        self._records = {}  # archive_id => record
        self._lock = threading.Lock()  # Thread safety for concurrent access

    def add_record(self, record: dict):
        # P0-3: Idempotency - Check if record already exists (thread-safe)
        with self._lock:
            archive_id = record.get("archive_id") or record.get("record_id")
            record_id = record.get("record_id") or archive_id
            user_id = record.get("user_id") or record.get("user_id_str")
            user_email = record.get("user_email")
            
            # Check by archive_id first
            if archive_id and archive_id in self._records:
                existing = self._records[archive_id]
                # Verify it belongs to same user
                if (str(existing.get("user_id")) == str(user_id) or 
                    existing.get("user_id_str") == str(user_id) or
                    existing.get("user_email") == user_email):
                    # Record already exists - return existing (idempotent)
                    existing["idempotent"] = True
                    existing["exists_since"] = existing.get("added_at")
                    return existing
            
            # Check by record_id + user_id (for concurrent requests with same record_id)
            if record_id:
                for existing_id, existing_record in self._records.items():
                    if (existing_record.get("record_id") == record_id and
                        (str(existing_record.get("user_id")) == str(user_id) or
                         existing_record.get("user_id_str") == str(user_id) or
                         existing_record.get("user_email") == user_email)):
                        # Record with same record_id + user exists - return existing (idempotent)
                        existing_record["idempotent"] = True
                        existing_record["exists_since"] = existing_record.get("added_at")
                        return existing_record
            
            # New record - assign archive_id if not set
            if not archive_id:
                archive_id = str(uuid.uuid4())
                record["archive_id"] = archive_id
            
            # Store new record
            self._records[archive_id] = record
            return record

    def list_user_records(self, user_id: int):
        return [
            v for v in self._records.values()
            if v.get("user_id") == user_id
        ]

    def get_record(self, archive_id: str):
        with self._lock:
            return self._records.get(archive_id)

    def delete_record(self, archive_id: str):
        return self._records.pop(archive_id, None) is not None

    def update_record(self, archive_id: str, payload: dict):
        if archive_id not in self._records:
            return None
        self._records[archive_id].update(payload)
        return self._records[archive_id]


user_library_service = UserLibraryService()
