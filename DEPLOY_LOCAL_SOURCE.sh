#!/bin/bash
# Cloud Shell'de çalıştır - Local source ile deploy

cd ~/records_ai_v2

echo "📋 1. Dosya kontrolleri..."
echo "Procfile exists: $(test -f Procfile && echo 'YES' || echo 'NO')"
echo "runtime.txt exists: $(test -f runtime.txt && echo 'YES' || echo 'NO')"
echo "requirements.txt exists: $(test -f requirements.txt && echo 'YES' || echo 'NO')"
echo "backend/main.py exists: $(test -f backend/main.py && echo 'YES' || echo 'NO')"

echo ""
echo "📋 2. .gcloudignore dockerfile check:"
grep -i dockerfile .gcloudignore

echo ""
echo "📋 3. Current git status:"
git status --short | head -5

echo ""
echo "🚀 4. Deploy with LOCAL source (--source . means current directory)..."
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --project records-ai
