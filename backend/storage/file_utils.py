# UTF-8, English only

import os
from pathlib import Path

def ensure_folder(path: str) -> str:
    """
    Ensures that a folder exists for storing uploaded files.
    Returns the normalized folder path.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return str(p)
