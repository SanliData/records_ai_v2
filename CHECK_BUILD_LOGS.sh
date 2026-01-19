#!/bin/bash
# Build log'larını kontrol et

# Son build ID'yi al
BUILD_ID=$(gcloud builds list --limit=1 --format="value(id)" --project records-ai --region us-central1)

if [ -z "$BUILD_ID" ]; then
    echo "❌ Build bulunamadı. Manuel kontrol:"
    echo "https://console.cloud.google.com/cloud-build/builds?project=969278596906"
else
    echo "📋 Son build log'ları ($BUILD_ID):"
    gcloud builds log "$BUILD_ID" --project records-ai --region us-central1
fi

# Alternatif: Web console URL
echo ""
echo "🌐 Veya web console'dan kontrol et:"
echo "https://console.cloud.google.com/cloud-build/builds?project=969278596906"
