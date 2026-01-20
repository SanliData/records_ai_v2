#!/bin/bash
# Final Production Deploy Script
# Run in Google Cloud Shell

set -e

PROJECT_ID="records-ai"
SERVICE_NAME="records-ai-v2"
REGION="us-central1"

echo "========================================"
echo "Records AI V2 - Production Deploy"
echo "========================================"
echo ""

# Step 1: Set project
echo "[1/4] Setting GCP project..."
gcloud config set project $PROJECT_ID

# Step 2: Verify authentication
echo ""
echo "[2/4] Checking authentication..."
gcloud auth list --filter=status:ACTIVE --format="value(account)"

# Step 3: Deploy from source
echo ""
echo "[3/4] Deploying to Cloud Run..."
echo "This may take 5-10 minutes..."
echo ""

gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --max-instances 10 \
    --min-instances 0 \
    --timeout 300 \
    --memory 1Gi \
    --cpu 1 \
    --set-env-vars GOOGLE_ENTRYPOINT="uvicorn backend.main:app --host 0.0.0.0 --port \$PORT"

# Step 4: Get service URL
echo ""
echo "[4/4] Getting service URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region $REGION \
    --format="value(status.url)")

echo ""
echo "========================================"
echo "✅ Deployment Complete!"
echo "========================================"
echo ""
echo "Service URL: $SERVICE_URL"
echo ""
echo "Test Endpoints:"
echo "  Health:    $SERVICE_URL/health"
echo "  Whoami:    $SERVICE_URL/auth/whoami"
echo "  Files:     $SERVICE_URL/files/archive/{user_id}/{record_id}.jpg"
echo ""
echo "Static Files:"
echo "  - /files mount active (DEV mode)"
echo "  - Frontend can use: /files/archive/{user_id}/{record_id}.jpg"
echo ""
