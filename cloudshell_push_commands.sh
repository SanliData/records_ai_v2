#!/bin/bash
# Cloud Shell'de çalıştırılacak komutlar
# GitHub'a push için hazırlık

set -e

echo "========================================"
echo "Records AI V2 - GitHub Push (Cloud Shell)"
echo "========================================"
echo ""

# Configuration
REPO_DIR="~/records_ai"
SOURCE_DIR="~/records_ai_v2"

echo "[1/3] Checking repository..."
cd ~/records_ai || {
    echo "ERROR: ~/records_ai directory not found!"
    echo "Run: cd ~ && git clone https://github.com/SanliData/records_ai.git && cd records_ai"
    exit 1
}

echo "✓ Repository found"
echo "Current directory: $(pwd)"
echo ""

# Check if source files exist
echo "[2/3] Checking source files..."
if [ -d "$SOURCE_DIR" ]; then
    echo "✓ Source files found at: $SOURCE_DIR"
elif [ -f ~/records_ai_v2.zip ]; then
    echo "✓ ZIP file found, extracting..."
    cd ~
    unzip -q records_ai_v2.zip || unzip records_ai_v2.zip
    echo "✓ Extracted"
else
    echo "⚠ Source files not found!"
    echo ""
    echo "Please upload your local files first:"
    echo "1. Use Cloud Shell Editor → File → Upload Files"
    echo "2. Upload C:\\Users\\issan\\records_ai_v2 as ZIP"
    echo "3. Or use: gcloud cloud-shell scp from local PowerShell"
    echo ""
    read -p "Press Enter after uploading files..."
fi

echo ""

# Copy files to repository
echo "[3/3] Copying files to repository..."
cd ~/records_ai

# Backup .git if exists
if [ -d .git ]; then
    echo "✓ Git repository found"
else
    echo "⚠ .git directory not found, initializing..."
    git init
    git remote add origin https://github.com/SanliData/records_ai.git || true
    git fetch origin
    git checkout -b main || git checkout main || git branch -M main
fi

# Copy files (excluding .git if source has it)
echo "Copying files..."
if [ -d ~/records_ai_v2 ]; then
    # Copy excluding .git if it exists
    rsync -av --exclude='.git' ~/records_ai_v2/ . || cp -r ~/records_ai_v2/* .
else
    echo "⚠ Source directory not found at ~/records_ai_v2"
    echo "   Please upload files first"
    exit 1
fi

echo "✓ Files copied"
echo ""

# Show git status
echo "Git status:"
git status --short | head -20 || echo "No changes or git error"

echo ""
echo "========================================"
echo "Next Steps:"
echo "========================================"
echo ""
echo "1. Review changes:"
echo "   git status"
echo ""
echo "2. Add all changes:"
echo "   git add ."
echo ""
echo "3. Commit:"
echo "   git commit -m 'feat: Local changes from records_ai_v2'"
echo ""
echo "4. Push to GitHub:"
echo "   git push origin main"
echo ""
echo "   (If authentication error, use token:)"
echo "   git push https://YOUR_TOKEN@github.com/SanliData/records_ai.git main"
echo ""
