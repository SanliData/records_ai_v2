#!/bin/bash
# Cloud Shell Authentication and Deploy Script
# Run this in Google Cloud Shell

set -e

PROJECT_ID="records-ai"
SERVICE_NAME="records-ai-v2"
REGION="us-central1"

echo "========================================"
echo "Records AI V2 - Auth & Deploy"
echo "========================================"
echo ""

# Step 1: Check authentication
echo "[1/5] Checking authentication..."
ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1)

if [ -z "$ACTIVE_ACCOUNT" ]; then
    echo "⚠️  No active account found."
    echo ""
    echo "Running gcloud auth login..."
    echo "If browser opens, complete authentication there."
    echo "If in Cloud Shell, authentication should be automatic."
    echo ""
    
    # Try application-default login first (for Cloud Shell)
    gcloud auth application-default login 2>&1 || \
    gcloud auth login --no-launch-browser 2>&1 || \
    gcloud auth login
    
    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1)
fi

if [ -z "$ACTIVE_ACCOUNT" ]; then
    echo "❌ Authentication failed!"
    echo ""
    echo "Please run manually:"
    echo "  gcloud auth login"
    echo ""
    exit 1
fi

echo "✅ Authenticated as: $ACTIVE_ACCOUNT"
echo ""

# Step 2: Set project
echo "[2/5] Setting GCP project..."
gcloud config set project $PROJECT_ID
echo "✅ Project set to: $PROJECT_ID"
echo ""

# Step 3: Verify project access
echo "[3/5] Verifying project access..."
gcloud projects describe $PROJECT_ID > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Cannot access project: $PROJECT_ID"
    echo "   Check permissions or project ID"
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
echo "  Whoami:    $SERVICE_URL/auth/whoami"
echo ""
echo "Next Steps:"
echo "  1. Set environment variables:"
echo "     gcloud run services update records-ai-v2 --region us-central1 --set-env-vars OPENAI_API_KEY=your_key,DISCOGS_TOKEN=your_token"
echo ""
echo "  2. Test health endpoint:"
echo "     curl $SERVICE_URL/health"
echo ""
