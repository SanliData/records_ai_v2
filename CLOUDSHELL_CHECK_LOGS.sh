#!/bin/bash
# Check Cloud Run logs for startup errors

echo "Fetching recent logs..."
gcloud run logs read records-ai-v2 \
  --region us-central1 \
  --limit 50 \
  --project records-ai
