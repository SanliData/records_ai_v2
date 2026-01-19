# Push Changes with GitHub Token

## 1. Git Commit (PowerShell)

```powershell
# Stage all modified files
git add backend/main.py
git add backend/api/v1/upap_upload_router.py
git add backend/db.py
git add backend/core/error_handler.py
git add requirements.txt

# Commit
git commit -m "fix: critical security and stability fixes - auth, rate limiting, data persistence"

# Verify
git status
```

## 2. Push with Token (PowerShell)

```powershell
# Push using token
git push https://SanliData:YOUR_GITHUB_TOKEN@github.com/SanliData/records_ai_v2.git main
```

**OR** use environment variable (more secure):

```powershell
$env:GIT_TOKEN = "YOUR_GITHUB_TOKEN"
git push https://SanliData:$env:GIT_TOKEN@github.com/SanliData/records_ai_v2.git main
```

## 3. Alternative: Set Remote with Token

```powershell
# Update remote URL with token
git remote set-url origin https://SanliData:YOUR_GITHUB_TOKEN@github.com/SanliData/records_ai_v2.git

# Then push normally
git push origin main
```

## 4. One-Liner (All-in-One)

```powershell
git add backend/main.py backend/api/v1/upap_upload_router.py backend/db.py backend/core/error_handler.py requirements.txt && git commit -m "fix: critical security and stability fixes" && git push https://SanliData:YOUR_GITHUB_TOKEN@github.com/SanliData/records_ai_v2.git main
```

---

## Security Note

⚠️ Token is visible in command history. After push, consider:
- Revoking this token and creating a new one
- Using Git Credential Manager for secure storage
