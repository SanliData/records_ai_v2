# -*- coding: utf-8 -*-
"""
PublishStage – finalizes the pipeline output for external consumers.

For now this creates a simple publish payload; later this can:
- push to a message bus
- notify another service
- generate a public URL
"""

from typing import Any, Dict

from backend.services.upap.engine.stage_interface import StageInterface


class PublishStage(StageInterface):
    name = "publish"

    def validate_input(self, payload: Dict[str, Any]) -> None:
        if "archive_record" not in payload:
            raise ValueError("PublishStage: 'archive_record' missing in context")

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        archive_record: Dict[str, Any] = context["archive_record"]

        publish_payload = {
            "published": True,
            "archive_id": archive_record.get("archive_id"),
            "status": archive_record.get("status"),
            "source": archive_record.get("source"),
        }

        return publish_payload
