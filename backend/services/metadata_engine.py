# -*- coding: utf-8 -*-
# ======================================================
# DEPRECATED – Replaced by the UPAP pipeline
# Do NOT use. Scheduled for removal in V2 cleanup.
# ======================================================
#-*- coding: utf-8 -*-
"""
Metadata Engine (Final Version)
ROL-2/ROL-3 compliant
UTF-8 / English only
"""

import os
import uuid
from pathlib import Path
from typing import Optional, Dict

import cv2
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener
register_heif_opener()


class MetadataEngine:
    VALID_EXTENSIONS = [
        ".jpg", ".jpeg", ".png", ".heic", ".heif",
        ".webp", ".tiff", ".bmp", ".gif"
    ]

    def __init__(self):
        self.base_uploads = Path("data/uploads")
        self.base_normalized = Path("data/normalized")
        self.base_normalized.mkdir(parents=True, exist_ok=True)

    def _search_file(self, filename: str) -> Optional[Path]:
        filename_lower = filename.lower()
        root = Path(".")
        for path in root.rglob("*"):
            if path.is_file() and path.name.lower() == filename_lower:
                return path.resolve()
        return None

    def _load_image(self, input_path: str) -> Image.Image:
        input_path = Path(input_path)
        if not input_path.exists():
            found = self._search_file(input_path.name)
            if not found:
                raise RuntimeError(f"Cannot locate image anywhere: {input_path}")
            input_path = found

        try:
            pil_img = Image.open(str(input_path)).convert("RGB")
            return pil_img
        except UnidentifiedImageError:
            pass
        except Exception as e:
            raise RuntimeError(f"Cannot load image with Pillow: {e}")

        cv_img = cv2.imread(str(input_path))
        if cv_img is None:
            raise RuntimeError(f"Cannot load image: {input_path}")

        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(cv_img)

    def normalize_image(self, input_path: str, source: str = "unknown") -> Dict:
        img = self._load_image(input_path)

        out_name = f"{uuid.uuid4().hex}.jpg"
        out_path = self.base_normalized / out_name

        img.save(str(out_path), "JPEG", quality=90)

        width, height = img.size

        return {
            "normalized_path": str(out_path),
            "width": width,
            "height": height,
            "source": source
        }

    # -------------------------------------------------------
    # Existing function
    # -------------------------------------------------------
    def generate_metadata_guess(self, info: Dict) -> Dict:
        result = {}
        text = (info.get("text") or "").lower()

        if "vin" in text or "vehicle" in text:
            result["record_type"] = "automotive"
        elif "invoice" in text or "total" in text:
            result["record_type"] = "invoice"
        elif "serial" in text or "model" in text:
            result["record_type"] = "device"
        else:
            result["record_type"] = "unknown"

        result["contains_date"] = ("date" in text)

        return result

    # -------------------------------------------------------
    # MISSING FUNCTION Ã¢â€ â€™ NOW IMPLEMENTED
    # -------------------------------------------------------
    def metadata_guess_from_text(self, text: str) -> Dict:
        """
        Same heuristic as generate_metadata_guess(), but takes plain text.
        Used by analysis_service.
        """
        text_low = (text or "").lower()
        info = {"text": text_low}
        return self.generate_metadata_guess(info)


metadata_engine = MetadataEngine()

