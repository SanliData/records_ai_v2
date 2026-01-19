#!/bin/bash
# Cloud Shell Deployment Script
# GitHub: https://github.com/SanliData/records_ai_v2
# Domain: zyagrolia.com

set -e

echo "========================================"
echo "Records AI V2 - Cloud Shell Deploy"
echo "========================================"
echo ""

# Configuration
PROJECT_ID="records-ai"
SERVICE_NAME="records-ai-v2"
REGION="us-central1"
REPO_URL="https://github.com/SanliData/records_ai_v2.git"
REPO_DIR="records_ai_v2"

echo "Configuration:"
echo "  Project: $PROJECT_ID"
echo "  Service: $SERVICE_NAME"
echo "  Region: $REGION"
echo "  Repository: $REPO_URL"
echo ""

# Set project
echo "[1/5] Setting project..."
gcloud config set project $PROJECT_ID
echo "✓ Project set: $PROJECT_ID"
echo ""

# Clone or update repository
echo "[2/5] Cloning repository..."
if [ -d "$REPO_DIR" ]; then
    echo "  Directory exists, updating..."
    cd $REPO_DIR
    git pull origin main
    echo "✓ Repository updated"
else
    echo "  Cloning repository..."
    git clone $REPO_URL $REPO_DIR
    cd $REPO_DIR
    echo "✓ Repository cloned"
fi
echo ""

# Check if dockerfile exists
echo "[3/5] Checking source files..."
if [ ! -f "dockerfile" ]; then
    echo "❌ dockerfile not found!"
    exit 1
fi
echo "✓ Source files ready"
echo ""

# Deploy to Cloud Run
echo "[4/5] Deploying to Cloud Run..."
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
    exit 1
fi

echo ""
echo "[5/5] Getting service URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)" 2>&1)

echo ""
echo "========================================"
echo "✓ Deployment Complete!"
echo "========================================"
echo ""
echo "Cloud Run URL: $SERVICE_URL"
echo "Domain: https://zyagrolia.com"
echo ""
echo "Test URLs:"
echo "  Health:    https://zyagrolia.com/"
echo "  Upload:    https://zyagrolia.com/ui/upload.html"
echo "  Login:     https://zyagrolia.com/ui/login.html"
echo ""
echo "Next Steps:"
echo "1. Wait 1-2 minutes for service to fully start"
echo "2. Test: https://zyagrolia.com/ui/upload.html"
echo "3. Check logs: gcloud run logs read $SERVICE_NAME --region $REGION"
echo ""
