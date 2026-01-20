# Fix pip for Python 3.13 and install dependencies
# Run: .\fix_pip_install.ps1

$pythonPath = "C:\Users\issan\AppData\Local\Programs\Python\Python313\python.exe"

Write-Host "=== Fixing pip for Python 3.13 ===" -ForegroundColor Cyan
Write-Host ""

# Method 1: Download and reinstall pip using get-pip.py
Write-Host "Method 1: Reinstalling pip using get-pip.py..." -ForegroundColor Yellow

$getPipUrl = "https://bootstrap.pypa.io/get-pip.py"
$getPipFile = "$env:TEMP\get-pip.py"

try {
    Write-Host "Downloading get-pip.py..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $getPipUrl -OutFile $getPipFile -UseBasicParsing
    
    Write-Host "Running get-pip.py..." -ForegroundColor Yellow
    & $pythonPath $getPipFile --no-warn-script-location 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ pip reinstalled successfully" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host "⚠️  get-pip.py had issues, trying alternative..." -ForegroundColor Yellow
        Write-Host ""
    }
} catch {
    Write-Host "⚠️  Could not download get-pip.py: $_" -ForegroundColor Yellow
    Write-Host ""
}

# Method 2: Try installing without pip (using ensurepip)
Write-Host "Method 2: Using ensurepip..." -ForegroundColor Yellow
& $pythonPath -m ensurepip --default-pip 2>&1 | Out-Null

# Method 3: Try installing modules directly
Write-Host ""
Write-Host "Method 3: Installing dependencies..." -ForegroundColor Yellow

# Try to install aiohttp
Write-Host "Installing aiohttp..." -ForegroundColor Yellow
$aiohttpResult = & $pythonPath -m pip install --no-warn-script-location --disable-pip-version-check aiohttp 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ aiohttp installed" -ForegroundColor Green
} else {
    Write-Host "⚠️  aiohttp install failed, trying --user..." -ForegroundColor Yellow
    & $pythonPath -m pip install --user --no-warn-script-location --disable-pip-version-check aiohttp 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ aiohttp installed with --user" -ForegroundColor Green
    } else {
        Write-Host "❌ aiohttp installation failed" -ForegroundColor Red
    }
}

# Try to install psutil (optional, will work without it)
Write-Host "Installing psutil (optional)..." -ForegroundColor Yellow
$psutilResult = & $pythonPath -m pip install --no-warn-script-location --disable-pip-version-check psutil 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ psutil installed" -ForegroundColor Green
} else {
    Write-Host "⚠️  psutil install failed, trying --user..." -ForegroundColor Yellow
    & $pythonPath -m pip install --user --no-warn-script-location --disable-pip-version-check psutil 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ psutil installed with --user" -ForegroundColor Green
    } else {
        Write-Host "⚠️  psutil installation failed (optional - test will continue)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== Verification ===" -ForegroundColor Cyan

# Verify aiohttp (required)
$aiohttpCheck = & $pythonPath -c "import aiohttp; print('OK')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ aiohttp: OK" -ForegroundColor Green
} else {
    Write-Host "❌ aiohttp: FAILED" -ForegroundColor Red
    Write-Host "   Test cannot run without aiohttp" -ForegroundColor Yellow
    exit 1
}

# Verify psutil (optional)
$psutilCheck = & $pythonPath -c "import psutil; print('OK')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ psutil: OK" -ForegroundColor Green
} else {
    Write-Host "⚠️  psutil: Not available (optional - test will continue)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Ready to run test!" -ForegroundColor Green
Write-Host "   Run: .\run_stress_test.ps1" -ForegroundColor Cyan
