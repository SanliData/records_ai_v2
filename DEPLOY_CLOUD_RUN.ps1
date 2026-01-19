# Cloud Run Deployment Script (PowerShell)
# Deploys records_ai_v2 to Google Cloud Run

$PROJECT_ID = "records-ai"
$SERVICE_NAME = "records-ai-v2"
$REGION = "us-central1"

Write-Host "=== Cloud Run Deployment ===" -ForegroundColor Cyan
Write-Host "Project: $PROJECT_ID"
Write-Host "Service: $SERVICE_NAME"
Write-Host "Region: $REGION"
Write-Host ""

# Set project
Write-Host "Setting GCP project..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID

# Deploy from source
Write-Host "Deploying from source..." -ForegroundColor Yellow
gcloud run deploy $SERVICE_NAME `
  --source . `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --port 8080 `
  --max-instances 3 `
  --min-instances 0 `
  --timeout 300 `
  --memory 1Gi `
  --cpu 1 `
  --set-env-vars PORT=8080

# Get service URL
Write-Host ""
Write-Host "Getting service URL..." -ForegroundColor Yellow
$SERVICE_URL = gcloud run services describe $SERVICE_NAME `
  --region $REGION `
  --format="value(status.url)"

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "Service URL: $SERVICE_URL" -ForegroundColor Green
Write-Host ""
Write-Host "Testing health endpoint..."
try {
    $response = Invoke-WebRequest -Uri "$SERVICE_URL/health" -UseBasicParsing
    Write-Host $response.Content
} catch {
    Write-Host "Health check failed: $_" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "Done!" -ForegroundColor Green
