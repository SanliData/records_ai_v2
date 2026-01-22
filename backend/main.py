import os
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
# Frontend files are now in backend/frontend/ for Cloud Run
FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

# Create FastAPI app (MUST happen early)
app = FastAPI(title="Records_AI_V2", version="2.0.0")

# P1-3: Rate Limiting - Enable with fallback
RATE_LIMITING_ENABLED = False
limiter = None
fallback_limiter = None
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    RATE_LIMITING_ENABLED = True
    logger.info("Rate limiting enabled via slowapi")
except Exception as e:
    logger.warning(f"Rate limiting disabled (slowapi not available): {e}")
    # P1-3: Fallback - Simple in-memory rate limit
    try:
        from backend.core.rate_limit import SimpleRateLimiter
        fallback_limiter = SimpleRateLimiter(requests_per_minute=20)
        logger.info("Fallback rate limiting enabled (in-memory)")
    except Exception as fallback_error:
        logger.warning(f"Fallback rate limiting also failed: {fallback_error}")


# P1-3: Rate Limiting Middleware (fallback if slowapi not available)
if fallback_limiter:
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request as StarletteRequest
    from starlette.responses import JSONResponse
    
    class RateLimitMiddleware(BaseHTTPMiddleware):
        """P1-3: Fallback rate limiting middleware."""
        
        async def dispatch(self, request: StarletteRequest, call_next):
            # Only apply to upload endpoint
            if request.url.path == "/api/v1/upap/upload" and request.method == "POST":
                client_ip = request.client.host if request.client else "unknown"
                is_allowed, remaining = fallback_limiter.is_allowed(client_ip)
                
                if not is_allowed:
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "Rate limit exceeded",
                            "message": f"Maximum 20 requests per minute. Remaining: {remaining}",
                            "retry_after": 60
                        },
                        headers={
                            "Retry-After": "60",
                            "X-RateLimit-Remaining": str(remaining)
                        }
                    )
            
            response = await call_next(request)
            return response
    
    app.add_middleware(RateLimitMiddleware)
    logger.info("Rate limiting middleware enabled (fallback)")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://zyagrolia.com",
        "https://api.zyagrolia.com",
        "https://records-ai-v2-969278596906.us-central1.run.app",
        "http://localhost:8000",
        "http://localhost:3000",
        "*",  # Allow all origins for Cloud Run (can be restricted later)
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
    # #region agent log
    import json
    import time
    log_path = REPO_ROOT / ".cursor" / "debug.log"
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "sessionId": "debug-session",
                "runId": "startup",
                "hypothesisId": "startup",
                "location": "backend/main.py:startup_event",
                "message": "Startup event triggered",
                "data": {
                    "repo_root": str(REPO_ROOT),
                    "frontend_dir": str(FRONTEND_DIR),
                    "frontend_exists": FRONTEND_DIR.exists()
                },
                "timestamp": int(time.time() * 1000)
            }) + "\n")
    except Exception:
        pass
    # #endregion
    
    # Startup verification logs
    logger.info("=" * 60)
    logger.info("STARTUP VERIFICATION")
    logger.info("=" * 60)
    logger.info(f"REPO_ROOT={REPO_ROOT}")
    logger.info(f"FRONTEND_DIR={FRONTEND_DIR}")
    logger.info(f"FRONTEND_DIR_EXISTS={FRONTEND_DIR.exists()}")
    if FRONTEND_DIR.exists():
        html_files = list(FRONTEND_DIR.glob("*.html"))
        logger.info(f"HTML_FILES_COUNT={len(html_files)}")
        logger.info(f"HTML_FILES={[f.name for f in html_files[:5]]}")
    logger.info("=" * 60)
    
    # #region agent log
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "sessionId": "debug-session",
                "runId": "startup",
                "hypothesisId": "startup",
                "location": "backend/main.py:startup_event:before_init_db",
                "message": "Before init_db check",
                "data": {"init_db_available": init_db is not None},
                "timestamp": int(time.time() * 1000)
            }) + "\n")
    except Exception:
        pass
    # #endregion
    
    if init_db:
        try:
            init_db()
            logger.info("Database initialized successfully")
            # #region agent log
            try:
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps({
                        "sessionId": "debug-session",
                        "runId": "startup",
                        "hypothesisId": "startup",
                        "location": "backend/main.py:startup_event:init_db_success",
                        "message": "Database initialized successfully",
                        "data": {},
                        "timestamp": int(time.time() * 1000)
                    }) + "\n")
            except Exception:
                pass
            # #endregion
        except Exception as e:
            logger.error(f"Database initialization failed: {e}", exc_info=True)
            # #region agent log
            try:
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps({
                        "sessionId": "debug-session",
                        "runId": "startup",
                        "hypothesisId": "startup",
                        "location": "backend/main.py:startup_event:init_db_error",
                        "message": "Database initialization failed",
                        "data": {"error": str(e), "error_type": type(e).__name__},
                        "timestamp": int(time.time() * 1000)
                    }) + "\n")
            except Exception:
                pass
            # #endregion
            # Don't raise - allow app to start but log error
    else:
        logger.warning("Database initialization skipped (module not available)")
        # #region agent log
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "sessionId": "debug-session",
                    "runId": "startup",
                    "hypothesisId": "startup",
                    "location": "backend/main.py:startup_event:init_db_skipped",
                    "message": "Database initialization skipped",
                    "data": {},
                    "timestamp": int(time.time() * 1000)
                }) + "\n")
        except Exception:
            pass
        # #endregion

