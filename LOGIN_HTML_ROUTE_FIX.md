# LOGIN.HTML 404 FIX

## Problem
- User accessing `/login.html` gets 404 error
- Static files are mounted at `/ui/` only
- Frontend redirects to `login.html` (not `/ui/login.html`)

## Solution
Added explicit route handler for `/login.html` that serves `frontend/login.html`.

## Changes Made

**File:** `backend/main.py`

Added:
- `LOGIN_HTML` path definition (line ~133)
- Route handler `@app.get("/login.html")` (line ~137)

This serves `login.html` at both:
- `/login.html` (new route handler)
- `/ui/login.html` (via StaticFiles mount)

## Deployment

Commit and push:
```bash
git add backend/main.py
git commit -m "fix: add /login.html route handler to fix 404 error"
git push origin main
```

Then deploy:
```bash
gcloud run deploy records-ai-v2 --source . --region us-central1 --project records-ai --allow-unauthenticated --port 8080
```
