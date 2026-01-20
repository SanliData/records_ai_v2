# Install dependencies manually
# Run: .\install_dependencies.ps1

# Auto-detect Python
$pythonPath = $null

# Try common locations
$pythonPaths = @(
    "C:\Users\issan\AppData\Local\Programs\Python\Python313\python.exe",
    "C:\Users\issan\AppData\Local\Programs\Python\Python312\python.exe",
    "C:\Users\issan\AppData\Local\Programs\Python\Python311\python.exe"
)

foreach ($path in $pythonPaths) {
    if (Test-Path $path) {
        $version = & $path --version 2>&1
        if ($version -match "Python") {
            $pythonPath = $path
            break
        }
    }
}

# Try PATH
if (-not $pythonPath) {
    $pyInPath = Get-Command python -ErrorAction SilentlyContinue
    if ($pyInPath) {
        $pythonPath = $pyInPath.Source
    }
}

if (-not $pythonPath) {
    Write-Host "❌ Python not found!" -ForegroundColor Red
    Write-Host "Please install Python or update paths in script" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Using Python: $pythonPath" -ForegroundColor Green
$pythonVersion = & $pythonPath --version 2>&1
Write-Host "   Version: $pythonVersion" -ForegroundColor Gray
Write-Host ""

Write-Host "=== Installing Dependencies ===" -ForegroundColor Cyan
Write-Host ""

# Method 1: Try standard install
Write-Host "Method 1: Standard pip install..." -ForegroundColor Yellow
& $pythonPath -m pip install --upgrade pip 2>&1
& $pythonPath -m pip install aiohttp psutil 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Success!" -ForegroundColor Green
    exit 0
}

Write-Host ""
Write-Host "Method 2: User install..." -ForegroundColor Yellow
& $pythonPath -m pip install --user aiohttp psutil 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Success with --user flag!" -ForegroundColor Green
    exit 0
}

Write-Host ""
Write-Host "Method 3: Try ensurepip..." -ForegroundColor Yellow
& $pythonPath -m ensurepip --upgrade 2>&1
& $pythonPath -m pip install --no-cache-dir aiohttp psutil 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Success!" -ForegroundColor Green
    exit 0
}

Write-Host ""
Write-Host "❌ All methods failed" -ForegroundColor Red
Write-Host ""
Write-Host "Try manual installation:" -ForegroundColor Yellow
Write-Host "1. Open Python IDLE" -ForegroundColor Cyan
Write-Host "2. Run: import subprocess; subprocess.call(['pip', 'install', 'aiohttp', 'psutil'])" -ForegroundColor Cyan
Write-Host ""
Write-Host "Or use alternative Python installation" -ForegroundColor Yellow

exit 1
