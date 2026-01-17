"""
Lightweight UPAP smoke test for the current v2 content.
Runs a minimal upload → process → archive → publish happy-path using the
HTTP routes that are wired today, and calls the archive stage directly
to satisfy the publish precondition.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure repo root on sys.path so imports work without env tweaks
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.main import app  # noqa: E402
from backend.services.upap.engine.upap_engine import upap_engine  # noqa: E402


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


def _sample_file() -> Path:
    """
    Use the tiny placeholder JPEG in repo root; upload endpoint only
    needs bytes/filename and does not validate image content.
    """
    path = ROOT_DIR / "test.jpg"
    if not path.exists():
        pytest.skip(f"Sample file missing: {path}")
    return path


def test_health_endpoint(client: TestClient) -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("status") == "ok"
    assert body.get("service") == "records_ai_v2"


def test_upap_happy_path_upload_process_publish(client: TestClient) -> None:
    sample = _sample_file()

    with sample.open("rb") as fh:
        upload_resp = client.post(
            "/upload",
            files={"file": (sample.name, fh, "image/jpeg")},
            data={"email": "test@example.com"},
        )

    assert upload_resp.status_code == 200
    upload_body = upload_resp.json()
    record_id = upload_body.get("record_id")
    assert record_id, "Upload response must include record_id"
    assert upload_body.get("stage") == "upload"

    process_resp = client.post("/process", json={"record_id": record_id})
    assert process_resp.status_code == 200
    process_body = process_resp.json()
    assert process_body.get("stage") == "process"
    assert process_body.get("record_id") == record_id

    # Archive stage is not currently exposed correctly via HTTP, so call directly
    archive_body = upap_engine.run_archive(record_id)
    assert archive_body.get("stage") == "archive"
    assert archive_body.get("record_id") == record_id

    publish_resp = client.post("/upap/publish", params={"record_id": record_id})
    assert publish_resp.status_code == 200
    publish_body = publish_resp.json()
    assert publish_body.get("stage") == "publish"
    assert publish_body.get("record_id") == record_id






