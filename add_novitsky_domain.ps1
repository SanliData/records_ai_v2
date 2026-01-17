# novitskyarchive.com Domain Mapping Script
# Cloud Run'a novitskyarchive.com domain'ini ekler

$ErrorActionPreference = "Stop"

Write-Host "=== novitskyarchive.com Domain Mapping ===" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_ID = "records-ai"
$SERVICE_NAME = "records-ai-v2"
$REGION = "us-central1"
$DOMAIN = "novitskyarchive.com"

Write-Host "Proje: $PROJECT_ID" -ForegroundColor Green
Write-Host "Servis: $SERVICE_NAME" -ForegroundColor Green
Write-Host "Region: $REGION" -ForegroundColor Green
Write-Host "Domain: $DOMAIN" -ForegroundColor Green
Write-Host ""

Write-Host "Not: Cloud Run domain mappings Cloud Console üzerinden eklenir." -ForegroundColor Yellow
Write-Host ""
Write-Host "Domain mapping eklemek için:" -ForegroundColor White
Write-Host "1. Cloud Console'a gidin:" -ForegroundColor White
$consoleUrl = "https://console.cloud.google.com/run/domains?project=$PROJECT_ID"
Write-Host $consoleUrl -ForegroundColor Cyan
Write-Host ""
Write-Host "2. 'Add mapping' butonuna tıklayın" -ForegroundColor White
Write-Host ""
Write-Host "3. Aşağıdaki bilgileri girin:" -ForegroundColor White
Write-Host "   Domain: $DOMAIN" -ForegroundColor Green
Write-Host "   Service: $SERVICE_NAME" -ForegroundColor Green
Write-Host "   Region: $REGION" -ForegroundColor Green
Write-Host ""
Write-Host "4. DNS kayıtlarını Google Workspace'te güncelleyin (Cloud Console'da gösterilecek)" -ForegroundColor White
Write-Host ""
Write-Host "Domain mapping tamamlandıktan sonra:" -ForegroundColor Yellow
$frontendUrl = "https://" + $DOMAIN + "/ui/"
$homeUrl = "https://" + $DOMAIN + "/"
Write-Host "Frontend: $frontendUrl" -ForegroundColor Cyan
Write-Host "Home: $homeUrl" -ForegroundColor Cyan
Write-Host ""
