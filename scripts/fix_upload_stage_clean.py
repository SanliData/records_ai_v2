import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
FILE_PATH = os.path.join(PROJECT_ROOT, "backend/services/upap/upload/upload_stage.py")

print("Cleaning upload_stage.py ...")

with open(FILE_PATH, "r", encoding="utf-8") as f:
    text = f.read()

original = text

# 1) Remove literal \n and \r\n inside code
text = text.replace("\\n", "\n")
text = text.replace("\\r", "\n")

# 2) Fix class header indentation issues
text = re.sub(r"class\s+UploadStage:\s*", "class UploadStage:\n    ", text)

# 3) Ensure correct name attribute exists and is clean
text = re.sub(r"name\s*=\s*['\"]UploadStage['\"]", "name = 'UploadStage'", text)

# 4) Remove accidental duplicated indentation or symbols
text = re.sub(r"\n\s*\n\s*\n", "\n\n", text)

if text != original:
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write(text)
    print("✔ Fixed: upload_stage.py cleaned.")
else:
    print("No changes required.")

print("Now run:")
print("python -m backend.services.upap.engine.upap_validation")
