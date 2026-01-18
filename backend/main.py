from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Calculate paths robustly for Cloud Run buildpacks
# backend/main.py -> backend/ -> repo root
REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = REPO_ROOT / "frontend"
UPLOAD_HTML = FRONTEND_DIR / "upload.html"
LOGIN_HTML = FRONTEND_DIR / "login.html"

# Create FastAPI app (MUST happen early)
app = FastAPI(title="Records_AI_V2", version="2.0.0")

# Rate limiting - OPTIONAL (wrap in try/except)
RATE_LIMITING_ENABLED = False
limiter = None
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    RATE_LIMITING_ENABLED = True
    logger.info("Rate limiting enabled")
except Exception as e:
    logger.warning(f"Rate limiting disabled: {e}")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://zyagrolia.com",
        "http://localhost:8000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers - OPTIONAL (wrap in try/except)
try:
    from backend.core.error_handler import register_exception_handlers
    register_exception_handlers(app)
    logger.info("Exception handlers registered")
except Exception as e:
    logger.warning(f"Exception handlers disabled: {e}")

# Optional: Logging middleware
try:
    from backend.core.logging_middleware import LoggingMiddleware
    app.add_middleware(LoggingMiddleware)
    logger.info("Logging middleware registered")
except Exception as e:
    logger.warning(f"Logging middleware not available: {e}")

# Database initialization - OPTIONAL (wrap to prevent crash)
try:
    from backend.db import init_db
except Exception as e:
    logger.warning(f"Database module import failed: {e}")
    init_db = None

# Startup: Initialize database (if available)
@app.on_event("startup")
async def startup_event():
    """Initialize database and validate configuration on startup."""
    # Startup verification logs
    logger.info("=" * 60)
    logger.info("STARTUP VERIFICATION")
    logger.info("=" * 60)
    logger.info(f"REPO_ROOT={REPO_ROOT}")
    logger.info(f"FRONTEND_DIR={FRONTEND_DIR}")
    logger.info(f"FRONTEND_DIR_EXISTS={FRONTEND_DIR.exists()}")
    logger.info(f"UPLOAD_HTML_PATH={UPLOAD_HTML}")
    logger.info(f"FILE_EXISTS={UPLOAD_HTML.exists()}")
    logger.info("=" * 60)
    
    if init_db:
        try:
            init_db()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}", exc_info=True)
            # Don't raise - allow app to start but log error
    else:
        logger.warning("Database initialization skipped (module not available)")

# Health check endpoint - MUST remain JSON for monitoring
@app.get("/health")
def health():
    """Health check endpoint for monitoring."""
    return {"status": "ok"}

# Root endpoint - serves upload UI (NEVER JSON)
@app.get("/")
async def root():
    """Root endpoint serves upload page. Always returns HTML, never JSON."""
    if not UPLOAD_HTML.exists():
        logger.error(f"UPLOAD_HTML not found at: {UPLOAD_HTML}")
        # Return simple HTML error, not JSON
        from fastapi.responses import HTMLResponse
        return HTMLResponse(
            content=f"<html><body><h1>Upload UI Not Found</h1><p>Path: {UPLOAD_HTML}</p></body></html>",
            status_code=500,
            headers={"Cache-Control": "no-store"}
        )
    
    return FileResponse(
        str(UPLOAD_HTML),
        media_type="text/html",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate"}
    )

# Serve static frontend files - Use absolute string path for Cloud Run
if FRONTEND_DIR.exists():
    app.mount("/ui", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="ui")
    logger.info(f"Static files mounted at /ui from {FRONTEND_DIR}")
else:
    logger.warning(f"FRONTEND_DIR does not exist: {FRONTEND_DIR}")

# Serve login.html at root level for backward compatibility
@app.get("/login.html")
async def login_page():
    """Serve login.html for backward compatibility."""
    if LOGIN_HTML.exists():
        return FileResponse(
            str(LOGIN_HTML),
            media_type="text/html",
            headers={"Cache-Control": "no-store, no-cache, must-revalidate"}
        )
    return JSONResponse({"detail": "Not Found"}, status_code=404)

