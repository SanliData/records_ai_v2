# 🔐 GitHub Push - Güvenli Yöntem

## ✅ Commit Hazır
Commit başarıyla oluşturuldu:
```
[main 91e6475] fix: replace backend.storage imports with backend.db for production
 5 files changed, 222 insertions(+), 205 deletions(-)
```

## 🚀 Push Komutları

### Yöntem 1: Token ile URL (Hızlı)
```bash
git push https://YOUR_GITHUB_TOKEN@github.com/SanliData/records_ai_v2.git main
```

### Yöntem 2: Credential Helper (Önerilen - Güvenli)
```bash
# Token'ı credential helper'a kaydet
git config --global credential.helper store

# Push yap (ilk seferde token soracak)
git push origin main
# Username: SanliData
# Password: YOUR_GITHUB_TOKEN
```

### Yöntem 3: Interactive (En Güvenli)
```bash
git push origin main
# Username: SanliData
# Password: YOUR_GITHUB_TOKEN
```

---

## 📋 Bilgiler
- **Repository**: `SanliData/records_ai_v2`
- **Branch**: `main`
- **Token**: `YOUR_GITHUB_TOKEN`
- **Username**: `SanliData`

---

## ⚠️ Güvenlik Notu
Token'ı komut geçmişinde saklamamak için Yöntem 2 veya 3'ü kullanın.
