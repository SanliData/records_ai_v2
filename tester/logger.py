from pathlib import Path
from datetime import datetime
import json

ERROR_LIB = Path(r"C:\Users\issan\records_ai_v2\error_library")
CANONICAL = ERROR_LIB / "canonical_errors.json"
OCCURRENCES = ERROR_LIB / "occurrences.log"


def log_event(stage, error, classification, suggestion, context):
    key = classification.get("error_type", "UNKNOWN_ERROR")

    data = json.loads(CANONICAL.read_text(encoding="utf-8"))

    if key not in data:
        data[key] = {
            "first_seen": datetime.utcnow().isoformat() + "Z",
            "description": classification.get("message"),
            "solutions": suggestion
        }
        CANONICAL.write_text(json.dumps(data, indent=2), encoding="utf-8")
    else:
        with OCCURRENCES.open("a", encoding="utf-8") as f:
            f.write(
                f"{key} {datetime.utcnow().isoformat()} "
                f"record_id={context.get('record_id')}\n"
            )
