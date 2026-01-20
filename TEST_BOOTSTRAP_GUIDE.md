# Test Bootstrap Guide

## Overview

The stress test requires authenticated users. If a user doesn't exist in the database, the test will automatically bootstrap (create) the user using an admin token.

## Prerequisites

1. **AUTH_TOKEN**: Token for the test user (from `get_auth_token.ps1` or manual login)
2. **ADMIN_TOKEN**: Token for an admin user (required for bootstrap)
3. **API_BASE_URL**: API endpoint (defaults to Cloud Run URL)

## Setup Steps

### 1. Get User Token

```powershell
# Get test user token
.\get_auth_token.ps1

# Token is saved to .auth_token.txt and set in $env:AUTH_TOKEN
```

### 2. Get Admin Token

**Option A: Use an existing admin account**
- Log in with an admin email: `ednovitsky@novitskyarchive.com` or `isanli058@gmail.com`
- Save the token to `.admin_token.txt` or set `$env:ADMIN_TOKEN`

**Option B: Create admin token manually**
```powershell
# Login via API to get admin token
$adminEmail = "ednovitsky@novitskyarchive.com"
$adminPassword = "your-admin-password"

$response = Invoke-RestMethod -Uri "https://records-ai-v2-969278596906.us-central1.run.app/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body (@{email=$adminEmail; password=$adminPassword} | ConvertTo-Json)

$adminToken = $response.token
$adminToken | Out-File -FilePath ".admin_token.txt" -Encoding utf8
$env:ADMIN_TOKEN = $adminToken
```

### 3. Run Stress Test

```powershell
# The script automatically loads tokens from .auth_token.txt and .admin_token.txt
.\run_stress_test.ps1

# Or set environment variables manually:
$env:AUTH_TOKEN = "your-user-token"
$env:ADMIN_TOKEN = "your-admin-token"
$env:API_BASE_URL = "https://records-ai-v2-969278596906.us-central1.run.app"
.\run_stress_test.ps1
```

## Bootstrap Flow

1. **Test starts**: Calls `GET /auth/whoami` with `AUTH_TOKEN`
2. **If user exists**: Test proceeds normally
3. **If user missing (401)**: Test extracts email from `AUTH_TOKEN` and calls `POST /admin/bootstrap-user` with `ADMIN_TOKEN`
4. **User created**: Test retries `GET /auth/whoami`
5. **Test proceeds**: If successful, destructive tests run

## API Endpoints

### GET /auth/whoami
- **Auth**: Bearer token (any user)
- **Returns**: `{user_id, email, is_admin, is_active}`
- **Use**: Verify user exists and is active

### POST /admin/bootstrap-user
- **Auth**: Bearer token (admin only)
- **Body**: `{email: "user@example.com", is_admin: false}`
- **Returns**: `{status: "ok", existed: bool, user_id, email, is_admin, request_id}`
- **Use**: Create test users for stress testing

## Troubleshooting

### Error: "User not found and ADMIN_TOKEN not set"
- **Fix**: Set `$env:ADMIN_TOKEN` or create `.admin_token.txt`

### Error: "Bootstrap failed: 401"
- **Cause**: Admin token is invalid or expired
- **Fix**: Get a fresh admin token

### Error: "Bootstrap failed: 403"
- **Cause**: Token doesn't belong to an admin user
- **Fix**: Use an admin account token

### Error: "Cannot extract email from AUTH_TOKEN"
- **Cause**: AUTH_TOKEN is malformed
- **Fix**: Regenerate token with `.\get_auth_token.ps1`

## Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `API_BASE_URL` | No | API endpoint URL | Cloud Run URL |
| `AUTH_TOKEN` | Yes | Test user JWT token | From `.auth_token.txt` |
| `ADMIN_TOKEN` | Yes* | Admin JWT token | From `.admin_token.txt` |
| `TEST_EMAIL` | No | Test user email | `test@example.com` |

\* Required only if user needs to be bootstrapped

## Security Notes

- Admin tokens should be kept secure
- Bootstrap endpoint is admin-only and logged
- Tokens expire after a set time (check token expiration)
- Test users created via bootstrap are regular users unless `is_admin: true` is specified
