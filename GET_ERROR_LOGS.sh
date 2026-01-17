#!/bin/bash
# Get error logs for failed revision

REVISION="records-ai-v2-00046-c2h"
SERVICE="records-ai-v2"
PROJECT="records-ai"
REGION="us-central1"

echo "========================================"
echo "Checking logs for revision: $REVISION"
echo "========================================"
echo ""

echo "[1] Checking for ERROR level logs..."
gcloud logging read \
  "resource.type=\"cloud_run_revision\"
   resource.labels.service_name=\"$SERVICE\"
   resource.labels.revision_name=\"$REVISION\"
   resource.labels.location=\"$REGION\"
   severity>=ERROR" \
  --limit=20 \
  --format="table(timestamp,severity,textPayload)" \
  --project=$PROJECT

echo ""
echo "[2] Checking for application startup logs..."
gcloud logging read \
  "resource.type=\"cloud_run_revision\"
   resource.labels.service_name=\"$SERVICE\"
   resource.labels.revision_name=\"$REVISION\"
   resource.labels.location=\"$REGION\"
   (textPayload=~\"uvicorn\" OR textPayload=~\"Starting\" OR textPayload=~\"Error\" OR textPayload=~\"Traceback\" OR textPayload=~\"Exception\")" \
  --limit=30 \
  --format="table(timestamp,severity,textPayload)" \
  --project=$PROJECT

echo ""
echo "[3] Checking all logs (last 50 entries)..."
gcloud logging read \
  "resource.type=\"cloud_run_revision\"
   resource.labels.service_name=\"$SERVICE\"
   resource.labels.revision_name=\"$REVISION\"
   resource.labels.location=\"$REGION\"" \
  --limit=50 \
  --format="table(timestamp,severity,textPayload)" \
  --project=$PROJECT

echo ""
echo "========================================"
echo "Done. Look for ERROR, WARNING, or application crash logs above."
echo "========================================"



