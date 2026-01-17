#!/bin/bash
# Find Recent Builds

PROJECT_ID="records-ai"

echo "========================================"
echo "Finding Recent Builds"
echo "========================================"
echo ""

# Check all regions
REGIONS=("europe-west1" "us-central1" "us-east1" "europe-west4")

for REGION in "${REGIONS[@]}"; do
    echo "Checking region: $REGION"
    echo "----------------------------------------"
    
    gcloud builds list \
        --project=$PROJECT_ID \
        --region=$REGION \
        --limit=3 \
        --format="table(id,status,createTime,logUrl)" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo ""
    fi
done

echo ""
echo "========================================"
echo "To view a specific build log:"
echo "gcloud builds log <BUILD_ID> --project=$PROJECT_ID --region=<REGION>"
echo ""
echo "To view in Console:"
echo "https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
echo ""



