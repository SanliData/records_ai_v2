# Fix IAM Permissions - Records AI V2
# 403 Forbidden hatasını düzeltir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "403 Forbidden - IAM Permissions Fix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ID = "records-ai"
$SERVICE_NAME = "records-ai-v2"
$REGION = "europe-west1"

Write-Host "Proje: $PROJECT_ID" -ForegroundColor Green
Write-Host "Servis: $SERVICE_NAME" -ForegroundColor Green
Write-Host "Region: $REGION" -ForegroundColor Green
Write-Host ""

# Check gcloud
Write-Host "[1/3] Checking gcloud..." -ForegroundColor Yellow
$gcloud = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloud) {
    Write-Host "❌ gcloud bulunamadı!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ gcloud bulundu" -ForegroundColor Green
Write-Host ""

# Set project
Write-Host "[2/3] Setting project..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
Write-Host "✓ Proje: $PROJECT_ID" -ForegroundColor Green
Write-Host ""

# Fix IAM permissions
Write-Host "[3/3] Fixing IAM permissions..." -ForegroundColor Yellow
Write-Host "allUsers'a Cloud Run Invoker rolü veriliyor..." -ForegroundColor Gray
Write-Host ""

gcloud run services add-iam-policy-binding $SERVICE_NAME `
    --region=$REGION `
    --member="allUsers" `
    --role="roles/run.invoker" `
    --project=$PROJECT_ID

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ IAM Permissions Düzeltildi!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Service URL:" -ForegroundColor Yellow
    Write-Host "https://records-ai-v2-969278596906.europe-west1.run.app/ui/index.html" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Şimdi test edin!" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "❌ IAM permissions düzeltilemedi!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manuel olarak yapın:" -ForegroundColor Yellow
    Write-Host "1. Cloud Console'a gidin:" -ForegroundColor White
    Write-Host "   https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME/iam?project=$PROJECT_ID" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. 'Add principal' butonuna tıklayın" -ForegroundColor White
    Write-Host "3. Principal: allUsers" -ForegroundColor White
    Write-Host "4. Role: Cloud Run Invoker" -ForegroundColor White
    Write-Host "5. Save" -ForegroundColor White
}

Write-Host ""



