# Deploy to Cloud Run - Recognition Integration

## ✅ Git Push Complete
- All changes pushed to `origin/main`
- Token secrets removed from codebase
- Recognition integration ready for deployment

## 🚀 Cloud Run Deploy Commands

### Option 1: Deploy from Local (Recommended)

```bash
# Set project
gcloud config set project records-ai

# Deploy from source
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
  --set-env-vars OPENAI_API_KEY="your-openai-key" \
  --set-env-vars DISCOGS_TOKEN="your-discogs-token" \
  --set-env-vars SECRET_KEY="your-jwt-secret" \
  --set-env-vars DATABASE_URL="your-postgres-url"
```

### Option 2: Deploy from Cloud Shell

```bash
# Clone/pull latest
cd ~/records_ai_v2
git pull origin main

# Deploy
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
  --cpu 1
```

### Option 3: Build and Deploy Image

```bash
# Build image
gcloud builds submit --tag gcr.io/records-ai/records-ai-v2

# Deploy
gcloud run deploy records-ai-v2 \
  --image gcr.io/records-ai/records-ai-v2 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080
```

## 📋 Required Environment Variables

Set these before or after deployment:

```bash
gcloud run services update records-ai-v2 \
  --region us-central1 \
  --update-env-vars \
    OPENAI_API_KEY="your-openai-key",\
    DISCOGS_TOKEN="your-discogs-token",\
    SECRET_KEY="your-jwt-secret",\
    DATABASE_URL="postgresql://user:pass@host/dbname"
```

## ✅ Verify Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe records-ai-v2 \
  --region us-central1 \
  --format="value(status.url)")

echo "Service URL: $SERVICE_URL"

# Test health
curl $SERVICE_URL/health

# Test recognition (requires auth token)
curl -X POST $SERVICE_URL/api/v1/upap/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test_image.jpg" \
  -F "email=test@example.com"
```

## 🎯 What's New

- ✅ Recognition integration in upload flow
- ✅ Real artist/album/label extraction
- ✅ Marketplace API preparation (Phase 3 ready)
- ✅ Architectural alignment complete

## 📝 Notes

- Large file warning: `records_ai_v2.zip` (60MB) - consider removing or using Git LFS
- Database: Ensure PostgreSQL connection string is set
- OpenAI API: Required for recognition to work
- Discogs API: Required for pricing service
