# Production Hardening Execution Plan
**Status**: In Progress
**Date**: 2026-01-18

## Phase 1: Bug Fixes (CRITICAL - BLOCKING)

### TASK 1: Fix merge conflicts in upload.html
**Status**: IN PROGRESS
**Issue**: File has 5 merge conflict blocks
**Solution**: Keep HEAD version (modern UI), remove conflict markers
**Risk**: LOW - HEAD version is more complete
**Action**: Manual clean-up required (file too large for automated fix)

### TASK 2: Fix API endpoint mismatch  
**Status**: PENDING
**Current State**:
- Backend: `/upload` (no prefix in router)
- Frontend: Calls `/api/v1/upap/upload` OR `/upap/process/process/preview`

**Options**:
1. Add prefix `/api/v1/upap` to backend router (matches frontend expectation)
2. Change frontend to use `/upload` (simpler, matches backend)

**Decision**: Option 1 - Add prefix to backend (maintains frontend compatibility)
**Risk**: MEDIUM - Need to ensure no other code depends on `/upload`

---

## Phase 2: Security Lock (HIGH PRIORITY)

### TASK 3: Enforce Secret Manager
**Status**: PARTIALLY COMPLETE
- ✅ Removed hardcoded secrets
- ⏳ Need to add GCP Secret Manager integration
- ⏳ Local dev fallback logic

### TASK 4: Clean Python cache
**Status**: READY
- `.gitignore` already excludes `__pycache__/` and `*.pyc`
- Need to remove existing cache files from repo

---

## Phase 3-5: Pending after Phase 1 complete

Will proceed after critical fixes are deployed.

---

## Execution Order
1. ✅ Fix API endpoint (backend prefix) - NON-BREAKING
2. ⏳ Manual clean upload.html (requires review)
3. ⏳ Secret Manager integration
4. ⏳ Observability
5. ⏳ Cloud hardening
