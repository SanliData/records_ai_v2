# -*- coding: utf-8 -*-
# ======================================================
# DEPRECATED – Replaced by the UPAP pipeline
# Do NOT use. Scheduled for removal in V2 cleanup.
# ======================================================
#backend/services/vision_engine.py
# UTF-8, English only

from __future__ import annotations

import hashlib
from io import BytesIO
from pathlib import Path
from typing import Dict, Any

from PIL import Image

try:
    # Allow HEIC/HEIF support if pillow-heif is installed
    from pillow_heif import register_heif_opener

    register_heif_opener()
except Exception:
    # If pillow-heif is not available, HEIC files will fail at open()
    pass


class VisionEngine:
    """
    VisionEngine provides:
    - Robust image loading (JPEG/PNG/HEIC where supported)
    - Normalization helper (save to JPEG)
    - Deterministic image fingerprinting (SHA256)
    - Lightweight structural analysis (width/height)
    """

    def load_image(self, file_path: str | Path) -> Image.Image:
        """
        Load an image from disk and convert to RGB.
        Raises a clear RuntimeError if anything fails.
        """
        path = Path(file_path)
        if not path.exists():
            raise RuntimeError(f"VisionEngine.load_image: file not found: {path}")

        try:
            img = Image.open(path)
            # Force materialization and convert to RGB to normalize mode
            img.load()
            return img.convert("RGB")
        except Exception as exc:
            raise RuntimeError(f"VisionEngine.load_image: failed to open image: {exc}") from exc

    def save_as_jpeg(self, file_path: str | Path, target_dir: str | Path | None = None) -> str:
        """
        Normalize any supported input (HEIC, PNG, JPEG) to a JPEG file on disk.
        Returns the path to the JPEG file as a string.

        If target_dir is None, the JPEG is written next to the original image.
        """
        src_path = Path(file_path)
        img = self.load_image(src_path)

        if target_dir is None:
            target_dir = src_path.parent

        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        jpeg_name = src_path.stem + ".normalized.jpg"
        jpeg_path = target_dir / jpeg_name

        try:
            img.save(jpeg_path, format="JPEG", quality=95)
        except Exception as exc:
            raise RuntimeError(f"VisionEngine.save_as_jpeg: failed to save JPEG: {exc}") from exc

        return str(jpeg_path)

    def get_fingerprint(self, file_path: str | Path) -> str:
        """
        Compute a deterministic SHA256 fingerprint for the visual content.

        Implementation:
        - Load image
        - Encode to JPEG in memory with fixed parameters
        - Hash the resulting bytes
        """
        img = self.load_image(file_path)

        buf = BytesIO()
        try:
            img.save(buf, format="JPEG", quality=90)
        except Exception as exc:
            raise RuntimeError(f"VisionEngine.get_fingerprint: failed to encode JPEG: {exc}") from exc

        digest = hashlib.sha256(buf.getvalue()).hexdigest()
        return digest

    def analyze_image(self, file_path: str | Path) -> Dict[str, Any]:
        """
        Lightweight structural analysis.

        Returns a dict with:
        - status: "ok" | "error"
        - width, height
        - message
        """
        img = self.load_image(file_path)
        width, height = img.size

        return {
            "status": "ok",
            "width": width,
            "height": height,
            "message": "VisionEngine.analyze_image executed.",
        }


# Singleton instance used by the rest of the backend
vision_engine = VisionEngine()

