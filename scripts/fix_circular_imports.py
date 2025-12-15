# scripts/fix_circular_imports.py
# -*- coding: utf-8 -*-
"""
Automatically fixes circular imports for the Records_AI v2 router-hub architecture.

Rules:
1. api/v1/__init__.py must be empty.
2. No API router should import router_bus.
3. router_bus can import API routers, not the reverse.
4. Any illegal import is removed.

Safe, idempotent, repeatable.
"""

import os
import re

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TARGET_INIT = os.path.join(PROJECT_ROOT, "backend", "api", "v1", "__init__.py")

ILLEGAL_PATTERNS = [
    r"from\s+backend\.core\.router_bus\s+import\s+.*",
    r"import\s+backend\.core\.router_bus.*",
    r"from\s+backend\.api\.v1\s+import\s+.*",    # API init must not import routers
]


def clear_api_init():
    """Ensure api/v1/__init__.py is always empty (router hub requires it)."""
    print(f"[CLEAN] Resetting {TARGET_INIT}")
    with open(TARGET_INIT, "w", encoding="utf-8") as f:
        f.write("# API v1 package initializer (auto-cleaned)\n")


def remove_illegal_imports():
    """Scan backend folder and remove any illegal router_bus imports."""
    backend_dir = os.path.join(PROJECT_ROOT, "backend")
    print(f"[SCAN] Scanning for illegal imports in: {backend_dir}")

    for root, _, files in os.walk(backend_dir):
        for file in files:
            if not file.endswith(".py"):
                continue

            path = os.path.join(root, file)

            if "router_bus" in path.replace("\\", "/"):
                continue  # router_bus.py is allowed to import API routers

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            original = content

            for pattern in ILLEGAL_PATTERNS:
                content = re.sub(pattern, "", content)

            # Remove empty lines caused by stripping
            content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)

            if content != original:
                print(f"[FIX] Illegal imports removed → {path}")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)


def main():
    print("\n=== FIXING CIRCULAR IMPORTS ===")
    clear_api_init()
    remove_illegal_imports()
    print("=== DONE: Circular import system repaired ===\n")


if __name__ == "__main__":
    main()
