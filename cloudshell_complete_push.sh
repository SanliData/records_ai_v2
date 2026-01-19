#!/bin/bash
# Cloud Shell'de çalıştırılacak - Local revizyonu GitHub'a push etmek için

set -e

echo "========================================"
echo "Local Revizyonu GitHub'a Push"
echo "========================================"
echo ""

# Adım 1: Repository dizinine git
echo "[1/5] Repository dizinine gidiliyor..."
cd ~/records_ai || {
    echo "HATA: ~/records_ai bulunamadı!"
    echo "Önce: cd ~ && git clone https://github.com/SanliData/records_ai.git && cd records_ai"
    exit 1
}
echo "✓ Dizin: $(pwd)"
echo ""

# Adım 2: Dosyaların varlığını kontrol et
echo "[2/5] Local dosyalar kontrol ediliyor..."
if [ -d ~/records_ai_v2 ]; then
    echo "✓ ~/records_ai_v2 dizini bulundu"
    FILE_COUNT=$(find ~/records_ai_v2 -type f | wc -l)
    echo "  Dosya sayısı: $FILE_COUNT"
elif [ -f ~/records_ai_v2.zip ]; then
    echo "⚠ ZIP dosyası bulundu, çıkarılıyor..."
    cd ~
    unzip -q records_ai_v2.zip || unzip records_ai_v2.zip
    echo "✓ ZIP çıkarıldı"
    cd ~/records_ai
else
    echo "❌ Local dosyalar bulunamadı!"
    echo ""
    echo "Lütfen önce ZIP'i Cloud Shell'e yükleyin:"
    echo "1. Cloud Shell Editor → File → Upload Files"
    echo "2. records_ai_v2.zip dosyasını yükleyin"
    echo "3. unzip records_ai_v2.zip çalıştırın"
    exit 1
fi
echo ""

# Adım 3: Dosyaları repository'ye kopyala
echo "[3/5] Dosyalar repository'ye kopyalanıyor..."
# .git klasörünü korumak için önce kontrol
if [ -d .git ]; then
    echo "✓ .git klasörü mevcut, korunuyor"
    # .git hariç diğer her şeyi kopyala
    rsync -av --exclude='.git' ~/records_ai_v2/ . 2>/dev/null || cp -r ~/records_ai_v2/* . 2>/dev/null || {
        echo "⚠ Kopyalama hatası, alternatif yöntem deneniyor..."
        find ~/records_ai_v2 -type f ! -path "*/\.git/*" -exec cp --parents {} . \;
    }
else
    cp -r ~/records_ai_v2/* .
fi
echo "✓ Dosyalar kopyalandı"
echo ""

# Adım 4: Git durumunu kontrol et
echo "[4/5] Git durumu kontrol ediliyor..."
git status --short | head -20 || echo "Git durumu alınamadı"
echo ""

# Adım 5: Git işlemleri
echo "[5/5] Git işlemleri yapılıyor..."

echo ""
echo "⚠ Tüm değişiklikler eklenecek ve commit edilecek!"
echo ""
read -p "Devam etmek için Enter'a basın, iptal için Ctrl+C..."

# Add
echo "git add ."
git add .

# Commit
COMMIT_MSG="feat: Major revision - local changes $(date +'%Y-%m-%d %H:%M')"
echo "git commit -m \"$COMMIT_MSG\""
git commit -m "$COMMIT_MSG" || {
    echo "⚠ Commit başarısız (değişiklik olmayabilir)"
    echo "Mevcut durum:"
    git status --short
    exit 0
}

# Push
echo ""
echo "GitHub'a push ediliyor..."
echo "git push origin main"
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✓ BAŞARILI! GitHub'a push edildi"
    echo "========================================"
    echo ""
    echo "Repository: https://github.com/SanliData/records_ai"
    echo "Branch: main"
    echo ""
    echo "Sonraki adım: Production deployment"
    echo "  Local'den: .\QUICK_DEPLOY.ps1"
    echo "  VEYA GitHub'dan deploy için Cloud Build trigger kurun"
else
    echo ""
    echo "⚠ Push hatası!"
    echo ""
    echo "Çözüm: Personal Access Token kullanın:"
    echo "1. https://github.com/settings/tokens adresine gidin"
    echo "2. 'Generate new token (classic)' → Scopes: repo"
    echo "3. Token ile push:"
    echo "   git push https://YOUR_TOKEN@github.com/SanliData/records_ai.git main"
fi

echo ""
