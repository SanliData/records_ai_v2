# backend/core/service_bus.py
# UTF-8, English only

from backend.services.upload_service import upload_service
from backend.services.analysis_service import analysis_service
from backend.services.archive_service import archive_service
from backend.services.records_service import records_service
from backend.services.user_service import user_service
from backend.services.thumbnail_service import thumbnail_service


class ServiceBus:
    """
    Central hub that exposes all shared backend services.
    UPAP Engine and Routers use this bus instead of importing services directly.
    """

    def __init__(self):
        self.upload_service = upload_service
        self.analysis_service = analysis_service
        self.archive_service = archive_service
        self.records_service = records_service
        self.user_service = user_service
        self.thumbnail_service = thumbnail_service


# global instance
service_bus = ServiceBus()
