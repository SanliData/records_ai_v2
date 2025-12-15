# -*- coding: utf-8 -*-
"""
Global Error Handler – Role-3 Standard

Handles:
- HTTPException → normalized JSON
- Unexpected errors → 500 with stable schema
"""

import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)


def register_exception_handlers(app):

    @app.exception_handler(HTTPException)
    async def http_exc_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error_type": "http_exception",
                "detail": exc.detail,
                "path": request.url.path,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exc_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error_type": "unhandled_exception",
                "detail": "Internal Server Error",
                "path": request.url.path,
            },
        )
