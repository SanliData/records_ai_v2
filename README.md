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
```Access the application:
- **Home**: http://127.0.0.1:8000/ui/index.html
- **Upload**: http://127.0.0.1:8000/ui/upload.html
- **API Docs**: http://127.0.0.1:8000/docs---

## Frontend Pages### Anonymous Access (No Login Required)
- **Home** (`/ui/index.html`) - Explore UPAP platform
- **Upload & Analyze** (`/ui/upload.html`) - Upload and analyze records
- **Results Preview** (`/ui/results.html`) - View analysis results

### Authenticated Access (Login Required)
- **Archive Save** (`/ui/archive-save.html`) - Save records to personal archive
- **Library** (`/ui/library.html`) - View personal archive
- **Login** (`/ui/login.html`) - Sign in / Sign up

---## UPAP Pipeline ComplianceAll frontend pages use UPAP-compliant endpoints:

- **Upload**: `/upap/process/process/preview` (Upload → Process, preview mode)
- **Archive**: `/upap/archive/add` (Archive stage, requires auth)
- **Publish**: `/upap/publish` (Publish stage, requires archive)

See `UPAP_COMPATIBILITY_NOTES.md` for detailed UPAP compliance information.

---

## Production Deployment

- **Domain**: https://zyagrolia.com
- **API**: https://api.zyagrolia.com
- **Platform**: Google Cloud Run

See `DEPLOYMENT_STATUS.md` for deployment details and GitHub sync notes.
