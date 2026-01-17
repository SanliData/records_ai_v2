# Quick Deploy Script - Records AI V2
# Basit ve hızlı deployment script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Records AI V2 - Quick Deploy" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_ID = "records-ai"
$SERVICE_NAME = "records-ai-v2"
$REGION = "europe-west1"

Write-Host "Proje: $PROJECT_ID" -ForegroundColor Green
Write-Host "Servis: $SERVICE_NAME" -ForegroundColor Green
Write-Host "Region: $REGION" -ForegroundColor Green
Write-Host ""

# Check gcloud
Write-Host "[1/4] Checking gcloud..." -ForegroundColor Yellow
$gcloud = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloud) {
    Write-Host "❌ gcloud bulunamadı! Google Cloud CLI kurun." -ForegroundColor Red
    Write-Host "   https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ gcloud bulundu" -ForegroundColor Green
Write-Host ""

# Set project
Write-Host "[2/4] Setting project..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Proje ayarlanamadı. Devam ediyorum..." -ForegroundColor Yellow
}
Write-Host "✓ Proje: $PROJECT_ID" -ForegroundColor Green
Write-Host ""

# Deploy
Write-Host "[3/4] Deploying to Cloud Run..." -ForegroundColor Yellow
Write-Host "Bu işlem 5-10 dakika sürebilir..." -ForegroundColor Gray
Write-Host ""

gcloud run deploy $SERVICE_NAME `
    --source . `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --port 8080

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Deployment başarısız!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Yardım:" -ForegroundColor Yellow
    Write-Host "1. gcloud auth login" -ForegroundColor White
    Write-Host "2. DEPLOYMENT_STEP_BY_STEP.md dosyasına bakın" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "[4/5] Setting IAM permissions..." -ForegroundColor Yellow
Write-Host "allUsers'a Cloud Run Invoker rolü veriliyor..." -ForegroundColor Gray
gcloud run services add-iam-policy-binding $SERVICE_NAME `
    --region=$REGION `
    --member="allUsers" `
    --role="roles/run.invoker" `
    --project=$PROJECT_ID 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ IAM permissions ayarlandı" -ForegroundColor Green
} else {
    Write-Host "⚠ IAM permissions ayarlanamadı (devam ediliyor)" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "[5/5] Getting service URL..." -ForegroundColor Yellow
$serviceUrl = gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)" 2>&1

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ Deployment Başarılı!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

if ($serviceUrl -and -not $serviceUrl.StartsWith("ERROR")) {
    Write-Host "Service URL: $serviceUrl" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Test Sayfaları:" -ForegroundColor Yellow
    Write-Host "  Ana Sayfa: $serviceUrl/ui/index.html" -ForegroundColor White
    Write-Host "  Upload:    $serviceUrl/ui/upload.html" -ForegroundColor White
    Write-Host "  Login:     $serviceUrl/ui/login.html" -ForegroundColor White
    Write-Host "  Health:    $serviceUrl/health" -ForegroundColor White
} else {
    Write-Host "Service URL alınamadı." -ForegroundColor Yellow
    Write-Host "Cloud Console'dan kontrol edin:" -ForegroundColor White
    Write-Host "https://console.cloud.google.com/run?project=$PROJECT_ID" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "ÖNEMLİ: Browser cache temizleyin!" -ForegroundColor Yellow
Write-Host "  Ctrl+Shift+R (hard refresh)" -ForegroundColor White
Write-Host "  VEYA gizli pencere kullanın" -ForegroundColor White
Write-Host ""

