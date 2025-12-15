"""
records_ai_v2 – One-shot Tester Integration Script

ROLE: ROL-1 / ROL-2 / ROL-3 (Authorized)
SCOPE:
- Ensure tester + error_library are initialized
- Bind tester to UPAP validation router
- Router-principled, passive, no auto-fix
- Backup before modification

Encoding: UTF-8
"""

from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(__file__).resolve().parents[1]

TESTER_DIR = ROOT / "tester"
ERROR_LIB_DIR = ROOT / "error_library"

VALIDATION_FILE = (
    ROOT
    / "backend"
    / "services"
    / "upap"
    / "engine"
    / "upap_validation.py"
)

BACKUP_DIR = ROOT / "_tester_backups"
MARKER = ROOT / ".tester_bound"


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def bootstrap_directories():
    ensure_dir(TESTER_DIR)
    ensure_dir(ERROR_LIB_DIR)

    for f in [
        ERROR_LIB_DIR / "canonical_errors.json",
        ERROR_LIB_DIR / "external_knowledge.json",
        ERROR_LIB_DIR / "occurrences.log",
    ]:
        if not f.exists():
            f.write_text("{}" if f.suffix == ".json" else "", encoding="utf-8")


def ensure_tester_hooks():
    hooks_file = TESTER_DIR / "hooks.py"
    if hooks_file.exists():
        return

    hooks_file.write_text(
        """
# Encoding: UTF-8

from tester.detector import detect
from tester.classifier import classify
from tester.suggester import suggest
from tester.logger import log_event


def after_validation(context: dict):
    \"\"\"
    Passive validation router hook.
    Stateless. No side-effects.
    \"\"\"
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
""".lstrip(),
        encoding="utf-8",
    )


def backup_file(path: Path):
    ensure_dir(BACKUP_DIR)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"{path.name}.{timestamp}.bak"
    shutil.copy2(path, backup)
    print(f"[BACKUP] {backup.name}")


def bind_validation_router():
    if MARKER.exists():
        print("[SKIP] Tester already bound.")
        return

    if not VALIDATION_FILE.exists():
        raise FileNotFoundError(f"Validation file not found: {VALIDATION_FILE}")

    content = VALIDATION_FILE.read_text(encoding="utf-8")

    if "after_validation(" in content:
        print("[SKIP] Hook already present in validation file.")
        MARKER.write_text("already_bound\n", encoding="utf-8")
        return

    backup_file(VALIDATION_FILE)

    injection = """
from tester.hooks import after_validation
""".lstrip()

    hook_call = """
        after_validation({
            "pipeline": "UPAP",
            "stage": "validation",
            "schema": "pending_record",
            "record_id": getattr(data, "id", None),
            "status": "PASS"
        })
""".rstrip()

    lines = content.splitlines()
    new_lines = []
    injected_import = False
    injected_call = False

    for line in lines:
        if not injected_import and line.startswith("from"):
            new_lines.append(injection.rstrip())
            injected_import = True

        new_lines.append(line)

        if (
            not injected_call
            and "return" in line
            and "validate" in content
        ):
            new_lines.insert(len(new_lines) - 1, hook_call)
            injected_call = True

    VALIDATION_FILE.write_text("\n".join(new_lines), encoding="utf-8")

    MARKER.write_text(
        "tester_bound_to=upap_validation\nmode=passive\nauto_fix=disabled\n",
        encoding="utf-8",
    )

    print("[BIND] Tester bound to UPAP validation router.")


def main():
    print("=== APPLYING TESTER INTEGRATION ===")
    print("Mode: PASSIVE / OBSERVER")
    print("Auto-fix: DISABLED\n")

    bootstrap_directories()
    ensure_tester_hooks()
    bind_validation_router()

    print("\n[OK] Tester + records_ai_v2 integration complete.")
    print("==================================")


if __name__ == "__main__":
    main()
