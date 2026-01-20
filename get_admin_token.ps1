# PowerShell script to get ADMIN_TOKEN for stress testing
# Admin users: ednovitsky@novitskyarchive.com, isanli058@gmail.com
# Run: .\get_admin_token.ps1

param(
    [string]$Email = "ednovitsky@novitskyarchive.com",
    [string]$Password = "ism058SAN.,?",
    [string]$BaseUrl = "https://records-ai-v2-969278596906.us-central1.run.app"
)

Write-Host "=== Getting ADMIN_TOKEN for Stress Test ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Email: $Email"
Write-Host "Target: $BaseUrl"
Write-Host ""

# Prompt for password if not provided
if (-not $Password) {
    $SecurePassword = Read-Host "Enter password for $Email" -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecurePassword)
    $Password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
}
else {
    Write-Host "Using provided password..." -ForegroundColor Gray
}

Write-Host "Step 1: Logging in..." -ForegroundColor Yellow

try {
    $loginBody = @{
        email = $Email
        password = $Password
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod -Uri "$BaseUrl/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginBody `
        -ErrorAction Stop

    if ($loginResponse.status -eq "ok" -and $loginResponse.token) {
        $token = $loginResponse.token
        
        Write-Host "[OK] Login successful" -ForegroundColor Green
        Write-Host ""
        Write-Host "[OK] ADMIN_TOKEN retrieved successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Token (first 50 chars): $($token.Substring(0, [Math]::Min(50, $token.Length)))..."
        Write-Host ""
        
        # Save token to file
        $token | Out-File -FilePath ".admin_token.txt" -Encoding utf8 -NoNewline
        Write-Host "[INFO] Token saved to: .admin_token.txt" -ForegroundColor Cyan
        Write-Host ""
        
        # Set environment variable
        $env:ADMIN_TOKEN = $token
        Write-Host "[INFO] To use this token:" -ForegroundColor Cyan
        Write-Host "   PowerShell: `$env:ADMIN_TOKEN = Get-Content .admin_token.txt" -ForegroundColor Gray
        Write-Host "   Or: `$env:ADMIN_TOKEN = '$token'" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Now you can run: .\run_stress_test.ps1" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Login failed: Invalid response" -ForegroundColor Red
        exit 1
    }
} catch {
    $errorDetails = $_.Exception.Message
    if ($_.ErrorDetails.Message) {
        try {
            $errorJson = $_.ErrorDetails.Message | ConvertFrom-Json
            $errorDetails = $errorJson.detail
        } catch {
            $errorDetails = $_.ErrorDetails.Message
        }
    }
    
    Write-Host "[ERROR] Login failed: $errorDetails" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Check if user exists: User may need to be created first" -ForegroundColor Gray
    Write-Host "  2. Verify password is correct" -ForegroundColor Gray
    Write-Host "  3. Check if user is marked as admin in admin_service.py" -ForegroundColor Gray
    exit 1
}
