# backend/services/thumbnail_service.py
# UTF-8, English only

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from PIL import Image


class ThumbnailService:
    """
    ThumbnailService

    Creates small preview images (thumbnails) for uploaded files.
    Thumbnails are stored under:

        storage/thumbnails/{user_id}/{stem}_thumb.jpg
    """

    def __init__(self, base_dir: str = "storage/thumbnails", size: int = 128) -> None:
        self.base_dir = base_dir
        self.size = size

    def create_thumbnail(self, file_path: str, user_id: int) -> Optional[str]:
        """
        Create a thumbnail for the given image file.

        :param file_path: Original file path saved by upload_service.
        :param user_id: Numeric user id used to partition storage.
        :return: Relative thumbnail path (string) or None if failed.
        """

        original = Path(file_path)
        if not original.is_file():
            return None

        user_dir = Path(self.base_dir) / str(user_id)
        os.makedirs(user_dir, exist_ok=True)

        thumb_name = f"{original.stem}_thumb.jpg"
        thumb_path = user_dir / thumb_name

        try:
            with Image.open(original) as img:
                img = img.convert("RGB")
                img.thumbnail((self.size, self.size))
                img.save(thumb_path, format="JPEG", quality=85)
        except Exception:
            return None

        return str(thumb_path).replace("\\", "/")


# MUST EXIST — Global instance
thumbnail_service = ThumbnailService(size=128)
