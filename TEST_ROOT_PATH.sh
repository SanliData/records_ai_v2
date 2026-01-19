#!/bin/bash
# Cloud Shell'de çalıştır - Root path test

SERVICE_URL="https://records-ai-v2-969278596906.us-central1.run.app"

echo "🔍 Root path GET test (HEAD değil):"
curl -s "$SERVICE_URL/" | head -20

echo ""
echo "🔍 Content-Type kontrol:"
curl -s -I "$SERVICE_URL/" | grep -i content-type

echo ""
echo "✅ Test tamamlandı!"
