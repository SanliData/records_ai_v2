"""
GCP Error Reporting Integration
Captures exceptions and sends them to Google Cloud Error Reporting.
"""

import os
import logging

logger = logging.getLogger(__name__)

# Try to import GCP Error Reporting
try:
    from google.cloud import error_reporting
    ERROR_REPORTING_AVAILABLE = True
except ImportError:
    ERROR_REPORTING_AVAILABLE = False
    logger.warning(
        "google-cloud-error-reporting not installed. "
        "Error reporting will use standard logging only."
    )


class ErrorReporter:
    """
    Error reporter that sends exceptions to GCP Error Reporting.
    Falls back to standard logging if GCP client not available.
    """

    def __init__(self):
        self.client = None
        self.enabled = False

        if ERROR_REPORTING_AVAILABLE:
            try:
                # Determine environment
                environment = os.getenv("ENVIRONMENT", "production")
                
                # Initialize client
                self.client = error_reporting.Client()
                self.enabled = True
                logger.info(f"GCP Error Reporting enabled (environment: {environment})")
            except Exception as e:
                logger.warning(f"Failed to initialize GCP Error Reporting: {e}")

    def report_exception(self, exception: Exception, **kwargs):
        """
        Report an exception to GCP Error Reporting.

        Args:
            exception: The exception to report
            **kwargs: Additional context (request_id, path, user_id, etc.)
        """
        if self.enabled and self.client:
            try:
                # Build error context
                context = {}
                if "request_id" in kwargs:
                    context["request_id"] = kwargs["request_id"]
                if "path" in kwargs:
                    context["path"] = kwargs["path"]
                if "user_id" in kwargs:
                    context["user_id"] = kwargs["user_id"]

                # Report to GCP
                self.client.report_exception(exception=exception, context=context)
            except Exception as e:
                logger.error(f"Failed to report exception to GCP: {e}")
        
        # Always log locally as fallback
        logger.exception(
            "Exception occurred",
            exc_info=exception,
            extra=kwargs
        )

    def report_message(self, message: str, severity: str = "ERROR", **kwargs):
        """
        Report a custom error message to GCP Error Reporting.

        Args:
            message: Error message
            severity: ERROR, WARNING, CRITICAL
            **kwargs: Additional context
        """
        if self.enabled and self.client:
            try:
                context = {}
                if "request_id" in kwargs:
                    context["request_id"] = kwargs["request_id"]
                if "path" in kwargs:
                    context["path"] = kwargs["path"]

                self.client.report(message, severity=severity, context=context)
            except Exception as e:
                logger.error(f"Failed to report message to GCP: {e}")

        # Always log locally
        log_level = getattr(logging, severity.upper(), logging.ERROR)
        logger.log(log_level, message, extra=kwargs)


# Global error reporter instance
error_reporter = ErrorReporter()
