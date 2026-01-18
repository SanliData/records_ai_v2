# -*- coding: utf-8 -*-

from fastapi import APIRouter

from backend.api.v1.upap_upload_router import router as upap_upload_router
from backend.api.v1.upap_process_router import router as upap_process_router
from backend.api.v1.upap_archive_router import router as upap_archive_router
from backend.api.v1.upap_publish_router import router as upap_publish_router


router = APIRouter(
    prefix="/upap",
    tags=["UPAP"],
)

router.include_router(upap_upload_router)
router.include_router(upap_process_router)
router.include_router(upap_archive_router)
router.include_router(upap_publish_router)
