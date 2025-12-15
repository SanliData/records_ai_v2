# -*- coding: utf-8 -*-
# ======================================================
# DEPRECATED – Replaced by the UPAP pipeline
# Do NOT use. Scheduled for removal in V2 cleanup.
# ======================================================
import base64
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VISION_EXTRACTION_PROMPT = """
Extract vinyl record metadata from the image and return ONLY JSON.

REQUIRED JSON FIELDS:
{
  "title": string or null,
  "artist": string or null,
  "label": string or null,
  "catalog_number": string or null,
  "year": integer or null,
  "country": string or null,
  "format": "LP" | "EP" | "12-inch" | null,
  "matrix_info": string or null,
  "confidence": float (0.0Ã¢â‚¬â€œ1.0)
}

Rules:
- If unsure, return null.
- Do not hallucinate.
- Use visible text + visual cues.
- Detect runout codes if visible.
- Detect label name even if partially visible.
- confidence = model certainty (float).
"""

async def analyze_image_json(image_path):
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    b64 = base64.b64encode(img_bytes).decode()

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a vinyl metadata extraction engine."},
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": VISION_EXTRACTION_PROMPT},
                    {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64}"}
                ]
            }
        ],
        response_format={"type": "json_object"},
        max_tokens=500
    )

    return response.choices[0].message.parsed

