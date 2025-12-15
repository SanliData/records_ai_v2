"""
records_ai_v2 – Unified Update Runner (CANONICAL)

ROLE: ROL-1 / ROL-2 / ROL-3
GOAL:
- Single update entrypoint
- Guarantee tester core integrity
- Guarantee router bindings
- Idempotent & safe
- No business auto-fix

Encoding: UTF-8
"""

from pathlib import Path
from datetime import datetime
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]

TESTER = ROOT / "tester"
ERROR_LIB = ROOT / "error_library"
BACKUP_DIR = ROOT / "_tester_backups"

UPAP_VALIDATION = ROOT / "backend/services/upap/engine/upap_validation.py"
UPAP_UPLOAD = ROOT / "backend/services/upap/upload/upload_stage.py"
UPAP_PROCESS = ROOT / "backend/services/upap/process/process_stage.py"
UPAP_ARCHIVE = ROOT / "backend/services/upap/archive/archive_stage.py"

MARKER = ROOT / ".records_ai_update_marker"


def log(msg):
    print(f"[UPDATE] {msg}")


# -------------------------------------------------
# Backup helper
# -------------------------------------------------
def backup(path: Path):
    BACKUP_DIR.mkdir(exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"{path.name}.{ts}.bak"
    shutil.copy2(path, dest)
    log(f"Backup created: {dest.name}")


# -------------------------------------------------
# 1. Error library (safe)
# -------------------------------------------------
def ensure_error_library():
    ERROR_LIB.mkdir(exist_ok=True)

    for name in ["canonical_errors.json", "external_knowledge.json"]:
        p = ERROR_LIB / name
        if not p.exists():
            p.write_text("{}", encoding="utf-8")
            log(f"Created {name}")

    occ = ERROR_LIB / "occurrences.log"
    if not occ.exists():
        occ.write_text("", encoding="utf-8")
        log("Created occurrences.log")


# -------------------------------------------------
# 2. Tester core (FORCE-SAFE)
# -------------------------------------------------
def ensure_tester_core():
    TESTER.mkdir(exist_ok=True)

    modules = {
        "detector.py": """
def detect(context: dict):
    \"\"\"Passive detection hook.\"\"\"
    return True
""",
        "classifier.py": """
def classify(error: Exception, context: dict) -> dict:
    return {
        "error_type": type(error).__name__,
        "message": str(error),
        "stage": context.get("stage"),
    }
""",
        "suggester.py": """
def suggest(error: Exception, context: dict) -> list:
    return [
        "Inspect schema validation",
        "Check pipeline contracts",
        "Review recent changes"
    ]
""",
        "logger.py": f"""
from pathlib import Path
from datetime import datetime
import json

ERROR_LIB = Path(r"{ERROR_LIB}")
CANONICAL = ERROR_LIB / "canonical_errors.json"
OCCURRENCES = ERROR_LIB / "occurrences.log"


def log_event(stage, error, classification, suggestion, context):
    key = classification.get("error_type", "UNKNOWN_ERROR")

    data = json.loads(CANONICAL.read_text(encoding="utf-8"))

    if key not in data:
        data[key] = {{
            "first_seen": datetime.utcnow().isoformat() + "Z",
            "description": classification.get("message"),
            "solutions": suggestion
        }}
        CANONICAL.write_text(json.dumps(data, indent=2), encoding="utf-8")
    else:
        with OCCURRENCES.open("a", encoding="utf-8") as f:
            f.write(
                f"{{key}} {{datetime.utcnow().isoformat()}} "
                f"record_id={{context.get('record_id')}}\\n"
            )
""",
        "hooks.py": """
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
""",
    }

    for name, content in modules.items():
        path = TESTER / name
        path.write_text(content.lstrip(), encoding="utf-8")
        log(f"Ensured tester/{name}")


# -------------------------------------------------
# 3. Router binding (idempotent)
# -------------------------------------------------
def bind_router(path: Path, stage: str):
    if not path.exists():
        log(f"Skip {path.name} (not found)")
        return

    content = path.read_text(encoding="utf-8")
    if "after_validation(" in content:
        log(f"{path.name} already bound")
        return

    backup(path)

    import_line = "from tester.hooks import after_validation\n"
    hook = f"""
        after_validation({{
            "pipeline": "UPAP",
            "stage": "{stage}",
            "record_id": getattr(data, "id", None)
        }})
""".rstrip()

    lines = content.splitlines()
    out = []
    imported = False
    injected = False

    for line in lines:
        if not imported and line.startswith("from"):
            out.append(import_line.rstrip())
            imported = True

        out.append(line)

        if not injected and line.strip().startswith("return"):
            out.insert(len(out) - 1, hook)
            injected = True

    path.write_text("\\n".join(out), encoding="utf-8")
    log(f"Bound tester to {path.name}")


def apply_bindings():
    bind_router(UPAP_VALIDATION, "validation")
    bind_router(UPAP_UPLOAD, "upload")
    bind_router(UPAP_PROCESS, "process")
    bind_router(UPAP_ARCHIVE, "archive")


# -------------------------------------------------
# 4. Marker
# -------------------------------------------------
def write_marker():
    MARKER.write_text(
        f"updated_at={datetime.utcnow().isoformat()}Z\n",
        encoding="utf-8",
    )


def main():
    print("=== RECORDS_AI UNIFIED UPDATE RUNNER (CANONICAL) ===")
    print("Mode: PASSIVE / OBSERVER")
    print("Auto-fix: DISABLED\\n")

    ensure_error_library()
    ensure_tester_core()
    apply_bindings()
    write_marker()

    print("\\n[OK] records_ai_v2 update complete.")
    print("==================================================")


if __name__ == "__main__":
    main()
