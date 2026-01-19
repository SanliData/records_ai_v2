#!/bin/bash
# Cloud Shell'de çalıştır: bu komutları kopyala-yapıştır

# 1. Projeye git
cd ~/records_ai_v2

# 2. Son değişiklikleri çek
git pull https://SanliData:YOUR_GITHUB_TOKEN@github.com/SanliData/records_ai_v2.git main --no-rebase

# 3. Deploy et
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --project records-ai

# 4. Deploy sonrası kontrol
echo "✅ Deploy tamamlandı. Test etmek için:"
echo "curl https://zyagrolia.com/health"
echo "curl https://zyagrolia.com/"
