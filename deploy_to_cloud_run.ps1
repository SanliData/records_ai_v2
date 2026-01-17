# Google Cloud Run Deployment Script
# Records AI V2 - Frontend Refactoring Update
# Date: 2026-01-05

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Records AI V2 - Cloud Run Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_ID = "records-ai"
$SERVICE_NAME = "records-ai-v2"
$REGION = "europe-west1"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Project ID: $PROJECT_ID" -ForegroundColor Green
Write-Host "  Service: $SERVICE_NAME" -ForegroundColor Green
Write-Host "  Region: $REGION" -ForegroundColor Green
Write-Host ""

# Check if gcloud is authenticated
Write-Host "[1/5] Checking authentication..." -ForegroundColor Yellow
$currentProject = gcloud config get-value project 2>&1
if ($LASTEXITCODE -ne 0 -or $currentProject -notmatch $PROJECT_ID) {
    Write-Host "⚠ Authentication required or wrong project!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run:" -ForegroundColor Yellow
    Write-Host "  gcloud auth login" -ForegroundColor White
    Write-Host "  gcloud config set project $PROJECT_ID" -ForegroundColor White
    Write-Host ""
    exit 1
}
Write-Host "✓ Authenticated to project: $PROJECT_ID" -ForegroundColor Green
Write-Host ""

# Set project
Write-Host "[2/5] Setting project..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to set project!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Project set" -ForegroundColor Green
Write-Host ""

# Deploy using source (recommended method)
Write-Host "[3/5] Deploying to Cloud Run from source..." -ForegroundColor Yellow
Write-Host "This will build and deploy the latest code." -ForegroundColor Gray
Write-Host ""

$deployCmd = @(
    "gcloud run deploy $SERVICE_NAME",
    "--source .",
    "--platform managed",
    "--region $REGION",
    "--allow-unauthenticated",
    "--port 8080",
    "--project $PROJECT_ID"
)

# Optional: Add environment variables if needed
# $deployCmd += "--set-env-vars `"UPAP_ENABLE_OCR=false,UPAP_ENABLE_AI=false`""

Write-Host "Deploy command:" -ForegroundColor Cyan
Write-Host ($deployCmd -join " `n  ") -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "Deploy now? (Y/N)"
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "Deployment cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Starting deployment..." -ForegroundColor Yellow
Write-Host ""

$fullCmd = $deployCmd -join " "
Invoke-Expression $fullCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Check authentication: gcloud auth login" -ForegroundColor White
    Write-Host "2. Check project: gcloud config set project $PROJECT_ID" -ForegroundColor White
    Write-Host "3. Enable APIs: gcloud services enable run.googleapis.com cloudbuild.googleapis.com" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "[4/5] Getting service URL..." -ForegroundColor Yellow
$serviceUrl = gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)" 2>&1

if ($LASTEXITCODE -eq 0 -and $serviceUrl) {
    Write-Host "✓ Service deployed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Deployment Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Service URL: $serviceUrl" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Frontend Pages:" -ForegroundColor Yellow
    Write-Host "  Home:        $serviceUrl/ui/index.html" -ForegroundColor White
    Write-Host "  Upload:      $serviceUrl/ui/upload.html" -ForegroundColor White
    Write-Host "  Results:     $serviceUrl/ui/results.html" -ForegroundColor White
    Write-Host "  Archive:     $serviceUrl/ui/archive-save.html" -ForegroundColor White
    Write-Host "  Login:       $serviceUrl/ui/login.html" -ForegroundColor White
    Write-Host ""
    Write-Host "API Endpoints:" -ForegroundColor Yellow
    Write-Host "  Health:      $serviceUrl/health" -ForegroundColor White
    Write-Host "  API Docs:    $serviceUrl/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "[5/5] Testing health endpoint..." -ForegroundColor Yellow
    try {
        $healthResponse = Invoke-WebRequest -Uri "$serviceUrl/health" -UseBasicParsing -TimeoutSec 10
        if ($healthResponse.StatusCode -eq 200) {
            Write-Host "✓ Health check passed" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠ Health check failed (service may still be starting)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ Could not get service URL" -ForegroundColor Yellow
    Write-Host "Check Cloud Console: https://console.cloud.google.com/run?project=$PROJECT_ID" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Clear browser cache (Ctrl+Shift+R)" -ForegroundColor White
Write-Host "2. Test frontend pages" -ForegroundColor White
Write-Host "3. Verify UPAP endpoints" -ForegroundColor White
Write-Host "4. Check Cloud Run logs if needed: gcloud run logs read $SERVICE_NAME --region $REGION" -ForegroundColor White
Write-Host ""



