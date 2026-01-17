# Fix Container Startup Failure

## Problem

Container failed to start and listen on PORT=8080 within timeout.

Error: "The user-provided container failed to start and listen on the port defined provided by the PORT=8080 environment variable within the allocated timeout."

## Root Cause

The issue is NOT the port number. Cloud Run sets PORT=8080 automatically. The problem is:
1. Container startup is too slow
2. Health check timeout is too short
3. Application may not be starting correctly

## Solution: Increase Health Check Timeout

### Option 1: Via Console (Current Page)

1. In the revision details page, go to "Containers" tab
2. Find "Health Checks" section
3. Increase:
   - **Startup probe timeout:** 240s → 600s (or higher)
   - **Initial delay:** 0s → 60s
   - **Timeout:** 240s → 600s

### Option 2: Check Container Logs First

Before changing timeout, check logs:
1. Click "Open Cloud Logging" link in the error message
2. Look for application startup errors
3. Verify the container is actually starting

### Option 3: Fix Application Startup

The issue might be in the application code:
- Check if `main.py` wrapper is correct
- Verify `Procfile` is correct
- Ensure dependencies are installed

## Port Configuration

**DO NOT CHANGE PORT NUMBER:**
- Cloud Run automatically sets PORT=8080
- Application must listen on the PORT environment variable
- Changing port will NOT fix the issue

## Current Configuration

- PORT: 8080 (correct, set by Cloud Run)
- Startup probe: TCP 8080 every 240s
- Timeout: 240s (might be too short)

## Recommended Changes

1. **Increase startup probe timeout to 600s**
2. **Add initial delay of 60s**
3. **Check container logs for actual errors**

## Alternative: Check if Previous Revision Works

Previous revision (records-ai-v2-00045-mmm) shows green checkmark.
Check what's different between that and current failed revision.



