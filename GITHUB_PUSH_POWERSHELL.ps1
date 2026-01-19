# PowerShell Script - GitHub Push with Token
# Repository: https://github.com/SanliData/records_ai_v2

$ErrorActionPreference = "Stop"

Write-Host "GitHub Push - Token Authentication" -ForegroundColor Cyan
Write-Host ""

# Configuration
$REPO_URL = "https://github.com/SanliData/records_ai_v2.git"
$TOKEN = "YOUR_GITHUB_TOKEN"
$BRANCH = "main"

# Build authenticated URL
$AUTH_URL = $REPO_URL -replace "https://", "https://$TOKEN@"

Write-Host "[1/3] Setting remote URL with token..." -ForegroundColor Yellow
git remote set-url origin $AUTH_URL
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to set remote URL" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Remote URL updated" -ForegroundColor Green
Write-Host ""

Write-Host "[2/3] Checking status..." -ForegroundColor Yellow
git status
Write-Host ""

Write-Host "[3/3] Pushing to GitHub..." -ForegroundColor Yellow
git push origin $BRANCH

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Push successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Repository: $REPO_URL" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Push failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Check token permissions (needs 'repo' scope)" -ForegroundColor White
    Write-Host "2. Verify token is not expired" -ForegroundColor White
    Write-Host "3. Check repository access" -ForegroundColor White
    exit 1
}
