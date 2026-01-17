# Check Container Logs via gcloud CLI

## Problem

Cannot access logs via Console (authentication required).

## Solution: Use gcloud CLI

### In Cloud Shell, run:

```bash
# Get logs for the failed revision
gcloud logging read \
  'resource.type="cloud_run_revision"
   resource.labels.service_name="records-ai-v2"
   resource.labels.revision_name="records-ai-v2-00046-c2h"' \
  --limit=50 \
  --format=json \
  --project=records-ai

# OR simpler - last 50 log entries for the service
gcloud logging read \
  'resource.type="cloud_run_revision"
   resource.labels.service_name="records-ai-v2"' \
  --limit=50 \
  --project=records-ai

# OR with formatted output
gcloud logging read \
  'resource.type="cloud_run_revision"
   resource.labels.service_name="records-ai-v2"
   resource.labels.revision_name="records-ai-v2-00046-c2h"' \
  --limit=50 \
  --format="table(timestamp,severity,textPayload)" \
  --project=records-ai
```

## What to Look For

Common errors in logs:
1. **Import errors:** `ModuleNotFoundError`, `ImportError`
2. **Path errors:** `FileNotFoundError`, `No such file or directory`
3. **Application crashes:** `Traceback`, `Exception`
4. **Port binding errors:** `Address already in use`, `Permission denied`
5. **Startup timeouts:** No errors but application takes too long to start

## Common Issues and Fixes

### Issue 1: ModuleNotFoundError
**Error:** `ModuleNotFoundError: No module named 'xxx'`
**Fix:** Add missing module to requirements.txt

### Issue 2: FileNotFoundError for backend/main.py
**Error:** `FileNotFoundError: [Errno 2] No such file or directory: 'backend/main.py'`
**Fix:** Check if main.py wrapper is correct, verify file structure

### Issue 3: Application crashes during startup
**Error:** Traceback with application-specific errors
**Fix:** Fix the application code error shown in traceback

### Issue 4: Slow startup (no errors)
**Symptom:** No errors but container doesn't start within timeout
**Fix:** Increase health check timeout settings

## Quick Check Command

```bash
# Just show errors and warnings
gcloud logging read \
  'resource.type="cloud_run_revision"
   resource.labels.service_name="records-ai-v2"
   resource.labels.revision_name="records-ai-v2-00046-c2h"
   (severity>=ERROR OR severity>=WARNING)' \
  --limit=20 \
  --format="table(timestamp,severity,textPayload)" \
  --project=records-ai
```



