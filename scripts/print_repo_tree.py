"""
Print repository tree for records_ai_v2
ROLE: ROL-3
Purpose: Structural audit before router binding
Encoding: UTF-8
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXCLUDE_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules"
}


def print_tree(path: Path, prefix: str = ""):
    items = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    for index, item in enumerate(items):
        if item.name in EXCLUDE_DIRS:
            continue

        connector = "└── " if index == len(items) - 1 else "├── "
        print(prefix + connector + item.name)

        if item.is_dir():
            extension = "    " if index == len(items) - 1 else "│   "
            print_tree(item, prefix + extension)


def main():
    print(f"\n=== records_ai_v2 TREE @ {ROOT} ===\n")
    print_tree(ROOT)
    print("\n=== END TREE ===\n")


if __name__ == "__main__":
    main()
