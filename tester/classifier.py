def classify(error: Exception, context: dict) -> dict:
    return {
        "error_type": type(error).__name__,
        "message": str(error),
        "stage": context.get("stage"),
    }
