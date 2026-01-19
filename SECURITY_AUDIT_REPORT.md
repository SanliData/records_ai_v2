# Security Audit Report - records_ai_v2
**Date**: 2026-01-18
**Phase**: 1 - Security Hardening
**Status**: CRITICAL ISSUES FOUND

---

## EXECUTIVE SUMMARY

**CRITICAL**: Hardcoded secrets found in production code.
**HIGH**: Missing Secret Manager integration.
**MEDIUM**: OAuth Client ID hardcoded in frontend.

---

## FINDINGS

### 🔴 CRITICAL - Hardcoded Secrets

#### 1. Discogs API Token (EXPOSED)
**File**: `backend/services/vinyl_pricing_service.py:13`
**Issue**: Hardcoded API token with fallback value
```python
DISCOGS_TOKEN = os.getenv("DISCOGS_TOKEN", "LSZAwZzoglUrbLSkoyFijkxGqQfZ1RKMjyS6a")
```
**Risk**: Token is publicly visible in repository
**Action**: Remove fallback, require env var, migrate to Secret Manager

#### 2. Service Token (Hardcoded)
**Files**: 
- `backend/api/routes/oauth.py:6`
- `backend/api/routes/app.py:11`
**Issue**: Hardcoded bearer token for ChatGPT app integration
```python
SERVICE_TOKEN = "recordsai-chatgpt-app-token"
```
**Risk**: Weak authentication, predictable token
**Action**: Generate secure token, use env var or Secret Manager

#### 3. Suspicious Environment Variable Name
**File**: `backend/services/openai_client.py:20`
**Issue**: Environment variable name appears to be a secret
```python
api_key = os.getenv("proj_kC4kttheJQf0J7LL80C9Q5n0")
```
**Risk**: Confusing, not following standards
**Action**: Rename to `OPENAI_API_KEY`, use Secret Manager

---

### 🟡 MEDIUM - Configuration Issues

#### 4. OAuth Client ID in Frontend
**File**: `frontend/login.html:238`
**Issue**: Google OAuth Client ID hardcoded in HTML
```javascript
client_id: '969278596906-afqorvadshqquuhts4rpk0620dgg1fa4.apps.googleusercontent.com'
```
**Risk**: Client ID is public, but should be configurable
**Action**: Load from environment variable at build time or runtime config

---

### ✅ GOOD PRACTICES FOUND

1. `.gitignore` properly excludes secrets (`*.json`, `*.key`, `.env`)
2. Most API keys use `os.getenv()` without fallbacks
3. Database URL uses env var with SQLite fallback (acceptable for dev)

---

## REMEDIATION PLAN

### Task 1: Remove Hardcoded Secrets
- Remove fallback from `DISCOGS_TOKEN`
- Replace hardcoded `SERVICE_TOKEN` with env var
- Fix OpenAI env var naming

### Task 2: Implement Secret Manager Support
- Create secret loader utility
- Fail fast if required secrets missing
- Document required secrets

---

## RISK ASSESSMENT

| Issue | Severity | Impact | Exploitability | Priority |
|-------|----------|--------|----------------|----------|
| Discogs Token Exposed | CRITICAL | High | Easy | P0 |
| Service Token Hardcoded | HIGH | Medium | Medium | P1 |
| OpenAI Env Var Naming | MEDIUM | Low | Low | P2 |
| OAuth Client ID | LOW | Very Low | N/A | P3 |

---

## NEXT STEPS

1. ✅ Remove hardcoded secrets (this session)
2. ⏳ Implement Secret Manager (this session)
3. ⏳ Add secret validation at startup
4. ⏳ Document all required environment variables
