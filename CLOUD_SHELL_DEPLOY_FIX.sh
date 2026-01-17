#!/bin/bash
# Cloud Shell Deployment Fix Script
# Sorun: Build Dockerfile bulamıyor + IAM policy engeli

echo "========================================"
echo "Cloud Shell Deployment Fix"
echo "========================================"
echo ""

PROJECT_ID="records-ai"
SERVICE_NAME="records-ai-v2"
REGION="europe-west1"

echo "Proje: $PROJECT_ID"
echo "Servis: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

# Check if we're in the right directory
echo "[1/5] Checking files..."
if [ ! -f "backend/main.py" ]; then
    echo "❌ backend/main.py bulunamadı!"
    echo ""
    echo "Dosyaların olduğu dizine gidin:"
    echo "  cd ~/records_ai_v2"
    echo "VEYA dosyaları Cloud Shell'e yükleyin"
    exit 1
fi

# Check Dockerfile
if [ -f "dockerfile" ] && [ ! -f "Dockerfile" ]; then
    echo "[2/5] Renaming dockerfile -> Dockerfile..."
    mv dockerfile Dockerfile
    echo "✓ dockerfile -> Dockerfile"
elif [ ! -f "Dockerfile" ] && [ ! -f "dockerfile" ]; then
    echo "❌ Dockerfile bulunamadı!"
    exit 1
else
    echo "[2/5] ✓ Dockerfile mevcut"
fi
echo ""

# Set project
echo "[3/5] Setting project..."
gcloud config set project $PROJECT_ID
echo "✓ Proje: $PROJECT_ID"
echo ""

# Try to fix IAM (may fail due to org policy)
echo "[4/5] Attempting IAM permissions fix..."
gcloud run services add-iam-policy-binding $SERVICE_NAME \
    --region=$REGION \
    --member="allUsers" \
    --role="roles/run.invoker" \
    --project=$PROJECT_ID 2>&1 | grep -q "FAILED_PRECONDITION"

if [ $? -eq 0 ]; then
    echo "⚠ IAM policy hatası (organization policy engeli)"
    echo "   Build'den sonra Console'dan 'Allow unauthenticated invocations' yapın"
else
    echo "✓ IAM permissions ayarlandı"
fi
echo ""

# Deploy
echo "[5/5] Deploying to Cloud Run..."
echo "Bu işlem 5-10 dakika sürebilir..."
echo ""

gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --project $PROJECT_ID

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✓ Deployment Başarılı!"
    echo "========================================"
    echo ""
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)" 2>/dev/null)
    if [ ! -z "$SERVICE_URL" ]; then
        echo "Service URL: $SERVICE_URL"
        echo ""
        echo "Test Sayfaları:"
        echo "  Ana Sayfa: $SERVICE_URL/ui/index.html"
        echo "  Upload:    $SERVICE_URL/ui/upload.html"
        echo "  Health:    $SERVICE_URL/health"
    fi
    
    echo ""
    echo "⚠ EĞER 403 HATASI ALIYORSANIZ:"
    echo "1. Cloud Console'a gidin:"
    echo "   https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME?project=$PROJECT_ID"
    echo "2. 'EDIT & DEPLOY NEW REVISION' butonuna tıklayın"
    echo "3. 'SECURITY' sekmesine gidin"
    echo "4. 'Allow unauthenticated invocations' seçeneğini işaretleyin"
    echo "5. 'DEPLOY' butonuna tıklayın"
else
    echo ""
    echo "❌ Deployment başarısız!"
    echo ""
    echo "Build loglarını kontrol edin:"
    echo "https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
fi

echo ""



