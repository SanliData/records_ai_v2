# Run Final Stress Test - Quick Guide

## Problem
Python 3.13 pip has compatibility issues. Manual installation required.

## Solution

### Option 1: Fix pip and install modules

1. **Open Windows Command Prompt or PowerShell** (as Administrator)

2. **Install modules:**
```cmd
python -m pip install --upgrade pip
python -m pip install aiohttp psutil
```

Or if above doesn't work:
```cmd
python -m pip install --upgrade --force-reinstall pip
python -m pip install aiohttp psutil
```

### Option 2: Use Python IDLE

1. **Open Python IDLE** (from Start Menu > Python 3.13 > IDLE)

2. **Install modules in IDLE:**
```python
import subprocess
import sys

subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp", "psutil"])
```

3. **Run test in IDLE:**
   - File > Open > `tests/final_stress_test.py`
   - Run > Run Module (F5)

### Option 3: Use PowerShell

1. **Open PowerShell**

2. **Set environment variable:**
```powershell
$env:AUTH_TOKEN = "your-jwt-token"
```

3. **Install and run:**
```powershell
python -m pip install aiohttp psutil
python tests/final_stress_test.py
```

### Option 4: Use venv (Recommended)

1. **Create virtual environment:**
```cmd
python -m venv venv
venv\Scripts\activate
```

2. **Install dependencies:**
```cmd
pip install -r requirements.txt
```

3. **Run test:**
```cmd
python tests/final_stress_test.py
```

## Quick Command (if pip works)

```cmd
cd C:\Users\issan\records_ai_v2
set AUTH_TOKEN=your-jwt-token
python -m pip install aiohttp psutil
python tests/final_stress_test.py
```

## Expected Output

```
======================================================================
FINAL PRE-PRODUCTION DESTRUCTION TEST
======================================================================

✅ [PHASE 1] 500 Parallel Uploads: PASS
✅ [PHASE 2] Auth Attack: PASS
✅ [PHASE 3] AI Service Chaos: PASS
...

Security Score: 9.5/10 ✅
Stability Score: 9.8/10 ✅

FINAL DECISION: GO LIVE
```

## Troubleshooting

**If pip still fails:**
- Reinstall Python 3.13
- Or use Python 3.11/3.12 instead
- Or install modules manually from wheels

**If AUTH_TOKEN not set:**
- Some authenticated tests will be skipped
- Phase 2 (Auth Attack) will still run (tests missing tokens)
- Other phases may show warnings
