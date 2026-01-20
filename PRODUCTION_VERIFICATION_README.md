# Production Security Verification Guide

## Overview

`tests/production_verification.py` script validates all critical security fixes identified in `CHAOS_TEST_REPORT.md` against the production Cloud Run deployment.

## Quick Start

```bash
# Set environment variables
export AUTH_TOKEN="your-jwt-token"
export API_BASE_URL="https://records-ai-v2-969278596906.us-central1.run.app"

# Run verification
python tests/production_verification.py
```

## Tests Performed

### Priority 1 (Critical):

1. **Path Traversal Protection**
   - Upload with filename: `../../../etc/passwd`
   - Expected: 400 Bad Request
   - Severity: 10

2. **MIME Spoofing Protection**
   - Upload EXE file with `Content-Type: image/jpeg`
   - Expected: 400 Bad Request (MIME mismatch)
   - Severity: 9

3. **Memory Exhaustion Protection**
   - Upload 60MB file (exceeds 50MB limit)
   - Expected: 413 Payload Too Large
   - Severity: 9

### Priority 2 (High):

4. **Parallel Upload Stress Test**
   - Send 20 simultaneous upload requests
   - Expected: Some rate-limited (429)
   - Severity: 8

5. **Archive Idempotency**
   - Send 5 identical archive requests
   - Expected: 4+ idempotent responses
   - Severity: 9

6. **OpenAI Timeout Protection**
   - Upload large image (should trigger OpenAI)
   - Expected: Completes within 35s (even if OpenAI fails)
   - Severity: 8

### Priority 3 (Medium):

7. **Auth Negative Test**
   - Request without auth token
   - Expected: 401 Unauthorized
   - Severity: 8

8. **XSS Injection Protection**
   - Archive with `<script>` tags
   - Expected: Script tags sanitized or rejected
   - Severity: 8

9. **Invalid Year Validation**
   - Archive with year 2099
   - Expected: 422 or sanitized
   - Severity: 4

10. **Duplicate Upload Retry**
    - Upload same file twice
    - Expected: Same record_id returned
    - Severity: 7

## Output Format

### Console Output:

```
======================================================================
PRODUCTION SECURITY VERIFICATION
Records_AI_V2 Security Fix Validation
======================================================================

Target: https://records-ai-v2-969278596906.us-central1.run.app
Auth: ✅ Token provided

✔ Path Traversal Protection
    HTTP: 400
    Duration: 1.23s

❌ MIME Spoofing Protection
    HTTP: 200
    Duration: 2.45s
    Fix: Check file_validation.py validate_file_signature()
    File: backend/core/file_validation.py
    Line: 170

...

======================================================================
TEST RESULTS SUMMARY
======================================================================

Test Name                      Status     Severity  
----------------------------------------------------------------------
Path Traversal                 ✔ PASS     10
MIME Spoofing                  ❌ FAIL    9
Memory Exhaustion              ✔ PASS     9
...

Security Score: 7.5/10 ⚠️

🚨 DEPLOY BLOCKED - CRITICAL SECURITY ISSUES FOUND 🚨
❌ MIME Spoofing
   Fix: Check file_validation.py validate_file_signature()
   File: backend/core/file_validation.py
   Line: 170

📄 Full report saved to: production_verification_report.json
```

### JSON Report:

```json
{
  "timestamp": "2025-01-19T12:00:00Z",
  "target_url": "https://records-ai-v2-969278596906.us-central1.run.app",
  "security_score": 8.5,
  "total_tests": 10,
  "passed": 8,
  "failed": 1,
  "warnings": 1,
  "critical_failures": 1,
  "deploy_blocked": true,
  "tests": [
    {
      "test_name": "Path Traversal Protection",
      "status": "PASS",
      "http_status": 400,
      "duration": 1.23,
      "message": "Path traversal attempt blocked"
    },
    ...
  ]
}
```

## Security Score Calculation

```
Security Score = (Sum of PASS severity) / (Total severity) × 10
```

**Interpretation:**
- **8.0-10.0**: ✅ Production-ready
- **6.0-7.9**: ⚠️ Warning - review before deployment
- **0.0-5.9**: ❌ Block deployment - critical issues

## Deploy Block Criteria

Deployment is **BLOCKED** if:
1. Any test with severity ≥ 9 fails
2. Security score < 6.0

## Exit Codes

- **0**: All tests passed - deployment allowed
- **1**: Critical failures found - deployment blocked

## CI/CD Integration

```bash
#!/bin/bash
# Pre-deployment security check

export AUTH_TOKEN="${CI_AUTH_TOKEN}"
export API_BASE_URL="${PRODUCTION_URL}"

python tests/production_verification.py
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "🚨 Security verification failed - deployment blocked"
    exit 1
fi

echo "✅ Security verification passed - proceeding with deployment"
```

## Fix Recommendations

If a test fails, the script provides:
1. **Error message** - What went wrong
2. **Fix suggestion** - How to fix it
3. **File location** - Where to fix it
4. **Line number** - Exact location

Example:
```
❌ MIME Spoofing Protection
   Fix: Check file_validation.py validate_file_signature() - verify magic bytes check
   File: backend/core/file_validation.py
   Line: 170
```

## Troubleshooting

### "AUTH_TOKEN not set"
- Set `export AUTH_TOKEN="your-token"`
- Get token from login endpoint: `/api/v1/auth/login`

### "Connection refused"
- Check `API_BASE_URL` is correct
- Verify Cloud Run service is running
- Check network connectivity

### "Test timeout"
- May indicate OpenAI timeout not working
- Check Cloud Run logs for errors
- Verify OpenAI API key is set

## Dependencies

```bash
pip install aiohttp
```

No other dependencies required (uses stdlib: asyncio, json, os, sys, time, uuid, datetime, pathlib)

## Manual Testing

If automated tests fail, manually verify:

1. **Path Traversal:**
   ```bash
   curl -X POST "${API_BASE}/api/v1/upap/upload" \
     -H "Authorization: Bearer ${AUTH_TOKEN}" \
     -F "file=@test.jpg;filename=../../../etc/passwd" \
     -F "email=test@example.com"
   # Should return 400
   ```

2. **MIME Spoofing:**
   ```bash
   echo "MZ\x90\x00" > fake.exe
   curl -X POST "${API_BASE}/api/v1/upap/upload" \
     -H "Authorization: Bearer ${AUTH_TOKEN}" \
     -F "file=@fake.exe;type=image/jpeg" \
     -F "email=test@example.com"
   # Should return 400 (MIME mismatch)
   ```

3. **Rate Limiting:**
   ```bash
   for i in {1..25}; do
     curl -X POST "${API_BASE}/api/v1/upap/upload" \
       -H "Authorization: Bearer ${AUTH_TOKEN}" \
       -F "file=@test.jpg" \
       -F "email=test@example.com" &
   done
   # Some should return 429
   ```

## Next Steps

After verification:
1. ✅ If all tests pass → Deploy to production
2. ❌ If tests fail → Fix issues, rerun tests
3. ⚠️ If warnings → Review and fix before next deployment

## Support

For issues or questions:
- Check `CHAOS_TEST_REPORT.md` for vulnerability details
- Review `FIX_PACK_SUMMARY.md` for fix implementations
- Check Cloud Run logs for runtime errors
