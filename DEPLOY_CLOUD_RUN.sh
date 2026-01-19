#!/bin/bash
# Cloud Run Deployment Script
# Deploys records_ai_v2 to Google Cloud Run

set -e  # Exit on error

PROJECT_ID="records-ai"
SERVICE_NAME="records-ai-v2"
REGION="us-central1"

echo "=== Cloud Run Deployment ==="
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

# Set project
echo "Setting GCP project..."
gcloud config set project $PROJECT_ID

# Deploy from source
echo "Deploying from source..."
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080 \
  --max-instances 3 \
  --min-instances 0 \
  --timeout 300 \
  --memory 1Gi \
  --cpu 1 \
  --set-env-vars PORT=8080

# Get service URL
echo ""
echo "Getting service URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format="value(status.url)")

echo ""
echo "✅ Deployment complete!"
echo "Service URL: $SERVICE_URL"
echo ""
echo "Testing health endpoint..."
curl -s "$SERVICE_URL/health" | head -5
echo ""
echo "Done!"
