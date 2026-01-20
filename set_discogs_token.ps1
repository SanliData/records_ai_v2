# Set Discogs Token for Local Development
# Usage: .\set_discogs_token.ps1

$tokenFile = ".discogs_token.txt"

if (Test-Path $tokenFile) {
    $token = Get-Content $tokenFile -Raw | ForEach-Object { $_.Trim() }
    $env:DISCOGS_TOKEN = $token
    Write-Host "✅ DISCOGS_TOKEN set from $tokenFile" -ForegroundColor Green
    Write-Host "   Token (first 10 chars): $($token.Substring(0, [Math]::Min(10, $token.Length)))..." -ForegroundColor Gray
} else {
    Write-Host "❌ Token file not found: $tokenFile" -ForegroundColor Red
    Write-Host "   Create it with: echo 'your_token' > $tokenFile" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "📋 To verify:" -ForegroundColor Cyan
Write-Host "   `$env:DISCOGS_TOKEN" -ForegroundColor Gray
Write-Host ""
Write-Host "📋 To start server with token:" -ForegroundColor Cyan
Write-Host "   .\set_discogs_token.ps1" -ForegroundColor Gray
Write-Host "   uvicorn backend.main:app --reload" -ForegroundColor Gray
