#!/bin/bash
# Cloud Shell Fix & Deploy Script
# Fixes merge conflicts and deploys records_ai_v2

set -e

echo "========================================"
echo "Fix Merge Conflicts & Deploy"
echo "========================================"
echo ""

PROJECT_ID="records-ai"
SERVICE_NAME="records-ai-v2"
REGION="us-central1"
REPO_DIR="records_ai_v2"

# Check if we're in the repo directory
if [ ! -d "$REPO_DIR" ]; then
    echo "❌ Repository directory not found: $REPO_DIR"
    exit 1
fi

cd $REPO_DIR

echo "[1/4] Fixing merge conflicts..."
echo ""

# Check git status
echo "Git status:"
git status

echo ""
echo "Aborting merge to start fresh..."
git merge --abort 2>/dev/null || echo "  (No active merge to abort)"

echo ""
echo "Resetting to clean state..."
git reset --hard HEAD 2>/dev/null || echo "  (Reset complete)"

echo ""
echo "Fetching latest from GitHub..."
git fetch origin main

echo ""
echo "Resetting to origin/main (GitHub'daki son hali)..."
git reset --hard origin/main

echo "✓ Repository is now clean and matches GitHub"
echo ""

# Verify dockerfile exists
echo "[2/4] Verifying source files..."
if [ ! -f "dockerfile" ]; then
    echo "❌ dockerfile not found!"
    exit 1
fi
echo "✓ dockerfile found"
echo ""

# Set project
echo "[3/4] Setting project..."
gcloud config set project $PROJECT_ID
echo "✓ Project set: $PROJECT_ID"
echo ""

# Deploy
echo "[4/4] Deploying to Cloud Run..."
echo "  Service: $SERVICE_NAME"
echo "  Region: $REGION"
echo "  This will take 5-10 minutes..."
echo ""

gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --project $PROJECT_ID

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Deployment failed!"
    echo ""
    echo "Check build logs:"
    echo "  gcloud builds list --limit=1 --region=$REGION"
    echo "  gcloud builds log --region=$REGION \$(gcloud builds list --limit=1 --format='value(id)' --region=$REGION)"
    exit 1
fi

echo ""
echo "========================================"
echo "✓ Deployment Complete!"
echo "========================================"
echo ""

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)" 2>&1)

echo "Cloud Run URL: $SERVICE_URL"
echo "Domain: https://zyagrolia.com"
echo ""
echo "Test: https://zyagrolia.com/ui/upload.html"
echo ""
