# UTF-8, English only

from typing import Dict, Any


_PREVIEW_STORE: Dict[str, Any] = {}


def save_preview(preview: Any) -> None:
    """
    Persist preview objects using preview_id as the canonical key.
    """
    if isinstance(preview, dict):
        preview_id = preview.get("preview_id")
    else:
        preview_id = getattr(preview, "preview_id", None)

    if not preview_id:
        raise AttributeError("Preview object missing preview_id")

    _PREVIEW_STORE[str(preview_id)] = preview


def get_preview(preview_id: str):
    return _PREVIEW_STORE.get(str(preview_id))
