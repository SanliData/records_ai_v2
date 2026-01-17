# Google Cloud Run Deployment Commands
Last Updated: 2026-01-05

## Quick Deploy

### Option 1: Using PowerShell Script (Recommended)
```powershell
.\deploy_to_cloud_run.ps1
```

### Option 2: Manual Deployment

#### 1. Authenticate
```powershell
gcloud auth login
gcloud config set project records-ai
```

#### 2. Enable Required APIs
```powershell
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

#### 3. Deploy from Source (Recommended)
```powershell
gcloud run deploy records-ai-v2 `
  --source . `
  --platform managed `
  --region europe-west1 `
  --allow-unauthenticated `
  --port 8080 `
  --project records-ai
```

#### 4. Alternative: Deploy with Docker Image

Build and push:
```powershell
# Build Docker image
docker build -t gcr.io/records-ai/records-ai-v2:latest .

# Push to Google Container Registry
docker push gcr.io/records-ai/records-ai-v2:latest

# Deploy
gcloud run deploy records-ai-v2 `
  --image gcr.io/records-ai/records-ai-v2:latest `
  --platform managed `
  --region europe-west1 `
  --allow-unauthenticated `
  --port 8080
```

## Check Deployment Status

```powershell
# Get service URL
gcloud run services describe records-ai-v2 --region europe-west1 --format "value(status.url)"

# View logs
gcloud run logs read records-ai-v2 --region europe-west1 --limit 50

# List all revisions
gcloud run revisions list --service records-ai-v2 --region europe-west1
```

## Environment Variables

To add environment variables during deployment:

```powershell
gcloud run deploy records-ai-v2 `
  --source . `
  --region europe-west1 `
  --set-env-vars "UPAP_ENABLE_OCR=false,UPAP_ENABLE_AI=false" `
  --allow-unauthenticated
```

## Update Existing Service

```powershell
gcloud run services update records-ai-v2 `
  --region europe-west1 `
  --update-env-vars "KEY=value"
```

## Troubleshooting

### Authentication Error
```powershell
gcloud auth login
gcloud config set account YOUR_EMAIL@example.com
```

### Build Failures
- Check `dockerfile` syntax
- Verify `requirements.txt` is correct
- Check Cloud Build logs in console

### Service Not Accessible
- Check IAM permissions: `gcloud run services get-iam-policy records-ai-v2 --region europe-west1`
- Verify `--allow-unauthenticated` flag is set
- Check domain mapping if using custom domain

### View Logs
```powershell
# Real-time logs
gcloud run logs tail records-ai-v2 --region europe-west1

# Recent logs
gcloud run logs read records-ai-v2 --region europe-west1 --limit 100
```

## Post-Deployment Checklist

- [ ] Service URL is accessible
- [ ] Health endpoint returns 200: `https://[SERVICE_URL]/health`
- [ ] Frontend pages load: `/ui/index.html`, `/ui/upload.html`
- [ ] API endpoints work: `/upap/process/process/preview`
- [ ] Browser cache cleared (hard refresh)
- [ ] Test anonymous upload flow
- [ ] Test authentication flow
- [ ] Check Cloud Run logs for errors

## Service URLs

After deployment, your service will be available at:
- **Service URL**: `https://records-ai-v2-[HASH].europe-west1.run.app`
- **Custom Domain** (if configured): `zyagrolia.com`

## Rollback

If deployment fails, you can rollback to previous revision:

```powershell
# List revisions
gcloud run revisions list --service records-ai-v2 --region europe-west1

# Rollback to specific revision
gcloud run services update-traffic records-ai-v2 `
  --region europe-west1 `
  --to-revisions REVISION_NAME=100
```



