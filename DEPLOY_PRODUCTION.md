# Production Deployment Guide

## ✅ Pre-Deployment Checklist

- [x] All changes committed to Git
- [x] Dependencies verified (numpy, email-validator in requirements.txt)
- [x] Safe imports implemented (numpy with fallback)
- [x] Sensitive files excluded from Git (.gitignore updated)
- [x] Application tested locally (health endpoint working)

---

## 🚀 Cloud Run Deployment

### Option 1: Cloud Shell Script (Recommended)

```bash
# In Google Cloud Shell
bash CLOUDSHELL_DEPLOY_MANUAL.sh
```

### Option 2: Manual Commands

```bash
# 1. Set project
gcloud config set project records-ai

# 2. Verify authentication
gcloud auth list

# 3. Deploy
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --max-instances 10 \
  --min-instances 0 \
  --timeout 300 \
  --memory 1Gi \
  --cpu 1 \
  --set-env-vars GOOGLE_ENTRYPOINT="uvicorn backend.main:app --host 0.0.0.0 --port \$PORT"
```

---

## 🔧 Required Environment Variables

After deployment, set these in Cloud Run:

```bash
# Set environment variables
gcloud run services update records-ai-v2 \
  --region us-central1 \
  --set-env-vars \
    OPENAI_API_KEY=your_openai_key_here,\
    DISCOGS_TOKEN=your_discogs_token_here,\
    DATABASE_URL=your_postgresql_url_here,\
    ENVIRONMENT=production
```

**Or use Secret Manager (Recommended):**

```bash
# Create secrets
echo -n "your_openai_key" | gcloud secrets create openai-api-key --data-file=-
echo -n "your_discogs_token" | gcloud secrets create discogs-token --data-file=-
echo -n "your_postgresql_url" | gcloud secrets create database-url --data-file=-

# Grant access
PROJECT_NUMBER=$(gcloud projects describe records-ai --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Update service to use secrets
gcloud run services update records-ai-v2 \
  --region us-central1 \
  --update-secrets \
    OPENAI_API_KEY=openai-api-key:latest,\
    DISCOGS_TOKEN=discogs-token:latest,\
    DATABASE_URL=database-url:latest
```

---

## ✅ Post-Deployment Verification

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe records-ai-v2 \
  --region us-central1 \
  --format="value(status.url)")

# Test health endpoint
curl $SERVICE_URL/health

# Expected: {"status":"ok"}
```

---

## 📋 Service Information

- **Project:** records-ai
- **Service:** records-ai-v2
- **Region:** us-central1
- **URL:** https://records-ai-v2-969278596906.us-central1.run.app

---

## 🔍 Troubleshooting

### Build Fails
- Check Cloud Build logs: `gcloud builds list --limit=1`
- Verify `main.py` exists in root
- Check `requirements.txt` for all dependencies

### Runtime Errors
- Check Cloud Run logs: `gcloud run services logs read records-ai-v2 --region us-central1`
- Verify environment variables are set
- Check database connection string

### Import Errors
- Verify all dependencies in `requirements.txt`
- Check Python version compatibility
- Review build logs for missing packages
