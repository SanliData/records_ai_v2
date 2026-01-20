# PowerShell script to run Final Stress Test
# Run: .\run_stress_test.ps1

Write-Host "=== Final Stress Test - PowerShell Runner ===" -ForegroundColor Cyan
Write-Host ""

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
        # Verify it's actually Python
        $version = & $path --version 2>&1
        if ($version -match "Python") {
            $pythonPath = $path
            break
        }
    } elseif ($path -match "^python|^py$") {
        # Try to run it directly
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

# Check if Python exists
if (-not $pythonPath -or -not (Test-Path $pythonPath)) {
    Write-Host "❌ Python not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Searched locations:" -ForegroundColor Yellow
    foreach ($path in $pythonPaths) {
        Write-Host "  - $path" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "Please install Python or update pythonPaths in this script" -ForegroundColor Yellow
    exit 1
}

# Verify Python version
$pythonVersion = & $pythonPath --version 2>&1
Write-Host "✅ Python found: $pythonPath" -ForegroundColor Green
Write-Host "   Version: $pythonVersion" -ForegroundColor Gray
Write-Host ""

# Check if modules are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$checkModules = & $pythonPath -c "import aiohttp, psutil; print('OK')" 2>&1

# #region agent log
$logDir = Join-Path $PSScriptRoot ".cursor"
$logPath = Join-Path $logDir "debug.log"
$sessionId = "debug-session"
$runId = "pip-diagnosis"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}
function Write-DebugLog {
    param($message, $data, $hypothesisId = "A")
    $entry = @{
        sessionId = $sessionId
        runId = $runId
        hypothesisId = $hypothesisId
        location = "run_stress_test.ps1:diagnostic"
        message = $message
        data = $data
        timestamp = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
    } | ConvertTo-Json -Compress
    Add-Content -Path $logPath -Value $entry -ErrorAction SilentlyContinue
}
# #endregion

# #region agent log
Write-DebugLog -message "Python version check" -data @{pythonPath = $pythonPath; pythonVersion = $pythonVersion} -hypothesisId "A"
# #endregion

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Dependencies missing - installing..." -ForegroundColor Yellow
    Write-Host ""
    
    # Check pip status first
    Write-Host "Checking pip status..." -ForegroundColor Yellow
    # #region agent log
    $pipVersionCheck = & $pythonPath -m pip --version 2>&1
    $pipOutputStr = $pipVersionCheck -join "`n"
    $pipHasError = ($LASTEXITCODE -ne 0) -or ($pipOutputStr -match "ValueError|Traceback|Error:|Exception:")
    $pipStatus = @{
        exitCode = $LASTEXITCODE
        output = $pipOutputStr.Substring(0, [Math]::Min(500, $pipOutputStr.Length))
        pipAvailable = (-not $pipHasError)
        hasErrorPattern = ($pipOutputStr -match "ValueError|Traceback|Error:|Exception:")
    }
    Write-DebugLog -message "Pip version check" -data $pipStatus -hypothesisId "A"
    # #endregion
    
    if ($pipHasError) {
        Write-Host "❌ Pip is broken - attempting to reinstall..." -ForegroundColor Red
        # #region agent log
        Write-DebugLog -message "Pip broken, starting reinstall" -data @{method = "get-pip.py"} -hypothesisId "B"
        # #endregion
        
        # Try to reinstall pip using get-pip.py bootstrap
        $getPipUrl = "https://bootstrap.pypa.io/get-pip.py"
        $getPipPath = Join-Path $env:TEMP "get-pip.py"
        
        try {
            Write-Host "Downloading pip bootstrap script..." -ForegroundColor Yellow
            Invoke-WebRequest -Uri $getPipUrl -OutFile $getPipPath -ErrorAction Stop
            # #region agent log
            Write-DebugLog -message "Downloaded get-pip.py" -data @{path = $getPipPath} -hypothesisId "B"
            # #endregion
            
            Write-Host "Reinstalling pip..." -ForegroundColor Yellow
            $pipReinstall = & $pythonPath $getPipPath --force-reinstall --no-warn-script-location 2>&1
            # #region agent log
            Write-DebugLog -message "Pip reinstall via get-pip.py" -data @{
                exitCode = $LASTEXITCODE
                output = ($pipReinstall -join "`n").Substring(0, [Math]::Min(500, ($pipReinstall -join "`n").Length))
            } -hypothesisId "B"
            # #endregion
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Pip reinstalled successfully" -ForegroundColor Green
            } else {
                Write-Host "⚠️  get-pip.py failed, trying ensurepip..." -ForegroundColor Yellow
                # #region agent log
                Write-DebugLog -message "get-pip.py failed, trying ensurepip" -data @{exitCode = $LASTEXITCODE} -hypothesisId "C"
                # #endregion
                
                $ensurePip = & $pythonPath -m ensurepip --upgrade --default-pip 2>&1
                # #region agent log
                Write-DebugLog -message "ensurepip result" -data @{
                    exitCode = $LASTEXITCODE
                    output = ($ensurePip -join "`n").Substring(0, [Math]::Min(500, ($ensurePip -join "`n").Length))
                } -hypothesisId "C"
                # #endregion
            }
            
            # Clean up
            if (Test-Path $getPipPath) {
                Remove-Item $getPipPath -ErrorAction SilentlyContinue
            }
        } catch {
            Write-Host "⚠️  Could not download get-pip.py: $_" -ForegroundColor Yellow
            # #region agent log
            Write-DebugLog -message "get-pip.py download failed" -data @{error = $_.ToString()} -hypothesisId "D"
            # #endregion
            
            # Fallback to ensurepip
            Write-Host "Trying ensurepip fallback..." -ForegroundColor Yellow
            $ensurePip = & $pythonPath -m ensurepip --upgrade --default-pip 2>&1
            # #region agent log
            Write-DebugLog -message "ensurepip fallback" -data @{
                exitCode = $LASTEXITCODE
                output = ($ensurePip -join "`n").Substring(0, [Math]::Min(500, ($ensurePip -join "`n").Length))
            } -hypothesisId "D"
            # #endregion
        }
        
        # Verify pip is now working
        $pipVerify = & $pythonPath -m pip --version 2>&1
        # #region agent log
        Write-DebugLog -message "Pip verification after reinstall" -data @{
            exitCode = $LASTEXITCODE
            output = ($pipVerify -join "`n")
            pipWorking = ($LASTEXITCODE -eq 0)
        } -hypothesisId "E"
        # #endregion
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Pip reinstall failed - pip is still broken" -ForegroundColor Red
            Write-Host "Error: $pipVerify" -ForegroundColor Red
            Write-Host ""
            Write-Host "Manual fix required:" -ForegroundColor Yellow
            Write-Host "  1. Download: https://bootstrap.pypa.io/get-pip.py" -ForegroundColor Cyan
            Write-Host "  2. Run: & `"$pythonPath`" get-pip.py --force-reinstall" -ForegroundColor Cyan
            exit 1
        } else {
            Write-Host "✅ Pip is now working: $pipVerify" -ForegroundColor Green
        }
        Write-Host ""
    } else {
        # Pip works, try upgrading it
        Write-Host "Upgrading pip..." -ForegroundColor Yellow
        $pipUpgrade = & $pythonPath -m pip install --upgrade pip --disable-pip-version-check 2>&1
        # #region agent log
        Write-DebugLog -message "Pip upgrade attempt" -data @{
            exitCode = $LASTEXITCODE
            output = ($pipUpgrade -join "`n").Substring(0, [Math]::Min(500, ($pipUpgrade -join "`n").Length))
        } -hypothesisId "A"
        # #endregion
        if ($LASTEXITCODE -ne 0) {
            Write-Host "⚠️  Pip upgrade failed (continuing anyway)" -ForegroundColor Yellow
        }
        Write-Host ""
    }
    
    # Install aiohttp (try multiple methods)
    Write-Host "Installing aiohttp..." -ForegroundColor Yellow
    $aiohttpInstall = & $pythonPath -m pip install --no-cache-dir --disable-pip-version-check aiohttp 2>&1
    $aiohttpOutputStr = $aiohttpInstall -join "`n"
    $aiohttpHasPipError = ($aiohttpOutputStr -match "ValueError.*rich|Traceback.*rich|pip\._vendor\.rich")
    # #region agent log
    Write-DebugLog -message "aiohttp install attempt 1" -data @{
        exitCode = $LASTEXITCODE
        output = $aiohttpOutputStr.Substring(0, [Math]::Min(500, $aiohttpOutputStr.Length))
        hasPipError = $aiohttpHasPipError
    } -hypothesisId "A"
    # #endregion
    if ($LASTEXITCODE -ne 0) {
        if ($aiohttpHasPipError) {
            Write-Host "❌ Pip error detected during install - pip appears broken" -ForegroundColor Red
            Write-Host "Attempting to reinstall pip and retry..." -ForegroundColor Yellow
            # Trigger pip reinstall
            $getPipUrl = "https://bootstrap.pypa.io/get-pip.py"
            $getPipPath = Join-Path $env:TEMP "get-pip.py"
            try {
                Invoke-WebRequest -Uri $getPipUrl -OutFile $getPipPath -ErrorAction Stop
                & $pythonPath $getPipPath --force-reinstall --no-warn-script-location 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✅ Pip reinstalled, retrying aiohttp install..." -ForegroundColor Green
                    $aiohttpInstall = & $pythonPath -m pip install --no-cache-dir --disable-pip-version-check aiohttp 2>&1
                    $aiohttpOutputStr = $aiohttpInstall -join "`n"
                }
                if (Test-Path $getPipPath) { Remove-Item $getPipPath -ErrorAction SilentlyContinue }
            } catch {
                Write-Host "⚠️  Could not reinstall pip: $_" -ForegroundColor Yellow
            }
        }
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Attempting alternative install method..." -ForegroundColor Yellow
            $aiohttpInstall = & $pythonPath -m pip install --user --no-cache-dir aiohttp 2>&1
            $aiohttpOutputStr = $aiohttpInstall -join "`n"
            # #region agent log
            Write-DebugLog -message "aiohttp install attempt 2 (--user)" -data @{
                exitCode = $LASTEXITCODE
                output = $aiohttpOutputStr.Substring(0, [Math]::Min(500, $aiohttpOutputStr.Length))
            } -hypothesisId "A"
            # #endregion
            if ($LASTEXITCODE -ne 0) {
                Write-Host "❌ Failed to install aiohttp" -ForegroundColor Red
                Write-Host "Error: $aiohttpOutputStr" -ForegroundColor Red
                Write-Host ""
                Write-Host "Manual installation required:" -ForegroundColor Yellow
                Write-Host "  & `"$pythonPath`" -m pip install aiohttp psutil" -ForegroundColor Cyan
                exit 1
            }
        }
    }
    
    # Install psutil
    Write-Host "Installing psutil..." -ForegroundColor Yellow
    $psutilInstall = & $pythonPath -m pip install --no-cache-dir --disable-pip-version-check psutil 2>&1
    # #region agent log
    Write-DebugLog -message "psutil install attempt 1" -data @{
        exitCode = $LASTEXITCODE
        output = ($psutilInstall -join "`n").Substring(0, [Math]::Min(500, ($psutilInstall -join "`n").Length))
    } -hypothesisId "A"
    # #endregion
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Attempting alternative install method..." -ForegroundColor Yellow
        $psutilInstall = & $pythonPath -m pip install --user --no-cache-dir psutil 2>&1
        # #region agent log
        Write-DebugLog -message "psutil install attempt 2 (--user)" -data @{
            exitCode = $LASTEXITCODE
            output = ($psutilInstall -join "`n").Substring(0, [Math]::Min(500, ($psutilInstall -join "`n").Length))
        } -hypothesisId "A"
        # #endregion
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to install psutil" -ForegroundColor Red
            Write-Host "Error: $psutilInstall" -ForegroundColor Red
            Write-Host ""
            Write-Host "Manual installation required:" -ForegroundColor Yellow
            Write-Host "  & `"$pythonPath`" -m pip install aiohttp psutil" -ForegroundColor Cyan
            exit 1
        }
    }
    
    # Verify installation
    $verifyInstall = & $pythonPath -c "import aiohttp, psutil; print('OK')" 2>&1
    # #region agent log
    Write-DebugLog -message "Dependency verification" -data @{
        exitCode = $LASTEXITCODE
        output = ($verifyInstall -join "`n")
        success = ($LASTEXITCODE -eq 0)
    } -hypothesisId "E"
    # #endregion
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Installation completed but verification failed" -ForegroundColor Yellow
        Write-Host "Continuing anyway - test may fail if modules unavailable" -ForegroundColor Yellow
    }
    Write-Host ""
} else {
    Write-Host "✅ All dependencies available" -ForegroundColor Green
    Write-Host ""
}

