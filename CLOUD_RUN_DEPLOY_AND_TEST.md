# Cloud Run Deploy and Test Commands

## 1. Deploy to Cloud Run

```bash
# In Cloud Shell
cd ~/records_ai_v2
git pull origin main

gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --project records-ai
```

## 2. Get Service URL

```bash
SERVICE_URL=$(gcloud run services describe records-ai-v2 \
  --region us-central1 \
  --project records-ai \
  --format="value(status.url)")

echo "Service URL: $SERVICE_URL"
```

## 3. Test Health Endpoint (Should return JSON)

```bash
curl $SERVICE_URL/health
```

**Expected output:**
```json
{"status":"ok"}
```

## 4. Test Root Endpoint (Should return HTML or clear error)

```bash
# Check headers
curl -I $SERVICE_URL/

# Get full response
curl $SERVICE_URL/
```

**Expected:**
- **Success:** HTML content with `Content-Type: text/html`
- **Failure:** JSON error with resolved paths (if file missing)

## 5. Check Logs for Path Information

```bash
gcloud run logs read records-ai-v2 \
  --region us-central1 \
  --limit 50 \
  --project records-ai
```

Look for startup logs:
```
REPO_ROOT: /workspace
FRONTEND_DIR: /workspace/frontend (exists: True/False)
UPLOAD_HTML: /workspace/frontend/upload.html (exists: True/False)
```

## 6. Verify UI is Served

```bash
# Should show HTML
curl -s $SERVICE_URL/ | head -20

# Should return index.html
curl -I $SERVICE_URL/ui/upload.html
```

---

## Troubleshooting

If root returns JSON error:
1. Check logs for "UPLOAD_HTML not found"
2. Verify `frontend/upload.html` exists in repository
3. Check `.gcloudignore` doesn't exclude `frontend/`
4. Verify build completed successfully

If health endpoint fails:
- Check Cloud Run revision is healthy
- Check startup logs for exceptions
