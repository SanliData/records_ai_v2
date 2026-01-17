# Complete Deployment First, Then Fix IAM

## Current Situation

You are in the deployment wizard (Networking/Settings tabs). The "Allow unauthenticated invocations" option is NOT available in the deployment wizard tabs.

## Solution: Two-Step Process

### Step 1: Complete Deployment

1. Review your settings in the current tabs
2. Click "Deploy" button at the bottom
3. Wait for deployment to complete

### Step 2: Fix IAM After Deployment

After deployment completes:

1. You'll be redirected to Service Details page
2. Look for tabs at the top: "Observability", "Revisions", "Source", "Triggers", "**PERMISSIONS**", "Networking", "Security", "YAML"
3. Click "**PERMISSIONS**" tab
4. Click "ADD PRINCIPAL" button
5. Add:
   - **New principals:** `allUsers`
   - **Select a role:** `Cloud Run Invoker`
6. Click "SAVE"
7. Confirm when asked "Allow unauthenticated invocations?"

## Direct Link After Deployment

```
https://console.cloud.google.com/run/detail/europe-west1/records-ai-v2/permissions?project=records-ai
```

## Why This Approach?

- The deployment wizard focuses on container/config settings
- IAM permissions are managed separately via PERMISSIONS tab
- This is the standard workflow for Cloud Run services

## Next Actions

1. **NOW:** Click "Deploy" to complete deployment
2. **THEN:** Go to PERMISSIONS tab and add `allUsers` with `Cloud Run Invoker` role



