# PowerShell script to install email-validator
# Run: .\install_email_validator.ps1

$pythonPath = "C:\Users\issan\AppData\Local\Programs\Python\Python313\python.exe"

if (-not (Test-Path $pythonPath)) {
    Write-Host "ERROR: Python not found at $pythonPath" -ForegroundColor Red
    exit 1
}

Write-Host "=== Installing email-validator ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Python: $pythonPath" -ForegroundColor Gray
Write-Host ""

Write-Host "Installing email-validator..." -ForegroundColor Yellow
& $pythonPath -m pip install email-validator 2>&1 | Out-Host

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ email-validator installed successfully" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Verifying installation..." -ForegroundColor Yellow
    $check = & $pythonPath -c "import email_validator; print('OK')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Verification passed" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "Testing admin_router import..." -ForegroundColor Yellow
        $test = & $pythonPath -c "from backend.api.v1.admin_router import router; print('admin_router imported OK')" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ admin_router imports successfully" -ForegroundColor Green
            Write-Host ""
            Write-Host "You can now start the server:" -ForegroundColor Cyan
            Write-Host "  .\start_local_server.ps1" -ForegroundColor Gray
        } else {
            Write-Host "❌ admin_router import failed:" -ForegroundColor Red
            Write-Host $test -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "❌ Verification failed:" -ForegroundColor Red
        Write-Host $check -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "❌ Installation failed" -ForegroundColor Red
    exit 1
}
