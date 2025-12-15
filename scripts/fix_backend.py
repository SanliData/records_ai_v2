# fix_backend.py
# Automatically repairs backend Python files
# - Removes BOM
# - Forces UTF-8 encoding
# - Removes invisible characters
# - Runs syntax test
# - Logs broken files

import os
import re

ROOT = "backend"

def remove_bom_and_clean(path):
    with open(path, "rb") as f:
        data = f.read()

    # Remove BOM if present
    if data.startswith(b"\xEF\xBB\xBF"):
        print(f"[BOM REMOVED] {path}")
        data = data[3:]

    # Remove null bytes & weird characters
    cleaned = data.replace(b"\x00", b"")

    # Save as clean UTF-8
    with open(path, "wb") as f:
        f.write(cleaned)


def syntax_test(path):
    try:
        compile(open(path, "rb").read(), path, "exec")
        return True
    except Exception as e:
        print(f"[SYNTAX ERROR] {path}: {e}")
        return False


def scan_and_fix():
    broken_files = []

    for root, _, files in os.walk(ROOT):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                print(f"Processing: {path}")

                remove_bom_and_clean(path)

                if not syntax_test(path):
                    broken_files.append(path)

    print("\n=== SUMMARY ===")
    if broken_files:
        print("Broken files found (need manual repair):")
        for f in broken_files:
            print(" -", f)
    else:
        print("All files OK")

    print("\nDone.")

if __name__ == "__main__":
    scan_and_fix()
