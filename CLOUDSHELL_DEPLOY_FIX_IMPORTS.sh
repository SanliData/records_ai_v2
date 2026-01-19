#!/bin/bash
# Cloud Shell deploy script - Import path fix
# Run this in Cloud Shell after push

set -e

echo "=== Pulling latest changes ==="
cd ~/records_ai_v2
git pull origin main

echo "=== Deploying to Cloud Run ==="
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --project records-ai

echo "=== Deployment complete ==="
echo "Check logs if startup fails:"
echo "gcloud run logs read records-ai-v2 --region us-central1 --limit 50 --project records-ai"
