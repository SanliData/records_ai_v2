# Güvenli GitHub Push Rehberi
## Hassas Bilgileri GitHub'a Göndermeden Push Etme

### 🔒 Güvenlik Kontrol Listesi

`.gitignore` dosyası şu dosyaları ignore ediyor:
- ✅ `*.json` - Tüm JSON dosyaları (keys, secrets içerebilir)
- ✅ `*.key`, `*.pem` - Key dosyaları
- ✅ `.env` - Environment variables
- ✅ `*.db` - Database dosyaları
- ✅ `sa-key.json`, `records-ai-runtime-key.json` - Specific keys
- ✅ `storage/`, `uploads/`, `data/` - User data

---

## ⚠️ KONTROL EDİLMESİ GEREKEN DOSYALAR

### 🔴 ASLA PUSH ETMEYİN:

1. **`sa-key.json`** - Service Account Key (Google Cloud)
2. **`records-ai-runtime-key.json`** - Runtime Key
3. **`*.db` dosyaları** - Database dosyaları:
   - `records_ai_v2.db`
   - `records_ai.db`
   - `records.db`
4. **`.env`** - Environment variables
5. **`*.key`, `*.pem`** - Private keys

---

## ✅ GÜVENLİ PUSH ADIMLARI

### ADIM 1: Git Durumunu Kontrol Et

**PowerShell'de:**

```powershell
cd C:\Users\issan\records_ai_v2

# Durumu kontrol et
git status
```

### ADIM 2: Güvenli Olmayan Dosyaları Kontrol Et

```powershell
# Güvenli olmayan dosyalar stage'de mi kontrol et
git status --ignored
```

### ADIM 3: .gitignore'ı Güçlendir (Gerekirse)

`.gitignore` dosyası zaten iyi, ama kontrol edelim. Eğer eksikse şu satırları ekleyin:

```gitignore
# Secrets / keys (zaten var)
*.json
*.key
*.pem
.env
sa-key.json
records-ai-runtime-key.json

# Databases (zaten var)
*.db

# Önemli: Özel key dosyalarını ekle
records-ai-runtime-key.json
sa-key.json
**/sa-key.json
**/*-key.json
```

---

## 🔍 ADIM ADIM GÜVENLİ PUSH

### ADIM 1: Sadece Kod Dosyalarını Ekle

**Tek tek ekleyerek (ÖNERİLEN):**

```powershell
cd C:\Users\issan\records_ai_v2

# Sadece kod dosyalarını ekle
git add backend/
git add frontend/
git add scripts/
git add requirements.txt
git add dockerfile
git add README.md
git add .gitignore
git add alembic/
git add tests/
git add docs/
```

**VEYA** `.gitignore` güvenli ise:

```powershell
git add .
```

### ADIM 2: Stage'deki Dosyaları Kontrol Et

```powershell
# Stage'e eklenen dosyaları listele
git status

# ÖNEMLİ: Aşağıdaki dosyalar listede OLMAMALI:
# - sa-key.json
# - records-ai-runtime-key.json
# - *.db
# - .env
```

### ADIM 3: Eğer Güvenli Olmayan Dosya Görürseniz

```powershell
# Stage'den çıkar
git reset HEAD sa-key.json
git reset HEAD records-ai-runtime-key.json
git reset HEAD *.db
```

### ADIM 4: Commit ve Push

```powershell
# Commit
git commit -m "feat: Production deployment - us-central1, OAuth fixes, merge conflicts resolved"

# Push
git push origin main
```

---

## 🛡️ .gitignore Kontrolü

`.gitignore` dosyanızda şunlar olmalı:

```gitignore
# Secrets / keys
*.json
*.key
*.pem
.env
sa-key.json
records-ai-runtime-key.json

# Databases
*.db

# Uploads / runtime data
uploads/
storage/
media/
data/
```

**Not:** `*.json` kuralı **tüm JSON dosyalarını** ignore ediyor. Eğer bazı JSON dosyalarını (örneğin `records_ai.app.json`) push etmek isterseniz, `.gitignore`'ı güncellemeniz gerekir.

---

## ✅ GÜVENLİ PUSH KONTROL LİSTESİ

Push etmeden önce kontrol edin:

- [ ] `sa-key.json` stage'de DEĞİL
- [ ] `records-ai-runtime-key.json` stage'de DEĞİL
- [ ] `*.db` dosyaları stage'de DEĞİL
- [ ] `.env` dosyası stage'de DEĞİL
- [ ] `git status` çıktısını kontrol ettiniz
- [ ] Sadece kod dosyaları stage'de

---

## 🔧 .gitignore'ı Güncelleme (Opsiyonel)

Eğer bazı JSON dosyalarını push etmek isterseniz (örneğin config dosyaları), `.gitignore`'ı şöyle güncelleyin:

```gitignore
# Secrets / keys - spesifik dosyaları ignore et
sa-key.json
records-ai-runtime-key.json
*-key.json
*-secret.json

# Ama diğer JSON dosyalarına izin ver (opsiyonel)
# !records_ai.app.json
```

---

## 📋 Hızlı Güvenli Push Komutları

```powershell
cd C:\Users\issan\records_ai_v2

# 1. Durumu kontrol et
git status

# 2. Sadece güvenli dosyaları ekle
git add backend/
git add frontend/
git add scripts/
git add requirements.txt
git add dockerfile
git add README.md
git add .gitignore

# 3. Güvenli olmayan dosyaları kontrol et
git status | Select-String -Pattern "sa-key|records-ai-runtime-key|\.db$|\.env"

# 4. Eğer yukarıdaki komut sonuç döndürürse, o dosyaları stage'den çıkar
# git reset HEAD [dosya_adı]

# 5. Commit ve push
git commit -m "feat: Production deployment updates"
git push origin main
```

---

**ÖNEMLİ:** Push etmeden önce mutlaka `git status` çıktısını kontrol edin!

---

**Son Güncelleme:** 2026-01-18
