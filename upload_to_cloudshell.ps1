# Local dosyaları Cloud Shell'e yükleme script'i
# PowerShell'de bu script'i çalıştırın

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Local Dosyaları Cloud Shell'e Yükleme" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$LOCAL_DIR = "C:\Users\issan\records_ai_v2"
$CLOUD_SHELL_DIR = "~/records_ai_v2"

Write-Host "Local dizin: $LOCAL_DIR" -ForegroundColor Green
Write-Host "Cloud Shell hedef: $CLOUD_SHELL_DIR" -ForegroundColor Green
Write-Host ""

# Check if gcloud is available
$gcloudCmd = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudCmd) {
    Write-Host "❌ gcloud bulunamadı!" -ForegroundColor Red
    Write-Host "   Google Cloud CLI kurun: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

Write-Host "⚠ NOT: Bu yöntem tüm dosyaları yükleyebilir ama zaman alabilir." -ForegroundColor Yellow
Write-Host "   Alternatif: Cloud Shell Editor → Upload Files (ZIP olarak)" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "Devam etmek istiyor musunuz? (Y/N)"

if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "İptal edildi." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternatif: Cloud Shell Editor kullanarak ZIP yükleyin:" -ForegroundColor Cyan
    Write-Host "1. Cloud Shell'de Editor açın" -ForegroundColor White
    Write-Host "2. File → Upload Files" -ForegroundColor White
    Write-Host "3. records_ai_v2 klasörünü ZIP yapıp yükleyin" -ForegroundColor White
    exit 0
}

Write-Host ""
Write-Host "Dosyalar Cloud Shell'e yükleniyor..." -ForegroundColor Yellow
Write-Host "Bu işlem birkaç dakika sürebilir..." -ForegroundColor Gray
Write-Host ""

# Upload files using gcloud cloud-shell scp
# Note: This command may vary depending on gcloud version
gcloud cloud-shell scp --recurse "$LOCAL_DIR/*" "cloudshell:$CLOUD_SHELL_DIR/"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Dosyalar Cloud Shell'e yüklendi!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Şimdi Cloud Shell'de şu komutları çalıştırın:" -ForegroundColor Cyan
    Write-Host "  cd ~/records_ai" -ForegroundColor White
    Write-Host "  cp -r ~/records_ai_v2/* ." -ForegroundColor White
    Write-Host "  git status" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "⚠ Upload başarısız olabilir." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternatif yöntem: Cloud Shell Editor" -ForegroundColor Cyan
    Write-Host "1. Cloud Shell'de Editor açın" -ForegroundColor White
    Write-Host "2. File → Upload Files" -ForegroundColor White
    Write-Host "3. records_ai_v2 klasörünü ZIP yapıp yükleyin" -ForegroundColor White
}

Write-Host ""
