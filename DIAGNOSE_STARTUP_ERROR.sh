#!/bin/bash
# Diagnose Cloud Run container startup failure

echo "=== Checking Revision Logs ==="
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=records-ai-v2 AND resource.labels.revision_name=records-ai-v2-00053-cc4" \
  --limit 50 \
  --project records-ai \
  --format "table(timestamp,textPayload,jsonPayload.message)"

echo ""
echo "=== Checking Build Logs ==="
echo "Build URL: https://console.cloud.google.com/cloud-build/builds;region=us-central1/53fcd72a-c248-474b-9542-8cb117464846?project=969278596906"

echo ""
echo "=== Most Recent Run Logs ==="
gcloud run logs read records-ai-v2 \
  --region us-central1 \
  --limit 100 \
  --project records-ai
