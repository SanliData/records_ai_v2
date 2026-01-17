# Check Container Logs Before Changing Settings

## Current Error

Container failed to start on PORT=8080 within timeout.

## Important: Check Logs First

Before changing timeout settings, check what's actually failing:

### Steps:

1. Click "Open Cloud Logging" link (visible in error message)
2. OR go to: https://console.cloud.google.com/run/detail/us-central1/records-ai-v2/logs?project=records-ai
3. Look for errors during container startup
4. Check if application is actually starting

## Possible Issues in Logs:

- Import errors (missing modules)
- Application crashes during startup
- Database connection errors
- Missing environment variables
- Path errors (backend/main.py not found)

## Why Port Change Won't Help

- Cloud Run sets PORT=8080 automatically
- Application must use PORT environment variable
- Changing port number won't fix startup issues

## After Checking Logs

If logs show:
- **Slow startup:** Increase health check timeout
- **Import errors:** Fix dependencies or imports
- **Path errors:** Fix main.py wrapper or file structure
- **Crash:** Fix application code errors

## Recommended Order

1. Check logs first (most important)
2. Fix any application errors found
3. If startup is just slow, then increase timeout
4. Redeploy



