# Quick Deploy - Records AI V2 to Cloud Run
# Auto-commits changes and deploys from GitHub

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Records AI V2 - Quick Deploy" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ID = "records-ai"
$SERVICE_NAME = "records-ai-v2"
$REGION = "us-central1"
$BRANCH = "main"

# Skip auto-commit - deploy directly
Write-Host "Deploying current code..." -ForegroundColor Yellow
Write-Host "(Commit manually if needed)" -ForegroundColor Gray

# Set project
gcloud config set project $PROJECT_ID 2>&1 | Out-Null

# Fetch latest
Write-Host "Fetching latest code..." -ForegroundColor Yellow
git fetch origin $BRANCH
git checkout $BRANCH

# Deploy
Write-Host ""
Write-Host "Deploying to Cloud Run..." -ForegroundColor Yellow
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
    --cpu 1 `
    --clear-base-image

if ($LASTEXITCODE -eq 0) {
    $serviceUrl = gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)" 2>&1
    Write-Host ""
    Write-Host "Deployment Complete!" -ForegroundColor Green
    if ($serviceUrl) {
        Write-Host "Service URL: $serviceUrl" -ForegroundColor Cyan
    }
} else {
    Write-Host "Deployment failed!" -ForegroundColor Red
}
