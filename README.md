# records_ai_v2 (Records_AI v2)

Records_AI v2 is a FastAPI-based backend that runs an **UPAP-only** pipeline for ingest → process → archive → publish, with optional OCR/AI stages gated by configuration. The project is designed to run locally via Uvicorn, in Docker, and on Google Cloud Run.

---

## Status

- **Service:** `records_ai_v2`
- **Mode:** UPAP-only
- **Auto-fix:** Disabled by design (detect / classify / suggest only)
- **Primary entrypoint:** `backend/main.py` (`backend.main:app`)

---

## What is UPAP?

UPAP is the canonical pipeline in v2:

1. **Upload** (file intake)
2. **Process** (OCR / AI / feature extraction; gated)
3. **Archive** (persist canonical archive record)
4. **Publish** (make archive visible / queryable)

UPAP is treated as the **authoritative v2 flow**. Legacy layers may exist in the codebase, but new work should connect to UPAP.

---

## API

### Base path
Most routes are served under:

- ` /api/v1`

### Common endpoints (typical)
- `GET /api/v1/docs` (Swagger UI, if enabled)
- `POST /api/v1/upap/upload`
- Other UPAP routes are composed by the UPAP router modules under `backend/api/v1/`

> Note: `GET /` may return 404 by default unless explicitly added. Use `/api/v1/...` routes.

---

## Local Development (Windows / PowerShell)

From repository root:

```powershell
cd C:\Users\issan\records_ai_v2
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
