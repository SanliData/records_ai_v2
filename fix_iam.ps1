# IAM Policy Fix for Cloud Run Service
# Public erişim için IAM policy ayarlama

Write-Host "IAM Policy ayarlanıyor..." -ForegroundColor Yellow

# Alternatif yöntem: Cloud Console'dan veya gcloud CLI ile
Write-Host ""
Write-Host "Public erişim için şu komutu çalıştırın:" -ForegroundColor Cyan
Write-Host ""
Write-Host 'gcloud run services add-iam-policy-binding records-ai-v2 \' -ForegroundColor Green
Write-Host '  --region=europe-west1 \' -ForegroundColor Green
Write-Host '  --member="allUsers" \' -ForegroundColor Green
Write-Host '  --role="roles/run.invoker"' -ForegroundColor Green
Write-Host ""
Write-Host "VEYA Cloud Console'dan:" -ForegroundColor Cyan
Write-Host "1. https://console.cloud.google.com/run adresine gidin" -ForegroundColor White
Write-Host "2. records-ai-v2 servisini seçin" -ForegroundColor White
Write-Host "3. 'PERMISSIONS' sekmesine gidin" -ForegroundColor White
Write-Host "4. 'ADD PRINCIPAL' butonuna tıklayın" -ForegroundColor White
Write-Host "5. Principal: allUsers" -ForegroundColor White
Write-Host "6. Role: Cloud Run Invoker" -ForegroundColor White
Write-Host "7. Save" -ForegroundColor White




