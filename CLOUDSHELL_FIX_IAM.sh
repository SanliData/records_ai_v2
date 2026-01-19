#!/bin/bash
# Fix IAM Policy for Cloud Run Service

SERVICE_NAME="records-ai-v2"
REGION="us-central1"
PROJECT_ID="records-ai"

echo "Setting IAM policy for public access..."
echo ""

gcloud run services add-iam-policy-binding $SERVICE_NAME \
    --region=$REGION \
    --member="allUsers" \
    --role="roles/run.invoker" \
    --project=$PROJECT_ID

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ IAM policy set successfully!"
    echo ""
    echo "Service is now publicly accessible at:"
    echo "  https://records-ai-v2-969278596906.us-central1.run.app"
    echo "  https://zyagrolia.com"
else
    echo ""
    echo "⚠ IAM policy setting failed"
    echo "Service may already have correct permissions"
fi

echo ""
