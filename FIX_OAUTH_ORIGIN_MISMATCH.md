# OAuth Origin Mismatch - Hızlı Çözüm

## 🔴 Sorun
Google OAuth `origin_mismatch` hatası: `http://127.0.0.1:8082` origin'i kayıtlı değil.

## ✅ Çözüm (2 Dakika)

### Adım 1: Google Cloud Console'a Git
1. https://console.cloud.google.com/apis/credentials?project=records-ai
2. OAuth 2.0 Client ID'yi bul: `969278596906-afqorvadshqquuhts4rpk0620dgg1fa4`
3. **EDIT** butonuna tıkla

### Adım 2: Authorized JavaScript Origins Ekle
**Authorized JavaScript origins** bölümüne ekle:
```
http://127.0.0.1:8082
http://localhost:8082
http://127.0.0.1:8000
http://localhost:8000
```

### Adım 3: Authorized Redirect URIs Ekle
**Authorized redirect URIs** bölümüne ekle:
```
http://127.0.0.1:8082/auth/callback
http://localhost:8082/auth/callback
http://127.0.0.1:8000/auth/callback
http://localhost:8000/auth/callback
```

### Adım 4: SAVE
**SAVE** butonuna tıkla (değişiklikler 1-2 dakika içinde aktif olur)

## 🚀 Alternatif: Production URL'leri de Ekle
Production için de ekle:
```
https://zyagrolia.com
https://api.zyagrolia.com
https://records-ai-v2-969278596906.us-central1.run.app
```

## ✅ Test
1. Tarayıcıyı yenile (hard refresh: CTRL+SHIFT+R)
2. http://127.0.0.1:8082/login.html
3. "Google ile oturum açın" butonuna tıkla
4. Artık çalışmalı!

## 📝 Not
Değişiklikler Google tarafında 1-2 dakika içinde aktif olur. Hala çalışmazsa:
- Tarayıcı cache'ini temizle
- Incognito mode'da dene
- 2 dakika bekle ve tekrar dene
