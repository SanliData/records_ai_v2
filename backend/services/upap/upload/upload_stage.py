# -*- coding: utf-8 -*-
"""
UploadStage – stores the uploaded file on disk under storage/uploads/{user_id}/
"""

from tester.hooks import after_validation
from typing import Any, Dict
from pathlib import Path

from backend.services.upap.engine.stage_interface import StageInterface


class UploadStage(StageInterface):
    name = "upload"

    def validate_input(self, payload: Dict[str, Any]) -> None:
        if "file_bytes" not in payload:
            raise ValueError("UploadStage.run() requires 'file_bytes'")
        if "filename" not in payload:
            raise ValueError("UploadStage.run() requires 'filename'")
        if "user_id" not in payload:
            raise ValueError("UploadStage.run() requires 'user_id'")

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        file_bytes: bytes = context["file_bytes"]
        filename: str = context["filename"]
        user_id: str = context["user_id"]

        base_dir = Path("storage") / "uploads" / user_id
        base_dir.mkdir(parents=True, exist_ok=True)

        target_path = base_dir / filename

        with target_path.open("wb") as f:
            f.write(file_bytes)


        after_validation({'pipeline': 'UPAP', 'stage': 'upload', 'schema': 'pending_record', 'status': 'PASS'})
        return {
            "saved_to": str(target_path),
            "size_bytes": len(file_bytes),
            "user_id": user_id,
            "filename": filename,
        }