# Health check endpoint - MUST remain JSON for monitoring
@app.get("/health")
def health():
    """Health check endpoint for monitoring."""
    # #region agent log
    import json
    import time
    log_path = REPO_ROOT / ".cursor" / "debug.log"
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "sessionId": "debug-session",
                "runId": "test",
                "hypothesisId": "A",
                "location": "backend/main.py:health",
                "message": "Health check called",
                "data": {"endpoint": "/health"},
                "timestamp": int(time.time() * 1000)
            }) + "\n")
    except Exception:
        pass
    # #endregion
    return {"status": "ok"}

# API Routers - OPTIONAL (wrap each to prevent crash)
ROUTERS_LOADED = []

# #region agent log
import json
import time
log_path = REPO_ROOT / ".cursor" / "debug.log"
try:
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "sessionId": "debug-session",
            "runId": "router_loading",
            "hypothesisId": "router_imports",
            "location": "backend/main.py:before_router_imports",
            "message": "Starting router imports",
            "data": {},
            "timestamp": int(time.time() * 1000)
        }) + "\n")
except Exception:
    pass
# #endregion

try:
    from backend.api.v1.upap_upload_router import router as upap_upload_router
    app.include_router(upap_upload_router)
    ROUTERS_LOADED.append("upap_upload")
    # #region agent log
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "sessionId": "debug-session",
                "runId": "router_loading",
                "hypothesisId": "router_imports",
                "location": "backend/main.py:upap_upload_router",
                "message": "Router loaded successfully",
                "data": {"router": "upap_upload"},
                "timestamp": int(time.time() * 1000)
            }) + "\n")
    except Exception:
        pass
    # #endregion
except Exception as e:
    logger.error(f"Failed to load upap_upload_router: {e}", exc_info=True)
    # #region agent log
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "sessionId": "debug-session",
                "runId": "router_loading",
                "hypothesisId": "router_imports",
                "location": "backend/main.py:upap_upload_router",
                "message": "Router failed to load",
                "data": {"router": "upap_upload", "error": str(e), "error_type": type(e).__name__},
                "timestamp": int(time.time() * 1000)
            }) + "\n")
    except Exception:
        pass
    # #endregion

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

# V2 AI-Orchestrated Pipeline Routers
try:
    from backend.api.v1.upap_upload_router_v2 import router as upap_upload_router_v2
    app.include_router(upap_upload_router_v2)
    ROUTERS_LOADED.append("upap_upload_v2")
except Exception as e:
    logger.error(f"Failed to load upap_upload_router_v2: {e}", exc_info=True)

