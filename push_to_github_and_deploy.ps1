# GitHub'a Push ve Production Deploy Script
# Records AI V2 - Local değişiklikleri GitHub'a push edip canlıya alır

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Records AI V2 - GitHub Push & Deploy" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$GITHUB_REPO = "https://github.com/SanliData/records_ai.git"
$PROJECT_ID = "records-ai"
$SERVICE_NAME = "records-ai-v2"
$REGION = "europe-west1"

Write-Host "Repository: $GITHUB_REPO" -ForegroundColor Green
Write-Host "Project: $PROJECT_ID" -ForegroundColor Green
Write-Host "Service: $SERVICE_NAME" -ForegroundColor Green
Write-Host ""

# Check if Git is available
Write-Host "[1/4] Checking Git installation..." -ForegroundColor Yellow
$gitCmd = Get-Command git -ErrorAction SilentlyContinue

if (-not $gitCmd) {
    Write-Host "❌ Git bulunamadı!" -ForegroundColor Red
    Write-Host ""
    Write-Host "SEÇENEK A: Cloud Shell kullanarak GitHub'a push" -ForegroundColor Yellow
    Write-Host "  1. Google Cloud Shell'i açın: https://console.cloud.google.com/cloudshell" -ForegroundColor White
    Write-Host "  2. Aşağıdaki komutları Cloud Shell'de çalıştırın:" -ForegroundColor White
    Write-Host ""
    Write-Host "  cd ~" -ForegroundColor Cyan
    Write-Host "  git clone $GITHUB_REPO" -ForegroundColor Cyan
    Write-Host "  cd records_ai" -ForegroundColor Cyan
    Write-Host "  # Local'deki dosyaları buraya kopyalayın veya Cloud Shell Upload ile yükleyin" -ForegroundColor Gray
    Write-Host "  git add ." -ForegroundColor Cyan
    Write-Host "  git commit -m 'feat: Local changes from records_ai_v2'" -ForegroundColor Cyan
    Write-Host "  git push origin main" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "SEÇENEK B: Git kurulumu (önerilen)" -ForegroundColor Yellow
    Write-Host "  Git for Windows indirin: https://git-scm.com/download/win" -ForegroundColor White
    Write-Host "  Kurulum sonrası PowerShell'i yeniden başlatın" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Devam etmek için 'D' (Deploy without push) veya 'C' (Cancel) yazın"
    if ($choice -eq "D" -or $choice -eq "d") {
        Write-Host ""
        Write-Host "⚠ GitHub'a push olmadan direkt deploy ediliyor..." -ForegroundColor Yellow
        $skipGit = $true
    } else {
        Write-Host "İptal edildi." -ForegroundColor Yellow
        exit 0
    }
} else {
    Write-Host "✓ Git bulundu: $($gitCmd.Source)" -ForegroundColor Green
    Write-Host ""
    $skipGit = $false
}

