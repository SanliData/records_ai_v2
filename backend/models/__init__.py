#backend/models/__init__.py
# UTF-8, English only
# Final, law-compliant, book-compliant model export

from .archive_record import ArchiveRecord as ArchiveRecordPydantic
from .pending_record import PendingRecord as PendingRecordPydantic
from .archive_record_db import ArchiveRecord
from .pending_record_db import PendingRecord
from .user import User

__all__ = [
    "ArchiveRecordPydantic",
    "PendingRecordPydantic",
    "ArchiveRecord",
    "PendingRecord",
    "User",
]
