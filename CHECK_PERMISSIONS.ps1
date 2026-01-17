# IAM İzin Kontrol Script'i
# Cloud Run deployment için gerekli izinleri kontrol eder

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "IAM İzin Kontrolü" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ID = "records-ai"
$SERVICE_NAME = "records-ai-v2"
$REGION = "europe-west1"

# Get current user
Write-Host "[1/4] Mevcut kullanıcı bilgisi..." -ForegroundColor Yellow
$currentAccount = gcloud config get-value account 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ gcloud authentication yapılmamış!" -ForegroundColor Red
    Write-Host "   gcloud auth login çalıştırın" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Kullanıcı: $currentAccount" -ForegroundColor Green
Write-Host ""

# Check project access
Write-Host "[2/4] Proje erişimi kontrol ediliyor..." -ForegroundColor Yellow
$project = gcloud projects describe $PROJECT_ID 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Proje erişilemiyor: $PROJECT_ID" -ForegroundColor Red
    Write-Host "   IAM izinlerinizi kontrol edin" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Proje erişilebilir: $PROJECT_ID" -ForegroundColor Green
Write-Host ""

# Check IAM roles
Write-Host "[3/4] IAM rolleriniz kontrol ediliyor..." -ForegroundColor Yellow
Write-Host ""

$roles = gcloud projects get-iam-policy $PROJECT_ID `
    --flatten="bindings[].members" `
    --format="value(bindings.role)" `
    --filter="bindings.members:user:$currentAccount" 2>&1

if ($LASTEXITCODE -eq 0 -and $roles) {
    Write-Host "Mevcut Rolleriniz:" -ForegroundColor Green
    $roles | ForEach-Object {
        Write-Host "  - $_" -ForegroundColor White
    }
    Write-Host ""
    
    # Check for required roles
    $hasRunAdmin = $roles -match "roles/run.admin" -or $roles -match "roles/owner" -or $roles -match "roles/editor"
    $hasCloudBuild = $roles -match "roles/cloudbuild" -or $roles -match "roles/owner" -or $roles -match "roles/editor"
    
    if ($hasRunAdmin) {
        Write-Host "✓ Cloud Run Admin izni var" -ForegroundColor Green
    } else {
        Write-Host "⚠ Cloud Run Admin izni YOK" -ForegroundColor Yellow
        Write-Host "  Deployment yapmak için gerekli!" -ForegroundColor Yellow
    }
    
    if ($hasCloudBuild) {
        Write-Host "✓ Cloud Build izni var" -ForegroundColor Green
    } else {
        Write-Host "⚠ Cloud Build izni YOK" -ForegroundColor Yellow
        Write-Host "  --source ile deployment için gerekli!" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ Roller alınamadı" -ForegroundColor Yellow
    Write-Host "  IAM sayfasından manuel kontrol edin:" -ForegroundColor White
    Write-Host "  https://console.cloud.google.com/iam-admin/iam?project=$PROJECT_ID" -ForegroundColor Cyan
}
Write-Host ""

# Test Cloud Run access
Write-Host "[4/4] Cloud Run erişimi test ediliyor..." -ForegroundColor Yellow
$services = gcloud run services list --region $REGION 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Cloud Run erişilebilir" -ForegroundColor Green
    Write-Host ""
    
    # Check if service exists
    $serviceExists = $services -match $SERVICE_NAME
    if ($serviceExists) {
        Write-Host "✓ Servis mevcut: $SERVICE_NAME" -ForegroundColor Green
        
        # Try to get service details (read permission test)
        $serviceInfo = gcloud run services describe $SERVICE_NAME --region $REGION 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Servis bilgisi alındı (okuma izni OK)" -ForegroundColor Green
        } else {
            Write-Host "⚠ Servis bilgisi alınamadı (okuma izni sorunu)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "ℹ Servis henüz oluşturulmamış (deployment ile oluşturulacak)" -ForegroundColor Cyan
    }
} else {
    Write-Host "❌ Cloud Run erişilemiyor" -ForegroundColor Red
    Write-Host "   Hata: $services" -ForegroundColor Red
    Write-Host "   IAM izinlerinizi kontrol edin" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Özet" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Final recommendation
if ($hasRunAdmin -and $hasCloudBuild) {
    Write-Host "✅ Tüm izinler mevcut! Deployment yapabilirsiniz." -ForegroundColor Green
    Write-Host ""
    Write-Host "Deployment komutu:" -ForegroundColor Yellow
    Write-Host "  .\QUICK_DEPLOY.ps1" -ForegroundColor White
    Write-Host "  VEYA" -ForegroundColor Gray
    Write-Host "  gcloud run deploy $SERVICE_NAME --source . --region $REGION" -ForegroundColor White
} else {
    Write-Host "⚠ Eksik izinler var!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Yapılacaklar:" -ForegroundColor Yellow
    Write-Host "1. IAM sayfasına gidin:" -ForegroundColor White
    Write-Host "   https://console.cloud.google.com/iam-admin/iam?project=$PROJECT_ID" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Email adresinizi bulun: $currentAccount" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Şu rolleri ekleyin:" -ForegroundColor White
    if (-not $hasRunAdmin) {
        Write-Host "   - Cloud Run Admin (roles/run.admin)" -ForegroundColor White
    }
    if (-not $hasCloudBuild) {
        Write-Host "   - Cloud Build Editor (roles/cloudbuild.builds.editor)" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "4. VEYA Owner/Editor rolü ekleyin (tüm izinler)" -ForegroundColor White
    Write-Host ""
    Write-Host "5. İzinler eklendikten sonra 1-2 dakika bekleyin" -ForegroundColor White
    Write-Host ""
    Write-Host "6. Bu script'i tekrar çalıştırın: .\CHECK_PERMISSIONS.ps1" -ForegroundColor White
}

Write-Host ""



