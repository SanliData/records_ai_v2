# Deployment Commands & Verification - Post-Fix

## 1. Git Commit & Push

```powershell
# Add all changed files
git add backend/main.py
git add backend/api/v1/upap_upload_router.py
git add backend/db.py
git add backend/core/error_handler.py
git add requirements.txt

# Commit
git commit -m "fix: critical security and stability fixes - auth, rate limiting, data persistence"

# Push
git push origin main
```

## 2. Cloud Shell Deploy

```bash
cd ~/records_ai_v2
git pull origin main

gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --max-instances 3 \
  --min-instances 0 \
  --timeout 300 \
  --cpu-boost \
  --project records-ai
```

## 3. Verification Commands

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe records-ai-v2 \
  --region us-central1 \
  --project records-ai \
  --format="value(status.url)")

echo "Service URL: $SERVICE_URL"

# Test health endpoint (should return JSON)
curl $SERVICE_URL/health
# Expected: {"status":"ok"}

# Test root endpoint (should return HTML, NOT JSON)
curl -I $SERVICE_URL/
# Expected: Content-Type: text/html

curl $SERVICE_URL/ | head -20
# Expected: HTML content

# Test upload endpoint WITHOUT auth (should fail 401)
curl -X POST $SERVICE_URL/api/v1/upap/upload \
  -F "file=@test.mp3" \
  -F "email=test@example.com"
# Expected: 401 Unauthorized

# Test upload endpoint WITH auth (should work or fail on email mismatch)
# Note: Requires valid Bearer token
TOKEN="your_token_here"
curl -X POST $SERVICE_URL/api/v1/upap/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.mp3" \
  -F "email=user@example.com"
```

## 4. Security Checklist

- [x] Upload endpoint requires authentication
- [x] Email validation enforced
- [x] File size limit: 50MB
- [x] MIME type validation: audio only
- [x] Rate limiting: 5/min on upload, 20/min on analyze
- [x] SQLite fallback removed
- [x] Error handler import path fixed
- [x] Root endpoint always serves HTML

## 5. Startup Log Verification

```bash
# Check startup logs for path verification
gcloud run logs read records-ai-v2 \
  --region us-central1 \
  --limit 50 \
  --project records-ai | grep -E "STARTUP|REPO_ROOT|UPLOAD_HTML|FILE_EXISTS"
```

Expected logs:
```
STARTUP VERIFICATION
REPO_ROOT=/workspace
FRONTEND_DIR=/workspace/frontend
FRONTEND_DIR_EXISTS=True
UPLOAD_HTML_PATH=/workspace/frontend/upload.html
FILE_EXISTS=True
```
