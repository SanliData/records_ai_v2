from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path
import logging

from core.logging_middleware import LoggingMiddleware
from core.error_handler import register_exception_handlers

# Calculate repo root: backend/main.py -> backend/ -> repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_HTML = REPO_ROOT / "frontend" / "upload.html"

logger = logging.getLogger(__name__)

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
    # Startup: Validate secrets and initialize database
    from core.secrets import SecretLoader
    try:
        SecretLoader.validate_required_secrets()
    except RuntimeError as e:
        # Fail fast if required secrets are missing
        import sys
        print(f"FATAL: {e}", file=sys.stderr)
        raise
    
    init_db()
    
    # Log upload HTML path for verification
    logger.info("UPLOAD_HTML path=%s exists=%s", str(UPLOAD_HTML), UPLOAD_HTML.exists())
    
    yield
    # Shutdown: cleanup if needed

def create_app() -> FastAPI:
    app = FastAPI(
        title="Records_AI_V2",
        version="2.0.0",
        lifespan=lifespan,
    )

    # Register exception handlers (before routes)
    register_exception_handlers(app)

    # Add structured logging middleware
    app.add_middleware(LoggingMiddleware)

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

    @app.get("/health")
    def health():
        """Health check endpoint for monitoring."""
        return {"status": "ok"}

    @app.get("/")
    async def root():
        """Root endpoint serves upload page."""
        return FileResponse(
            UPLOAD_HTML,
            media_type="text/html",
            headers={"Cache-Control": "no-store"}
        )

    return app

app = create_app()


