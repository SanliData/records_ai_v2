# Otomatik Deployment Script
# Records AI V2 - Tüm adımları otomatik yürütür

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Records AI V2 - Otomatik Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ID = "records-ai"
$SERVICE_NAME = "records-ai-v2"
$REGION = "europe-west1"

# ADIM 1: Authentication Kontrolü
Write-Host "[ADIM 1/6] Authentication kontrol ediliyor..." -ForegroundColor Yellow
$authList = gcloud auth list --format="value(account)" 2>&1
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($authList)) {
    Write-Host "⚠ Authentication gerekli!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Tarayıcınız açılacak, Google hesabınızla giriş yapın..." -ForegroundColor Cyan
    Write-Host ""
    gcloud auth login --no-launch-browser 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Authentication başarısız!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Manuel olarak çalıştırın:" -ForegroundColor Yellow
        Write-Host "  gcloud auth login" -ForegroundColor White
        exit 1
    }
} else {
    Write-Host "✓ Authenticated: $authList" -ForegroundColor Green
}
Write-Host ""

# ADIM 2: Proje Ayarlama
Write-Host "[ADIM 2/6] Proje ayarlanıyor..." -ForegroundColor Yellow
$currentProject = gcloud config get-value project 2>&1
if ($currentProject -ne $PROJECT_ID) {
    gcloud config set project $PROJECT_ID 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠ Proje ayarlanamadı, devam ediliyor..." -ForegroundColor Yellow
    } else {
        Write-Host "✓ Proje ayarlandı: $PROJECT_ID" -ForegroundColor Green
    }
} else {
    Write-Host "✓ Proje zaten ayarlı: $PROJECT_ID" -ForegroundColor Green
}
Write-Host ""

# ADIM 3: Gerekli API'leri Aktif Etme
Write-Host "[ADIM 3/6] Gerekli API'ler kontrol ediliyor..." -ForegroundColor Yellow
$apis = @(
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "containerregistry.googleapis.com"
)

foreach ($api in $apis) {
    Write-Host "  Checking $api..." -ForegroundColor Gray
    $enabled = gcloud services list --enabled --filter="name:$api" --format="value(name)" 2>&1
    if ([string]::IsNullOrWhiteSpace($enabled)) {
        Write-Host "  Enabling $api..." -ForegroundColor Yellow
        gcloud services enable $api --project=$PROJECT_ID 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ $api aktif edildi" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ $api aktif edilemedi (izin gerekebilir)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ✓ $api zaten aktif" -ForegroundColor Green
    }
}
Write-Host ""

# ADIM 4: İzin Kontrolü
Write-Host "[ADIM 4/6] İzinler kontrol ediliyor..." -ForegroundColor Yellow
$account = gcloud config get-value account 2>&1
Write-Host "  Hesap: $account" -ForegroundColor Gray

# Test: Proje erişimi
$projectTest = gcloud projects describe $PROJECT_ID 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Proje erişilebilir" -ForegroundColor Green
} else {
    Write-Host "  ❌ Proje erişilemiyor!" -ForegroundColor Red
    Write-Host ""
    Write-Host "IAM sayfasından izin kontrol edin:" -ForegroundColor Yellow
    Write-Host "  https://console.cloud.google.com/iam-admin/iam?project=$PROJECT_ID" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Gerekli roller:" -ForegroundColor Yellow
    Write-Host "  - Cloud Run Admin (roles/run.admin)" -ForegroundColor White
    Write-Host "  - Cloud Build Editor (roles/cloudbuild.builds.editor)" -ForegroundColor White
    Write-Host "  VEYA Owner/Editor rolü" -ForegroundColor White
    exit 1
}

# Test: Cloud Run erişimi
$runTest = gcloud run services list --region $REGION --limit 1 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Cloud Run erişilebilir" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Cloud Run erişiminde sorun olabilir" -ForegroundColor Yellow
    Write-Host "  Devam ediliyor..." -ForegroundColor Gray
}
Write-Host ""

# ADIM 5: Deployment Öncesi Kontroller
Write-Host "[ADIM 5/6] Deployment öncesi kontroller..." -ForegroundColor Yellow

# Dockerfile kontrolü
if (Test-Path "dockerfile") {
    Write-Host "  ✓ dockerfile bulundu" -ForegroundColor Green
} else {
    Write-Host "  ❌ dockerfile bulunamadı!" -ForegroundColor Red
    exit 1
}

# requirements.txt kontrolü
if (Test-Path "requirements.txt") {
    Write-Host "  ✓ requirements.txt bulundu" -ForegroundColor Green
} else {
    Write-Host "  ⚠ requirements.txt bulunamadı" -ForegroundColor Yellow
}

