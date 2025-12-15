# UTF-8 — English only

import uuid

class UserLibraryService:

    def __init__(self):
        self._records = {}  # archive_id => record

    def add_record(self, record: dict):
        archive_id = record.get("archive_id") or str(uuid.uuid4())
        record["archive_id"] = archive_id
        self._records[archive_id] = record
        return record

    def list_user_records(self, user_id: int):
        return [
            v for v in self._records.values()
            if v.get("user_id") == user_id
        ]

    def get_record(self, archive_id: str):
        return self._records.get(archive_id)

    def delete_record(self, archive_id: str):
        return self._records.pop(archive_id, None) is not None

    def update_record(self, archive_id: str, payload: dict):
        if archive_id not in self._records:
            return None
        self._records[archive_id].update(payload)
        return self._records[archive_id]


user_library_service = UserLibraryService()
