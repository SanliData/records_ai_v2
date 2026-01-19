# Google OAuth Origin Mismatch Fix

## Problem

**Error:** `Error 400: origin_mismatch`

**Cause:** The JavaScript origin (where the OAuth request comes from) is not registered in Google Cloud Console.

**Current Origin:** `https://records-ai-v2-969278596906.us-central1.run.app`

## Solution

### Step 1: Go to Google Cloud Console

1. Open: https://console.cloud.google.com
2. Select project: `records-ai` (or your project)
3. Navigate to: **APIs & Services** → **Credentials**

### Step 2: Find OAuth 2.0 Client

1. Look for **OAuth 2.0 Client IDs**
2. Find the client ID used by your application
3. Click **Edit** (pencil icon)

### Step 3: Add Authorized JavaScript Origins

In the **Authorized JavaScript origins** section, add:

```
https://records-ai-v2-969278596906.us-central1.run.app
```

**Also keep existing origins:**
- `http://localhost:8000` (for local dev)
- `http://127.0.0.1:8000` (for local dev)
- `https://zyagrolia.com` (if using custom domain)
- `https://api.zyagrolia.com` (if using custom domain)

### Step 4: Add Authorized Redirect URIs

In the **Authorized redirect URIs** section, add:

```
https://records-ai-v2-969278596906.us-central1.run.app/auth/callback
https://records-ai-v2-969278596906.us-central1.run.app/login.html
```

**Also keep existing redirect URIs:**
- `http://localhost:8000/auth/callback`
- `http://127.0.0.1:8000/auth/callback`

### Step 5: Save Changes

Click **Save** at the bottom.

### Step 6: Wait for Propagation

Changes may take a few minutes to propagate. Wait 2-5 minutes, then try again.

## Quick Checklist

- [ ] Added Cloud Run origin to **Authorized JavaScript origins**
- [ ] Added Cloud Run redirect URIs to **Authorized redirect URIs**
- [ ] Saved changes
- [ ] Waited 2-5 minutes for propagation
- [ ] Tested Google sign-in again

## Alternative: Create New OAuth Client

If you can't find the existing client:

1. **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. Application type: **Web application**
4. Name: `records-ai-v2-cloud-run`
5. **Authorized JavaScript origins:**
   ```
   https://records-ai-v2-969278596906.us-central1.run.app
   http://localhost:8000
   http://127.0.0.1:8000
   ```
6. **Authorized redirect URIs:**
   ```
   https://records-ai-v2-969278596906.us-central1.run.app/auth/callback
   http://localhost:8000/auth/callback
   ```
7. Click **Create**
8. Copy **Client ID** and **Client Secret**
9. Update environment variables in Cloud Run:
   ```bash
   gcloud run services update records-ai-v2 \
     --region us-central1 \
     --update-env-vars \
       GOOGLE_CLIENT_ID="your-client-id",\
       GOOGLE_CLIENT_SECRET="your-client-secret"
   ```

## Testing

After fixing:

1. Go to: `https://records-ai-v2-969278596906.us-central1.run.app/login.html`
2. Click "Sign in with Google"
3. Should redirect to Google sign-in (no origin_mismatch error)
4. After signing in, should redirect back to your app

## Troubleshooting

### Still getting origin_mismatch?
- Wait 5-10 minutes (Google caches OAuth config)
- Clear browser cache
- Check exact origin in error message matches what you added
- Verify no typos in origin URL

### Multiple OAuth clients?
- Check which client ID is used in your code
- Make sure you're editing the correct client
- Check environment variables: `GOOGLE_CLIENT_ID`

### Local works but Cloud Run doesn't?
- Cloud Run origin not added to OAuth client
- Follow Step 3 above

## Environment Variables

Make sure these are set in Cloud Run:

```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

Set them with:
```bash
gcloud run services update records-ai-v2 \
  --region us-central1 \
  --update-env-vars \
    GOOGLE_CLIENT_ID="your-client-id",\
    GOOGLE_CLIENT_SECRET="your-client-secret"
```
