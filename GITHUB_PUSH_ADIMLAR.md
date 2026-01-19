# GitHub'a Push - Adım Adım Rehber
## Local Değişiklikleri GitHub'a Gönderme

### 📍 Durum
- ✅ Git kurulu ve çalışıyor
- ✅ Repository: https://github.com/SanliData/records_ai
- ✅ Local path: `C:\Users\issan\records_ai_v2`

---

## ADIM ADIM PUSH İŞLEMİ

### ADIM 1: Repository Dizinine Git

**PowerShell'de (kendi pencerenizde):**

```powershell
cd C:\Users\issan\records_ai_v2
```

---

### ADIM 2: Git Kullanıcı Bilgilerini Ayarla

```powershell
git config --global user.name "Isanli"
git config --global user.email "ednovitsky@novitskyarchive.com"
```

---

### ADIM 3: Git Durumunu Kontrol Et

```powershell
git status
```

**Beklenen çıktı:**
- Değişen dosyaların listesi görünecek
- VEYA "nothing to commit" (eğer değişiklik yoksa)

---

### ADIM 4: Remote Repository'yi Kontrol Et

```powershell
git remote -v
```

**Eğer remote yoksa veya yanlışsa:**

```powershell
# Eski remote'u sil (eğer varsa)
git remote remove origin

# Yeni remote ekle
git remote add origin https://github.com/SanliData/records_ai.git

# Kontrol et
git remote -v
```

**Beklenen çıktı:**
```
origin  https://github.com/SanliData/records_ai.git (fetch)
origin  https://github.com/SanliData/records_ai.git (push)
```

---

### ADIM 5: Değişiklikleri Stage'e Ekle

```powershell
git add .
```

**VEYA** sadece belirli dosyalar:

```powershell
# Sadece önemli dosyaları ekle
git add requirements.txt
git add backend/main.py
git add frontend/
```

---

### ADIM 6: Commit Oluştur

```powershell
git commit -m "feat: Major revision - us-central1 deployment, OAuth fixes, merge conflict resolutions"
```

**VEYA** daha detaylı:

```powershell
git commit -m "feat: Production deployment updates

- Fixed merge conflicts in requirements.txt and backend/main.py
- Deployed to us-central1 region (USA)
- Updated OAuth Client ID in frontend
- Added tinydb to requirements
- Fixed BOM encoding issues"
```

---

### ADIM 7: GitHub'a Push Et

```powershell
git push origin main
```

**Eğer ilk push ise veya branch farklıysa:**

```powershell
git push -u origin main
```

---

### ADIM 8: Authentication (Eğer Gerekirse)

Eğer "Permission denied" veya authentication hatası alırsanız:

#### Yöntem 1: Personal Access Token

1. **GitHub'da Token oluşturun:**
   - https://github.com/settings/tokens
   - "Generate new token (classic)"
   - Scopes: `repo` seçin
   - Token'ı kopyalayın

2. **Token ile push:**

```powershell
git push https://YOUR_TOKEN@github.com/SanliData/records_ai.git main
```

#### Yöntem 2: Credential Manager

Git Credential Manager otomatik olarak açılabilir. GitHub'a login yapın.

---

## ✅ Kontrol

Push başarılı olduktan sonra:

1. **GitHub'da kontrol edin:**
   - https://github.com/SanliData/records_ai
   - Son commit'inizi görmeli

2. **Commit kontrol:**

```powershell
git log --oneline -3
```

---

## 🆘 Sorun Giderme

### "remote origin already exists" hatası
**Çözüm:**
```powershell
git remote remove origin
git remote add origin https://github.com/SanliData/records_ai.git
```

### "Permission denied" hatası
**Çözüm:** Personal Access Token kullanın (ADIM 8)

### "nothing to commit" mesajı
**Çözüm:** Zaten tüm değişiklikler commit edilmiş

### "fatal: not a git repository" hatası
**Çözüm:**
```powershell
git init
git remote add origin https://github.com/SanliData/records_ai.git
```

---

## 📋 Hızlı Komut Dizisi

Tüm işlemleri tek seferde:

```powershell
cd C:\Users\issan\records_ai_v2
git config --global user.name "Isanli"
git config --global user.email "ednovitsky@novitskyarchive.com"
git remote remove origin 2>$null
git remote add origin https://github.com/SanliData/records_ai.git
git add .
git commit -m "feat: Production deployment - us-central1, OAuth fixes"
git push origin main
```

---

**Son Güncelleme:** 2026-01-18
