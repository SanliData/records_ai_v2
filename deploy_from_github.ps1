# Deploy Records AI V2 from GitHub to Cloud Run
# Kullanım: .\deploy_from_github.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Records AI V2 - GitHub'dan Deploy" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_ID = "records-ai"
$SERVICE_NAME = "records-ai-v2"
$REGION = "us-central1"
$REPO_URL = "https://github.com/SanliData/records_ai_v2.git"
$BRANCH = "main"

Write-Host "Yapılandırma:" -ForegroundColor Yellow
Write-Host "  Proje: $PROJECT_ID" -ForegroundColor Green
Write-Host "  Servis: $SERVICE_NAME" -ForegroundColor Green
Write-Host "  Bölge: $REGION" -ForegroundColor Green
Write-Host "  Repository: $REPO_URL" -ForegroundColor Green
Write-Host "  Branch: $BRANCH" -ForegroundColor Green
Write-Host ""

# 1. Git durumunu kontrol et
Write-Host "[1/4] Git durumu kontrol ediliyor..." -ForegroundColor Yellow
$gitStatus = git status --short
if ($gitStatus) {
    Write-Host "⚠️  Commit edilmemiş değişiklikler var:" -ForegroundColor Yellow
    git status --short
    Write-Host ""
    $commit = Read-Host "Önce commit ve push yapmak ister misiniz? (E/H)"
    if ($commit -eq "E" -or $commit -eq "e") {
        Write-Host ""
        Write-Host "Commit mesajı:" -ForegroundColor Yellow
        $message = Read-Host
        if (-not $message) {
            $message = "Update before deployment"
        }
        git add .
        git commit -m $message
        Write-Host "✓ Commit yapıldı" -ForegroundColor Green
        Write-Host ""
        Write-Host "GitHub'a push ediliyor..." -ForegroundColor Yellow
        git push origin $BRANCH
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Push başarısız!" -ForegroundColor Red
            exit 1
        }
        Write-Host "✓ GitHub'a push edildi" -ForegroundColor Green
        Write-Host ""
    }
} else {
    Write-Host "✓ Git temiz, değişiklik yok" -ForegroundColor Green
    Write-Host ""
}

# 2. Authentication kontrol
Write-Host "[2/4] Authentication kontrol ediliyor..." -ForegroundColor Yellow
$authCheck = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $authCheck -or $authCheck -match "ERROR") {
    Write-Host "❌ Authenticate olunmamış. Lütfen çalıştırın:" -ForegroundColor Red
    Write-Host "   gcloud auth login" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Authenticated: $authCheck" -ForegroundColor Green
Write-Host ""

# 3. Proje ayarla
Write-Host "[3/4] Proje ayarlanıyor..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Proje ayarlanamadı, devam ediliyor..." -ForegroundColor Yellow
}
Write-Host "✓ Proje: $PROJECT_ID" -ForegroundColor Green
Write-Host ""

# 4. Cloud Run'a deploy
Write-Host "[4/4] Cloud Run'a deploy ediliyor..." -ForegroundColor Yellow
Write-Host "Bu işlem 5-10 dakika sürebilir..." -ForegroundColor Gray
Write-Host ""

# Önce GitHub'dan latest code'u çek (Cloud Build için)
Write-Host "GitHub'dan güncel kod alınıyor..." -ForegroundColor Cyan
git fetch origin $BRANCH
git checkout $BRANCH
Write-Host "✓ Kod güncel" -ForegroundColor Green
Write-Host ""

# Cloud Build ile build ve deploy et
Write-Host "Cloud Build ile build ediliyor..." -ForegroundColor Cyan
Write-Host ""

# Local source'dan deploy et (GitHub'dan çekilen kod ile)
gcloud run deploy $SERVICE_NAME `
    --source . `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --port 8080 `
    --max-instances 10 `
    --min-instances 0 `
    --timeout 300 `
    --memory 1Gi `
    --cpu 1 `
    --clear-base-image

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Deploy başarısız!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternatif: Cloud Console'dan manuel deploy:" -ForegroundColor Yellow
    Write-Host "1. https://console.cloud.google.com/run?project=$PROJECT_ID" -ForegroundColor Cyan
    Write-Host "2. Service'i seçin > 'Deploy new revision'" -ForegroundColor White
    Write-Host "3. 'Continuously deploy' seçeneğini kullanın (GitHub trigger)" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "[5/5] Servis URL'i alınıyor..." -ForegroundColor Yellow
$serviceUrl = gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)" 2>&1

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ Deploy Tamamlandı!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

if ($serviceUrl -and -not $serviceUrl.StartsWith("ERROR")) {
    Write-Host "Servis URL: $serviceUrl" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Test Endpoint'leri:" -ForegroundColor Yellow
    Write-Host "  Health:    $serviceUrl/health" -ForegroundColor White
    Write-Host "  Docs:      $serviceUrl/docs" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "Servis URL alınamadı." -ForegroundColor Yellow
    Write-Host "Cloud Console'dan kontrol edin:" -ForegroundColor White
    Write-Host "https://console.cloud.google.com/run?project=$PROJECT_ID" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Tamamlandı!" -ForegroundColor Green
