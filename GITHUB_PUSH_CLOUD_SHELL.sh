#!/bin/bash
# Cloud Shell'den GitHub'a Push Script
# Records AI V2 - Local değişiklikleri GitHub'a push etmek için

set -e

echo "========================================"
echo "Records AI V2 - GitHub Push (Cloud Shell)"
echo "========================================"
echo ""

# Configuration
GITHUB_REPO="https://github.com/SanliData/records_ai.git"
REPO_NAME="records_ai"

echo "Repository: $GITHUB_REPO"
echo ""

# Check if Git is available
echo "[1/4] Checking Git installation..."
if ! command -v git &> /dev/null; then
    echo "ERROR: Git not found!"
    echo "Installing Git..."
    sudo apt-get update
    sudo apt-get install -y git
fi
echo "✓ Git found: $(git --version)"
echo ""

# Clone or update repository
echo "[2/4] Setting up repository..."
cd ~

if [ -d "$REPO_NAME" ]; then
    echo "Repository already exists, updating..."
    cd $REPO_NAME
    git pull origin main || true
else
    echo "Cloning repository..."
    git clone $GITHUB_REPO
    cd $REPO_NAME
fi
echo "✓ Repository ready"
echo ""

# Instructions for copying files
echo "[3/4] Manual step required:"
echo ""
echo "Please copy your local files to Cloud Shell:"
echo "1. Use Cloud Shell Editor (File → Upload Files)"
echo "2. Upload the local C:\\Users\\issan\\records_ai_v2 directory (as ZIP or files)"
echo "3. Extract if needed: unzip records_ai_v2.zip"
echo "4. Copy files: cp -r records_ai_v2/* ~/$REPO_NAME/"
echo ""
read -p "Press Enter after copying files..."

# Git operations
echo "[4/4] Git operations..."
echo ""

# Check status
git status --short

# Add all changes
echo "Adding files..."
git add .

# Commit
COMMIT_MSG="feat: Local changes from records_ai_v2 - $(date +'%Y-%m-%d %H:%M')"
echo "Commit message: $COMMIT_MSG"
git commit -m "$COMMIT_MSG" || echo "No changes to commit"

# Push
echo ""
echo "Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✓ Successfully pushed to GitHub!"
    echo "========================================"
    echo ""
    echo "Repository: $GITHUB_REPO"
    echo "Branch: main"
    echo ""
else
    echo ""
    echo "ERROR: Push failed!"
    echo ""
    echo "Possible issues:"
    echo "1. Authentication required (use Personal Access Token)"
    echo "2. Repository permissions"
    echo ""
    echo "Solution: Use token for push"
    echo "  git push https://YOUR_TOKEN@github.com/SanliData/records_ai.git main"
    echo ""
fi