# Frontend dosyaları kontrolü
$frontendFiles = @("index.html", "upload.html", "results.html", "archive-save.html", "login.html")
$missingFiles = @()
foreach ($file in $frontendFiles) {
    if (-not (Test-Path "frontend\$file")) {
        $missingFiles += $file
    }
}
if ($missingFiles.Count -eq 0) {
    Write-Host "  ✓ Tüm frontend dosyaları mevcut" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Eksik dosyalar: $($missingFiles -join ', ')" -ForegroundColor Yellow
}
Write-Host ""

# ADIM 6: Deployment
Write-Host "[ADIM 6/6] Cloud Run'a deploy ediliyor..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Bu işlem 5-10 dakika sürebilir..." -ForegroundColor Gray
Write-Host "Docker image build ediliyor..." -ForegroundColor Gray
Write-Host ""

$deployStart = Get-Date
gcloud run deploy $SERVICE_NAME `
    --source . `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --port 8080 `
    --project $PROJECT_ID `
    --quiet 2>&1

$deployResult = $LASTEXITCODE
$deployDuration = (Get-Date) - $deployStart

Write-Host ""

if ($deployResult -eq 0) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ Deployment Başarılı!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Süre: $([math]::Round($deployDuration.TotalMinutes, 1)) dakika" -ForegroundColor Cyan
    Write-Host ""
    
    # Service URL al
    Write-Host "Service bilgileri alınıyor..." -ForegroundColor Yellow
    $serviceUrl = gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)" 2>&1
    
    if ($serviceUrl -and -not $serviceUrl.StartsWith("ERROR")) {
        Write-Host ""
        Write-Host "Service URL: $serviceUrl" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Frontend Sayfaları:" -ForegroundColor Yellow
        Write-Host "  🏠 Ana Sayfa:    $serviceUrl/ui/index.html" -ForegroundColor White
        Write-Host "  📤 Upload:       $serviceUrl/ui/upload.html" -ForegroundColor White
        Write-Host "  📊 Results:      $serviceUrl/ui/results.html" -ForegroundColor White
        Write-Host "  💾 Archive:      $serviceUrl/ui/archive-save.html" -ForegroundColor White
        Write-Host "  🔐 Login:        $serviceUrl/ui/login.html" -ForegroundColor White
        Write-Host ""
        Write-Host "API Endpoints:" -ForegroundColor Yellow
        Write-Host "  ❤️  Health:       $serviceUrl/health" -ForegroundColor White
        Write-Host "  📚 API Docs:      $serviceUrl/docs" -ForegroundColor White
        Write-Host ""
        
        # Health check
        Write-Host "Health check yapılıyor..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
        try {
            $healthResponse = Invoke-WebRequest -Uri "$serviceUrl/health" -UseBasicParsing -TimeoutSec 10 -ErrorAction SilentlyContinue
            if ($healthResponse.StatusCode -eq 200) {
                Write-Host "✓ Health check başarılı!" -ForegroundColor Green
            }
        } catch {
            Write-Host "⚠ Health check zaman aşımı (servis başlıyor olabilir)" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "ÖNEMLİ: Browser Cache Temizleme" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Yeni değişiklikleri görmek için:" -ForegroundColor Yellow
    Write-Host "  1. Ctrl+Shift+R (Hard Refresh)" -ForegroundColor White
    Write-Host "  2. VEYA Ctrl+Shift+Delete ile cache temizle" -ForegroundColor White
    Write-Host "  3. VEYA Gizli pencere kullan" -ForegroundColor White
    Write-Host ""
    
} else {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "❌ Deployment Başarısız!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Süre: $([math]::Round($deployDuration.TotalMinutes, 1)) dakika" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Olası nedenler:" -ForegroundColor Yellow
    Write-Host "  1. IAM izinleri eksik olabilir" -ForegroundColor White
    Write-Host "  2. APIler aktif olmayabilir" -ForegroundColor White
    Write-Host "  3. Build hatası olabilir" -ForegroundColor White
    Write-Host ""
    Write-Host "Yardım:" -ForegroundColor Yellow
    Write-Host "  - Logları kontrol edin:" -ForegroundColor White
    Write-Host "    gcloud run logs read $SERVICE_NAME --region $REGION --limit 50" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  - IAM izinlerini kontrol edin:" -ForegroundColor White
    Write-Host "    https://console.cloud.google.com/iam-admin/iam?project=$PROJECT_ID" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  - Build loglarını kontrol edin:" -ForegroundColor White
    Write-Host "    https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host ""

