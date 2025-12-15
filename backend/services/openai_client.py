# -*- coding: utf-8 -*-
# ======================================================
# DEPRECATED – Replaced by the UPAP pipeline
# Do NOT use. Scheduled for removal in V2 cleanup.
# ======================================================
#backend/services/openai_client.py
# UTF-8, English only

from __future__ import annotations
from typing import Any, Dict, Optional
from pathlib import Path
import base64
import os

from openai import OpenAI


class OpenAIVisionClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        self.client = OpenAI(api_key=api_key)

    def _encode_image(self, file_path: Path | str, raw_bytes: Optional[bytes]) -> str:
        if raw_bytes is not None:
            data = raw_bytes
        else:
            with open(file_path, "rb") as f:
                data = f.read()
        return base64.b64encode(data).decode("utf-8")

    def analyze_image(self, file_path: Path | str, raw_bytes: Optional[bytes] = None) -> Dict[str, Any]:
        """
        Calls OpenAI Vision + Text to get:
          - OCR-like label text
          - artist/album/label/year guess
          - fingerprint-ish features (matrix text, runout, etc.)
        """
        image_b64 = self._encode_image(file_path, raw_bytes)

        prompt = (
            "You are an expert in vinyl record identification.\n"
            "1) Read all visible text on the label (OCR).\n"
            "2) Extract structured metadata: artist, album, label, catalog_number, release_year if visible.\n"
            "3) Describe any runout matrix / etching text or distinctive markers useful as a fingerprint.\n"
            "4) Return a JSON object with keys: "
            "ocr_text, ai_guess, fingerprint, confidence (0-1).\n"
        )

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You respond ONLY with valid JSON and no extra text.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            },
                        },
                    ],
                },
            ],
            temperature=0.2,
        )

        raw = response.choices[0].message.content
        # We assume raw is JSON. In real code we wrap with try/except.
        import json

        data = json.loads(raw)

        return {
            "ocr_text": data.get("ocr_text", ""),
            "ai_guess": data.get("ai_guess", {}),
            "fingerprint": data.get("fingerprint", {}),
            "confidence": float(data.get("confidence", 0.0)),
        }