# Check AUTH_TOKEN (try to load from file first)
if (-not $env:AUTH_TOKEN -and (Test-Path ".auth_token.txt")) {
    $env:AUTH_TOKEN = (Get-Content ".auth_token.txt" -Raw).Trim()
    Write-Host "✅ Loaded AUTH_TOKEN from .auth_token.txt" -ForegroundColor Green
    Write-Host ""
}

# Check ADMIN_TOKEN (required for user bootstrap)
if (-not $env:ADMIN_TOKEN -and (Test-Path ".admin_token.txt")) {
    $env:ADMIN_TOKEN = (Get-Content ".admin_token.txt" -Raw).Trim()
    Write-Host "✅ Loaded ADMIN_TOKEN from .admin_token.txt" -ForegroundColor Green
    Write-Host ""
}

if (-not $env:AUTH_TOKEN) {
    Write-Host "⚠️  AUTH_TOKEN not set - some tests will be skipped" -ForegroundColor Yellow
    Write-Host "Get token with: .\get_auth_token.ps1" -ForegroundColor Cyan
    Write-Host "Or set it with: `$env:AUTH_TOKEN = 'your-jwt-token'" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "✅ AUTH_TOKEN is set" -ForegroundColor Green
    Write-Host ""
}

if (-not $env:ADMIN_TOKEN) {
    Write-Host "⚠️  ADMIN_TOKEN not set - user bootstrap will fail if user missing" -ForegroundColor Yellow
    Write-Host "Set it with: `$env:ADMIN_TOKEN = 'admin-jwt-token'" -ForegroundColor Yellow
    Write-Host "Or save to: .admin_token.txt" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "✅ ADMIN_TOKEN is set (required for user bootstrap)" -ForegroundColor Green
    Write-Host ""
}

