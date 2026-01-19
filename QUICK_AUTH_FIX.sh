#!/bin/bash
# Quick GCloud Authentication Fix
# Run this script to fix authentication and deploy

set -e

echo "=== GCloud Authentication Fix ==="
echo ""

# Step 1: Check current auth status
echo "1. Checking authentication status..."
if gcloud auth list --filter=status:ACTIVE --format='value(account)' | grep -q .; then
    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format='value(account)')
    echo "   ✅ Authenticated as: $ACTIVE_ACCOUNT"
else
    echo "   ❌ No active account found"
    echo "   🔐 Starting authentication..."
    gcloud auth login
fi

# Step 2: Check project
echo ""
echo "2. Checking project configuration..."
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
if [ "$CURRENT_PROJECT" = "records-ai" ]; then
    echo "   ✅ Project set to: records-ai"
else
    echo "   ⚠️  Project is: ${CURRENT_PROJECT:-not set}"
    echo "   🔧 Setting project to records-ai..."
    gcloud config set project records-ai
fi

# Step 3: Verify configuration
echo ""
echo "3. Verifying configuration..."
echo "   Account: $(gcloud config get-value account)"
echo "   Project: $(gcloud config get-value project)"

# Step 4: Test Cloud Run access
echo ""
echo "4. Testing Cloud Run permissions..."
if gcloud run services list --region us-central1 --limit=1 &>/dev/null; then
    echo "   ✅ Cloud Run access confirmed"
else
    echo "   ⚠️  Cloud Run access test failed"
    echo "   This might indicate missing IAM permissions"
    echo "   Required roles: roles/run.admin, roles/iam.serviceAccountUser"
fi

# Step 5: Deploy
echo ""
echo "5. Ready to deploy!"
echo ""
read -p "Deploy now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Deploying..."
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
      --cpu 1 \
      --set-env-vars PORT=8080
else
    echo "Skipping deploy. Run manually when ready:"
    echo "  gcloud run deploy records-ai-v2 --source . --region us-central1 --allow-unauthenticated --port 8080"
fi

echo ""
echo "Done!"
