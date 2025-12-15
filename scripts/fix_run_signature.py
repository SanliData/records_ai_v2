import os
import re

# Stage file paths
STAGE_FILES = [
    "backend/services/upap/auth/auth_stage.py",
    "backend/services/upap/upload/upload_stage.py",
    "backend/services/upap/process/process_stage.py",
    "backend/services/upap/archive/archive_stage.py",
    "backend/services/upap/publish/publish_stage.py",
]

print("\n=== FIXING run() SIGNATURES (Python Patch) ===\n")

BASE = os.getcwd()

for relative_path in STAGE_FILES:
    full_path = os.path.join(BASE, relative_path)

    if not os.path.exists(full_path):
        print(f"[SKIP] File not found: {relative_path}")
        continue

    print(f"[PATCH] Fixing: {relative_path}")

    with open(full_path, "r", encoding="utf-8") as f:
        text = f.read()

    original_text = text

    # Remove chained return types like -> dict -> Dict[str, Any]
    text = re.sub(r"->\s*dict\s*->\s*Dict\[str,\s*Any\]", "-> dict", text)

    # Remove ANY double return type "-> X -> Y"
    text = re.sub(r"->\s*[^:\n]+->\s*[^:\n]+", "-> dict", text)

    # Force correct signature
    text = re.sub(
        r"def\s+run\s*\([^\)]*\)\s*->\s*[^:]+:",
        "def run(self, context: dict) -> dict:",
        text
    )

    if text != original_text:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"[OK] Patched successfully.")
    else:
        print(f"[OK] Already correct.")

print("\n=== DONE ===")
print("Now run again:")
print("python -m backend.services.upap.engine.upap_validation\n")
