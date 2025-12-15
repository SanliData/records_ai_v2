"""
records_ai – Initial Tester & Error Library Bootstrap Script

ROLE: ROL-3 (Senior Engineer)
PURPOSE:
- Enable tester hooks (detect / classify / suggest)
- Initialize canonical error library
- Prepare learning spider storage (passive mode)
- NO auto-fix
- NO core logic modification

Encoding: UTF-8
"""

from pathlib import Path
import json
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[1]

TESTER_DIR = BASE_DIR / "tester"
ERROR_LIB_DIR = BASE_DIR / "error_library"

CANONICAL_ERRORS = ERROR_LIB_DIR / "canonical_errors.json"
OCCURRENCES_LOG = ERROR_LIB_DIR / "occurrences.log"
EXTERNAL_KNOWLEDGE = ERROR_LIB_DIR / "external_knowledge.json"


def ensure_dir(path: Path):
    if not path.exists():
        path.mkdir(parents=True)
        print(f"[INIT] Created directory: {path}")


def ensure_file(path: Path, default_content):
    if not path.exists():
        with path.open("w", encoding="utf-8") as f:
            json.dump(default_content, f, indent=2)
        print(f"[INIT] Created file: {path}")


def ensure_log_file(path: Path):
    if not path.exists():
        with path.open("w", encoding="utf-8") as f:
            f.write("")
        print(f"[INIT] Created log file: {path}")


def bootstrap_tester():
    ensure_dir(TESTER_DIR)

    modules = [
        "detector.py",
        "classifier.py",
        "suggester.py",
        "logger.py",
        "hooks.py",
        "__init__.py",
    ]

    for module in modules:
        module_path = TESTER_DIR / module
        if not module_path.exists():
            module_path.write_text(
                "# Tester module placeholder\n",
                encoding="utf-8"
            )
            print(f"[INIT] Created tester module: {module}")


def bootstrap_error_library():
    ensure_dir(ERROR_LIB_DIR)

    ensure_file(
        CANONICAL_ERRORS,
        default_content={}
    )

    ensure_file(
        EXTERNAL_KNOWLEDGE,
        default_content={}
    )

    ensure_log_file(OCCURRENCES_LOG)


def write_system_marker():
    marker = BASE_DIR / ".tester_enabled"
    if not marker.exists():
        marker.write_text(
            f"tester_enabled_at={datetime.utcnow().isoformat()}Z\n"
            "auto_fix=DISABLED\n",
            encoding="utf-8"
        )
        print("[INIT] Tester system marker created")


def main():
    print("=== records_ai | Initial Tester Update ===")
    print("Auto-fix: DISABLED")
    print("Mode: DETECT / CLASSIFY / SUGGEST ONLY\n")

    bootstrap_tester()
    bootstrap_error_library()
    write_system_marker()

    print("\n[INIT] Tester & Error Library successfully initialized.")
    print("[INIT] System ready for continuous error logging.")
    print("===========================================")


if __name__ == "__main__":
    main()
