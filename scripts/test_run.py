# -*- coding: utf-8 -*-
"""
Simple end-to-end test runner for the UPAP pipeline.

Run from project root:
    python -m scripts.test_run
"""

from pathlib import Path

from backend.services.upap.engine.upap_engine import upap_engine


def main() -> None:
    root_file = Path("test.jpg")
    if not root_file.exists():
        raise FileNotFoundError(
            f"'test.jpg' file not found in project root. Please add a sample file."
        )

    with root_file.open("rb") as f:
        file_bytes = f.read()

    email = "test@example.com"
    filename = root_file.name

    result = upap_engine.run_full_pipeline(
        email=email,
        file_bytes=file_bytes,
        filename=filename,
    )

    print("\n=== UPAP FULL PIPELINE RESULT ===")
    for name, data in result.items():
        print(f"\n[{name.upper()}]")
        print(data)


if __name__ == "__main__":
    main()
