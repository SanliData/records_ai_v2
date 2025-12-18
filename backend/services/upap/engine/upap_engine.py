# -*- coding: utf-8 -*-

from typing import Dict
from uuid import uuid4

from backend.services.upap.engine.stage_interface import StageInterface
from backend.services.upap.upload.upload_stage import UploadStage
from backend.services.upap.process.process_stage import ProcessStage
from backend.services.upap.archive.archive_stage import ArchiveStage


class UPAPEngine:
    """
    UPAP V2 – Minimal, stabil engine.
    - Stage registry korunur (future-proof)
    - Upload-only fast path açık
    """

    def __init__(self) -> None:
        self._stages: Dict[str, StageInterface] = {}
        self.register_stage(UploadStage())
        self.register_stage(ProcessStage())
        self.register_stage(ArchiveStage())

    def register_stage(self, stage: StageInterface) -> None:
        self._stages[stage.name] = stage

    def get_stage(self, name: str) -> StageInterface:
        if name not in self._stages:
            raise KeyError(f"Stage '{name}' not registered")
        return self._stages[name]

    def run_stage(self, name: str, context: dict) -> dict:
        stage = self.get_stage(name)
        stage.validate_input(context)
        return stage.run(context)

    # === UPAP-ONLY FAST PATH ===
    def run_upload_only(self, *, file, email: str) -> dict:
        """
        Router’dan direkt çağrılır.
        Engine içinde stage zinciri çalıştırmaz.
        """
        return {
            "stage": "upload",
            "status": "ok",
            "record_id": str(uuid4()),
            "filename": file.filename,
            "email": email,
            "size_bytes": file.size if hasattr(file, "size") else None,
        }


# Global singleton
upap_engine = UPAPEngine()
