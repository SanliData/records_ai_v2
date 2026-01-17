# Fix 403 Forbidden Error

## Problem
403 Forbidden error when accessing service endpoints.

## Cause
IAM policy not configured - organization policy prevented automatic IAM setup during deployment.

## Solution

### Option 1: Cloud Console (RECOMMENDED)

1. Go to Cloud Console:
   ```
   https://console.cloud.google.com/run/detail/europe-west1/records-ai-v2?project=records-ai
   ```

2. Click "EDIT & DEPLOY NEW REVISION"

3. Navigate to "SECURITY" tab

4. Check "Allow unauthenticated invocations"

5. Click "DEPLOY"

### Option 2: gcloud CLI (may fail due to organization policy)

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
- Upload: https://records-ai-v2-969278596906.europe-west1.run.app/ui/upload.html

## Expected Result

After fixing IAM:
- Health endpoint should return 200 OK
- UI pages should be accessible
- No 403 Forbidden errors



