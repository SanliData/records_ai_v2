# Run Final Stress Test - PowerShell Guide

## Quick Start

### Option 1: Use PowerShell Script (Recommended)

```powershell
# Navigate to project directory
cd C:\Users\issan\records_ai_v2

# Run the PowerShell script
.\run_stress_test.ps1
```

The script will:
- ✅ Check Python installation
- ✅ Install missing dependencies (aiohttp, psutil)
- ✅ Run the stress test
- ✅ Display results

### Option 2: Manual Commands

```powershell
# Navigate to project
cd C:\Users\issan\records_ai_v2

# Set Python path (or add to PATH)
$python = "C:\Users\issan\AppData\Local\Programs\Python\Python313\python.exe"

# Install dependencies
& $python -m pip install aiohttp psutil

# Set AUTH_TOKEN (optional but recommended)
$env:AUTH_TOKEN = "your-jwt-token"

# Set API URL (optional)
$env:API_BASE_URL = "https://records-ai-v2-969278596906.us-central1.run.app"

# Run test
& $python tests/final_stress_test.py
```

### Option 3: One-Liner

```powershell
cd C:\Users\issan\records_ai_v2; $env:AUTH_TOKEN="your-token"; & "C:\Users\issan\AppData\Local\Programs\Python\Python313\python.exe" -m pip install -q aiohttp psutil; & "C:\Users\issan\AppData\Local\Programs\Python\Python313\python.exe" tests/final_stress_test.py
```

## Get AUTH_TOKEN

If you need to get a JWT token:

```powershell
# Login and get token
$response = Invoke-RestMethod -Uri "https://records-ai-v2-969278596906.us-central1.run.app/api/v1/auth/login" -Method POST -Body (@{email="your@email.com"; password="your-password"} | ConvertTo-Json) -ContentType "application/json"
$env:AUTH_TOKEN = $response.access_token
```

## Expected Output

```
======================================================================
FINAL PRE-PRODUCTION DESTRUCTION TEST
======================================================================

✅ [PHASE 1] 500 Parallel Uploads: PASS
✅ [PHASE 2] Auth Attack: PASS
✅ [PHASE 3] AI Service Chaos: PASS
✅ [PHASE 4] File Attack: PASS
✅ [PHASE 5] Database Torture: PASS
✅ [PHASE 6] Cloud Failure: PASS
✅ [PHASE 7] Frontend Abuse: PASS

======================================================================
FINAL TEST SUMMARY
======================================================================

Security Score: 9.5/10 ✅
Stability Score: 9.8/10 ✅

======================================================================
FINAL DECISION: GO LIVE
======================================================================

✅ PRODUCTION APPROVED

📄 Full report saved to: final_kill_test_report.json
```

## Troubleshooting

**"python is not recognized"**
- Use full path: `C:\Users\issan\AppData\Local\Programs\Python\Python313\python.exe`
- Or use the PowerShell script: `.\run_stress_test.ps1`

**"Module not found"**
- Script will auto-install: `aiohttp`, `psutil`
- Or manually: `& $python -m pip install aiohttp psutil`

**"AUTH_TOKEN not set"**
- Set in PowerShell: `$env:AUTH_TOKEN = "your-token"`
- Or use script (will warn but continue)

## Duration

- **Approximate time**: 10-15 minutes
- **Phase 1 (Load Test)**: ~5 minutes
- **Phase 2-7**: ~5-10 minutes

## Output Files

- **Console**: Real-time test results
- **JSON Report**: `final_kill_test_report.json`
- **Exit Code**: 0 = GO LIVE, 1 = BLOCK
