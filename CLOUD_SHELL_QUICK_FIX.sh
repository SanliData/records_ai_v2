#!/bin/bash
# Quick Fix - Dockerfile + Deploy

echo "========================================"
echo "Quick Fix - Records AI V2"
echo "========================================"

PROJECT_ID="records-ai"
SERVICE_NAME="records-ai-v2"
REGION="europe-west1"

# Fix Dockerfile name
if [ -f "dockerfile" ] && [ ! -f "Dockerfile" ]; then
    echo "[1/4] Renaming dockerfile -> Dockerfile..."
    mv dockerfile Dockerfile
    echo "✓ Done"
elif [ -f "Dockerfile" ]; then
    echo "[1/4] ✓ Dockerfile exists"
else
    echo "[1/4] ❌ Dockerfile not found!"
    exit 1
fi

# Check backend/main.py
if [ ! -f "backend/main.py" ]; then
    echo "[2/4] ❌ backend/main.py not found!"
    echo "Make sure you're in the project directory"
    exit 1
fi
echo "[2/4] ✓ Files check OK"

# Set project
echo "[3/4] Setting project..."
gcloud config set project $PROJECT_ID
echo "✓ Project: $PROJECT_ID"

# Deploy
echo "[4/4] Deploying..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --project $PROJECT_ID

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✓ DEPLOYMENT SUCCESS!"
    echo "========================================"
    echo ""
    echo "⚠ IF 403 ERROR:"
    echo "Go to Console > Service > EDIT > SECURITY"
    echo "Check 'Allow unauthenticated invocations'"
    echo ""
else
    echo ""
    echo "❌ Deployment failed!"
    echo "Check build logs:"
    echo "https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
fi



