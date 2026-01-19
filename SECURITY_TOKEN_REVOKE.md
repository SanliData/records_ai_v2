# 🚨 ACİL GÜVENLİK: GitHub Token İptal

## ❌ Sızdırılan Token
`YOUR_GITHUB_TOKEN`

## ✅ YAPILACAKLAR (ÖNCELİK SIRASI)

### 1️⃣ Token'ı HEMEN İPTAL ET
1. GitHub'a git: https://github.com/settings/tokens
2. Token listesini bul
3. `YOUR_GITHUB_TOKEN` token'ını BUL
4. ❌ **REVOKE** / **Delete** butonuna tıkla
5. Onayla

### 2️⃣ Yeni Token Oluştur
1. GitHub → Settings → Developer settings → Personal Access Tokens → **Tokens (classic)**
2. **Generate new token (classic)**
3. **Sadece bu yetkileri seç:**
   - ✅ `repo` (read + write)
   - ❌ admin
   - ❌ delete
   - ❌ workflow
   - ❌ org erişimleri
4. Token'ı **KOPYALA** (bir daha gösterilmez)

### 3️⃣ Güvenli Kimlik Doğrulama (Windows/Credential Manager)

#### Cloud Shell için:
```bash
# Token'ı environment variable olarak kaydet (geçici)
export GITHUB_TOKEN="YENİ_TOKEN_BURAYA"

# Git credential helper kullan
git config --global credential.helper store

# İlk kez pull yap (token sorulacak)
git pull origin main
# Username: SanliData
# Password: YENİ_TOKEN_BURAYA (şifre değil, token!)
```

#### Local Windows için:
```powershell
# Git Credential Manager'ı etkinleştir
git config --global credential.helper manager

# İlk pull'da token girin
git pull origin main
# Username: SanliData  
# Password: YENİ_TOKEN_BURAYA
```

### 4️⃣ ❌ ASLA YAPMA
```bash
# ❌ BUNU ASLA KULLANMA
git pull https://username:TOKEN@github.com/...

# ❌ Token'ı komut satırına yazma
# ❌ Token'ı dosyaya kaydetme
# ❌ Token'ı commit etme
```

### 5️⃣ ✅ DOĞRU YÖNTEMLER

#### Cloud Shell'de:
```bash
# Normal pull (credential helper kullanır)
git pull origin main
```

#### Deploy (token gerektirmez):
```bash
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --project records-ai
```

## 🔒 Token Güvenliği İpuçları

1. **Token'ı sadece bir kez kopyala** - ekran görüntüsü alma
2. **Token'ı asla commit etme** - `.gitignore`'a ekle
3. **Token'ı asla paylaşma** - private chat'lerde bile
4. **Düzenli olarak rotate et** - 90 günde bir yenile
5. **Minimal yetkiler ver** - sadece gerekli scope'lar

## 📋 Token İptal Sonrası Kontrol

Token iptal edildikten sonra:
```bash
# Bu komut başarısız olmalı
git pull https://SanliData:YOUR_GITHUB_TOKEN@github.com/...
# ❌ Expected: Authentication failed
```

## ✅ Token İptal Edildikten Sonra

1. Yeni token oluşturuldu mu? ✅
2. Credential helper yapılandırıldı mı? ✅
3. `git pull origin main` çalışıyor mu? ✅
