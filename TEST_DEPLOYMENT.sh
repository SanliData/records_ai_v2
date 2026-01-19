#!/bin/bash
# Cloud Shell'de çalıştır - Deploy test

SERVICE_URL="https://records-ai-v2-969278596906.us-central1.run.app"
DOMAIN="https://zyagrolia.com"

echo "🔍 1. Health check:"
curl -s "$SERVICE_URL/health" | jq . || curl -s "$SERVICE_URL/health"

echo ""
echo "🔍 2. Root path (should return HTML, not JSON):"
curl -s -I "$SERVICE_URL/" | head -5

echo ""
echo "🔍 3. Custom domain check:"
curl -s -I "$DOMAIN/health" | head -5 || echo "Domain mapping kontrol edilemedi"

echo ""
echo "✅ Test tamamlandı!"
