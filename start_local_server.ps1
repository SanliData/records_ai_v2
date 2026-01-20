# PowerShell script to start local API server
# Run: .\start_local_server.ps1

# Auto-detect Python path
$pythonPaths = @(
    "C:\Users\issan\AppData\Local\Programs\Python\Python313\python.exe",
    "C:\Users\issan\AppData\Local\Programs\Python\Python312\python.exe",
    "C:\Users\issan\AppData\Local\Programs\Python\Python311\python.exe",
    (Get-Command python -ErrorAction SilentlyContinue).Source,
    (Get-Command python3 -ErrorAction SilentlyContinue).Source,
    "python.exe",
    "py.exe"
)

$pythonPath = $null
foreach ($path in $pythonPaths) {
    if ($path -and (Test-Path $path)) {
        $version = & $path --version 2>&1
        if ($version -match "Python") {
            $pythonPath = $path
            break
        }
    } elseif ($path -match "^python|^py$") {
        try {
            $version = & $path --version 2>&1
            if ($version -match "Python") {
                $pythonPath = $path
                break
            }
        } catch {
            # Continue to next
        }
    }
}

# If still not found, try common Python installation paths
if (-not $pythonPath) {
    $commonPaths = Get-ChildItem "C:\Users\issan\AppData\Local\Programs\Python" -ErrorAction SilentlyContinue | 
                Where-Object { $_.PSIsContainer } | 
                Sort-Object Name -Descending |
                ForEach-Object { Join-Path $_.FullName "python.exe" }
    
    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            $pythonPath = $path
            break
        }
    }
}

if (-not $pythonPath -or -not (Test-Path $pythonPath)) {
    Write-Host "❌ Python not found!" -ForegroundColor Red
    Write-Host "Please install Python or update pythonPaths in this script" -ForegroundColor Yellow
    exit 1
}

Write-Host "=== Starting Local API Server ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Python found: $pythonPath" -ForegroundColor Green
Write-Host "   Version: $(& $pythonPath --version 2>&1)" -ForegroundColor Gray
Write-Host ""

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$checkDeps = & $pythonPath -c "import uvicorn, fastapi; print('OK')" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Dependencies missing - installing..." -ForegroundColor Yellow
    Write-Host ""
    
    $requirementsPath = Join-Path $PSScriptRoot "requirements.txt"
    if (Test-Path $requirementsPath) {
        Write-Host "Installing from requirements.txt..." -ForegroundColor Gray
        & $pythonPath -m pip install -q -r $requirementsPath 2>&1 | Out-Null
        # Explicitly ensure email-validator is installed (required for pydantic.EmailStr)
        & $pythonPath -m pip install -q email-validator 2>&1 | Out-Null
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
    Write-Host ""
}

# Check if port 8000 is in use
Write-Host "Checking port 8000..." -ForegroundColor Yellow
$portCheck = netstat -ano | findstr :8000
$port = 8000

if ($portCheck) {
    Write-Host "⚠️  Port 8000 is already in use" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "  1. Kill process using port 8000" -ForegroundColor Gray
    Write-Host "  2. Use different port (8001)" -ForegroundColor Gray
    Write-Host ""
    
    $choice = Read-Host "Choose option (1/2, default: 2)"
    
    if ($choice -eq "1") {
        # Find PID using port 8000
        $lines = netstat -ano | findstr :8000
        foreach ($line in $lines) {
            if ($line -match '\s+(\d+)$') {
                $pid = $matches[1]
                Write-Host "Killing process PID: $pid" -ForegroundColor Yellow
                taskkill /PID $pid /F 2>&1 | Out-Null
                Start-Sleep -Seconds 1
            }
        }
        Write-Host "[OK] Port 8000 freed" -ForegroundColor Green
    } else {
        $port = 8001
        Write-Host "[INFO] Using port $port instead" -ForegroundColor Cyan
    }
    Write-Host ""
}

Write-Host "Starting server on http://127.0.0.1:$port..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

# Start server (foreground)
Set-Location $PSScriptRoot
& $pythonPath -m uvicorn backend.main:app --host 127.0.0.1 --port $port
