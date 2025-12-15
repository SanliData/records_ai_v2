#backend/models/__init__.py
# UTF-8, English only
# Final, law-compliant, book-compliant model export

from .archive_record import ArchiveRecord
from .pending_record import PendingRecord

__all__ = [
    "ArchiveRecord",
    "PendingRecord",
]