# Set default API URL if not set
if (-not $env:API_BASE_URL) {
    $env:API_BASE_URL = "https://records-ai-v2-969278596906.us-central1.run.app"
}

Write-Host "Target: $env:API_BASE_URL" -ForegroundColor Cyan
Write-Host "Auth Token: $(if ($env:AUTH_TOKEN) { 'Set ✅' } else { 'Not set ⚠️' })" -ForegroundColor $(if ($env:AUTH_TOKEN) { 'Green' } else { 'Yellow' })
Write-Host "Admin Token: $(if ($env:ADMIN_TOKEN) { 'Set ✅' } else { 'Not set ⚠️' })" -ForegroundColor $(if ($env:ADMIN_TOKEN) { 'Green' } else { 'Yellow' })
Write-Host ""

Write-Host "=== Starting Final Stress Test ===" -ForegroundColor Cyan
Write-Host "This may take 10-15 minutes..." -ForegroundColor Yellow
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Run test
& $pythonPath tests/final_stress_test.py

# Capture exit code
$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "✅ Test completed successfully" -ForegroundColor Green
    Write-Host "📄 Report: final_kill_test_report.json" -ForegroundColor Cyan
} else {
    Write-Host "❌ Test failed or deployment blocked" -ForegroundColor Red
    Write-Host "📄 Check final_kill_test_report.json for details" -ForegroundColor Yellow
}

exit $exitCode
