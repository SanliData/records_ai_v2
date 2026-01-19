# Deploy to zyagrolia.com - records_ai_v2 Repository
# PowerShell Deployment Script

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Records AI V2 - zyagrolia.com Deploy" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_ID = "records-ai"
$SERVICE_NAME = "records-ai-v2"
$REGION = "us-central1"  # USA'den upload için en uygun

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Project ID: $PROJECT_ID" -ForegroundColor Green
Write-Host "  Service: $SERVICE_NAME" -ForegroundColor Green
Write-Host "  Region: $REGION" -ForegroundColor Green
Write-Host "  Domain: zyagrolia.com" -ForegroundColor Green
Write-Host ""

# Check if gcloud is authenticated
Write-Host "[1/6] Checking authentication..." -ForegroundColor Yellow
$currentAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if ($LASTEXITCODE -ne 0 -or -not $currentAccount) {
    Write-Host "⚠ Authentication required!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run:" -ForegroundColor Yellow
    Write-Host "  gcloud auth login" -ForegroundColor White
    Write-Host ""
    exit 1
}
Write-Host "✓ Authenticated as: $currentAccount" -ForegroundColor Green
Write-Host ""

# Set project
Write-Host "[2/6] Setting project..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Failed to set project!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Project set: $PROJECT_ID" -ForegroundColor Green
Write-Host ""

# Check current directory
Write-Host "[3/6] Checking source directory..." -ForegroundColor Yellow
$currentDir = Get-Location
Write-Host "  Working directory: $currentDir" -ForegroundColor Gray

# Check if dockerfile exists
if (-not (Test-Path "dockerfile")) {
    Write-Host "⚠ dockerfile not found!" -ForegroundColor Red
    Write-Host "  Please run this script from the repository root." -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Source files ready" -ForegroundColor Green
Write-Host ""

# Deploy to Cloud Run
Write-Host "[4/6] Deploying to Cloud Run..." -ForegroundColor Yellow
Write-Host "  Region: $REGION" -ForegroundColor Gray
Write-Host "  Service: $SERVICE_NAME" -ForegroundColor Gray
Write-Host "  This will take 5-10 minutes..." -ForegroundColor Gray
Write-Host ""

$deployCmd = "gcloud run deploy $SERVICE_NAME " +
    "--source . " +
    "--platform managed " +
    "--region $REGION " +
    "--allow-unauthenticated " +
    "--port 8080 " +
    "--project $PROJECT_ID"

Write-Host "Deploy command:" -ForegroundColor Cyan
Write-Host "  $deployCmd" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "Deploy now? (Y/N)"
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "Deployment cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Starting deployment..." -ForegroundColor Yellow
Write-Host ""

Invoke-Expression $deployCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Check authentication: gcloud auth login" -ForegroundColor White
    Write-Host "2. Enable APIs:" -ForegroundColor White
    Write-Host "   gcloud services enable run.googleapis.com cloudbuild.googleapis.com" -ForegroundColor White
    Write-Host "3. Check Cloud Console logs" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "[5/6] Getting service URL..." -ForegroundColor Yellow
$serviceUrl = gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)" 2>&1

if ($LASTEXITCODE -eq 0 -and $serviceUrl) {
    Write-Host "✓ Service deployed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Deployment Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Cloud Run URL: $serviceUrl" -ForegroundColor Cyan
    Write-Host "Domain: https://zyagrolia.com" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Test URLs:" -ForegroundColor Yellow
    Write-Host "  Health:    https://zyagrolia.com/" -ForegroundColor White
    Write-Host "  Upload:    https://zyagrolia.com/ui/upload.html" -ForegroundColor White
    Write-Host "  Login:     https://zyagrolia.com/ui/login.html" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "⚠ Could not get service URL" -ForegroundColor Yellow
}

# Test health endpoint
Write-Host "[6/6] Testing deployment..." -ForegroundColor Yellow
try {
    $healthUrl = "https://zyagrolia.com/"
    $healthResponse = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 30 -ErrorAction Stop
    if ($healthResponse.StatusCode -eq 200) {
        Write-Host "✓ Health check passed!" -ForegroundColor Green
        Write-Host "  Response: $($healthResponse.Content)" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠ Health check failed or service still starting" -ForegroundColor Yellow
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Gray
    Write-Host "  Wait 1-2 minutes and try: https://zyagrolia.com/" -ForegroundColor White
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Wait 1-2 minutes for service to fully start" -ForegroundColor White
Write-Host "2. Clear browser cache (Ctrl+Shift+R)" -ForegroundColor White
Write-Host "3. Test: https://zyagrolia.com/ui/upload.html" -ForegroundColor White
Write-Host "4. Check logs: gcloud run logs read $SERVICE_NAME --region $REGION" -ForegroundColor White
Write-Host ""
