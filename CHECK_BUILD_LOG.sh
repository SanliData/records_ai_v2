#!/bin/bash
# Check Cloud Build Log

BUILD_ID="9b0bd0c2-b6a5-47d4-93cc-d7998b971249"
PROJECT_ID="records-ai"
REGION="europe-west1"

echo "========================================"
echo "Cloud Build Log Viewer"
echo "========================================"
echo ""
echo "Build ID: $BUILD_ID"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Get build log
echo "Fetching build log..."
echo ""

gcloud builds log $BUILD_ID --project=$PROJECT_ID --region=$REGION

echo ""
echo "========================================"
echo "Build log retrieved"
echo "========================================"
echo ""
echo "To view in Console:"
echo "https://console.cloud.google.com/cloud-build/builds/$BUILD_ID?project=$PROJECT_ID&region=$REGION"
echo ""
