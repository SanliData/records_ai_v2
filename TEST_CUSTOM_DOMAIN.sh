#!/bin/bash
# Cloud Shell'de çalıştır - Custom domain test

echo "🔍 Custom domain test: zyagrolia.com"
echo ""

echo "1. Health check:"
curl -s https://zyagrolia.com/health

echo ""
echo "2. Root path (HTML olmalı):"
curl -s https://zyagrolia.com/ | head -10

echo ""
echo "✅ Test tamamlandı!"
