# PowerShell script to verify endpoints exist (not 404/405)
# Run: .\verify_endpoints.ps1 [port]

param(
    [int]$Port = 8000,
    [string]$BaseUrl = "http://127.0.0.1"
)

$base = "$BaseUrl`:$Port"

Write-Host "=== Verifying Endpoints ===" -ForegroundColor Cyan
Write-Host "Base URL: $base"
Write-Host ""

$endpoints = @(
    @{Method="GET"; Path="/auth/whoami"; Expected="401 (not 404)"; AcceptCodes=@(401)},
    @{Method="POST"; Path="/admin/bootstrap-user"; Expected="401/403 (not 404/405)"; AcceptCodes=@(401, 403)},
    @{Method="GET"; Path="/health"; Expected="200"; AcceptCodes=@(200)}
)

$allPassed = $true

foreach ($ep in $endpoints) {
    $url = "$base$($ep.Path)"
    Write-Host "Testing: $($ep.Method) $($ep.Path)..." -ForegroundColor Yellow
    
    try {
        if ($ep.Method -eq "GET") {
            $response = Invoke-WebRequest -Uri $url -Method GET -ErrorAction Stop
        } else {
            $body = @{email="test@example.com"} | ConvertTo-Json
            $response = Invoke-WebRequest -Uri $url -Method POST -ContentType "application/json" -Body $body -ErrorAction Stop
        }
        
        $statusCode = $response.StatusCode
        $expectedCodes = $ep.AcceptCodes
        
        if ($statusCode -in $expectedCodes) {
            Write-Host "  ✅ PASS: Got $statusCode ($($ep.Expected))" -ForegroundColor Green
        } elseif ($statusCode -eq 404 -or $statusCode -eq 405) {
            Write-Host "  ❌ FAIL: Got $statusCode but expected $($ep.Expected)" -ForegroundColor Red
            Write-Host "     This means the endpoint is NOT registered!" -ForegroundColor Red
            $allPassed = $false
        } else {
            Write-Host "  ⚠️  WARN: Got $statusCode but expected one of: $($expectedCodes -join ', ')" -ForegroundColor Yellow
        }
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode) {
            $expectedCodes = $ep.AcceptCodes
            if ($statusCode -in $expectedCodes) {
                Write-Host "  ✅ PASS: Got $statusCode ($($ep.Expected))" -ForegroundColor Green
            } elseif ($statusCode -eq 404 -or $statusCode -eq 405) {
                Write-Host "  ❌ FAIL: Got $statusCode but expected $($ep.Expected)" -ForegroundColor Red
                Write-Host "     This means the endpoint is NOT registered!" -ForegroundColor Red
                $allPassed = $false
            } else {
                Write-Host "  ⚠️  WARN: Got $statusCode but expected one of: $($expectedCodes -join ', ')" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  ❌ ERROR: $_" -ForegroundColor Red
            $allPassed = $false
        }
    }
    Write-Host ""
}

if ($allPassed) {
    Write-Host "✅ All endpoints verified!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ Some endpoints failed verification" -ForegroundColor Red
    exit 1
}
