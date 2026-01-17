#!/bin/bash
# Build log kontrol ve analiz

echo "=========================================="
echo "Build Log Analizi"
echo "=========================================="
echo ""

# Son build ID
BUILD_ID=$(gcloud builds list --limit 1 --format="value(id)")

if [ -z "$BUILD_ID" ]; then
    echo "❌ Build bulunamadı"
    exit 1
fi

echo "Build ID: $BUILD_ID"
echo ""

# Hata mesajlarını filtrele
echo "Hata Mesajları:"
echo "=========================================="
gcloud builds log $BUILD_ID 2>&1 | grep -i "error\|failed\|exception" | head -20

echo ""
echo "=========================================="
echo ""
echo "Tam log için:"
echo "gcloud builds log $BUILD_ID"
echo ""
echo "VEYA Cloud Console:"
echo "https://console.cloud.google.com/cloud-build/builds/$BUILD_ID?project=records-ai"



