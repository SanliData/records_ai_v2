#!/bin/bash
# Deploy to Cloud Run via Cloud Shell
# Run this in Google Cloud Shell

cd ~/records_ai_v2 || (git clone https://github.com/SanliData/records_ai_v2.git && cd records_ai_v2)

# Pull latest changes
git pull origin main

# Set project
gcloud config set project records-ai

# Deploy to Cloud Run
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

echo ""
echo "=== Deployment Complete ==="
echo "Service URL: https://records-ai-v2-969278596906.us-central1.run.app"
