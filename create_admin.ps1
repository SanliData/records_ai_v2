# PowerShell script to create admin user
# Run: .\create_admin.ps1

param(
    [string]$Email = "ednovitsky@novitskyarchive.com",
    [string]$Password = "ism058SAN.,?"
)

Write-Host "=== Create Admin User ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Email: $Email" -ForegroundColor Yellow
Write-Host "Admin: Yes" -ForegroundColor Yellow
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

Write-Host "✅ Python found: $pythonPath" -ForegroundColor Green
Write-Host "   Version: $(& $pythonPath --version 2>&1)" -ForegroundColor Gray
Write-Host ""

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$checkDeps = & $pythonPath -c "import sqlalchemy, pydantic, bcrypt; print('OK')" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Dependencies missing - installing from requirements.txt..." -ForegroundColor Yellow
    Write-Host ""
    
    # Install dependencies from requirements.txt
    $requirementsPath = Join-Path $PSScriptRoot "requirements.txt"
    if (Test-Path $requirementsPath) {
        Write-Host "Installing from requirements.txt..." -ForegroundColor Gray
        $installDeps = & $pythonPath -m pip install -q -r $requirementsPath 2>&1
        # Explicitly ensure email-validator is installed (required for pydantic.EmailStr)
        & $pythonPath -m pip install -q email-validator 2>&1 | Out-Null
    }
    else {
        # Fallback: install minimal required packages
        Write-Host "requirements.txt not found, installing minimal packages..." -ForegroundColor Gray
        $installDeps = & $pythonPath -m pip install -q sqlalchemy psycopg2-binary bcrypt python-jose pydantic email-validator 2>&1
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        Write-Host "Error: $installDeps" -ForegroundColor Red
        Write-Host ""
        Write-Host "Manual installation:" -ForegroundColor Yellow
        Write-Host "   & `"$pythonPath`" -m pip install -r requirements.txt" -ForegroundColor Cyan
        exit 1
    }
    
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
    Write-Host ""
}

Write-Host "Creating admin user..." -ForegroundColor Yellow
Write-Host ""

# Run the Python script
& $pythonPath scripts/create_admin_user.py --email $Email --password $Password --admin

$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "✅ Admin user created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now:" -ForegroundColor Cyan
    Write-Host "   1. Login: .\get_admin_token.ps1 -Email $Email" -ForegroundColor Gray
    Write-Host "   2. Run tests: .\run_stress_test.ps1" -ForegroundColor Gray
} else {
    Write-Host "❌ Failed to create admin user" -ForegroundColor Red
    Write-Host "Check the error messages above" -ForegroundColor Yellow
}

exit $exitCode
