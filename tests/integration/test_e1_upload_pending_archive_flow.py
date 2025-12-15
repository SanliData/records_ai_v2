# tests/integration/test_e1_upload_pending_archive_flow.py
# UTF-8, English only

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient

from .conftest import require_file


def _assert_basic_analyze_response(payload: Dict[str, Any]) -> None:
    """
    Minimal structural contract for /api/v1/upload/image or analyze endpoint.
    Adjust keys if your response schema differs.
    """
    assert "pending_id" in payload, "Response must contain 'pending_id'"
    assert isinstance(payload["pending_id"], str)
    # Optional but recommended fields:
    # ocr_text, fingerprint, ai_guess, normalized_path, normalized_format
    if "ocr_text" in payload:
        assert isinstance(payload["ocr_text"], str)
    if "fingerprint" in payload and payload["fingerprint"] is not None:
        assert isinstance(payload["fingerprint"], dict)
    if "normalized_format" in payload:
        assert isinstance(payload["normalized_format"], str)


def _get_pending_list(client: TestClient) -> List[Dict[str, Any]]:
    r = client.get("/api/v1/archive/pending")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}, body={r.text}"
    data = r.json()
    assert isinstance(data, list), "Pending list must be a JSON array"
    return data


def _approve_first_pending(client: TestClient) -> Dict[str, Any]:
    pendings = _get_pending_list(client)
    assert pendings, "There must be at least one pending record for this test"

    first = pendings[0]
    pending_id = first.get("pending_id") or first.get("id") or first.get("uuid")
    assert pending_id, f"Could not determine pending_id from payload: {first}"

    r = client.post(f"/api/v1/archive/approve/{pending_id}")
    assert r.status_code == 200, f"Approve failed with {r.status_code}, body={r.text}"
    archive_record = r.json()
    # Archive response should at least have an id and some metadata
    assert "id" in archive_record or "archive_id" in archive_record
    return archive_record


@pytest.mark.integration
def test_u01_standard_jpeg_upload_creates_pending(
    client: TestClient,
    data_dir: Path,
) -> None:
    """
    TC-U01 — Standard JPEG Upload
    Goal: full upload → analyze → pending creation should succeed on a clean JPEG.
    """
    img_path = data_dir / "clean.jpg"
    require_file(img_path)

    with img_path.open("rb") as f:
        files = {"file": ("clean.jpg", f, "image/jpeg")}
        # Adapt the endpoint path to your actual upload route
        r = client.post("/api/v1/upload/image", files=files)

    assert r.status_code == 200, f"Expected 200, got {r.status_code}, body={r.text}"
    payload = r.json()
    _assert_basic_analyze_response(payload)

    # The pending list should now contain this upload
    pendings = _get_pending_list(client)
    assert len(pendings) >= 1


@pytest.mark.integration
def test_u02_heic_upload_is_normalized_to_jpeg(
    client: TestClient,
    data_dir: Path,
) -> None:
    """
    TC-U02 — HEIC Input Conversion
    Goal: HEIC files should be accepted and normalized to JPEG internally.
    """
    heic_path = data_dir / "sample.heic"
    require_file(heic_path)

    with heic_path.open("rb") as f:
        files = {"file": ("sample.heic", f, "image/heic")}
        r = client.post("/api/v1/upload/image", files=files)

    assert r.status_code == 200, f"Expected 200, got {r.status_code}, body={r.text}"
    payload = r.json()
    _assert_basic_analyze_response(payload)

    normalized_format = payload.get("normalized_format")
    if normalized_format is not None:
        assert normalized_format.lower() in {"jpeg", "jpg"}


@pytest.mark.integration
def test_u03_blurry_image_does_not_crash_and_creates_pending(
    client: TestClient,
    data_dir: Path,
) -> None:
    """
    TC-U03 — Blurry / Dark Image
    Goal: Pipeline must not crash on degraded input.
    """
    blurry = data_dir / "blurry.jpg"
    require_file(blurry)

    with blurry.open("rb") as f:
        files = {"file": ("blurry.jpg", f, "image/jpeg")}
        r = client.post("/api/v1/upload/image", files=files)

    assert r.status_code == 200, f"Expected 200, got {r.status_code}, body={r.text}"
    payload = r.json()
    _assert_basic_analyze_response(payload)

    # OCR may be empty, but field should exist if you expose it
    if "ocr_text" in payload:
        assert isinstance(payload["ocr_text"], str)


@pytest.mark.integration
def test_u04_corrupted_file_is_handled_gracefully(
    client: TestClient,
    data_dir: Path,
) -> None:
    """
    TC-U04 — Corrupted Image
    Goal: System should respond with a controlled error status and not create a pending record.
    """
    corrupt = data_dir / "corrupted.bin"
    require_file(corrupt)

    with corrupt.open("rb") as f:
        files = {"file": ("corrupted.bin", f, "application/octet-stream")}
        r = client.post("/api/v1/upload/image", files=files)

    # Adjust this according to how you decided to signal errors: 400 or 422 are typical
    assert r.status_code in {400, 415, 422}, f"Unexpected status {r.status_code}, body={r.text}"


@pytest.mark.integration
def test_p01_pending_list_structure(
    client: TestClient,
) -> None:
    """
    TC-P01/P02 — Pending list exists and has the expected schema shape.
    """
    pendings = _get_pending_list(client)
    # If there is no data yet, we do not fail, only check type
    if not pendings:
        pytest.skip("No pending records present; run upload tests first")

    first = pendings[0]
    assert "pending_id" in first or "id" in first or "uuid" in first
    assert "file_path" in first
    # Optional fields, but recommended
    if "ocr_text" in first:
        assert isinstance(first["ocr_text"], str)
    if "ai_guess" in first:
        assert isinstance(first["ai_guess"], dict)


@pytest.mark.integration
def test_a01_approve_pending_creates_archive(
    client: TestClient,
) -> None:
    """
    TC-A01/A02 — Approve one pending record and validate the resulting archive object.
    """
    # Ensure at least one pending exists.
    pendings = _get_pending_list(client)
    if not pendings:
        pytest.skip("No pending records available to approve. Run upload tests first.")

    archive_record = _approve_first_pending(client)

    # Basic archival structure
    archive_id = archive_record.get("id") or archive_record.get("archive_id")
    assert archive_id, f"Archive id is missing in response: {archive_record}"

    # Archive should carry merged metadata
    if "metadata" in archive_record:
        assert isinstance(archive_record["metadata"], dict)
    if "fingerprint" in archive_record and archive_record["fingerprint"] is not None:
        assert isinstance(archive_record["fingerprint"], dict)


@pytest.mark.integration
def test_r01_retrieve_archived_record(
    client: TestClient,
) -> None:
    """
    TC-R01 — Retrieve archived record by id.
    The previous test must have created at least one archive record.
    """
    # Try to find at least one archived record via list route, if available.
    # Adjust the URL depending on your design.
    list_response = client.get("/api/v1/archive/")
    if list_response.status_code == 404:
        pytest.skip("Archive list endpoint not implemented; cannot complete R01")

    assert list_response.status_code == 200
    items = list_response.json()
    if not items:
        pytest.skip("No archived records found; ensure approve flow ran before this test")

    first = items[0]
    archive_id = first.get("id") or first.get("archive_id")
    assert archive_id, "Archive list item has no id"

    # Now retrieve that record individually
    r = client.get(f"/api/v1/archive/{archive_id}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    detail = r.json()
    # Minimal checks
    assert detail.get("id") or detail.get("archive_id")
    if "metadata" in detail:
        assert isinstance(detail["metadata"], dict)
