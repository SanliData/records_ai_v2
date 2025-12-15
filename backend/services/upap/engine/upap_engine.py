# -*- coding: utf-8 -*-
# UPAPEngine – unified pipeline executor (auth → upload → process → archive → publish)

from typing import Any, Dict

from backend.services.upap.auth.auth_stage import AuthStage
from backend.services.upap.upload.upload_stage import UploadStage
from backend.services.upap.process.process_stage import ProcessStage
from backend.services.upap.archive.archive_stage import ArchiveStage
from backend.services.upap.publish.publish_stage import PublishStage
from backend.services.upap.engine.stage_interface import StageInterface


class UPAPEngine:
    """
    Orchestrates all UPAP stages.

    Each stage must implement:
        - validate_input(payload: dict) -> None
        - run(context: dict) -> dict

    Pipeline order:
        1. auth
        2. upload
        3. process
        4. archive
        5. publish
    """

    def __init__(self) -> None:
        self._stages: Dict[str, StageInterface] = {
            "auth": AuthStage(),
            "upload": UploadStage(),
            "process": ProcessStage(),
            "archive": ArchiveStage(),
            "publish": PublishStage(),
        }

    def get_stage(self, name: str) -> StageInterface:
        if name not in self._stages:
            raise ValueError(f"Unknown stage: {name}")
        return self._stages[name]

    def run_stage(self, name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single stage by name.

        1) Validate input (validate_input)
        2) Execute stage (run)
        3) Ensure dict output
        """
        stage = self.get_stage(name)

        # Contract-level validation
        stage.validate_input(payload)

        # Runtime execution
        result = stage.run(payload)

        if not isinstance(result, dict):
            raise TypeError(
                f"{stage.__class__.__name__}.run() must return dict, "
                f"got {type(result).__name__}"
            )

        return result

    def run_full_pipeline(
        self, email: str, file_bytes: bytes, filename: str
    ) -> Dict[str, Any]:
        """
        Convenience method to run the full UPAP pipeline
        from raw user input.

        Steps:
            - auth:    email -> user identity
            - upload:  file_bytes + filename + user_id -> stored file path
            - process: file_path -> processing result
            - archive: process_result -> archive record
            - publish: archive_record -> publish payload
        """

        # 1) auth
        auth = self.run_stage(
            "auth",
            {
                "email": email,
            },
        )

        # 2) upload
        upload = self.run_stage(
            "upload",
            {
                "email": email,
                "user_id": auth["user_id"],
                "file_bytes": file_bytes,
                "filename": filename,
            },
        )

        # 3) process
        process = self.run_stage(
            "process",
            {
                "file_path": upload["saved_to"],
            },
        )

        # 4) archive
        archive = self.run_stage(
            "archive",
            {
                "process_result": process,
            },
        )

        # 5) publish
        publish = self.run_stage(
            "publish",
            {
                "archive_record": archive,
            },
        )

        return {
            "auth": auth,
            "upload": upload,
            "process": process,
            "archive": archive,
            "publish": publish,
        }


# Export global singleton (UPAP is always single-engine)
upap_engine = UPAPEngine()
