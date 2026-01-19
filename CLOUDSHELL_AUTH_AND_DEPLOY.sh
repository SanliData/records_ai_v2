#!/bin/bash
# Cloud Shell'de çalıştır

# 1. Mevcut hesapları listele
echo "📋 Mevcut hesaplar:"
gcloud auth list

# 2. Mevcut proje/config'i kontrol et
echo ""
echo "📋 Mevcut config:"
gcloud config list

# 3. Projeyi ayarla (gerekirse)
gcloud config set project records-ai

# 4. Account seçimi (ilk listedeki hesabı kullan)
ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1)
if [ -n "$ACCOUNT" ]; then
    echo "✅ Active account bulundu: $ACCOUNT"
    gcloud config set account "$ACCOUNT"
else
    echo "⚠️  Active account bulunamadı. Login yapılıyor..."
    gcloud auth login
fi

# 5. Deploy
echo ""
echo "🚀 Deploy başlatılıyor..."
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --project records-ai
