#!/bin/bash
# Cloud Shell'de çalıştır

BUILD_ID="39bca02c-e695-4c00-a6cf-7a8af7434cbc"

echo "📋 Build log'ları ($BUILD_ID):"
gcloud builds log "$BUILD_ID" --project records-ai --region us-central1
