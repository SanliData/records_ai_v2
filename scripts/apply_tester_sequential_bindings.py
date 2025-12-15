"""
records_ai_v2 – Sequential Tester Router Bindings

ROLE: ROL-1 / ROL-2 / ROL-3
SCOPE:
- Bind tester sequentially: upload → process → archive
- Validation already bound
- Passive observer only
- Backup before each modification
- Idempotent

Encoding: UTF-8
"""

from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(__file__).resolve().parents[1]

BACKUP_DIR = ROOT / "_tester_backups"

ROUTERS = [
    {
        "name": "UPLOAD",
        "file": ROOT / "backend/services/upap/upload/upload_stage.py",
        "context": {
            "pipeline": "UPAP",
            "stage": "upload",
            "schema": "pending_record",
            "status": "PASS"
        }
    },
    {
        "name": "PROCESS",
        "file": ROOT / "backend/services/upap/process/process_stage.py",
        "context": {
            "pipeline": "UPAP",
            "stage": "process",
            "schema": "pending_record",
            "status": "PASS"
        }
    },
    {
        "name": "ARCHIVE",
        "file": ROOT / "backend/services/upap/archive/archive_stage.py",
        "context": {
            "pipeline": "UPAP",
            "stage": "archive",
            "schema": "archive_record",
            "status": "PASS"
        }
    },
]


def ensure_backup(path: Path):
    BACKUP_DIR.mkdir(exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"{path.name}.{ts}.bak"
    shutil.copy2(path, backup)
    print(f"[BACKUP] {backup.name}")


def bind_router(router):
    path = router["file"]
    name = router["name"]

    if not path.exists():
        print(f"[SKIP] {name}: file not found")
        return

    content = path.read_text(encoding="utf-8")

    if "after_validation(" in content:
        print(f"[SKIP] {name}: tester already bound")
        return

    ensure_backup(path)

    import_line = "from tester.hooks import after_validation\n"

    hook_block = f"""
        after_validation({router['context']})
""".rstrip()

    lines = content.splitlines()
    new_lines = []
    import_injected = False
    hook_injected = False

    for line in lines:
        if not import_injected and line.startswith("from"):
            new_lines.append(import_line.rstrip())
            import_injected = True

        new_lines.append(line)

        if not hook_injected and line.strip().startswith("return"):
            new_lines.insert(len(new_lines) - 1, hook_block)
            hook_injected = True

    path.write_text("\n".join(new_lines), encoding="utf-8")
    print(f"[BIND] {name} router bound")


def main():
    print("=== APPLYING SEQUENTIAL TESTER BINDINGS ===")
    print("Mode: PASSIVE / OBSERVER")
    print("Auto-fix: DISABLED\n")

    for router in ROUTERS:
        bind_router(router)

    print("\n[OK] Sequential router bindings complete.")
    print("=========================================")


if __name__ == "__main__":
    main()
