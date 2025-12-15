# -*- coding: utf-8 -*-
"""
Records_AI V2 – FastAPI Entrypoint (Role-3 Gold Standard)
UTF-8, English-only, no BOM.

Responsibilities:
- Application factory
- Router registration (legacy + UPAP)
- Global middleware
- Global exception handling
- Database initialization hook

Forbidden:
- Business logic
- Direct DB queries (except init_db())
- Service calls
"""

from __future__ import annotations

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Core infrastructure
from backend.core.db import init_db
from backend.core.router_bus import router_bus
from backend.core.error_handler import register_exception_handlers

# V1 routers
from backend.api.v1.upload_router import router as upload_router
from backend.api.v1.search_router import router as search_router
from backend.api.v1.user_library_router import router as user_library_router
from backend.api.v1.documentation_router import router as documentation_router
from backend.api.v1.archive_router import router as archive_router
from backend.api.v1.admin_router import router as admin_router
from backend.api.v1.auth_router import router as auth_router
from backend.api.v1.records_router import router as records_router
from backend.api.v1.analyze_record import router as analyze_router

# UPAP routers
from backend.api.v1.upap_router import router as upap_router
from backend.api.v1.upap_dashboard_router import router as upap_dashboard_router


# --------------------------------------------------------------------------- #
# App Factory                                                                  #
# --------------------------------------------------------------------------- #

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Role-3 Guarantees:
    - This file only performs wiring.
    - HTTP path ownership belongs to routers.
    - Zero business logic.
    """

    app = FastAPI(
        title="Records_AI V2 Backend",
        version="2.0.0",
        description="UPAP-centric upload → process → archive → publish pipeline."
    )

    # ---------------------- CORS (fully open for development) ----------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --------------------------- Global Error Handlers ---------------------------
    register_exception_handlers(app)

    # ------------------------------ Router Registry ------------------------------
    routers = [
        upload_router,
        search_router,
        user_library_router,
        documentation_router,
        archive_router,
        admin_router,
        auth_router,
        records_router,
        analyze_router,
        upap_router,
        upap_dashboard_router,   # UPAP pipeline entrypoints
    ]

    for r in routers:
        router_bus.register(r)
        app.include_router(r)

    # -------------------------------- Startup Hook -------------------------------
    @app.on_event("startup")
    async def on_startup() -> None:
        logging.info("Initializing database (init_db)...")
        init_db()
        logging.info("Database initialization completed.")

    # -------------------------------- Healthcheck --------------------------------
    @app.get("/")
    async def root() -> dict:
        return {
            "status": "ok",
            "service": "records_ai_v2",
            "mode": "UPAP-centric",
            "version": "2.0.0"
        }

    return app


# Entrypoint (Uvicorn)
app = create_app()
