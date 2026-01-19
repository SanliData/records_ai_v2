# EXECUTE THESE COMMANDS - DEPLOYMENT

## ⚠️ Git Not in PATH

PowerShell can't find `git`. Use **Git Bash** or add git to PATH.

## ✅ FIXES VERIFIED LOCALLY

All files are clean:
- ✅ No merge conflict markers found
- ✅ Duplicate title tag removed
- ✅ Valid HTML structure

## 🚀 DEPLOYMENT STEPS

### Step 1: Open Git Bash (or CMD with git in PATH)

Run these commands in Git Bash:

```bash
cd /c/Users/issan/records_ai_v2

# Verify files are clean
git status

# Stage fixed files
git add frontend/upload.html
git add frontend/novitsky/index.html
git add frontend/novitsky/works.html
git add frontend/novitsky/biography.html

# Commit
git commit -m "fix: remove merge conflict markers from frontend HTML"

# Push
git push origin main
```

### Step 2: Deploy to Cloud Run

**Option A: From PowerShell (after git push):**
```powershell
gcloud run deploy records-ai-v2 --source . --region us-central1 --project records-ai --allow-unauthenticated --port 8080
```

**Option B: From Cloud Shell (recommended):**
```bash
cd ~/records_ai_v2
git pull origin main
gcloud run deploy records-ai-v2 --source . --region us-central1 --project records-ai --allow-unauthenticated --port 8080
```

## 📊 SUMMARY

**Files Fixed:**
1. `frontend/upload.html` - Duplicate title removed, no conflict markers
2. `frontend/novitsky/index.html` - Clean
3. `frontend/novitsky/works.html` - Clean  
4. `frontend/novitsky/biography.html` - Clean

**Status:**
- ✅ Local files verified clean (no conflict markers)
- ⏳ Waiting for git push
- ⏳ Waiting for Cloud Run deployment

**Next:** Run git commands above, then deploy.
