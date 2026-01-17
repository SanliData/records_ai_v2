# Fix 403 Forbidden Error

## Problem
403 Forbidden error when accessing the service URL.

## Cause
IAM policy not set - organization policy prevented automatic IAM setup.

## Solution

### Option 1: Console (RECOMMENDED)

1. Go to Cloud Console:
   ```
   https://console.cloud.google.com/run/detail/europe-west1/records-ai-v2?project=records-ai
   ```

2. Click "EDIT & DEPLOY NEW REVISION"

3. Go to "SECURITY" tab

4. Check "Allow unauthenticated invocations"

5. Click "DEPLOY"

### Option 2: gcloud CLI (may fail due to org policy)

```bash
gcloud beta run services add-iam-policy-binding records-ai-v2 \
  --region=europe-west1 \
  --member=allUsers \
  --role=roles/run.invoker \
  --project=records-ai
```

## Test After Fix

Service URL: https://records-ai-v2-969278596906.europe-west1.run.app

Test endpoints:
- Health: https://records-ai-v2-969278596906.europe-west1.run.app/health
- Home: https://records-ai-v2-969278596906.europe-west1.run.app/ui/index.html



