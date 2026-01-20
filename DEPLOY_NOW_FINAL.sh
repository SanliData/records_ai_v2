#!/bin/bash
# Final Deployment Script - Records AI V2
# Run this in Google Cloud Shell or local terminal with gcloud CLI

set -e

PROJECT_ID="records-ai"
SERVICE_NAME="records-ai-v2"
REGION="us-central1"

echo "========================================"
echo "Records AI V2 - Final Deployment"
echo "========================================"
echo ""
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

# Step 1: Authentication
echo "[1/5] Checking authentication..."
ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1 || echo "")

if [ -z "$ACTIVE_ACCOUNT" ]; then
    echo "⚠️  No active account found."
    echo "Running gcloud auth login..."
    gcloud auth login --no-launch-browser 2>&1 || gcloud auth login
    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1)
fi

if [ -z "$ACTIVE_ACCOUNT" ]; then
    echo "❌ Authentication failed!"
    exit 1
fi

echo "✅ Authenticated as: $ACTIVE_ACCOUNT"
echo ""

# Step 2: Set project
echo "[2/5] Setting GCP project..."
gcloud config set project $PROJECT_ID
echo "✅ Project set"
echo ""

# Step 3: Verify project access
echo "[3/5] Verifying project access..."
if ! gcloud projects describe $PROJECT_ID > /dev/null 2>&1; then
    echo "❌ Cannot access project: $PROJECT_ID"
    exit 1
fi
echo "✅ Project access verified"
echo ""

# Step 4: Deploy
echo "[4/5] Deploying to Cloud Run..."
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

# Step 5: Get service URL
echo ""
echo "[5/5] Getting service URL..."
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
echo "  OpenAI:    $SERVICE_URL/openai/analyze"
echo "  Channels:  $SERVICE_URL/channels/publish"
echo "  Commerce:  $SERVICE_URL/commerce/analytics/dashboard"
echo "  Shipping:  $SERVICE_URL/shipping/analytics/dashboard"
echo ""
echo "Next Steps:"
echo "  1. Set environment variables (if needed):"
echo "     gcloud run services update $SERVICE_NAME --region $REGION \\"
echo "       --set-env-vars OPENAI_API_KEY=your_key,DISCOGS_TOKEN=your_token"
echo ""
echo "  2. Test health endpoint:"
echo "     curl $SERVICE_URL/health"
echo ""
