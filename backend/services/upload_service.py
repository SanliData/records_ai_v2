# File: backend/services/upload_service.py
# -*- coding: utf-8 -*-
"""
UploadService
Unified upload handler used by UPAP UploadStage.

Role-3 design:
- Provides a single stable method: save_file()
- Stores uploaded files under /storage/uploads/<user_id>/
- Returns absolute file path for pipeline use
"""

import os
from fastapi import UploadFile


class UploadService:
    BASE_DIR = "storage/uploads"

    def save_file(self, file: UploadFile, user_id: int) -> str:
        """
        Saves uploaded file to user-specific directory.

        :param file: FastAPI UploadFile object
        :param user_id: integer user id
        :return: absolute file path
        """

        if not file:
            raise ValueError("UploadService.save_file: file is missing")

        if user_id is None:
            raise ValueError("UploadService.save_file: user_id is missing")

        # Ensure user directory exists
        user_dir = os.path.join(self.BASE_DIR, str(user_id))
        os.makedirs(user_dir, exist_ok=True)

        # Build file path
        filename = file.filename or "uploaded_file"
        file_path = os.path.join(user_dir, filename)

        # Save file contents
        with open(file_path, "wb") as f:
            content = file.file.read()
            f.write(content)

        return file_path


# GLOBAL INSTANCE
upload_service = UploadService()
