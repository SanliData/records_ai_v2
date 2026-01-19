# 🔧 OAuth Origin Mismatch Düzeltme

## ❌ Hata
**Error 400: origin_mismatch**

`https://zyagrolia.com` domain'i Google OAuth client konfigürasyonunda tanımlı değil.

## ✅ ÇÖZÜM: Google Cloud Console'da OAuth Client Güncelle

### Adım 1: Google Cloud Console'a Git
1. **Google Cloud Console**: https://console.cloud.google.com/
2. **Project seç**: `records-ai` (Project ID: 969278596906)
3. **Navigation Menu** (☰) → **APIs & Services** → **Credentials**

### Adım 2: OAuth Client'ı Bul
1. **OAuth 2.0 Client IDs** listesinde şunu bul:
   - **Client ID**: `969278596906-afqorvadshqquuhts4rpk0620dgg1fa4`
   - **Name**: Muhtemelen "Web client" veya benzeri

2. **Edit** (✏️) butonuna tıkla

### Adım 3: Authorized JavaScript Origins Ekle
**Authorized JavaScript origins** bölümüne şunları ekle:

```
https://zyagrolia.com
https://records-ai-v2-969278596906.us-central1.run.app
```

**ÖNEMLİ:**
- Protocol (`https://`) ekle
- Trailing slash (`/`) ekleme
- Her origin'i ayrı satıra yaz

### Adım 4: Authorized Redirect URIs (Gerekirse)
Eğer OAuth callback kullanıyorsan, **Authorized redirect URIs** bölümüne ekle:

```
https://zyagrolia.com/auth/callback
https://records-ai-v2-969278596906.us-central1.run.app/auth/callback
```

### Adım 5: Kaydet
1. **Save** butonuna tıkla
2. Değişiklikler **hemen aktif olur** (güncelleme gerekmez)

### Adım 6: Test Et
1. Tarayıcıda `https://zyagrolia.com/login.html` aç
2. "Sign in with Google" butonuna tıkla
3. OAuth hatası artık görünmemeli

---

## 📋 Mevcut Konfigürasyon (Kontrol İçin)

**OAuth Client ID:**
```
969278596906-afqorvadshqquuhts4rpk0620dgg1fa4.apps.googleusercontent.com
```

**Kullanım yeri:**
- `frontend/login.html` → `google.accounts.id.initialize()`

**Backend endpoint:**
- `POST /auth/login/google` → `backend/api/v1/auth_router.py`

---

## ⚠️ GÜVENLİK NOTLARI

1. **Sadece kendi domain'lerini ekle** - Başka domain ekleme
2. **HTTPS zorunlu** - HTTP ekleme
3. **Test domain'lerini kaldır** - Production'da sadece `zyagrolia.com` olmalı

---

## ✅ Doğrulama

OAuth client'ı güncelledikten sonra:

```bash
# Test: Login sayfasını aç
curl -I https://zyagrolia.com/login.html

# OAuth akışı çalışmalı (browser'da test et)
```
