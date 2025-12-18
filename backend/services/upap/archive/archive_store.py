# -*- coding: utf-8 -*-
"""
ArchiveStore
------------
File-based, idempotent archive storage.

Layout:
- storage/state/{record_id}.json
- storage/archive/{archive_id}.json
"""

from pathlib import Path
from typing import Dict, Any
import json
import uuid
import time


class ArchiveStore:
    def __init__(self) -> None:
        self.state_dir = Path("storage") / "state"
        self.archive_dir = Path("storage") / "archive"

        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------
    # State helpers
    # -------------------------------------------------

    def _state_path(self, record_id: str) -> Path:
        return self.state_dir / f"{record_id}.json"

    def load_state(self, record_id: str) -> Dict[str, Any] | None:
        path = self._state_path(record_id)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def save_state(self, record_id: str, data: Dict[str, Any]) -> None:
        path = self._state_path(record_id)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # -------------------------------------------------
    # Archive helpers
    # -------------------------------------------------

    def create_archive(
        self,
        record_id: str,
        process_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Idempotent archive creation.
        """
        # 1) Check existing state
        state = self.load_state(record_id)
        if state and state.get("status") == "archived":
            return state["archive_record"]

        # 2) Create new archive
        archive_id = str(uuid.uuid4())
        archive_record = {
            "archive_id": archive_id,
            "record_id": record_id,
            "status": "archived",
            "source": process_result.get("file_path"),
            "features": process_result.get("features", {}),
            "created_at": int(time.time()),
        }

        # 3) Persist archive
        archive_path = self.archive_dir / f"{archive_id}.json"
        archive_path.write_text(
            json.dumps(archive_record, indent=2),
            encoding="utf-8",
        )

        # 4) Update state
        self.save_state(
            record_id,
            {
                "record_id": record_id,
                "status": "archived",
                "archive_record": archive_record,
            },
        )

        return archive_record
