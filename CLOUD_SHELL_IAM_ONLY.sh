#!/bin/bash
# Cloud Shell - Sadece IAM Permissions Fix

echo "========================================"
echo "IAM Permissions Fix - Cloud Shell"
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
gcloud config set project $PROJECT_ID

# Fix IAM permissions
echo "allUsers'a Cloud Run Invoker rolü veriliyor..."
echo ""

gcloud run services add-iam-policy-binding $SERVICE_NAME \
    --region=$REGION \
    --member="allUsers" \
    --role="roles/run.invoker" \
    --project=$PROJECT_ID

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✓ IAM Permissions Düzeltildi!"
    echo "========================================"
    echo ""
    echo "Service URL:"
    echo "https://records-ai-v2-969278596906.europe-west1.run.app/ui/index.html"
    echo ""
    echo "Şimdi test edin!"
else
    echo ""
    echo "❌ IAM permissions düzeltilemedi!"
    echo ""
    echo "Organization policy engeli var. Alternatif çözüm:"
    echo ""
    echo "1. Cloud Console'a gidin:"
    echo "   https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME?project=$PROJECT_ID"
    echo ""
    echo "2. 'EDIT & DEPLOY NEW REVISION' butonuna tıklayın"
    echo "3. 'SECURITY' sekmesine gidin"
    echo "4. 'Allow unauthenticated invocations' seçeneğini işaretleyin"
    echo "5. 'DEPLOY' butonuna tıklayın"
fi

echo ""



