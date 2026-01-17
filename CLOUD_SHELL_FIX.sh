#!/bin/bash
# Cloud Shell için IAM ve Deployment Fix Script

echo "========================================"
echo "Records AI V2 - Cloud Shell Fix"
echo "========================================"
echo ""

PROJECT_ID="records-ai"
SERVICE_NAME="records-ai-v2"
REGION="europe-west1"

echo "Proje: $PROJECT_ID"
echo "Servis: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

# Set project
echo "[1/4] Setting project..."
gcloud config set project $PROJECT_ID
echo "✓ Proje: $PROJECT_ID"
echo ""

# Fix IAM permissions (bypass organization policy)
echo "[2/4] Fixing IAM permissions..."
echo "allUsers'a Cloud Run Invoker rolü veriliyor..."
gcloud run services add-iam-policy-binding $SERVICE_NAME \
    --region=$REGION \
    --member="allUsers" \
    --role="roles/run.invoker" \
    --project=$PROJECT_ID

if [ $? -eq 0 ]; then
    echo "✓ IAM permissions ayarlandı"
else
    echo "⚠ IAM permissions ayarlanamadı (organization policy engeli olabilir)"
    echo "Alternatif: Console'dan 'Allow unauthenticated invocations' seçeneğini kullanın"
fi
echo ""

# Check if we're in the right directory
echo "[3/4] Checking directory..."
if [ ! -f "backend/main.py" ]; then
    echo "⚠ backend/main.py bulunamadı!"
    echo "Dosyaların olduğu dizine gidin:"
    echo "  cd records_ai_v2"
    echo "VEYA dosyaları Cloud Shell'e yükleyin"
    exit 1
fi
echo "✓ Dosyalar bulundu"
echo ""

# Deploy
echo "[4/4] Deploying to Cloud Run..."
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
else
    echo ""
    echo "❌ Deployment başarısız!"
    echo ""
    echo "Build loglarını kontrol edin:"
    echo "https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
    echo ""
    echo "VEYA build loglarını görmek için:"
    echo "gcloud builds list --limit=1 --format='value(id)' | xargs -I {} gcloud builds log {}"
fi

echo ""



