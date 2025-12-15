# UTF-8
# Automatically removes old imports referencing backend.models.types
# and rewrites them to correct imports.

import os
import re

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
TARGET_IMPORT = "backend.models.types"

# What we replace it with (based on your new architecture)
# ImageInfo / MetadataGuess / MergedMetadata are defined inside metadata_engine now
REPLACEMENT = "from backend.services.metadata_engine import ImageInfo, MetadataGuess, MergedMetadata"

def fix_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if TARGET_IMPORT not in content:
        return False

    new_content = re.sub(
        rf"from\s+{re.escape(TARGET_IMPORT)}\s+import\s+.*",
        REPLACEMENT,
        content,
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True


def scan_and_fix():
    changes = []

    for root, _, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                if fix_file(full_path):
                    changes.append(full_path)

    print("=== IMPORT REPAIR REPORT ===")
    if not changes:
        print("No files needed updating.")
    else:
        print("Fixed imports in:")
        for c in changes:
            print("  -", c)
    print("=== DONE ===")


if __name__ == "__main__":
    scan_and_fix()
