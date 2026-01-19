# 🚀 Cloud Run Deployment - Final Steps

## ✅ Completed
- ✅ Git push successful (commit: 80d2f44)
- ✅ Build fixes applied (defensive dependencies)
- ✅ All optional dependencies wrapped

## 📋 Deploy Commands

### Option 1: Google Cloud Shell (Recommended)

1. Open Cloud Shell: https://shell.cloud.google.com
2. Clone/pull latest code:
```bash
cd ~
git clone https://github.com/SanliData/records_ai_v2.git || cd records_ai_v2 && git pull origin main
cd records_ai_v2
```

3. Deploy:
```bash
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --max-instances 3 \
  --min-instances 0 \
  --timeout 300 \
  --memory 1Gi \
  --cpu 1 \
  --set-env-vars PORT=8080
```

### Option 2: Set Environment Variables (After Deploy)

If you need to set environment variables:

```bash
gcloud run services update records-ai-v2 \
  --region us-central1 \
  --update-env-vars \
    OPENAI_API_KEY="your-openai-key",\
    DISCOGS_TOKEN="your-discogs-token",\
    SECRET_KEY="your-jwt-secret",\
    DATABASE_URL="postgresql://user:pass@host/dbname"
```

### Option 3: One-Line Deploy (Cloud Shell)

```bash
cd ~/records_ai_v2 && git pull origin main && gcloud run deploy records-ai-v2 --source . --region us-central1 --allow-unauthenticated --port 8080
```

## ✅ Verify Deployment

After deployment completes:

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe records-ai-v2 \
  --region us-central1 \
  --format="value(status.url)")

echo "Service URL: $SERVICE_URL"

# Test health
curl $SERVICE_URL/health

# Test root
curl -I $SERVICE_URL/
```

## 📝 What's Deployed

- ✅ Recognition integration (Phase 1 complete)
- ✅ Defensive dependencies (build fixes)
- ✅ UPAP pipeline (100/100 validation)
- ✅ PostgreSQL + SQLAlchemy auth
- ✅ Marketplace API preparation (Phase 3 ready)

## 🔧 Troubleshooting

If build fails:
1. Check build logs: `gcloud builds list --limit=1`
2. View logs: `gcloud builds log <BUILD_ID>`
3. Check service logs: `gcloud run services logs read records-ai-v2 --region us-central1`

If app fails to start:
1. Check environment variables are set
2. Verify DATABASE_URL is correct
3. Check service logs for errors

## 🎯 Expected Result

- ✅ Build succeeds (no missing dependencies)
- ✅ App starts without errors
- ✅ `/health` returns `{"status":"ok"}`
- ✅ `/api/v1/upap/upload` requires authentication
- ✅ Recognition works (if OPENAI_API_KEY set)

---

**Ready to deploy!** Use Cloud Shell for best results.
