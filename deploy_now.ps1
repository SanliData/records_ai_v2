# Quick Deploy Script - Records AI V2 to Cloud Run
# Run: .\deploy_now.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Records AI V2 - Deploy to Cloud Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_ID = "records-ai"
$SERVICE_NAME = "records-ai-v2"
$REGION = "us-central1"

Write-Host "Project: $PROJECT_ID" -ForegroundColor Green
Write-Host "Service: $SERVICE_NAME" -ForegroundColor Green
Write-Host "Region: $REGION" -ForegroundColor Green
Write-Host ""

# Check gcloud
Write-Host "[1/5] Checking gcloud..." -ForegroundColor Yellow
$gcloud = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloud) {
    Write-Host "❌ gcloud not found! Install Google Cloud CLI." -ForegroundColor Red
    Write-Host "   https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ gcloud found" -ForegroundColor Green
Write-Host ""

# Check authentication
Write-Host "[2/5] Checking authentication..." -ForegroundColor Yellow
$authCheck = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $authCheck -or $authCheck -match "ERROR") {
    Write-Host "❌ Not authenticated. Please run:" -ForegroundColor Red
    Write-Host "   gcloud auth login" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Or use application default credentials:" -ForegroundColor Yellow
    Write-Host "   gcloud auth application-default login" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Authenticated as: $authCheck" -ForegroundColor Green
Write-Host ""

# Set project
Write-Host "[3/5] Setting project..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Failed to set project. Continuing anyway..." -ForegroundColor Yellow
}
Write-Host "✅ Project: $PROJECT_ID" -ForegroundColor Green
Write-Host ""

# Deploy
Write-Host "[4/5] Deploying to Cloud Run..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes..." -ForegroundColor Gray
Write-Host ""

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
    --cpu 1

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. gcloud auth login" -ForegroundColor White
    Write-Host "  2. gcloud auth application-default login" -ForegroundColor White
    Write-Host "  3. Check project permissions" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "[5/5] Getting service URL..." -ForegroundColor Yellow
$serviceUrl = gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)" 2>&1

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

if ($serviceUrl -and -not $serviceUrl.StartsWith("ERROR")) {
    Write-Host "Service URL: $serviceUrl" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Test Endpoints:" -ForegroundColor Yellow
    Write-Host "  Health:    $serviceUrl/health" -ForegroundColor White
    Write-Host "  Whoami:    $serviceUrl/auth/whoami" -ForegroundColor White
    Write-Host "  Bootstrap: $serviceUrl/admin/bootstrap-user" -ForegroundColor White
    Write-Host ""
    Write-Host "Verify endpoints:" -ForegroundColor Yellow
    Write-Host "  .\verify_endpoints.ps1 -Port 8080" -ForegroundColor White
    Write-Host "  (Update API_BASE_URL to $serviceUrl)" -ForegroundColor Gray
} else {
    Write-Host "Service URL could not be retrieved." -ForegroundColor Yellow
    Write-Host "Check Cloud Console:" -ForegroundColor White
    Write-Host "https://console.cloud.google.com/run?project=$PROJECT_ID" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
