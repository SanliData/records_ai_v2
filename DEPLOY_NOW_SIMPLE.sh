#!/bin/bash
# Simple Cloud Run Deploy
# Run this in Google Cloud Shell

set -e

echo "=== Deploying to Cloud Run ==="
echo ""

# Pull latest code
echo "1. Pulling latest code..."
cd ~/records_ai_v2 2>/dev/null || git clone https://github.com/SanliData/records_ai_v2.git ~/records_ai_v2 && cd ~/records_ai_v2
git pull origin main

# Set project
echo ""
echo "2. Setting GCP project..."
gcloud config set project records-ai

# Deploy
echo ""
echo "3. Deploying to Cloud Run..."
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

# Get URL
echo ""
echo "4. Getting service URL..."
SERVICE_URL=$(gcloud run services describe records-ai-v2 \
  --region us-central1 \
  --format="value(status.url)")

echo ""
echo "✅ Deployment complete!"
echo "Service URL: $SERVICE_URL"
echo ""
echo "Test: curl $SERVICE_URL/health"
