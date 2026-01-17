#!/bin/bash
# Cloud Shell'de bu komutları çalıştırın

# Önce dizini kontrol edin
echo "Mevcut dizin: $(pwd)"
echo ""

# Dosyaların olduğu dizine gidin (veya yeni klasör oluşturun)
if [ -d "records_ai_v2" ]; then
    cd records_ai_v2
    echo "✓ records_ai_v2 dizinine gidildi"
elif [ -f "backend/main.py" ]; then
    echo "✓ backend/main.py bulundu, mevcut dizinde"
else
    echo "⚠ Dosyalar bulunamadı. Lütfen dosyaların olduğu dizine gidin veya yükleyin"
    echo ""
    echo "Cloud Shell Editor ile:"
    echo "1. Sağ üstte 'Open Editor' (kalem ikonu) tıklayın"
    echo "2. Local records_ai_v2 klasörünü Cloud Shell'e yükleyin"
    echo "3. Tekrar bu script'i çalıştırın"
    exit 1
fi

# main.py oluştur
echo ""
echo "[1/5] main.py wrapper oluşturuluyor..."
cat > main.py << 'EOF'
"""
Root entrypoint wrapper for Cloud Run buildpacks.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from backend.main import app
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
EOF
echo "✓ main.py oluşturuldu"

# Procfile oluştur
echo "[2/5] Procfile oluşturuluyor..."
echo "web: uvicorn backend.main:app --host 0.0.0.0 --port \$PORT" > Procfile
echo "✓ Procfile oluşturuldu"

# runtime.txt oluştur
echo "[3/5] runtime.txt oluşturuluyor..."
echo "python-3.11" > runtime.txt
echo "✓ runtime.txt oluşturuldu"

# Dosyaları kontrol et
echo ""
echo "[4/5] Dosyalar kontrol ediliyor..."
if [ ! -f "backend/main.py" ]; then
    echo "❌ HATA: backend/main.py bulunamadı!"
    exit 1
fi
if [ ! -f "requirements.txt" ]; then
    echo "❌ HATA: requirements.txt bulunamadı!"
    exit 1
fi
echo "✓ Tüm dosyalar hazır"

# Deploy
echo ""
echo "[5/5] Deploy ediliyor..."
echo "Bu işlem 5-10 dakika sürebilir..."
echo ""

gcloud config set project records-ai && \
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✓ DEPLOYMENT BAŞARILI!"
    echo "========================================"
    echo ""
    SERVICE_URL=$(gcloud run services describe records-ai-v2 --region europe-west1 --format "value(status.url)" 2>/dev/null)
    if [ ! -z "$SERVICE_URL" ]; then
        echo "Service URL: $SERVICE_URL"
        echo ""
        echo "Test Sayfaları:"
        echo "  Ana Sayfa: $SERVICE_URL/ui/index.html"
        echo "  Upload:    $SERVICE_URL/ui/upload.html"
        echo "  Health:    $SERVICE_URL/health"
    fi
else
    echo ""
    echo "❌ Deployment başarısız!"
    echo "Build loglarını kontrol edin:"
    echo "https://console.cloud.google.com/cloud-build/builds?project=records-ai"
fi



