#!/bin/bash
# Cloud Shell'de çalıştır - Deploy'u düzelt

cd ~/records_ai_v2

echo "📋 1. Local source'u kontrol et..."
ls -la | grep -E "Procfile|runtime.txt|requirements.txt|backend"

echo ""
echo "📋 2. Git durumu:"
git status --short | head -10

echo ""
echo "📋 3. .gcloudignore'da dockerfile var mı?"
grep -i dockerfile .gcloudignore || echo "❌ dockerfile .gcloudignore'da yok!"

echo ""
echo "🚀 4. Deploy başlatılıyor (--source . ile local source kullanılacak)..."
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --project records-ai \
  --no-use-remote-build

echo ""
echo "✅ Deploy tamamlandı!"