# Git operations (if Git is available)
if (-not $skipGit) {
    Write-Host "[2/4] Git işlemleri..." -ForegroundColor Yellow
    
    # Check current directory
    $currentDir = Get-Location
    Write-Host "Current directory: $currentDir" -ForegroundColor Gray
    
    # Check git status
    Write-Host "Git durumu kontrol ediliyor..." -ForegroundColor Gray
    $gitStatus = git status --short 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠ Git komutu hatası. Repository olmayabilir." -ForegroundColor Yellow
        
        # Try to initialize or check remote
        $remoteCheck = git remote -v 2>&1
        if ($LASTEXITCODE -eq 0 -and $remoteCheck) {
            Write-Host "Remote bulundu:" -ForegroundColor Gray
            Write-Host $remoteCheck -ForegroundColor Gray
        } else {
            Write-Host "Git remote ekleniyor..." -ForegroundColor Yellow
            git remote add origin $GITHUB_REPO 2>&1 | Out-Null
        }
    } else {
        if ($gitStatus) {
            Write-Host "Değişiklikler bulundu:" -ForegroundColor Green
            Write-Host $gitStatus -ForegroundColor Gray
        } else {
            Write-Host "✓ Tüm değişiklikler zaten commit edilmiş" -ForegroundColor Green
        }
    }
    
    # Ask for commit message
    Write-Host ""
    $commitMsg = Read-Host "Commit mesajı (Enter = varsayılan)"
    if ([string]::IsNullOrWhiteSpace($commitMsg)) {
        $commitMsg = "feat: Local changes - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    }
    
    # Add, commit, and push
    Write-Host ""
    Write-Host "Git işlemleri yapılıyor..." -ForegroundColor Yellow
    
    Write-Host "  git add ." -ForegroundColor Gray
    git add . 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Dosyalar eklendi" -ForegroundColor Green
    }
    
    Write-Host "  git commit -m `"$commitMsg`"" -ForegroundColor Gray
    git commit -m "$commitMsg" 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Commit oluşturuldu" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Commit hatası (değişiklik olmayabilir)" -ForegroundColor Yellow
    }
    
    # Push to GitHub
    Write-Host ""
    Write-Host "GitHub'a push ediliyor..." -ForegroundColor Yellow
    $pushConfirm = Read-Host "GitHub'a push edilsin mi? (Y/N)"
    
    if ($pushConfirm -eq "Y" -or $pushConfirm -eq "y") {
        Write-Host "  git push origin main" -ForegroundColor Gray
        git push origin main 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✓ GitHub'a başarıyla push edildi!" -ForegroundColor Green
            Write-Host "  Repository: $GITHUB_REPO" -ForegroundColor Cyan
        } else {
            Write-Host ""
            Write-Host "⚠ Push hatası oluştu." -ForegroundColor Yellow
            Write-Host "  Token veya authentication gerekebilir." -ForegroundColor Yellow
            Write-Host "  GitHub: Settings → Developer settings → Personal access tokens" -ForegroundColor White
        }
    } else {
        Write-Host "Push iptal edildi." -ForegroundColor Yellow
    }
    
    Write-Host ""
}

# Deployment
Write-Host "[3/4] Production deployment kontrolü..." -ForegroundColor Yellow

# Check gcloud
$gcloudCmd = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudCmd) {
    Write-Host "❌ gcloud bulunamadı!" -ForegroundColor Red
    Write-Host "   Google Cloud CLI kurun: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ gcloud bulundu" -ForegroundColor Green

# Check authentication
Write-Host "Authentication kontrol ediliyor..." -ForegroundColor Gray
$currentProject = gcloud config get-value project 2>&1
if ($LASTEXITCODE -ne 0 -or $currentProject -notmatch $PROJECT_ID) {
    Write-Host "⚠ Authentication gerekli veya proje yanlış!" -ForegroundColor Yellow
    Write-Host "  Çalıştırın: gcloud auth login" -ForegroundColor White
    Write-Host "  Çalıştırın: gcloud config set project $PROJECT_ID" -ForegroundColor White
} else {
    Write-Host "✓ Authenticated: $currentProject" -ForegroundColor Green
}

Write-Host ""

# Deploy confirmation
Write-Host "[4/4] Production Deployment" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠ Bu işlem canlı sisteme deploy edecek!" -ForegroundColor Yellow
Write-Host "  Service: $SERVICE_NAME" -ForegroundColor White
Write-Host "  Region: $REGION" -ForegroundColor White
Write-Host "  Source: Local files (--source .)" -ForegroundColor White
Write-Host ""

$deployConfirm = Read-Host "Production'a deploy edilsin mi? (Y/N)"

if ($deployConfirm -eq "Y" -or $deployConfirm -eq "y") {
    Write-Host ""
    Write-Host "Deploy başlatılıyor... (5-10 dakika sürebilir)" -ForegroundColor Yellow
    Write-Host ""
    
    # Set project
    gcloud config set project $PROJECT_ID 2>&1 | Out-Null
    
    # Deploy command
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
        
        # Get service URL
        $serviceUrl = gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)" 2>&1
        
        if ($serviceUrl -and -not $serviceUrl.StartsWith("ERROR")) {
            Write-Host "Service URL: $serviceUrl" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Test Sayfaları:" -ForegroundColor Yellow
            Write-Host "  Ana Sayfa: $serviceUrl/ui/index.html" -ForegroundColor White
            Write-Host "  Upload:    $serviceUrl/ui/upload.html" -ForegroundColor White
            Write-Host "  Health:    $serviceUrl/health" -ForegroundColor White
            Write-Host ""
            Write-Host "⚠ ÖNEMLİ: Browser cache temizleyin!" -ForegroundColor Yellow
            Write-Host "  Ctrl+Shift+R (hard refresh)" -ForegroundColor White
        }
    } else {
        Write-Host ""
        Write-Host "❌ Deployment başarısız!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Troubleshooting:" -ForegroundColor Yellow
        Write-Host "1. gcloud auth login" -ForegroundColor White
        Write-Host "2. gcloud config set project $PROJECT_ID" -ForegroundColor White
        Write-Host "3. QUICK_DEPLOY.ps1 script'ini deneyin" -ForegroundColor White
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "Deployment iptal edildi." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Manuel deploy için:" -ForegroundColor Cyan
    Write-Host "  .\QUICK_DEPLOY.ps1" -ForegroundColor White
    Write-Host "  veya" -ForegroundColor White
    Write-Host "  .\deploy_to_cloud_run.ps1" -ForegroundColor White
}

Write-Host ""
