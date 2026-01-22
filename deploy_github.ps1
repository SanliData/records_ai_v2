# Deploy Records AI V2 from GitHub to Cloud Run
# Usage: .\deploy_github.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Records AI V2 - Deploy from GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_ID = "records-ai"
$SERVICE_NAME = "records-ai-v2"
$REGION = "us-central1"
$BRANCH = "main"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Project: $PROJECT_ID" -ForegroundColor Green
Write-Host "  Service: $SERVICE_NAME" -ForegroundColor Green
Write-Host "  Region: $REGION" -ForegroundColor Green
Write-Host ""

# 1. Check git status
Write-Host "[1/4] Checking git status..." -ForegroundColor Yellow
$gitStatus = git status --short
if ($gitStatus) {
    Write-Host "Uncommitted changes found:" -ForegroundColor Yellow
    git status --short
    Write-Host ""
    $commit = Read-Host "Commit and push first? (Y/N)"
    if ($commit -eq "Y" -or $commit -eq "y") {
        Write-Host ""
        Write-Host "Commit message:" -ForegroundColor Yellow
        $message = Read-Host
        if (-not $message) {
            $message = "Update before deployment"
        }
        git add .
        git commit -m $message
        Write-Host "Commit done" -ForegroundColor Green
        Write-Host ""
        Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
        git push origin $BRANCH
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Push failed!" -ForegroundColor Red
            exit 1
        }
        Write-Host "Pushed to GitHub" -ForegroundColor Green
        Write-Host ""
    }
} else {
    Write-Host "Git is clean" -ForegroundColor Green
    Write-Host ""
}

# 2. Check authentication
Write-Host "[2/4] Checking authentication..." -ForegroundColor Yellow
$authCheck = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $authCheck -or $authCheck -match "ERROR") {
    Write-Host "Not authenticated. Please run:" -ForegroundColor Red
    Write-Host "   gcloud auth login" -ForegroundColor Yellow
    exit 1
}
Write-Host "Authenticated: $authCheck" -ForegroundColor Green
Write-Host ""

# 3. Set project
Write-Host "[3/4] Setting project..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Could not set project, continuing..." -ForegroundColor Yellow
}
Write-Host "Project: $PROJECT_ID" -ForegroundColor Green
Write-Host ""

# 4. Deploy to Cloud Run
Write-Host "[4/4] Deploying to Cloud Run..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes..." -ForegroundColor Gray
Write-Host ""

# Fetch latest code from GitHub
Write-Host "Fetching latest code from GitHub..." -ForegroundColor Cyan
git fetch origin $BRANCH
git checkout $BRANCH
Write-Host "Code is up to date" -ForegroundColor Green
Write-Host ""

# Deploy from local source (after fetching from GitHub)
Write-Host "Building and deploying..." -ForegroundColor Cyan
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

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Deployment failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative: Manual deploy from Cloud Console:" -ForegroundColor Yellow
    Write-Host "1. https://console.cloud.google.com/run?project=$PROJECT_ID" -ForegroundColor Cyan
    Write-Host "2. Select service > Deploy new revision" -ForegroundColor White
    Write-Host "3. Use Continuously deploy option (GitHub trigger)" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "[5/5] Getting service URL..." -ForegroundColor Yellow
$serviceUrl = gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)" 2>&1

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

if ($serviceUrl -and -not $serviceUrl.StartsWith("ERROR")) {
    Write-Host "Service URL: $serviceUrl" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Test Endpoints:" -ForegroundColor Yellow
    Write-Host "  Health:    $serviceUrl/health" -ForegroundColor White
    Write-Host "  Docs:      $serviceUrl/docs" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "Could not get service URL" -ForegroundColor Yellow
    Write-Host "Check Cloud Console:" -ForegroundColor White
    Write-Host "https://console.cloud.google.com/run?project=$PROJECT_ID" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
