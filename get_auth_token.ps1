# Get AUTH_TOKEN for stress test
# Run: .\get_auth_token.ps1

$BASE_URL = "https://records-ai-v2-969278596906.us-central1.run.app"
$TEST_EMAIL = "test@example.com"
$TEST_PASSWORD = "TestPassword123!"

Write-Host "=== Getting AUTH_TOKEN for Stress Test ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Email: $TEST_EMAIL" -ForegroundColor Yellow
Write-Host "Target: $BASE_URL" -ForegroundColor Yellow
Write-Host ""

# Try to register first (will fail if user exists, that's OK)
Write-Host "Step 1: Registering user..." -ForegroundColor Yellow
$registerBody = @{
    email = $TEST_EMAIL
    password = $TEST_PASSWORD
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "$BASE_URL/auth/register" `
        -Method Post `
        -Body $registerBody `
        -ContentType "application/json" `
        -ErrorAction SilentlyContinue
    
    if ($registerResponse.token) {
        Write-Host "[OK] User registered successfully" -ForegroundColor Green
        $token = $registerResponse.token
    }
} catch {
    # User might already exist, try login instead
    Write-Host "[WARN] Registration failed (user may already exist), trying login..." -ForegroundColor Yellow
}

# If no token from register, try login
if (-not $token) {
    Write-Host "Step 2: Logging in..." -ForegroundColor Yellow
    $loginBody = @{
        email = $TEST_EMAIL
        password = $TEST_PASSWORD
    } | ConvertTo-Json

    try {
        $loginResponse = Invoke-RestMethod -Uri "$BASE_URL/auth/login" `
            -Method Post `
            -Body $loginBody `
            -ContentType "application/json"
        
        if ($loginResponse.token) {
            Write-Host "[OK] Login successful" -ForegroundColor Green
            $token = $loginResponse.token
        } else {
            Write-Host "[ERROR] Login failed: No token in response" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "[ERROR] Login failed: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please check:" -ForegroundColor Yellow
        Write-Host "  1. Server is running at $BASE_URL" -ForegroundColor Cyan
        Write-Host "  2. User exists in database" -ForegroundColor Cyan
        Write-Host "  3. Email/password are correct" -ForegroundColor Cyan
        exit 1
    }
}

# Set environment variable for current session
$env:AUTH_TOKEN = $token

# Save to file for future use
$tokenFile = ".auth_token.txt"
$token | Out-File -FilePath $tokenFile -Encoding utf8 -NoNewline

Write-Host ""
Write-Host "[OK] AUTH_TOKEN retrieved successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Token (first 50 chars): $($token.Substring(0, [Math]::Min(50, $token.Length)))..." -ForegroundColor Cyan
Write-Host ""
Write-Host "[INFO] Token saved to: $tokenFile" -ForegroundColor Yellow
Write-Host ""
Write-Host "[INFO] To use this token:" -ForegroundColor Cyan
Write-Host "   PowerShell: `$env:AUTH_TOKEN = Get-Content .auth_token.txt" -ForegroundColor White
Write-Host "   Or: `$env:AUTH_TOKEN = '$token'" -ForegroundColor White
Write-Host ""
Write-Host "Now you can run: .\run_stress_test.ps1" -ForegroundColor Green
