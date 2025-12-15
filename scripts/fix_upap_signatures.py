import os
import re

# scripts klasöründeyiz → project root bir üst klasör
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

STAGE_FILES = [
    "backend/services/upap/auth/auth_stage.py",
    "backend/services/upap/upload/upload_stage.py",
    "backend/services/upap/process/process_stage.py",
    "backend/services/upap/archive/archive_stage.py",
    "backend/services/upap/publish/publish_stage.py",
]

print("\n=== FIXING UPAP run() SIGNATURES ===\n")

for rel_path in STAGE_FILES:
    full_path = os.path.join(PROJECT_ROOT, rel_path)

    if not os.path.exists(full_path):
        print(f"[SKIP] File not found: {rel_path}")
        continue

    print(f"[PATCH] {rel_path}")

    with open(full_path, "r", encoding="utf-8") as f:
        text = f.read()

    original = text

    # Remove broken double return annotations
    text = re.sub(r"->\s*dict\s*->\s*Dict\[str,\s*Any\]", "-> dict", text)
    text = re.sub(r"->\s*[^:\n]+->\s*[^:\n]+", "-> dict", text)

    # Ensure correct signature
    text = re.sub(
        r"def\s+run\s*\([^\)]*\)\s*->\s*[^:]+:",
        "def run(self, context: dict) -> dict:",
        text
    )

    if text != original:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(text)
        print("[OK] Patched.")
    else:
        print("[OK] Already correct.")

print("\n=== DONE ===")
print("Next: python -m backend.services.upap.engine.upap_validation\n")
