# PowerShell script to verify endpoints are registered in FastAPI app
# Run: .\test_endpoints_import.ps1

$pythonPath = "C:\Users\issan\AppData\Local\Programs\Python\Python313\python.exe"

Write-Host "=== Verifying Endpoints in FastAPI App ===" -ForegroundColor Cyan
Write-Host ""

$pythonScript = @"
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

try:
    from backend.main import app
    
    # Get all routes
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            for method in route.methods:
                if method != 'HEAD':
                    routes.append(f"{method} {route.path}")
    
    # Check for required endpoints
    whoami = [r for r in routes if 'whoami' in r.lower()]
    bootstrap = [r for r in routes if 'bootstrap' in r.lower()]
    
    print(f"Total routes: {len(routes)}")
    print(f"")
    print(f"/auth/whoami routes: {whoami}")
    print(f"/admin/bootstrap-user routes: {bootstrap}")
    print(f"")
    
    if whoami:
        print("✅ /auth/whoami endpoint exists")
    else:
        print("❌ /auth/whoami endpoint NOT found")
        
    if bootstrap:
        print("✅ /admin/bootstrap-user endpoint exists")
    else:
        print("❌ /admin/bootstrap-user endpoint NOT found")
        
    if whoami and bootstrap:
        print("")
        print("✅ All required endpoints are registered!")
        sys.exit(0)
    else:
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"@

$scriptPath = Join-Path $env:TEMP "test_endpoints_temp.py"
$pythonScript | Out-File -FilePath $scriptPath -Encoding UTF8

try {
    Set-Location "C:\Users\issan\records_ai_v2"
    & $pythonPath $scriptPath 2>&1
    $exitCode = $LASTEXITCODE
} finally {
    Remove-Item $scriptPath -ErrorAction SilentlyContinue
}

exit $exitCode
