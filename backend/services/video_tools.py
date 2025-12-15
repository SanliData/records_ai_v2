# -*- coding: utf-8 -*-
# ======================================================
# DEPRECATED – Replaced by the UPAP pipeline
# Do NOT use. Scheduled for removal in V2 cleanup.
# ======================================================
import os
import cv2
import tempfile
from uuid import uuid4
from fastapi import UploadFile

MEDIA_ROOT = "media/uploads/"


class VideoTools:
    def __init__(self):
        os.makedirs(MEDIA_ROOT, exist_ok=True)

    def extract_primary_frame(self, file: UploadFile) -> str:
        temp_name = f"{uuid4().hex}.mp4"
        temp_path = os.path.join(tempfile.gettempdir(), temp_name)

        with open(temp_path, "wb") as f:
            f.write(file.file.read())

        cap = cv2.VideoCapture(temp_path)
        ok, frame = cap.read()
        cap.release()

        if not ok:
            raise RuntimeError("Could not extract frame from video.")

        output_name = f"{uuid4().hex}_frame.jpg"
        output_path = os.path.join(MEDIA_ROOT, output_name)

        cv2.imwrite(output_path, frame)

        return output_path.replace("\\", "/")

video_tools = VideoTools()

