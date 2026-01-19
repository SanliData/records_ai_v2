# backend/core/service_bus.py
# UTF-8, English only

from backend.services.upload_service import upload_service
from backend.services.analysis_service import analysis_service
from backend.services.records_service import records_service
from backend.services.thumbnail_service import thumbnail_service


class ServiceBus:
    """
    Central hub that exposes all shared backend services.
    UPAP Engine and Routers use this bus instead of importing services directly.
    Note: User and auth services are now DB-dependent and should be injected via Depends.
    """

    def __init__(self):
        self.upload_service = upload_service
        self.analysis_service = analysis_service
        self.records_service = records_service
        self.thumbnail_service = thumbnail_service


# global instance
service_bus = ServiceBus()
