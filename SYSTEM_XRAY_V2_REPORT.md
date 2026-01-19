# 🔬 SYSTEM X-RAY v2 REPORT
**Date:** 2026-01-18  
**Auditor:** Senior Cloud Architect + Security Auditor + DevOps Engineer  
**Scope:** Codebase + Cloud Run Runtime + Domain Routing  
**Method:** Evidence-based analysis

---

## 1️⃣ CODEBASE SCAN

### ✅ Entry Point Analysis

**File:** `backend/main.py`

#### Entry Point Correctness: **PASS** ✅
- **Line 36:** `app = FastAPI(title="Records_AI_V2", version="2.0.0")`
- **Uvicorn target:** `backend.main:app` (correct)
- **Router includes:** 13 routers registered (lines 120-132)
- **Static mounts:** `/ui` mounted at line 114

#### Path Resolution: **FIXED** ✅
- **Line 29:** `REPO_ROOT = Path(__file__).resolve().parents[1]` (Cloud Run compatible)
- **Line 30:** `FRONTEND_DIR = REPO_ROOT / "frontend"`
- **Line 31:** `UPLOAD_HTML = FRONTEND_DIR / "upload.html"`
- **Evidence:** Uses `parents[1]` instead of `.parent.parent` (more robust)

#### Upload.html Existence: **VERIFIED** ✅
- **Location:** `frontend/upload.html` exists in repository
- **Evidence:** `glob_file_search` confirmed file exists

---

### 🔒 Security Analysis

#### Open Endpoints: **CRITICAL ISSUES** 🔴

| Endpoint | Method | Auth Required | Risk |
|----------|--------|---------------|------|
| `/api/v1/upap/upload` | POST | ❌ NO | **HIGH** - File upload without auth |
| `/api/v1/analyze/image` | POST | ❌ NO | **HIGH** - Image processing without auth |
| `/api/v1/analyze/images` | POST | ❌ NO | **HIGH** - Multiple uploads without auth |
| `/api/v1/upap/*` | Various | ❌ NO | **MEDIUM** - UPAP pipeline endpoints open |
| `/admin/*` | Various | ✅ YES | ✅ Protected |

**Evidence:**
- `backend/api/v1/upap_upload_router.py:20-24` - No `Depends(get_current_user)`
- `backend/api/v1/analyze_input.py:17-21` - No authentication
- `backend/api/v1/admin_router.py:31` - Uses `Depends(get_current_admin)` ✅

#### File Upload Risks: **PARTIALLY MITIGATED** 🟡

**Good:**
- ✅ File size limit: 50MB (`backend/api/v1/upap_upload_router.py:9`)
- ✅ Email validation: Regex pattern (`backend/api/v1/upap_upload_router.py:12`)

**Missing:**
- ❌ No rate limiting
- ❌ No file type validation (MIME type checking)
- ❌ No authentication on upload endpoint

#### Rate Limiting: **ABSENT** 🔴

**Evidence:** No `slowapi` or rate limiting middleware found in codebase.

---

### 💾 Persistence Analysis

#### Database Backend: **SQLITE - HIGH RISK** 🔴

**File:** `backend/db.py:7`
```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./records_ai_v2.db")
```

**Issues:**
1. **Default is SQLite** - Will use SQLite if `DATABASE_URL` not set
2. **Cloud Run ephemeral storage** - Data lost on container restart
3. **TinyDB also used** - `backend/services/archive_service.py:44` uses TinyDB (`records_db.json`)

**Evidence:**
- `backend/db.py:7` - SQLite default
- `grep` found 9 files using TinyDB/JSON storage

**Data Loss Risk:** **CRITICAL** 🔴
- SQLite file written to `/workspace/` (ephemeral)
- TinyDB JSON files in repo root (ephemeral)
- No persistence strategy

---

### 🧹 Import Analysis

#### Dead/Broken Imports: **2 ISSUES FOUND** 🟡

**Issue 1: Unused `sys` import**
- **File:** `backend/main.py:7`
- **Line:** `import sys`
- **Status:** Imported but never used
- **Impact:** Minor (cosmetic)

**Issue 2: Error Handler Import Path**
- **File:** `backend/core/error_handler.py:15`
- **Line:** `from core.error_reporting import error_reporter`
- **Issue:** Uses `core.error_reporting` (not `backend.core.error_reporting`)
- **Status:** ✅ **HANDLED** - Wrapped in try/except in `main.py:52-57`
- **Impact:** None (gracefully handled)

