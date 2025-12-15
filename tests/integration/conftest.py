# tests/integration/conftest.py
# UTF-8, English only

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Import the live app
from backend.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """
    Shared FastAPI TestClient for integration tests.

    Uses the real application object, including real routing and DB wiring.
    """
    return TestClient(app)


@pytest.fixture(scope="session")
def data_dir() -> Path:
    """
    Base directory for test media files.
    Adjust if you prefer a different layout.
    """
    return Path(__file__).parent.parent / "data"


def require_file(path: Path) -> None:
    """
    Helper that fails with a clear message if the required test file is missing.
    """
    if not path.exists():
        pytest.skip(f"Test media file missing: {path}")
