#!/bin/bash
# Cloud Shell'de çalıştır - Son build log'larını kontrol et

echo "📋 Son build'in ID'sini al..."
BUILD_ID=$(gcloud builds list --limit=1 --format="value(id)" --project records-ai --region us-central1)

if [ -z "$BUILD_ID" ]; then
    echo "❌ Build bulunamadı. Manuel kontrol:"
    echo "https://console.cloud.google.com/cloud-build/builds?project=969278596906"
else
    echo "✅ Build ID: $BUILD_ID"
    echo ""
    echo "📋 Son 100 satır log:"
    gcloud builds log "$BUILD_ID" --project records-ai | tail -100
fi
