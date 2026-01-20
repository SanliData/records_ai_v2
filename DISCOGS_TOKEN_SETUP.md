# Discogs Token Setup Guide

## 🔒 Security Best Practices

**NEVER commit tokens to git!**

The Discogs token is stored securely and only accessed via environment variables.

---

## 📋 Local Development Setup

### Option 1: Using Helper Script (Recommended)

```powershell
# Set token from file
.\set_discogs_token.ps1

# Start server
uvicorn backend.main:app --reload
```

### Option 2: Manual Environment Variable

```powershell
# Set token directly (session only)
$env:DISCOGS_TOKEN = "your_token_here"

# Or from file
$env:DISCOGS_TOKEN = Get-Content .discogs_token.txt -Raw | ForEach-Object { $_.Trim() }
```

### Option 3: .env File (if using python-dotenv)

Create `.env` file:
```
DISCOGS_TOKEN=your_token_here
```

---

## ☁️ Cloud Run Production Setup

### Option 1: Environment Variable (Simple)

```bash
gcloud run services update records-ai-v2 \
  --set-env-vars DISCOGS_TOKEN=your_token_here \
  --region us-central1
```

### Option 2: Secret Manager (Recommended for Production)

```bash
# 1. Create secret
echo -n "your_token_here" | gcloud secrets create discogs-token \
  --data-file=- \
  --replication-policy="automatic"

# 2. Grant access to Cloud Run service account
gcloud secrets add-iam-policy-binding discogs-token \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# 3. Update Cloud Run service to use secret
gcloud run services update records-ai-v2 \
  --update-secrets DISCOGS_TOKEN=discogs-token:latest \
  --region us-central1
```

---

## ✅ Security Checklist

- [x] Token file (`.discogs_token.txt`) in `.gitignore`
- [x] Token NOT hardcoded in code
- [x] Token only accessed via `os.getenv("DISCOGS_TOKEN")`
- [x] Token NOT in git history
- [ ] Token stored in Secret Manager (production)
- [ ] Token rotated regularly

---

## 🔄 Token Rotation

If token is compromised:

1. Generate new token at: https://www.discogs.com/settings/developers
2. Update environment variable or Secret Manager
3. Restart Cloud Run service
4. Revoke old token in Discogs settings

---

## 📝 Notes

- Token is required for Discogs collection features
- Without token, collection features will be unavailable (graceful degradation)
- Token is user-specific (ednovitsky's Discogs account)
