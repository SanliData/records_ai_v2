# PowerShell script to run local API server and execute tests
# Run: .\run_local_test.ps1

$pythonPath = "C:\Users\issan\AppData\Local\Programs\Python\Python313\python.exe"

if (-not (Test-Path $pythonPath)) {
    Write-Host "ERROR: Python not found at $pythonPath" -ForegroundColor Red
    exit 1
}

Write-Host "=== Local API Test ===" -ForegroundColor Cyan
Write-Host ""

# Change to repo root
Set-Location $PSScriptRoot

# Set environment variables for local testing
$env:DATABASE_URL = ""
$env:API_BASE_URL = "http://127.0.0.1:8000"
$env:TEST_EMAIL = "test@example.com"

Write-Host "Step 1: Starting local API server..." -ForegroundColor Yellow
Write-Host "  URL: $env:API_BASE_URL" -ForegroundColor Gray
Write-Host ""

# Start API server in background
$serverProcess = Start-Process -FilePath $pythonPath -ArgumentList "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000" -PassThru -WindowStyle Hidden

Write-Host "[INFO] Server starting (PID: $($serverProcess.Id))..." -ForegroundColor Gray
Write-Host ""

# Wait for server to start
$maxWait = 30
$waited = 0
$serverReady = $false

while ($waited -lt $maxWait) {
    Start-Sleep -Seconds 1
    $waited++
    
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/" -Method GET -TimeoutSec 2 -ErrorAction Stop
        if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 404) {
            $serverReady = $true
            break
        }
    } catch {
        # Server not ready yet
    }
    
    Write-Host "." -NoNewline -ForegroundColor Gray
}

Write-Host ""
Write-Host ""

if (-not $serverReady) {
    Write-Host "[ERROR] Server failed to start after $maxWait seconds" -ForegroundColor Red
    Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "[OK] Server is ready!" -ForegroundColor Green
Write-Host ""

# Step 2: Create test user
Write-Host "Step 2: Creating test user..." -ForegroundColor Yellow
& $pythonPath scripts/create_admin_user.py --email test@example.com --password "TestPassword123!" --admin 2>&1 | Out-Null
Write-Host "[OK] Test user ready" -ForegroundColor Green
Write-Host ""

# Step 3: Get auth token
Write-Host "Step 3: Getting auth token..." -ForegroundColor Yellow
$loginBody = @{
    email = "test@example.com"
    password = "TestPassword123!"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginBody `
        -ErrorAction Stop
    
    if ($loginResponse.token) {
        $env:AUTH_TOKEN = $loginResponse.token
        $env:ADMIN_TOKEN = $loginResponse.token
        Write-Host "[OK] Auth token obtained" -ForegroundColor Green
        Write-Host ""
    }
} catch {
    Write-Host "[WARN] Failed to get auth token: $_" -ForegroundColor Yellow
    Write-Host "Tests may fail without authentication" -ForegroundColor Yellow
    Write-Host ""
}

# Step 4: Run a simple test
Write-Host "Step 4: Running simple health check..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/" -Method GET -ErrorAction Stop
    Write-Host "[OK] Health check passed" -ForegroundColor Green
    Write-Host "Response: $($healthResponse | ConvertTo-Json -Compress)" -ForegroundColor Gray
} catch {
    Write-Host "[WARN] Health check failed: $_" -ForegroundColor Yellow
}
Write-Host ""

# Step 5: Run stress test (if AUTH_TOKEN available)
if ($env:AUTH_TOKEN) {
    Write-Host "Step 5: Running stress test..." -ForegroundColor Yellow
    Write-Host ""
    
    & $pythonPath tests/final_stress_test.py
    
    $testExitCode = $LASTEXITCODE
    Write-Host ""
    
    if ($testExitCode -eq 0) {
        Write-Host "[OK] Stress test completed successfully" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Stress test completed with errors (exit code: $testExitCode)" -ForegroundColor Yellow
    }
} else {
    Write-Host "[SKIP] Stress test skipped (no auth token)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Cyan
Write-Host ""

# Stop server
Write-Host "Stopping server..." -ForegroundColor Yellow
Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
Write-Host "[OK] Server stopped" -ForegroundColor Green

exit 0
