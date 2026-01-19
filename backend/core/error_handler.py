# -*- coding: utf-8 -*-
"""
Global Error Handler – Role-3 Standard

Handles:
- HTTPException → normalized JSON
- Unexpected errors → 500 with stable schema
- GCP Error Reporting integration
"""

import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# Defensive import: error_reporting is optional
try:
    from backend.core.error_reporting import error_reporter
    ERROR_REPORTING_AVAILABLE = True
except ImportError:
    ERROR_REPORTING_AVAILABLE = False
    logger.warning("error_reporting module not available - using fallback error handling")
    # Create stub error_reporter
    class ErrorReporterStub:
        def report_exception(self, **kwargs):
            pass
        def report_message(self, **kwargs):
            pass
    error_reporter = ErrorReporterStub()


def register_exception_handlers(app):

    @app.exception_handler(HTTPException)
    async def http_exc_handler(request: Request, exc: HTTPException):
        request_id = getattr(request.state, "request_id", None)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error_type": "http_exception",
                "detail": exc.detail,
                "path": request.url.path,
                "request_id": request_id,
            },
            headers={"X-Request-ID": request_id} if request_id else None,
        )

    @app.exception_handler(Exception)
    async def unhandled_exc_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", None)
        path = request.url.path

        # Report to GCP Error Reporting
        error_reporter.report_exception(
            exception=exc,
            request_id=request_id,
            path=path,
        )

        logger.exception("Unhandled error", exc_info=exc, extra={
            "request_id": request_id,
            "path": path,
        })

        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error_type": "unhandled_exception",
                "detail": "Internal Server Error",
                "path": path,
                "request_id": request_id,
            },
            headers={"X-Request-ID": request_id} if request_id else None,
        )
