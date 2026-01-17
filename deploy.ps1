# Deployment Script for Records AI V2
# Google Cloud Run Deployment

$ErrorActionPreference = "Stop"

Write-Host "=== Records AI V2 Deployment ===" -ForegroundColor Cyan
Write-Host ""

# Configuration - Bu değerleri kendi projenize göre güncelleyin
$PROJECT_ID = Read-Host "Google Cloud Project ID"
$SERVICE_NAME = "records-ai-v2"
$REGION = Read-Host "Cloud Run Region (örn: europe-west1, us-central1)"

if ([string]::IsNullOrWhiteSpace($PROJECT_ID)) {
    Write-Host "Project ID gerekli!" -ForegroundColor Red
    exit 1
}

if ([string]::IsNullOrWhiteSpace($REGION)) {
    $REGION = "europe-west1"
    Write-Host "Region belirtilmedi, varsayılan: $REGION" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Proje: $PROJECT_ID" -ForegroundColor Green
Write-Host "Servis: $SERVICE_NAME" -ForegroundColor Green
Write-Host "Region: $REGION" -ForegroundColor Green
Write-Host ""

# 1. Docker build
Write-Host "[1/4] Docker image build ediliyor..." -ForegroundColor Yellow
$imageTag = "gcr.io/$PROJECT_ID/$SERVICE_NAME`:latest"
docker build -t $imageTag .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker build başarısız!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Docker image oluşturuldu: $imageTag" -ForegroundColor Green

# 2. Google Cloud'a push
Write-Host ""
Write-Host "[2/4] Google Cloud Container Registry'ye push ediliyor..." -ForegroundColor Yellow
docker push $imageTag

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker push başarısız! gcloud auth configure-docker çalıştırın" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Image Cloud Registry'ye push edildi" -ForegroundColor Green

# 3. Environment variables kontrolü
Write-Host ""
Write-Host "[3/4] Environment variables kontrol ediliyor..." -ForegroundColor Yellow
$envVars = @()

$openaiKey = $env:OPENAI_API_KEY
if ($openaiKey) {
    $envVars += "OPENAI_API_KEY=$openaiKey"
    Write-Host "✓ OPENAI_API_KEY bulundu" -ForegroundColor Green
} else {
    Write-Host "⚠ OPENAI_API_KEY bulunamadı (opsiyonel)" -ForegroundColor Yellow
}

# 4. Cloud Run deploy
Write-Host ""
Write-Host "[4/4] Cloud Run'a deploy ediliyor..." -ForegroundColor Yellow

$deployCmd = "gcloud run deploy $SERVICE_NAME " +
    "--image $imageTag " +
    "--platform managed " +
    "--region $REGION " +
    "--allow-unauthenticated " +
    "--port 8080"

if ($envVars.Count -gt 0) {
    $envVarsStr = $envVars -join ","
    $deployCmd += " --set-env-vars `"$envVarsStr`""
}

Write-Host "Komut: $deployCmd" -ForegroundColor Gray
Invoke-Expression $deployCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host "Deployment başarısız!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Deployment Tamamlandı! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Servis URL'i:" -ForegroundColor Cyan
gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)"
Write-Host ""
Write-Host "Frontend: https://zyagrolia.com/ui/upload.html" -ForegroundColor Cyan
Write-Host "API: https://api.zyagrolia.com" -ForegroundColor Cyan
Write-Host ""




