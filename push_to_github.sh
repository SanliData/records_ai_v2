#!/bin/bash
# Cloud Shell'de çalıştırılacak script
# Bu script'i Cloud Shell Editor'de oluşturup çalıştırabilirsiniz

set -e

echo "========================================"
echo "Local Revizyonu GitHub'a Push"
echo "========================================"
echo ""

# Adım 1: ZIP'i çıkar
echo "[1/4] ZIP dosyası çıkarılıyor..."
if [ -f "records_ai_v2 (2).zip" ]; then
    unzip -q "records_ai_v2 (2).zip" || unzip "records_ai_v2 (2).zip"
    echo "✓ ZIP çıkarıldı"
else
    echo "⚠ ZIP dosyası bulunamadı, mevcut dizinde:"
    ls -la *.zip 2>/dev/null || echo "ZIP dosyası yok"
fi
echo ""

# Adım 2: Repository'ye git
echo "[2/4] Repository dizinine gidiliyor..."
if [ -d ~/records_ai ]; then
    cd ~/records_ai
    echo "✓ Dizin: $(pwd)"
else
    echo "⚠ Repository bulunamadı, oluşturuluyor..."
    cd ~
    git clone https://github.com/SanliData/records_ai.git
    cd ~/records_ai
fi
echo ""

# Adım 3: Dosyaları kopyala
echo "[3/4] Dosyalar kopyalanıyor..."
if [ -d ~/records_ai_v2 ]; then
    cp -r ~/records_ai_v2/* . 2>/dev/null || rsync -av --exclude='.git' ~/records_ai_v2/ . || true
    echo "✓ Dosyalar kopyalandı"
else
    echo "⚠ records_ai_v2 dizini bulunamadı"
fi
echo ""

# Adım 4: Git işlemleri
echo "[4/4] Git işlemleri..."
git add .
git commit -m "feat: Major revision - local changes $(date +'%Y-%m-%d %H:%M')" || echo "⚠ Commit başarısız (değişiklik olmayabilir)"
git push origin main || echo "⚠ Push hatası - token gerekebilir"

echo ""
echo "========================================"
echo "İşlem tamamlandı!"
echo "========================================"
echo ""
echo "GitHub: https://github.com/SanliData/records_ai"
echo ""