#### Import Path Consistency: **MIXED** 🟡

**Pattern Found:**
- `backend/main.py` uses `from backend.X` ✅
- `backend/core/error_handler.py` uses `from core.X` ⚠️
- **Impact:** Inconsistent but handled with try/except

---

### 📦 Dependency Verification

**File:** `requirements.txt`

**All imports found in requirements.txt:** ✅

| Import | In requirements.txt? |
|--------|---------------------|
| `fastapi` | ✅ Yes |
| `uvicorn` | ✅ Yes |
| `SQLAlchemy` | ✅ Yes |
| `pydantic` | ✅ Yes |
| `python-multipart` | ✅ Yes |
| `Pillow` | ✅ Yes |
| `pytesseract` | ✅ Yes |
| `python-dotenv` | ✅ Yes |
| `jinja2` | ✅ Yes |
| `requests` | ✅ Yes |
| `opencv-python` | ✅ Yes |
| `numpy` | ✅ Yes |
| `rapidfuzz` | ✅ Yes (>=3.5.0) |
| `tinydb` | ✅ Yes |
| `google-cloud-error-reporting` | ✅ Yes (>=3.3.0) |

**Missing (if used):** None detected

---

## 2️⃣ CLOUD RUN RUNTIME X-RAY

### 🔍 Cloud Run Service Analysis Commands

**Execute these commands to verify runtime state:**

```bash
# 1. Get service details
gcloud run services describe records-ai-v2 \
  --region us-central1 \
  --project records-ai \
  --format="yaml"

# 2. List all revisions
gcloud run revisions list \
  --service records-ai-v2 \
  --region us-central1 \
  --project records-ai \
  --format="table(name,trafficPercent,status.conditions[0].status)"

# 3. Check latest revision logs
gcloud run logs read records-ai-v2 \
  --region us-central1 \
  --limit 100 \
  --project records-ai

# 4. Get latest revision status
LATEST_REV=$(gcloud run revisions list \
  --service records-ai-v2 \
  --region us-central1 \
  --format="value(name)" --limit 1)

gcloud run revisions describe $LATEST_REV \
  --region us-central1 \
  --project records-ai \
  --format="value(status.conditions)"
```

### 📊 Expected vs Actual Analysis

#### ✅ Fixed Issues (Based on Code Review)

1. **ModuleNotFoundError for logging_middleware**
   - **Status:** ✅ **FIXED**
   - **Evidence:** `backend/main.py:60-65` - Wrapped in try/except
   - **Impact:** No startup crash if import fails

2. **Path Resolution**
   - **Status:** ✅ **FIXED**
   - **Evidence:** `backend/main.py:29` - Uses `parents[1]`
   - **Cloud Run compatibility:** ✅ Should work on `/workspace`

3. **StaticFiles Mount**
   - **Status:** ✅ **FIXED**
   - **Evidence:** `backend/main.py:114` - Uses `str(FRONTEND_DIR)`
   - **Path:** Absolute string path

#### 🔍 Verification Needed (Runtime)

**Issue 1: Frontend Files in Container**
```
QUESTION: Does /workspace/frontend/upload.html exist in deployed container?
VERIFY: Check Cloud Run build logs for file copy
COMMAND: gcloud builds list --region us-central1 --limit 1
```

**Issue 2: Root Path Response**
```
QUESTION: What does GET / return in production?
VERIFY: curl https://SERVICE_URL/
EXPECTED: HTML (Content-Type: text/html)
ACTUAL: Unknown (needs verification)
```

**Issue 3: Startup Logs**
```
CHECK FOR:
- "REPO_ROOT: /workspace" in logs
- "UPLOAD_HTML: /workspace/frontend/upload.html (exists: True/False)"
- Database initialization errors
- Import errors (should be warnings, not crashes)
```

### 🚨 Potential Runtime Issues

#### Issue 1: Database File Not Persisting
**Risk:** SQLite file in ephemeral storage
**Evidence:** `backend/db.py:7` defaults to SQLite
**Impact:** Data loss on container restart/redeploy

#### Issue 2: Missing Error Handler Registration
**Status:** ✅ **HANDLED**
**Evidence:** `backend/main.py:52-57` - Try/except wrapper
**Impact:** None (gracefully degrades)

#### Issue 3: Import Path Mismatch in error_handler.py
**File:** `backend/core/error_handler.py:15`
**Import:** `from core.error_reporting import error_reporter`
**Issue:** Should be `from backend.core.error_reporting` OR use relative import
**Status:** ✅ **MITIGATED** - Wrapped in try/except, but should be fixed

