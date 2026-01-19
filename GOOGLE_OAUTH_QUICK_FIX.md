# Google OAuth Quick Fix

## Error
**Error 400: origin_mismatch**

The Cloud Run origin is not registered in Google OAuth credentials.

## Quick Fix (5 minutes)

### Step 1: Open Google Cloud Console
https://console.cloud.google.com/apis/credentials?project=records-ai

### Step 2: Find OAuth Client
- Look for **OAuth 2.0 Client IDs**
- Click on your client (or create new one)

### Step 3: Add Cloud Run Origin

**Authorized JavaScript origins:**
```
https://records-ai-v2-969278596906.us-central1.run.app
```

**Authorized redirect URIs:**
```
https://records-ai-v2-969278596906.us-central1.run.app/auth/callback
```

### Step 4: Save
Click **Save** button

### Step 5: Wait
Wait 2-5 minutes for changes to propagate

### Step 6: Test
Try Google sign-in again

## Complete List (Keep All Origins)

**Authorized JavaScript origins:**
```
http://localhost:8000
http://127.0.0.1:8000
https://zyagrolia.com
https://api.zyagrolia.com
https://records-ai-v2-969278596906.us-central1.run.app
```

**Authorized redirect URIs:**
```
http://localhost:8000/auth/callback
http://127.0.0.1:8000/auth/callback
https://zyagrolia.com/auth/callback
https://api.zyagrolia.com/auth/callback
https://records-ai-v2-969278596906.us-central1.run.app/auth/callback
```

## Screenshot Guide

1. Go to: https://console.cloud.google.com/apis/credentials
2. Find **OAuth 2.0 Client IDs** section
3. Click on your client ID
4. Scroll to **Authorized JavaScript origins**
5. Click **+ ADD URI**
6. Paste: `https://records-ai-v2-969278596906.us-central1.run.app`
7. Scroll to **Authorized redirect URIs**
8. Click **+ ADD URI**
9. Paste: `https://records-ai-v2-969278596906.us-central1.run.app/auth/callback`
10. Click **SAVE**

Done! Wait 2-5 minutes and try again.
