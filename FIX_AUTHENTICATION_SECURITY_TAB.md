# Fix Authentication - Security Tab

## Current Status

You are in the Security tab. Currently:
- "Require authentication" is CHECKED (this causes 403 errors)
- "Allow public access" is UNCHECKED (this is what we need)

## Solution

### Steps:

1. **In the "Authentication" section (left panel):**
   - Click the radio button for **"Allow public access"**
   - This will uncheck "Require authentication"

2. **Save the changes:**
   - Look for a "Save" or "Deploy" button
   - Click it to apply the changes

3. **Wait for deployment to complete**

## What This Does

- "Allow public access" = No authentication checks
- This is equivalent to adding `allUsers` with `Cloud Run Invoker` role via IAM
- The service will be accessible without authentication

## After Saving

The service will be publicly accessible and the 403 error will be resolved.

## Test URLs

After saving:
- Health: https://records-ai-v2-969278596906.europe-west1.run.app/health
- Home: https://records-ai-v2-969278596906.europe-west1.run.app/ui/index.html