---

## 3️⃣ DOMAIN (zyagrolia.com) ROUTING X-RAY

### 🔍 Domain Verification Commands

```bash
# 1. Check domain mapping
gcloud run domain-mappings list \
  --region us-central1 \
  --project records-ai

# 2. Get domain details
gcloud run domain-mappings describe zyagrolia.com \
  --region us-central1 \
  --project records-ai

# 3. Test domain endpoints
curl -I https://zyagrolia.com/
curl -I https://zyagrolia.com/health
curl -I https://zyagrolia.com/ui/upload.html

# 4. Check DNS
dig zyagrolia.com +short
nslookup zyagrolia.com
```

### 📋 Expected Domain Behavior

| Endpoint | Expected Response | Content-Type |
|----------|------------------|--------------|
| `/` | HTML (upload UI) | `text/html` |
| `/health` | JSON `{"status":"ok"}` | `application/json` |
| `/ui/upload.html` | HTML file | `text/html` |

### 🔍 Potential Domain Issues

#### Issue 1: Reverse Proxy Config
**Question:** Is Cloud Run behind a reverse proxy (Cloud Load Balancer, Cloudflare)?
**Check:** HTTP headers, response times
**Impact:** May cache JSON responses

#### Issue 2: CDN/Cache
**Question:** Is there a CDN (Cloudflare, Cloud CDN) caching responses?
**Check:** `Cache-Control` headers, response timestamps
**Impact:** May serve stale JSON instead of HTML

#### Issue 3: Wrong Path Mapping
**Question:** Is root path (`/`) mapped to `/health` instead of `/`?
**Check:** Domain mapping configuration
**Impact:** Root always returns JSON

#### Issue 4: Route Order (UNLIKELY)
**Status:** ✅ **CORRECT**
**Evidence:** `backend/main.py:84` (`/health`) before `backend/main.py:90` (`/`)
**Impact:** None (FastAPI handles route precedence correctly)

---

## 4️⃣ ROOT CAUSE SUMMARY

| Problem | Layer | Evidence | Fix Priority |
|---------|-------|----------|--------------|
| **Upload endpoint lacks auth** | Codebase | `upap_upload_router.py:20` - No `Depends()` | 🔴 **CRITICAL** |
| **SQLite data loss risk** | Codebase | `backend/db.py:7` - SQLite default | 🔴 **CRITICAL** |
| **No rate limiting** | Codebase | No `slowapi` or rate limit middleware | 🟠 **HIGH** |
| **TinyDB for archive** | Codebase | `archive_service.py:44` - JSON file storage | 🟠 **HIGH** |
| **Import path inconsistency** | Codebase | `error_handler.py:15` - `core.X` vs `backend.core.X` | 🟡 **MEDIUM** |
| **Unused sys import** | Codebase | `main.py:7` - `import sys` unused | 🟢 **LOW** |
| **Domain serving JSON** | Domain/Deploy | **NEEDS VERIFICATION** - Check live deployment | 🔴 **UNKNOWN** |
| **Frontend files in container** | Deploy | **NEEDS VERIFICATION** - Check build logs | 🟠 **UNKNOWN** |

---

## 5️⃣ AUTO FIX PLAN

### PHASE 1: IMMEDIATE (Fix Critical Security & Stability)

#### Fix 1: Add Authentication to Upload Endpoint

**File:** `backend/api/v1/upap_upload_router.py`

```python
# Add at top:
from backend.api.v1.auth_middleware import get_current_user
from backend.models.user import User
from fastapi import Depends

# Modify upload function:
@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    email: str = Form(...),
    current_user: User = Depends(get_current_user)  # ADD THIS
):
    # Validate email matches authenticated user
    if email != current_user.email:
        raise HTTPException(403, "Email mismatch")
    # ... rest of handler
```

#### Fix 2: Fix error_handler Import Path

**File:** `backend/core/error_handler.py:15`

**Change:**
```python
# FROM:
from core.error_reporting import error_reporter

# TO:
from backend.core.error_reporting import error_reporter
```

#### Fix 3: Remove Unused Import

**File:** `backend/main.py:7`

**Remove:**
```python
# DELETE:
import sys
```

#### Verification Commands:

