import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

STAGE_FILES = [
    "backend/services/upap/auth/auth_stage.py",
    "backend/services/upap/upload/upload_stage.py",
    "backend/services/upap/process/process_stage.py",
    "backend/services/upap/archive/archive_stage.py",
    "backend/services/upap/publish/publish_stage.py",
]

def clean_text(text):
    original = text

    # Remove literal PowerShell artifacts
    text = text.replace("\\n", "\n").replace("\\r", "\n")

    # Normalize spacing
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

    # Fix class header patterns broken by PowerShell
    text = re.sub(
        r"class\s+(\w+Stage):\\n", 
        r"class \1:\n    ", 
        text
    )
    text = re.sub(
        r"class\s+(\w+Stage):\s*", 
        r"class \1:\n    ", 
        text
    )

    # Fix run() signature uniformly
    text = re.sub(
        r"def run\(.*?\):",
        "def run(self, context: dict) -> dict:",
        text
    )

    return text if text != original else None


def fix_file(path):
    abs_path = os.path.join(PROJECT_ROOT, path)
    if not os.path.exists(abs_path):
        print(f"[SKIP] File not found: {path}")
        return

    with open(abs_path, "r", encoding="utf-8") as f:
        text = f.read()

    cleaned = clean_text(text)

    if cleaned:
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(cleaned)
        print(f"[FIXED] {path}")
    else:
        print(f"[OK] {path} already clean.")


print("\n=== CLEANING ALL UPAP STAGES ===\n")
for f in STAGE_FILES:
    fix_file(f)

print("\n=== DONE ===")
print("Run validation:")
print("python -m backend.services.upap.engine.upap_validation")
