# Security Fix - Password Removal

## Issue
Hardcoded passwords were committed to the public GitHub repository.

## Actions Taken

1. **Removed hardcoded passwords from all scripts:**
   - `create_admin.ps1` - Now prompts for password
   - `get_admin_token.ps1` - Now prompts for password
   - `cloudshell_create_admin.sh` - Now prompts for password
   - `cloudshell_create_admin_db.py` - Now prompts for password

2. **Added .gitignore:**
   - Token files (`.auth_token.txt`, `.admin_token.txt`)
   - Secret files (`*.secret`, `*.key`, `*.pem`)
   - Environment files (`.env`)

3. **Git History Cleanup Required:**
   The password still exists in git history. To completely remove it:

   ```bash
   # Option 1: Use git filter-branch (slow but thorough)
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch create_admin.ps1 get_admin_token.ps1 cloudshell_create_admin.sh cloudshell_create_admin_db.py scripts/create_admin_user.py" \
     --prune-empty --tag-name-filter cat -- --all

   # Option 2: Use BFG Repo-Cleaner (faster, recommended)
   # Download from: https://rtyley.github.io/bfg-repo-cleaner/
   bfg --replace-text passwords.txt

   # After cleanup, force push (WARNING: This rewrites history)
   git push --force --all
   ```

## Immediate Actions Required

1. **Change the password immediately:**
   - Log in to the system
   - Change password for `ednovitsky@novitskyarchive.com`
   - Use a strong, unique password

2. **Review access logs:**
   - Check if unauthorized access occurred
   - Review Cloud Run access logs
   - Check database access logs

3. **Rotate any related credentials:**
   - If this password was used elsewhere, change it
   - Review all systems that might have been accessed

## Prevention

- Never commit passwords or secrets to git
- Use environment variables or secure secret management
- Use `.gitignore` for sensitive files
- Use pre-commit hooks to scan for secrets
- Consider using tools like `git-secrets` or `truffleHog`