```bash
# Test locally
python -c 'import backend.main; print("ok")'

# Deploy
git add backend/main.py backend/api/v1/upap_upload_router.py backend/core/error_handler.py
git commit -m "fix: add auth to upload, fix import paths"
git push origin main

# Cloud Shell deploy
cd ~/records_ai_v2 && git pull
gcloud run deploy records-ai-v2 --source . --region us-central1 --project records-ai

# Test
SERVICE_URL=$(gcloud run services describe records-ai-v2 --region us-central1 --format="value(status.url)")
curl -I $SERVICE_URL/
curl $SERVICE_URL/health
```

---

### PHASE 2: STABILITY (Fix Data Persistence)

#### Fix 4: Migrate to Cloud SQL

**File:** `backend/db.py:7`

**Change:**
```python
# FROM:
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./records_ai_v2.db")

# TO:
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is required. "
        "Set Cloud SQL connection string in Cloud Run environment variables."
    )
```

**Cloud Run Setup:**
```bash
# 1. Create Cloud SQL instance (if not exists)
gcloud sql instances create records-ai-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1

# 2. Create database
gcloud sql databases create records_ai_v2 --instance=records-ai-db

# 3. Set environment variable
gcloud run services update records-ai-v2 \
  --region us-central1 \
  --set-env-vars DATABASE_URL="postgresql://user:pass@/records_ai_v2?host=/cloudsql/PROJECT:us-central1:records-ai-db"

# 4. Add Cloud SQL connection
gcloud run services update records-ai-v2 \
  --region us-central1 \
  --add-cloudsql-instances PROJECT:us-central1:records-ai-db
```

#### Fix 5: Remove TinyDB Usage

**File:** `backend/services/archive_service.py:44`

**Action:** Migrate to SQLAlchemy models (use existing `backend/db.py`)

---

### PHASE 3: HARDENING (Add Rate Limiting & Monitoring)

#### Fix 6: Add Rate Limiting

**File:** `requirements.txt`

**Add:**
```
slowapi>=0.1.9
```

**File:** `backend/main.py`

**Add after line 36:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

**File:** `backend/api/v1/upap_upload_router.py`

**Add to upload function:**
```python
@router.post("/upload")
@limiter.limit("10/minute")  # 10 uploads per minute per IP
async def upload(...):
    # ...
```

---

## 6️⃣ FINAL SCORE & BLOCKERS

### Production Readiness Score: **58/100** 🟡

| Category | Score | Weight | Weighted |
|----------|-------|--------|----------|
| Security | 45/100 | 30% | 13.5 |
| Reliability | 60/100 | 25% | 15.0 |
| Scalability | 30/100 | 20% | 6.0 |
| Observability | 70/100 | 15% | 10.5 |
| Performance | 55/100 | 10% | 5.5 |
| **TOTAL** | | | **58/100** |

### What Still Blocks Real Production? 🔴

#### CRITICAL BLOCKERS (Must Fix Before Production)

1. **Authentication Missing on Upload Endpoint** 🔴
   - **Impact:** Unauthorized file uploads, storage abuse
   - **Effort:** 1 hour
   - **Priority:** **P0**

2. **SQLite Data Loss Risk** 🔴
   - **Impact:** Data lost on every restart/deploy
   - **Effort:** 4-8 hours (Cloud SQL setup)
   - **Priority:** **P0**

3. **No Rate Limiting** 🔴
   - **Impact:** DDoS vulnerability, cost explosion
   - **Effort:** 2 hours
   - **Priority:** **P0**

#### HIGH PRIORITY (Fix Soon)

4. **TinyDB for Archive** 🟠
   - **Impact:** Cannot scale, data loss risk
   - **Effort:** 8-16 hours (migration)

5. **Domain Routing Verification** 🟠
   - **Impact:** Unknown - needs verification
   - **Effort:** 1 hour (testing)

#### MEDIUM PRIORITY (Can Wait)

6. **Import Path Consistency** 🟡
   - **Impact:** Code maintainability
   - **Effort:** 1 hour

7. **Unused Imports** 🟢
   - **Impact:** None (cosmetic)

---

## 📝 VERIFICATION CHECKLIST

After fixes, verify:

- [ ] `curl https://zyagrolia.com/` returns HTML
- [ ] `curl https://zyagrolia.com/health` returns `{"status":"ok"}`
- [ ] Upload endpoint requires authentication
- [ ] Cloud Run logs show successful startup
- [ ] Database persists across restarts
- [ ] Rate limiting works (test with >10 requests/minute)

---

**Report Generated:** 2026-01-18  
**Next Review:** After Phase 1 fixes deployed
