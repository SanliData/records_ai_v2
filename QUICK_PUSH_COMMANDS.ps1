# Quick Push Script - PowerShell
# Run this in PowerShell from project root

$ErrorActionPreference = "Stop"

Write-Host "=== Staging Files ===" -ForegroundColor Green
git add backend/main.py
git add backend/api/v1/upap_upload_router.py
git add backend/db.py
git add backend/core/error_handler.py
git add requirements.txt

Write-Host "`n=== Committing ===" -ForegroundColor Green
git commit -m "fix: critical security and stability fixes - auth, rate limiting, data persistence"

Write-Host "`n=== Pushing to GitHub ===" -ForegroundColor Green
git push https://SanliData:YOUR_GITHUB_TOKEN@github.com/SanliData/records_ai_v2.git main

Write-Host "`n=== Done! ===" -ForegroundColor Green
Write-Host "Next: Deploy from Cloud Shell" -ForegroundColor Yellow
