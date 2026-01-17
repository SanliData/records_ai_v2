"""
Simple CLI client for the live UPAP v2 API running at api.zyagrolia.com.

Usage (from repo root, in venv):

  python -m scripts.upap_cli path/to/image.jpg --email you@example.com

This will:
  1) Upload the image
  2) Run process
  3) Archive
  4) Publish
and print the final JSON responses.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import requests


BASE_URL = "https://api.zyagrolia.com"


def _print_step(title: str) -> None:
    print(f"\n=== {title} ===")


def upload(path: Path, email: str) -> dict:
    _print_step("UPLOAD")
    url = f"{BASE_URL}/upload"
    with path.open("rb") as f:
        files = {"file": (path.name, f, "image/jpeg")}
        data = {"email": email}
        resp = requests.post(url, files=files, data=data, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    print(data)
    return data


def process(record_id: str) -> dict:
    _print_step("PROCESS")
    url = f"{BASE_URL}/process"
    payload = {"record_id": record_id}
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    print(data)
    return data


def archive(record_id: str) -> dict:
    _print_step("ARCHIVE")
    url = f"{BASE_URL}/archive"
    # FastAPI form field
    resp = requests.post(url, data={"record_id": record_id}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    print(data)
    return data


def publish(record_id: str) -> dict:
    _print_step("PUBLISH")
    url = f"{BASE_URL}/upap/publish"
    resp = requests.post(url, params={"record_id": record_id}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    print(data)
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="UPAP v2 one-shot upload → publish CLI")
    parser.add_argument("image", type=str, help="Path to image file (jpg/png)")
    parser.add_argument("--email", required=True, help="Email to attach to upload")

    args = parser.parse_args(argv)
    img_path = Path(args.image)
    if not img_path.is_file():
        print(f"File not found: {img_path}", file=sys.stderr)
        return 1

    upload_data = upload(img_path, args.email)
    record_id = upload_data.get("record_id")
    if not record_id:
        print("No record_id in upload response", file=sys.stderr)
        return 1

    process(record_id)
    archive(record_id)
    publish(record_id)

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())







