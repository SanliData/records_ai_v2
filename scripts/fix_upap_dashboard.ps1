# FIX UPAP DASHBOARD – CANONICAL
$ErrorActionPreference = "Stop"

Write-Host "== UPAP Dashboard Fix Started =="

$apiPath = "backend/api/v1"
$mainPath = "backend/main.py"

$upapDashboardPath = "$apiPath/upap_dashboard_router.py"
$legacySummaryPath = "$apiPath/upap_dashboard_summary_router.py"

# Remove legacy summary router
if (Test-Path $legacySummaryPath) {
    Remove-Item $legacySummaryPath -Force
    Write-Host "Removed legacy summary router"
}

# Write canonical UPAP dashboard router
@"
from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(
    prefix="/upap/dashboard",
    tags=["upap-dashboard"],
)

@router.get("/summary")
def dashboard_summary():
    return {
        "status": "ok",
        "scope": "system",
        "records_total": 0,
        "users_total": 0,
        "pending_recognition": 0,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }
"@ | Set-Content $upapDashboardPath -Encoding UTF8

Write-Host "upap_dashboard_router.py written"

# Rewrite main.py (canonical)
@"
from fastapi import FastAPI

from backend.api.v1.upap_upload_router import router as upap_upload_router
from backend.api.v1.upap_process_router import router as upap_process_router
from backend.api.v1.upap_archive_router import router as upap_archive_router
from backend.api.v1.upap_publish_router import router as upap_publish_router
from backend.api.v1.upap_dashboard_router import router as upap_dashboard_router
from backend.api.v1.dashboard_router import router as dashboard_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Records_AI_V2",
        version="2.0.0",
    )

    app.include_router(upap_upload_router)
    app.include_router(upap_process_router)
    app.include_router(upap_archive_router)
    app.include_router(upap_publish_router)
    app.include_router(upap_dashboard_router)
    app.include_router(dashboard_router)

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
"@ | Set-Content $mainPath -Encoding UTF8

Write-Host "main.py rewritten"

Write-Host ""
Write-Host "=== FIX COMPLETE ==="
Write-Host "Expected endpoints:"
Write-Host "GET  /dashboard"
Write-Host "POST /upap/upload"
Write-Host "GET  /upap/dashboard/summary"
Write-Host ""
Write-Host "Next step: docker build and deploy"
