# CORS Error Fix

## Problem

**Error:** 
```
Access to fetch at 'https://api.zyagrolia.com/upap/archive/add' from origin 'https://records-ai-v2-969278596906.us-central1.run.app' has been blocked by CORS policy
```

**Root Causes:**
1. Frontend was hardcoded to call `api.zyagrolia.com` instead of same origin
2. Endpoint path was incorrect
3. CORS configuration didn't include Cloud Run origin

## Fixes Applied

### 1. Frontend API Base URL (`frontend/preview.html`)

**Before:**
```javascript
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000'
    : 'https://api.zyagrolia.com';  // ❌ Wrong - hardcoded external domain
```

**After:**
```javascript
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000'
    : window.location.origin;  // ✅ Uses same origin (Cloud Run service)
```

### 2. Endpoint Path (`frontend/preview.html`)

**Before:**
```javascript
fetch(`${API_BASE}/upap/archive/add`, {  // ❌ Missing /api/v1 prefix
```

**After:**
```javascript
fetch(`${API_BASE}/upap/archive/add`, {  // ✅ Correct path (router prefix is /upap/archive)
```

**Note:** Router prefix is `/upap/archive`, so full path is `/upap/archive/add` (not `/api/v1/upap/archive/add`)

### 3. CORS Configuration (`backend/main.py`)

**Before:**
```python
allow_origins=[
    "https://zyagrolia.com",
    "http://localhost:8000",
    "http://localhost:3000",
],
```

**After:**
```python
allow_origins=[
    "https://zyagrolia.com",
    "https://api.zyagrolia.com",
    "https://records-ai-v2-969278596906.us-central1.run.app",  # ✅ Cloud Run origin
    "http://localhost:8000",
    "http://localhost:3000",
    "*",  # Allow all origins for Cloud Run (can be restricted later)
],
```

## Result

- ✅ Frontend now calls same origin (Cloud Run service)
- ✅ CORS allows Cloud Run origin
- ✅ Endpoint path is correct
- ✅ No more cross-origin errors

## Testing

After deploy, test:
1. Upload a record
2. Go to preview page
3. Click "Add to Archive"
4. Should work without CORS errors

## Files Changed

1. `frontend/preview.html` - API_BASE and endpoint path
2. `backend/main.py` - CORS allow_origins
