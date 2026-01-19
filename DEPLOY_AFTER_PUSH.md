# Deploy After Git Push

## 1. Git Push (Windows PowerShell)

```powershell
# Stage and commit
git add backend/main.py backend/api/v1/upap_upload_router.py backend/db.py backend/core/error_handler.py requirements.txt
git commit -m "fix: critical security and stability fixes - auth, rate limiting, data persistence"

# Push with token
git push https://SanliData:YOUR_GITHUB_TOKEN@github.com/SanliData/records_ai_v2.git main
```

## 2. Cloud Shell Deploy

After push succeeds, in Cloud Shell:

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

## 3. Verify Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe records-ai-v2 --region us-central1 --format="value(status.url)" --project records-ai)

# Test health
curl $SERVICE_URL/health

# Test root (should be HTML, not JSON)
curl -I $SERVICE_URL/

# Test upload without auth (should fail 401)
curl -X POST $SERVICE_URL/api/v1/upap/upload -F "file=@test.mp3" -F "email=test@example.com"
```

---

## Important: Set DATABASE_URL Before Deploy

The app will fail to start if DATABASE_URL is not set.

**Option 1: Cloud SQL (Recommended)**
```bash
# Set Cloud SQL connection string
gcloud run services update records-ai-v2 \
  --region us-central1 \
  --set-env-vars DATABASE_URL="postgresql://user:pass@host/dbname" \
  --project records-ai
```

**Option 2: Temporary SQLite (For Testing Only)**
```bash
# WARNING: Data will be lost on restart
gcloud run services update records-ai-v2 \
  --region us-central1 \
  --set-env-vars DATABASE_URL="sqlite:///./temp.db" \
  --project records-ai
```

---

## Expected Results

✅ App starts without errors
✅ `/health` returns `{"status":"ok"}`
✅ `/` returns HTML (not JSON)
✅ `/api/v1/upap/upload` requires authentication (401 without token)
