from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from backend.api.v1.upap_upload_router import router as upap_upload_router
from backend.api.v1.upap_process_router import router as upap_process_router
from backend.api.v1.upap_archive_router import router as upap_archive_router
from backend.api.v1.upap_archive_add_router import router as upap_archive_add_router
from backend.api.v1.upap_publish_router import router as upap_publish_router
from backend.api.v1.upap_recognition_router import router as upap_recognition_router
from backend.api.v1.upap_system_archive_router import router as upap_system_archive_router
from backend.api.v1.upap_dashboard_router import router as upap_dashboard_router
from backend.api.v1.dashboard_router import router as dashboard_router
from backend.api.v1.vinyl_pricing_router import router as vinyl_pricing_router
from backend.api.v1.marketplace_router import router as marketplace_router
from backend.api.v1.auth_router import router as auth_router
from backend.api.v1.admin_router import router as admin_router
from backend.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    init_db()
    yield
    # Shutdown: cleanup if needed


def create_app() -> FastAPI:
    app = FastAPI(
        title="Records_AI_V2",
        version="2.0.0",
        lifespan=lifespan,
    )

    # Mount static files for frontend
    app.mount("/ui", StaticFiles(directory="frontend", html=True), name="ui")

    app.include_router(upap_upload_router)
    app.include_router(upap_process_router)
    app.include_router(upap_archive_router)
    app.include_router(upap_archive_add_router)
    app.include_router(upap_publish_router)
    app.include_router(upap_recognition_router)
    app.include_router(upap_system_archive_router)
    app.include_router(upap_dashboard_router)
    app.include_router(dashboard_router)
    app.include_router(vinyl_pricing_router)
    app.include_router(marketplace_router)
    app.include_router(auth_router)
    app.include_router(admin_router)

    @app.get("/")
    def health():
        return {
            "status": "ok",
            "service": "records_ai_v2",
            "mode": "UPAP-only",
            "version": "2.0.0",
        }

    return app


app = create_app()


