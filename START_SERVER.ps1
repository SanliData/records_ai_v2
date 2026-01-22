# Start Server Script - Records AI V2
# Run: .\START_SERVER.ps1

$pythonPath = "C:\Users\issan\AppData\Local\Programs\Python\Python313\python.exe"

if (-not (Test-Path $pythonPath)) {
    Write-Host "❌ Python not found at: $pythonPath" -ForegroundColor Red
    Write-Host "Please update the path in START_SERVER.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Records AI V2 Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Python: $pythonPath" -ForegroundColor Green
Write-Host "Port: 8082" -ForegroundColor Green
Write-Host ""
Write-Host "Server will start at: http://127.0.0.1:8082" -ForegroundColor Yellow
Write-Host "Press CTRL+C to stop" -ForegroundColor Yellow
Write-Host ""

& $pythonPath main.py
