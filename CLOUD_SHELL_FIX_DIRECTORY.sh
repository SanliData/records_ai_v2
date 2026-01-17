#!/bin/bash
# Cloud Shell'de çalıştırın - Dosya dizini yoksa oluşturur

echo "========================================"
echo "Cloud Shell Setup"
echo "========================================"
echo ""

# Mevcut dizini kontrol et
CURRENT_DIR=$(pwd)
echo "Mevcut dizin: $CURRENT_DIR"
echo ""

# records_ai dizini var mı kontrol et
if [ -d "records_ai" ]; then
    echo "✓ records_ai dizini bulundu"
    cd records_ai
    echo "records_ai dizinine gidildi"
elif [ -f "backend/main.py" ]; then
    echo "✓ backend/main.py mevcut dizinde bulundu"
    # Mevcut dizinde devam et
else
    echo "⚠ Dosyalar bulunamadı"
    echo ""
    echo "Seçenek 1: records_ai dizininde çalış (varsa)"
    echo "Seçenek 2: Yeni dizin oluştur ve dosyaları yükle"
    echo ""
    read -p "records_ai dizinine gidilsin mi? (y/n): " choice
    if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
        if [ -d "records_ai" ]; then
            cd records_ai
        else
            echo "❌ records_ai dizini bulunamadı"
            exit 1
        fi
    else
        echo "Yeni dizin oluşturun veya dosyaları yükleyin"
        exit 1
    fi
fi

echo ""
echo "Mevcut dizin: $(pwd)"
echo ""

# backend/main.py var mı kontrol et
if [ ! -f "backend/main.py" ]; then
    echo "❌ HATA: backend/main.py bulunamadı!"
    echo ""
    echo "Lütfen dosyaları Cloud Shell'e yükleyin:"
    echo "1. Cloud Shell Editor'ü açın (sağ üstte kalem ikonu)"
    echo "2. Local records_ai_v2 klasörünü Cloud Shell'e yükleyin"
    echo "3. Tekrar bu script'i çalıştırın"
    exit 1
fi

echo "✓ backend/main.py bulundu"
echo ""

# main.py wrapper oluştur
echo "[1/4] main.py wrapper oluşturuluyor..."
cat > main.py << 'EOF'
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
echo "[2/4] Procfile oluşturuluyor..."
echo "web: uvicorn backend.main:app --host 0.0.0.0 --port \$PORT" > Procfile
echo "✓ Procfile oluşturuldu"

# runtime.txt oluştur
echo "[3/4] runtime.txt oluşturuluyor..."
echo "python-3.11" > runtime.txt
echo "✓ runtime.txt oluşturuldu"

# Deploy
echo ""
echo "[4/4] Deploy ediliyor..."
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
        echo "  Health:    $SERVICE_URL/health"
    fi
else
    echo ""
    echo "❌ Deployment başarısız!"
    echo "Build loglarını kontrol edin"
fi

echo ""



