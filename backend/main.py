from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging

# Database initialization
from backend.db import init_db

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# API Routers
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

# Exception handlers
from backend.core.error_handler import register_exception_handlers

# Optional: Logging middleware
try:
    from backend.core.logging_middleware import LoggingMiddleware
    LOGGING_MIDDLEWARE_AVAILABLE = True
except ImportError:
    LOGGING_MIDDLEWARE_AVAILABLE = False

# Calculate paths robustly for Cloud Run buildpacks
# backend/main.py -> backend/ -> repo root
REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = REPO_ROOT / "frontend"
UPLOAD_HTML = FRONTEND_DIR / "upload.html"

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Records_AI_V2", version="2.0.0")

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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

# Register exception handlers
register_exception_handlers(app)

# Add logging middleware if available
if LOGGING_MIDDLEWARE_AVAILABLE:
    app.add_middleware(LoggingMiddleware)
    logger.info("Logging middleware registered")
else:
    logger.warning("Logging middleware not available - skipped")

# Startup: Initialize database
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
    
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        # Don't raise - allow app to start but log error

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
LOGIN_HTML = FRONTEND_DIR / "login.html"

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

# Register API routers
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

# Local sanity check: python -c 'import backend.main; print("ok")'
