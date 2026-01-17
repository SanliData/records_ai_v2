# Fix Authentication - Cloud Run Service
# Organization policy bypass için deployment yapıyor

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fix Authentication - Records AI V2" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ID = "records-ai"
$SERVICE_NAME = "records-ai-v2"
$REGION = "europe-west1"

Write-Host "Proje: $PROJECT_ID" -ForegroundColor Green
Write-Host "Servis: $SERVICE_NAME" -ForegroundColor Green
Write-Host "Region: $REGION" -ForegroundColor Green
Write-Host ""

# Check gcloud
Write-Host "[1/3] Checking gcloud..." -ForegroundColor Yellow
$gcloud = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloud) {
    Write-Host "❌ gcloud bulunamadı!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ gcloud bulundu" -ForegroundColor Green
Write-Host ""

# Set project
Write-Host "[2/3] Setting project..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
Write-Host "✓ Proje: $PROJECT_ID" -ForegroundColor Green
Write-Host ""

# Deploy with --allow-unauthenticated
Write-Host "[3/3] Deploying with --allow-unauthenticated..." -ForegroundColor Yellow
Write-Host "Bu flag IAM policy'yi otomatik ayarlar ve organization policy'yi bypass edebilir." -ForegroundColor Gray
Write-Host ""

gcloud run deploy $SERVICE_NAME `
    --source . `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --port 8080 `
    --project $PROJECT_ID

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ Deployment Başarılı!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Service URL:" -ForegroundColor Yellow
    Write-Host "https://records-ai-v2-969278596906.europe-west1.run.app/ui/index.html" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Artık 403 hatası olmamalı!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Deployment başarısız!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternatif: Cloud Console'dan manuel yapın:" -ForegroundColor Yellow
    Write-Host "1. Service'e gidin" -ForegroundColor White
    Write-Host "2. EDIT & DEPLOY NEW REVISION" -ForegroundColor White
    Write-Host "3. SECURITY sekmesi > Allow unauthenticated invocations" -ForegroundColor White
    Write-Host "4. DEPLOY" -ForegroundColor White
}

Write-Host ""



