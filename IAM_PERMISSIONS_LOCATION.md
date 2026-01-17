# IAM Permissions Location

## Current Location Issue

You are in the "Security" tab, but "Allow unauthenticated invocations" is not visible there.

## Where to Find It

### Option 1: PERMISSIONS Tab (Most Likely)

1. Go back to Service Details page (click back arrow or service name)
2. Look for "PERMISSIONS" or "IAM" tab at the top
3. Click "PERMISSIONS" tab
4. Click "ADD PRINCIPAL"
5. Add:
   - Principal: `allUsers`
   - Role: `Cloud Run Invoker`
6. Save

### Option 2: Service Settings

1. Go to Service Details page
2. Look for "PERMISSIONS" section (not Security tab)
3. Or use "Manage Permissions" link

### Option 3: During Deploy (Alternative Method)

1. In the current "Security" tab
2. Look for "Allow unauthenticated invocations" checkbox (might be at bottom)
3. If not visible, cancel and go to PERMISSIONS tab instead

## Direct Link to Permissions

```
https://console.cloud.google.com/run/detail/europe-west1/records-ai-v2/permissions?project=records-ai
```

## Alternative: After Deployment

If you can't find it during deployment:
1. Complete deployment first
2. Then go to Service Details > PERMISSIONS tab
3. Add `allUsers` with `Cloud Run Invoker` role



