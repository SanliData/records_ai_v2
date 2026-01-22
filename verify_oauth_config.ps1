# Verify Google OAuth Configuration
# This script checks if OAuth endpoints are accessible

Write-Host "=== Google OAuth Configuration Verification ===" -ForegroundColor Cyan
Write-Host ""

# Check if OAuth endpoint exists
$apiBase = "http://127.0.0.1:8000"
Write-Host "Testing OAuth endpoint: $apiBase/auth/login/google" -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "$apiBase/auth/login/google" -Method POST -Body '{"token":"test"}' -ContentType "application/json" -ErrorAction Stop
    Write-Host "✅ OAuth endpoint exists (status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "✅ OAuth endpoint exists (401 = authentication required, which is expected)" -ForegroundColor Green
    } elseif ($_.Exception.Response.StatusCode -eq 422) {
        Write-Host "✅ OAuth endpoint exists (422 = validation error, endpoint is working)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  OAuth endpoint may have issues: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== Manual Verification Steps ===" -ForegroundColor Cyan
Write-Host "1. Open: https://console.cloud.google.com/apis/credentials/consent" -ForegroundColor Yellow
Write-Host "2. Verify User Type = External" -ForegroundColor Yellow
Write-Host "3. Verify Status = In production" -ForegroundColor Yellow
Write-Host "4. Verify Test Users includes: isanli058@gmail.com" -ForegroundColor Yellow
Write-Host "5. Try logging in from browser" -ForegroundColor Yellow
Write-Host ""
