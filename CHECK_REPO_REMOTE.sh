#!/bin/bash
# Cloud Shell'de çalıştır - repo remote'unu kontrol et

echo "📋 Mevcut git remote'ları:"
git remote -v

echo ""
echo "📋 Mevcut branch:"
git branch

echo ""
echo "📋 Remote URL'i değiştir (eğer yanlışsa):"
echo "git remote set-url origin https://github.com/SanliData/records_ai_v2.git"
echo ""
echo "Veya mevcut remote'u kontrol et:"
echo "git remote get-url origin"
