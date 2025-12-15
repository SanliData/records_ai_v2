import os
import shutil

# --------------------------------------
# CONFIG
# --------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DELETE_PATHS = [
    # Old routers / API
    "backend/routes",
    "backend/analyze",
    "backend/analysis",
    "backend/api/v1/archive_router.py",
    "backend/api/v1/records_api.py",

    # Old services
    "backend/services/record_pipeline.py",
    "backend/services/popsike_client.py",
    "backend/services/discogs_client.py",
    "backend/services/musicbrainz_client.py",
    "backend/services/cover_search.py",
    "backend/services/matrix_decoder.py",
    "backend/services/runout_matcher.py",
    "backend/services/fingerprint.py",
    "backend/services/batch_importer.py",
    "backend/services/archive",
    "backend/services/archive_manager.py",
    "backend/services/archive_manager_service.py",
    "backend/services/analytics_engine.py",
    "backend/services/vinyl_cache.py",
    "backend/services/test_ai_client.py",

    # Old utils
    "backend/scan_and_fix_imports.py",
    "backend/fixer.py",
    "backend/old",
    "backend/tmp",
]

SAFE_DIRECTORIES = {
    "backend/services": [
        "ocr_engine.py",
        "vision_engine.py",
        "metadata_engine.py",
        "analysis_service.py",
        "__init__.py",
    ],
    "backend/api/v1": [
        "analyze_record.py",
        "__init__.py",
    ],
    "backend/core": [
        "router_bus.py",
        "service_bus.py",
        "__init__.py",
    ],
}


# --------------------------------------
# Helpers
# --------------------------------------

def safe_delete(path):
    full_path = os.path.join(PROJECT_ROOT, path)
    if not os.path.exists(full_path):
        return

    try:
        if os.path.isfile(full_path):
            os.remove(full_path)
            print(f"🗑️ Removed file: {path}")
        else:
            shutil.rmtree(full_path)
            print(f"🗑️ Removed folder: {path}")
    except Exception as e:
        print(f"⚠️ Could not delete {path}: {e}")


def clean_directory(directory, allowed_files):
    """
    Ensures the directory only contains allowed files.
    Everything else is deleted.
    """
    full_dir = os.path.join(PROJECT_ROOT, directory)
    if not os.path.isdir(full_dir):
        return

    for filename in os.listdir(full_dir):
        if filename not in allowed_files:
            path = os.path.join(directory, filename)
            safe_delete(path)


# --------------------------------------
# MAIN CLEANUP
# --------------------------------------

print("\n🔍 Cleaning v1 leftovers...\n")

for path in DELETE_PATHS:
    safe_delete(path)

print("\n🧹 Ensuring directories only contain v2 modules...\n")

for directory, allowed_files in SAFE_DIRECTORIES.items():
    clean_directory(directory, allowed_files)

print("\n✅ CLEANUP COMPLETE — v2 architecture is clean and stable!\n")
