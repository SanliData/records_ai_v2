from tester.detector import detect
from tester.classifier import classify
from tester.suggester import suggest
from tester.logger import log_event


def after_validation(context: dict):
    try:
        detect(context)
    except Exception as e:
        classification = classify(e, context)
        suggestion = suggest(e, context)
        log_event(
            stage=context.get("stage"),
            error=e,
            classification=classification,
            suggestion=suggestion,
            context=context,
        )
        raise
