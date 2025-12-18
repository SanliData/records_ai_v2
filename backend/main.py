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
