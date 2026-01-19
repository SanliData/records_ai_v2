# GCloud Authentication Fix Guide

## Problem Analysis

### Why This Error Happens

**Error:** "You do not currently have an active account selected. Please run: gcloud auth login"

**Root Cause:**
- `gcloud` CLI is not authenticated with any Google account
- No active account is set in the gcloud configuration
- This happens when:
  - First time using gcloud on this machine
  - Previous auth token expired
  - Using a new terminal/session without saved credentials

### Authentication Types Explained

#### 1. `gcloud auth login`
**Purpose:** Authenticates your user account for gcloud CLI commands
- Opens browser for OAuth flow
- Stores credentials in `~/.config/gcloud/`
- Required for: `gcloud run deploy`, `gcloud projects list`, etc.
- **Use this for:** Interactive CLI operations

#### 2. `gcloud auth application-default login`
**Purpose:** Sets Application Default Credentials (ADC) for client libraries
- Used by Python/Java/etc. client libraries
- Different credential store than `gcloud auth login`
- Required for: `google-cloud-*` Python packages
- **Use this for:** Application code that uses GCP client libraries

#### 3. `gcloud config set account`
**Purpose:** Switches between multiple authenticated accounts
- Only works if you've already run `gcloud auth login`
- Changes which account is "active" for commands
- **Use this for:** Switching between personal/work accounts

**For Cloud Run deploy, you need `gcloud auth login` (not application-default).**

---

## Step-by-Step Fix

### Step 1: Authenticate User Account

```bash
# This opens a browser - complete the OAuth flow
gcloud auth login

# If browser doesn't open automatically, use:
gcloud auth login --no-browser
# Then copy the URL and open in your browser
```

**Expected Output:**
```
You are now logged in as: your-email@gmail.com
```

### Step 2: Verify Active Account

```bash
# List all authenticated accounts
gcloud auth list

# Check current configuration
gcloud config list
```

**Expected Output:**
```
Credentialed Accounts
ACTIVE  ACCOUNT
*       your-email@gmail.com

[core]
account = your-email@gmail.com
project = (unset)
```

### Step 3: Set Project

```bash
# List available projects
gcloud projects list

# Set active project
gcloud config set project records-ai

# Verify project is set
gcloud config get-value project
```

**Expected Output:**
```
PROJECT_ID          NAME           PROJECT_NUMBER
records-ai          Records AI     123456789012

Updated property [core/project] to [records-ai].
records-ai
```

### Step 4: Verify IAM Permissions

```bash
# Check your current permissions
gcloud projects get-iam-policy records-ai \
  --flatten="bindings[].members" \
  --filter="bindings.members:user:$(gcloud config get-value account)" \
  --format="table(bindings.role)"

# Or check specific roles
gcloud projects get-iam-policy records-ai \
  --flatten="bindings[].members" \
  --format="table(bindings.role)" \
  | grep -E "(run\.admin|serviceAccountUser|cloudbuild\.builds\.editor)"
```

**Required Roles:**
- `roles/run.admin` - Deploy and manage Cloud Run services
- `roles/iam.serviceAccountUser` - Use service accounts
- `roles/cloudbuild.builds.editor` - Trigger builds

**If missing permissions, ask project admin to grant:**
```bash
# Admin runs this:
gcloud projects add-iam-policy-binding records-ai \
  --member="user:your-email@gmail.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding records-ai \
  --member="user:your-email@gmail.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding records-ai \
  --member="user:your-email@gmail.com" \
  --role="roles/cloudbuild.builds.editor"
```

### Step 5: Verify Cloud Run Access

```bash
# List existing Cloud Run services (tests permissions)
gcloud run services list --region us-central1

# If this works, you have the right permissions
```

---

## Complete Fix Sequence (Copy-Paste Ready)

```bash
# 1. Authenticate
gcloud auth login

# 2. Verify account
gcloud auth list
gcloud config list

# 3. Set project
gcloud config set project records-ai
gcloud config get-value project

# 4. Verify permissions (optional check)
gcloud projects get-iam-policy records-ai \
  --flatten="bindings[].members" \
  --filter="bindings.members:user:$(gcloud config get-value account)" \
  --format="table(bindings.role)"

# 5. Test Cloud Run access
gcloud run services list --region us-central1

# 6. Deploy
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080
```

---

## One-Line Deploy Retry

After authentication is complete:

```bash
gcloud run deploy records-ai-v2 --source . --platform managed --region us-central1 --allow-unauthenticated --port 8080 --max-instances 3 --min-instances 0 --timeout 300 --memory 1Gi --cpu 1
```

---

## Persisting Auth in Cloud Shell

### Cloud Shell (Automatic)
- **Cloud Shell automatically authenticates** when you open it
- No `gcloud auth login` needed
- Credentials persist across sessions
- **Just verify project is set:**
  ```bash
  gcloud config get-value project
  # If not set:
  gcloud config set project records-ai
  ```

### Local Machine (Manual)
- Credentials stored in `~/.config/gcloud/`
- Persist across terminal sessions
- **To refresh expired token:**
  ```bash
  gcloud auth login --update-adc
  ```

### CI/CD (Service Account)
- Use service account key file
- **DO NOT use `gcloud auth login` in CI/CD**
- Instead:
  ```bash
  gcloud auth activate-service-account --key-file=service-account-key.json
  ```

---

## Auth Sanity Checklist

Before deploying, verify:

- [ ] `gcloud auth list` shows ACTIVE account with `*`
- [ ] `gcloud config get-value project` returns `records-ai`
- [ ] `gcloud config get-value account` returns your email
- [ ] `gcloud run services list` works (tests permissions)
- [ ] `gcloud projects list` shows `records-ai` project

**Quick Check Command:**
```bash
echo "Account: $(gcloud config get-value account)" && \
echo "Project: $(gcloud config get-value project)" && \
echo "Auth Status: $(gcloud auth list --filter=status:ACTIVE --format='value(account)')"
```

**Expected Output:**
```
Account: your-email@gmail.com
Project: records-ai
Auth Status: your-email@gmail.com
```

---

## Troubleshooting

### "Permission denied" after auth
- Check IAM roles (Step 4 above)
- Ask project admin to grant required roles

### "Project not found"
- Verify project ID: `gcloud projects list`
- Check spelling: `records-ai` (not `records_ai` or `records-ai-v2`)

### "Browser can't open"
- Use `gcloud auth login --no-browser`
- Copy URL and open manually

### "Token expired"
- Run `gcloud auth login` again
- Or: `gcloud auth application-default login` (for client libraries)

---

## Final Verified Deploy Command

After completing authentication:

```bash
# Verify auth first
gcloud config get-value account && gcloud config get-value project

# Deploy
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --max-instances 3 \
  --min-instances 0 \
  --timeout 300 \
  --memory 1Gi \
  --cpu 1 \
  --set-env-vars PORT=8080
```

---

## Summary

**Quick Fix (3 commands):**
```bash
gcloud auth login                    # Authenticate
gcloud config set project records-ai # Set project
gcloud run deploy records-ai-v2 --source . --region us-central1 --allow-unauthenticated --port 8080
```

**In Cloud Shell (usually just):**
```bash
gcloud config set project records-ai  # Auth is automatic
gcloud run deploy records-ai-v2 --source . --region us-central1 --allow-unauthenticated --port 8080
```