# API Routers - OPTIONAL (wrap each to prevent crash)
ROUTERS_LOADED = []

try:
    from backend.api.v1.upap_upload_router import router as upap_upload_router
    app.include_router(upap_upload_router)
    ROUTERS_LOADED.append("upap_upload")
except Exception as e:
    logger.error(f"Failed to load upap_upload_router: {e}", exc_info=True)

try:
    from backend.api.v1.upap_process_router import router as upap_process_router
    app.include_router(upap_process_router)
    ROUTERS_LOADED.append("upap_process")
except Exception as e:
    logger.error(f"Failed to load upap_process_router: {e}", exc_info=True)

try:
    from backend.api.v1.upap_archive_router import router as upap_archive_router
    app.include_router(upap_archive_router)
    ROUTERS_LOADED.append("upap_archive")
except Exception as e:
    logger.error(f"Failed to load upap_archive_router: {e}", exc_info=True)

try:
    from backend.api.v1.upap_archive_add_router import router as upap_archive_add_router
    app.include_router(upap_archive_add_router)
    ROUTERS_LOADED.append("upap_archive_add")
except Exception as e:
    logger.error(f"Failed to load upap_archive_add_router: {e}", exc_info=True)

try:
    from backend.api.v1.upap_publish_router import router as upap_publish_router
    app.include_router(upap_publish_router)
    ROUTERS_LOADED.append("upap_publish")
except Exception as e:
    logger.error(f"Failed to load upap_publish_router: {e}", exc_info=True)

try:
    from backend.api.v1.upap_recognition_router import router as upap_recognition_router
    app.include_router(upap_recognition_router)
    ROUTERS_LOADED.append("upap_recognition")
except Exception as e:
    logger.error(f"Failed to load upap_recognition_router: {e}", exc_info=True)

try:
    from backend.api.v1.upap_system_archive_router import router as upap_system_archive_router
    app.include_router(upap_system_archive_router)
    ROUTERS_LOADED.append("upap_system_archive")
except Exception as e:
    logger.error(f"Failed to load upap_system_archive_router: {e}", exc_info=True)

try:
    from backend.api.v1.upap_dashboard_router import router as upap_dashboard_router
    app.include_router(upap_dashboard_router)
    ROUTERS_LOADED.append("upap_dashboard")
except Exception as e:
    logger.error(f"Failed to load upap_dashboard_router: {e}", exc_info=True)

try:
    from backend.api.v1.dashboard_router import router as dashboard_router
    app.include_router(dashboard_router)
    ROUTERS_LOADED.append("dashboard")
except Exception as e:
    logger.error(f"Failed to load dashboard_router: {e}", exc_info=True)

try:
    from backend.api.v1.vinyl_pricing_router import router as vinyl_pricing_router
    app.include_router(vinyl_pricing_router)
    ROUTERS_LOADED.append("vinyl_pricing")
except Exception as e:
    logger.error(f"Failed to load vinyl_pricing_router: {e}", exc_info=True)

try:
    from backend.api.v1.marketplace_router import router as marketplace_router
    app.include_router(marketplace_router)
    ROUTERS_LOADED.append("marketplace")
except Exception as e:
    logger.error(f"Failed to load marketplace_router: {e}", exc_info=True)

try:
    from backend.api.v1.auth_router import router as auth_router
    app.include_router(auth_router)
    ROUTERS_LOADED.append("auth")
except Exception as e:
    logger.error(f"Failed to load auth_router: {e}", exc_info=True)

try:
    from backend.api.v1.admin_router import router as admin_router
    app.include_router(admin_router)
    ROUTERS_LOADED.append("admin")
except Exception as e:
    logger.error(f"Failed to load admin_router: {e}", exc_info=True)

# Log router status
logger.info(f"Routers loaded: {len(ROUTERS_LOADED)}/{14}")
if ROUTERS_LOADED:
    logger.info(f"Loaded routers: {', '.join(ROUTERS_LOADED)}")

# Local run support
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8080)
