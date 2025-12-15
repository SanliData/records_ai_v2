"""
Fix tester/hooks.py to ensure after_validation exists

ROLE: ROL-3
Purpose:
- Guarantee after_validation hook exists
- Safe overwrite of hooks.py
- No business logic touched

Encoding: UTF-8
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS_FILE = ROOT / "tester" / "hooks.py"


HOOKS_CONTENT = """
# Encoding: UTF-8

from tester.detector import detect
from tester.classifier import classify
from tester.suggester import suggest
from tester.logger import log_event


def after_validation(context: dict):
    \"""
    Passive router hook for validation stage.
    Stateless. Observer-only.
    Does not swallow exceptions.
    \"""
    try:
        detect(context)
    except Exception as e:
        classification = classify(e, context)
        suggestion = suggest(e, context)

        log_event(
            stage="VALIDATE",
            error=e,
            classification=classification,
            suggestion=suggestion,
            context=context,
        )
        raise
""".lstrip()


def main():
    print("=== FIXING tester/hooks.py ===")

    if not HOOKS_FILE.exists():
        raise FileNotFoundError("tester/hooks.py not found")

    HOOKS_FILE.write_text(HOOKS_CONTENT, encoding="utf-8")

    print("[OK] tester/hooks.py updated")
    print("[OK] after_validation hook is now guaranteed")
    print("=================================")


if __name__ == "__main__":
    main()
