#!/bin/bash
# Cloud Shell'de çalıştır - Güvenli git pull

cd ~/records_ai_v2

echo "📋 1. Credential helper yapılandırılıyor..."
git config --global credential.helper store

echo ""
echo "📋 2. Git pull yapılıyor..."
echo "⚠️  Token sorulursa:"
echo "   Username: SanliData"
echo "   Password: YOUR_GITHUB_TOKEN"
echo ""
git pull origin main

echo ""
echo "✅ Pull tamamlandı!"
echo "💡 Token artık credential store'da güvenli şekilde saklandı."
