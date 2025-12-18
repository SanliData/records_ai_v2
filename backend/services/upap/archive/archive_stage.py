# -*- coding: utf-8 -*-
"""
ArchiveStage
------------
Creates a durable archive record from a processed record_id.
"""

from typing import Dict, Any

from backend.services.upap.engine.stage_interface import StageInterface
from backend.services.upap.archive.archive_store import ArchiveStore


class ArchiveStage(StageInterface):
    name = "archive"

    def __init__(self) -> None:
        self.store = ArchiveStore()

    def validate_input(self, payload: Dict[str, Any]) -> None:
        if "record_id" not in payload:
            raise ValueError("ArchiveStage requires 'record_id'")
        if "process_result" not in payload:
            raise ValueError("ArchiveStage requires 'process_result'")

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        record_id: str = context["record_id"]
        process_result: Dict[str, Any] = context["process_result"]

        archive_record = self.store.create_archive(
            record_id=record_id,
            process_result=process_result,
        )

        return {
            "stage": "archive",
            "status": "ok",
            "record_id": record_id,
            "archive_record": archive_record,
        }
