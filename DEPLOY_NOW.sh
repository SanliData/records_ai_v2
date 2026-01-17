#!/bin/bash
# Deploy Records AI V2 to Cloud Run
# Bu script Cloud Shell'de çalıştırılmalıdır

set -e

PROJECT_ID="records-ai"
SERVICE_NAME="records-ai-v2"
REGION="europe-west1"

echo "========================================"
echo "Records AI V2 - Deployment"
echo "========================================"
echo ""
echo "Proje: $PROJECT_ID"
echo "Servis: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

# Check if we're in the right directory
if [ ! -f "backend/main.py" ]; then
    echo "❌ HATA: backend/main.py bulunamadı!"
    echo "Lütfen proje root directory'sinde olduğunuzdan emin olun"
    exit 1
fi

# Check for main.py wrapper
if [ ! -f "main.py" ]; then
    echo "⚠ main.py wrapper bulunamadı, oluşturuluyor..."
    cat > main.py << 'EOF'
"""
Root entrypoint wrapper for Cloud Run buildpacks.
This file allows the Python buildpack to detect the application entrypoint.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import and run the actual application
from backend.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
EOF
    echo "✓ main.py oluşturuldu"
fi

# Check for Procfile
if [ ! -f "Procfile" ]; then
    echo "⚠ Procfile bulunamadı, oluşturuluyor..."
    echo "web: uvicorn backend.main:app --host 0.0.0.0 --port \$PORT" > Procfile
    echo "✓ Procfile oluşturuldu"
fi

# Check for runtime.txt
if [ ! -f "runtime.txt" ]; then
    echo "⚠ runtime.txt bulunamadı, oluşturuluyor..."
    echo "python-3.11" > runtime.txt
    echo "✓ runtime.txt oluşturuldu"
fi

# Set project
echo ""
echo "[1/3] Setting project..."
gcloud config set project $PROJECT_ID
echo "✓ Proje: $PROJECT_ID"

# Deploy
echo ""
echo "[2/3] Deploying to Cloud Run..."
echo "Bu işlem 5-10 dakika sürebilir..."
echo ""

gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --project $PROJECT_ID

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Deployment başarısız!"
    echo ""
    echo "Build loglarını kontrol edin:"
    echo "https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
    exit 1
fi

# Get service URL
echo ""
echo "[3/3] Getting service URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)" 2>/dev/null)

echo ""
echo "========================================"
echo "✓ DEPLOYMENT BAŞARILI!"
echo "========================================"
echo ""

if [ ! -z "$SERVICE_URL" ]; then
    echo "Service URL: $SERVICE_URL"
    echo ""
    echo "Test Sayfaları:"
    echo "  Ana Sayfa: $SERVICE_URL/ui/index.html"
    echo "  Upload:    $SERVICE_URL/ui/upload.html"
    echo "  Health:    $SERVICE_URL/health"
    echo ""
    
    echo "⚠ EĞER 403 HATASI ALIRSANIZ:"
    echo "1. Console'a gidin:"
    echo "   https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME?project=$PROJECT_ID"
    echo "2. 'EDIT & DEPLOY NEW REVISION' butonuna tıklayın"
    echo "3. 'SECURITY' sekmesine gidin"
    echo "4. 'Allow unauthenticated invocations' seçeneğini işaretleyin"
    echo "5. 'DEPLOY' butonuna tıklayın"
else
    echo "Service URL alınamadı"
    echo "Console'dan kontrol edin:"
    echo "https://console.cloud.google.com/run?project=$PROJECT_ID"
fi

echo ""



