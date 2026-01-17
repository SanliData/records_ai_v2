# UPAP v1 — Archive Stage Lock
Design Decision Record (DDR-UPAP-001)

**Status:** Binding / Irreversible  
**Last Updated:** 2025-12-13

---

## Overview

The UPAP (Upload → Process → Archive → Publish) pipeline enforces an immutable order of stages. The Archive stage is a critical checkpoint that requires authentication and must occur after Process and before Publish.

---

## Pipeline Order (Immutable)

```
Upload → Process → Archive → Publish
```

This order cannot be changed. Each stage depends on the previous one.

---

## Stage Details

### 1. Upload
- **Purpose:** File intake and storage
- **Authentication:** Optional (anonymous allowed for preview)
- **Endpoint:** `/upap/upload` (full) or `/upap/process/process/preview` (preview mode)
- **Output:** File stored, record_id generated

### 2. Process
- **Purpose:** OCR, AI analysis, feature extraction
- **Authentication:** Optional (runs in preview mode for anonymous users)
- **Dependencies:** Requires Upload stage completion
- **Optional Components:** OCR and AI stages (ENV gated)

### 3. Archive
- **Purpose:** Persist canonical archive record
- **Authentication:** **REQUIRED** (cannot be bypassed)
- **Dependencies:** Requires Upload and Process completion
- **Endpoint:** `/upap/archive/add`
- **Lock:** Archive stage is locked until authentication is provided

### 4. Publish
- **Purpose:** Make archive record visible and queryable
- **Authentication:** Required (inherits from Archive)
- **Dependencies:** Requires Archive stage completion
- **Endpoint:** `/upap/publish`
- **Validation:** PublishStage verifies Archive completion before execution

---

## Archive Stage Lock Mechanism

The Archive stage implements a lock mechanism:

1. **Preview Mode:** Upload + Process can run anonymously
2. **Archive Lock:** Archive stage requires authentication
3. **Validation:** `PublishStage` verifies `is_archived(record_id)` before execution

### Implementation

```python
# backend/services/upap/publish/publish_stage.py
def run(self, context: dict):
    record_id = context["record_id"]
    
    if not is_archived(record_id):
        raise ValueError("Record must be archived before publish")
    
    return {
        "status": "ok",
        "stage": "publish",
        "record_id": record_id
    }
```

---

## Frontend Integration

### Anonymous Flow
- **Upload & Analyze:** `/upap/process/process/preview`
- **View Results:** Preview records displayed without authentication
- **Save to Archive:** Redirects to login page

### Authenticated Flow
- **Archive Save:** `/upap/archive/add` (requires auth token)
- **Publish:** `/upap/publish` (requires archived record)

---

## Current Status (2025-12-13)

### UPAP Pipeline
- ✅ All core stages implemented and validated
- ✅ Archive stage lock enforced
- ✅ Publish stage validation active
- ⚠️ Optional OCR/AI stages disabled (ENV gated)

### Frontend Compliance
- ✅ All pages use UPAP-compliant endpoints
- ✅ Anonymous access for Upload + Process
- ✅ Authentication gate at Archive stage
- ✅ Clear separation between preview and archive flows

---

## Future Considerations

### UPAP as Separate Service

When UPAP becomes an independent service:

1. **Frontend Changes:**
   - UPAP service URL from environment variable
   - Direct API calls to UPAP service
   - Authentication token forwarding

2. **Backend Changes:**
   - UPAP service client wrapper
   - Service discovery configuration
   - Token forwarding mechanism

3. **Migration Checklist:**
   - [ ] UPAP service URL environment variable
   - [ ] Frontend config system
   - [ ] Backend UPAP client
   - [ ] Test endpoints migration
   - [ ] Documentation update

---

## Compliance

This DDR is binding and cannot be reversed. All implementations must respect:

1. Pipeline order: Upload → Process → Archive → Publish
2. Archive stage authentication requirement
3. Publish stage archive validation
4. Preview mode limitation (Upload + Process only)

---

## References- `backend/services/upap/engine/upap_engine.py` - UPAP Engine implementation
- `backend/services/upap/archive/archive_stage.py` - Archive stage
- `backend/services/upap/publish/publish_stage.py` - Publish stage validation
- `UPAP_COMPATIBILITY_NOTES.md` - UPAP compliance documentation
- `DEPLOYMENT_STATUS.md` - Current deployment status
