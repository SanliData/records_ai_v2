# Fix Google OAuth Error: 403 org_internal

## Problem

**Error:** `403 org_internal` when trying to log in with Google OAuth

**Root Cause:** OAuth consent screen is set to "Internal" user type, which restricts access to users within the same Google Workspace organization.

## Solution: Change to External User Type

### Step 1: Open Google Cloud Console

1. Go to: https://console.cloud.google.com
2. Select your project: `records-ai` (or your project name)
3. Navigate to: **APIs & Services** → **OAuth consent screen**

### Step 2: Change User Type

**Current Setting:**
- User type = **Internal**

**Action:**
1. Click **EDIT APP** button (top of the page)
2. On the **OAuth consent screen** tab:
   - Find **User Type** section
   - Change from **Internal** to **External**
   - Click **SAVE AND CONTINUE**

### Step 3: Configure OAuth Consent Screen

Complete the required fields (if not already filled):

1. **App information:**
   - App name: `Records AI V2` (or your app name)
   - User support email: Your email
   - App logo: (Optional)

2. **App domain:**
   - Application home page: `https://records-ai-v2-969278596906.us-central1.run.app`
   - Application privacy policy link: (Optional)
   - Application terms of service link: (Optional)
   - Authorized domains: (If using custom domain)

3. **Developer contact information:**
   - Email addresses: Your email

Click **SAVE AND CONTINUE** after each section.

### Step 4: Add Test Users

1. On the **Test users** section (or **Scopes** if Test users isn't visible yet):
2. Click **+ ADD USERS**
3. Add test user email: `isanli058@gmail.com`
4. Click **ADD**
5. Click **SAVE AND CONTINUE**

### Step 5: Publish App

**CRITICAL STEP:**

1. At the top of the OAuth consent screen, you'll see:
   - Status: **Testing** or **In production**

2. Click **PUBLISH APP** button (or **BACK TO DASHBOARD** → **PUBLISH APP**)

3. Confirm the publish action

4. Wait 1-2 minutes for changes to propagate

**Important:** 
- Publishing makes the app available to all Google users (external)
- In "Testing" mode, only test users can access
- Once published, you can add more test users or allow any Google account

### Step 6: Verify Configuration

**Authorized JavaScript origins** (APIs & Services → Credentials → OAuth 2.0 Client):
- `https://records-ai-v2-969278596906.us-central1.run.app`
- `http://localhost:8000`
- `http://127.0.0.1:8000`

**Authorized redirect URIs:**
- `https://records-ai-v2-969278596906.us-central1.run.app/auth/callback`
- `https://records-ai-v2-969278596906.us-central1.run.app/login.html`
- `http://localhost:8000/auth/callback`
- `http://127.0.0.1:8000/auth/callback`

### Step 7: Test Login

1. Open your app in browser
2. Try Google OAuth login
3. You should see Google login screen (not "org_internal" error)
4. After login, you should be redirected back to your app

## Expected Result

✅ No more `403 org_internal` error
✅ Google OAuth login works for external users
✅ Test user `isanli058@gmail.com` can log in

## Troubleshooting

**If you still see "org_internal" error:**
- Wait 2-3 minutes for Google to propagate changes
- Clear browser cache and cookies
- Try incognito/private browsing mode
- Verify OAuth consent screen status shows "In production"

**If "Publish App" button is grayed out:**
- Complete all required fields (marked with *)
- Make sure User Type is set to "External"
- Check that test users are added

## Notes

- External apps require verification if requesting sensitive scopes
- For testing, you can keep it in "Testing" mode with test users
- Once published, any Google account can log in (unless you restrict in code)
