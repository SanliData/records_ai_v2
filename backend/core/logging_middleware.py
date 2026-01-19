"""
Structured Logging Middleware
Generates request IDs, logs all requests in JSON format, and tracks performance.
"""

import json
import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


# Configure JSON formatter for structured logging
class JSONFormatter(logging.Formatter):
    """Formatter that outputs structured JSON logs."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "path"):
            log_data["path"] = record.path
        if hasattr(record, "method"):
            log_data["method"] = record.method
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "latency_ms"):
            log_data["latency_ms"] = record.latency_ms
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "error_stack"):
            log_data["error_stack"] = record.error_stack

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


# Setup structured logger
logger = logging.getLogger("records_ai_v2")
logger.setLevel(logging.INFO)

# Remove default handlers
logger.handlers.clear()

# Add console handler with JSON formatter
console_handler = logging.StreamHandler()
console_handler.setFormatter(JSONFormatter())
logger.addHandler(console_handler)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that:
    1. Generates unique request ID per request
    2. Logs structured JSON for all requests
    3. Attaches request ID to response headers
    4. Tracks request latency
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Attach to request state for use in handlers
        request.state.request_id = request_id

        # Start timing
        start_time = time.time()

        # Extract user info if available (from auth token)
        user_id = None
        try:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                # In production, extract user_id from token
                # For now, use token hash as identifier
                token = auth_header.replace("Bearer ", "").strip()
                if token:
                    user_id = token[:8]  # First 8 chars as identifier
        except Exception:
            pass

        # Extract path and method
        path = request.url.path
        method = request.method

        # Skip logging for health checks and static files
        skip_paths = ["/health", "/docs", "/openapi.json", "/favicon.ico"]
        should_log = not any(path.startswith(skip) for skip in skip_paths)

        # Process request
        status_code = 500
        error_stack = None

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            status_code = 500
            error_stack = str(exc)
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "path": path,
                    "method": method,
                    "status_code": status_code,
                    "user_id": user_id,
                    "error_stack": error_stack,
                },
            )
            raise
        finally:
            # Calculate latency
            latency_ms = round((time.time() - start_time) * 1000, 2)

            # Log request (if not skipped)
            if should_log:
                log_extra = {
                    "request_id": request_id,
                    "path": path,
                    "method": method,
                    "status_code": status_code,
                    "latency_ms": latency_ms,
                }

                if user_id:
                    log_extra["user_id"] = user_id

                if error_stack:
                    log_extra["error_stack"] = error_stack

                # Log based on status code
                if status_code >= 500:
                    logger.error("Request completed", extra=log_extra)
                elif status_code >= 400:
                    logger.warning("Request completed", extra=log_extra)
                else:
                    logger.info("Request completed", extra=log_extra)

        # Attach request ID to response header
        response.headers["X-Request-ID"] = request_id

        return response