try:
    from backend.api.v1.upap_archive_router_v2 import router as upap_archive_router_v2
    app.include_router(upap_archive_router_v2)
    ROUTERS_LOADED.append("upap_archive_v2")
except Exception as e:
    logger.error(f"Failed to load upap_archive_router_v2: {e}", exc_info=True)

try:
    from backend.api.v1.upap_preview_router_v2 import router as upap_preview_router_v2
    app.include_router(upap_preview_router_v2)
    ROUTERS_LOADED.append("upap_preview_v2")
except Exception as e:
    logger.error(f"Failed to load upap_preview_router_v2: {e}", exc_info=True)

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
    # #region agent log
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "sessionId": "debug-session",
                "runId": "router_loading",
                "hypothesisId": "router_imports",
                "location": "backend/main.py:auth_router",
                "message": "Router loaded successfully",
                "data": {"router": "auth"},
                "timestamp": int(time.time() * 1000)
            }) + "\n")
    except Exception:
        pass
    # #endregion
except Exception as e:
    logger.error(f"Failed to load auth_router: {e}", exc_info=True)
    # #region agent log
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "sessionId": "debug-session",
                "runId": "router_loading",
                "hypothesisId": "router_imports",
                "location": "backend/main.py:auth_router",
                "message": "Router failed to load",
                "data": {"router": "auth", "error": str(e), "error_type": type(e).__name__},
                "timestamp": int(time.time() * 1000)
            }) + "\n")
    except Exception:
        pass
    # #endregion

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

# Mount static frontend files at root - MUST be AFTER all routers
# This ensures API routes (/api/v1/*, /auth/*, etc.) take precedence
# StaticFiles with html=True will serve index.html for / and other HTML files
if FRONTEND_DIR.exists():
    # #region agent log
    import json
    log_path = REPO_ROOT / ".cursor" / "debug.log"
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "sessionId": "debug-session",
                "runId": "setup",
                "hypothesisId": "A",
                "location": "backend/main.py:mount_static",
                "message": "Mounting static files",
                "data": {
                    "frontend_dir": str(FRONTEND_DIR),
                    "exists": FRONTEND_DIR.exists(),
                    "files": list(FRONTEND_DIR.glob("*.html")) if FRONTEND_DIR.exists() else []
                },
                "timestamp": int(__import__("time").time() * 1000)
            }) + "\n")
    except Exception:
        pass
    # #endregion
    app.mount(
        "/",
        StaticFiles(directory=str(FRONTEND_DIR), html=True),
        name="frontend"
    )
    logger.info(f"Static files mounted at / from {FRONTEND_DIR}")
else:
    logger.warning(f"FRONTEND_DIR does not exist: {FRONTEND_DIR}")

# Mount storage directory for serving uploaded images
STORAGE_DIR = REPO_ROOT / "storage"
if STORAGE_DIR.exists():
    try:
        app.mount(
            "/storage",
            StaticFiles(directory=str(STORAGE_DIR)),
            name="storage"
        )
        logger.info(f"Storage files mounted at /storage from {STORAGE_DIR}")
    except Exception as e:
        logger.warning(f"Failed to mount storage directory: {e}")
else:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        app.mount(
            "/storage",
            StaticFiles(directory=str(STORAGE_DIR)),
            name="storage"
        )
        logger.info(f"Storage directory created and mounted at /storage")
    except Exception as e:
        logger.warning(f"Failed to mount storage directory: {e}")

# DEV ONLY: Mount /files as alias for /storage (temporary solution)
# PROD: Use Google Cloud Storage with signed URLs instead
if os.getenv("ENVIRONMENT", "dev").lower() == "dev":
    try:
        app.mount(
            "/files",
            StaticFiles(directory=str(STORAGE_DIR)),
            name="files"
        )
        logger.info(f"[DEV] Files mounted at /files from {STORAGE_DIR}")
    except Exception as e:
        logger.warning(f"[DEV] Failed to mount /files: {e}")

# Local run support
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8082))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port)