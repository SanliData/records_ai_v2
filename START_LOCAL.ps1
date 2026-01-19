# Local Server Start Script
# Run this from project root: C:\Users\issan\records_ai_v2

Write-Host "=== Starting Local Server ===" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
$projectDir = "C:\Users\issan\records_ai_v2"
Set-Location $projectDir
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow

# Check if virtual environment exists
$venvPath = Join-Path $projectDir ".venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & $venvPath
} else {
    Write-Host "❌ Virtual environment not found at: $venvPath" -ForegroundColor Red
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    
    # Check if Python is available
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        Write-Host "❌ Python not found. Please install Python first." -ForegroundColor Red
        exit 1
    }
    
    python -m venv .venv
    if (Test-Path $venvPath) {
        Write-Host "✅ Virtual environment created" -ForegroundColor Green
        & $venvPath
    } else {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Installing/updating dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

Write-Host ""
Write-Host "Starting server..." -ForegroundColor Green
Write-Host "Server will be available at: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start server
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
