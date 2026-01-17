# Finding "Allow Unauthenticated Invocations" Option

## Current Situation

You are in the "Security" tab of the deployment page, but the "Allow unauthenticated invocations" option is not visible here.

## Where to Find It

### Option 1: Check "Networking" Tab

1. Click on the "Networking" tab (next to Security)
2. Look for "Authentication" or "Allow unauthenticated invocations" checkbox
3. It might be there instead of Security tab

### Option 2: After Deployment (EASIEST)

1. Complete the current deployment (click "Deploy" with current settings)
2. After deployment completes, go to Service Details page
3. Click "PERMISSIONS" tab (not Security)
4. Click "ADD PRINCIPAL"
5. Add:
   - Principal: `allUsers`
   - Role: `Cloud Run Invoker`
6. Save

### Option 3: Cancel and Use Direct Link

1. Cancel this deployment
2. Go to Service Details > PERMISSIONS tab
3. Add IAM binding there
4. Then deploy again

## Recommended Approach

**EASIEST:** Complete deployment now, then fix IAM via PERMISSIONS tab after.

## Direct Permissions Link

After deployment, use:
```
https://console.cloud.google.com/run/detail/europe-west1/records-ai-v2/permissions?project=records-ai
```



