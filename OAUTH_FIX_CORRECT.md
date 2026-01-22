# ✅ OAuth Yapılandırması - DOĞRU YÖNTEM

## ⚠️ ÖNEMLİ: İki Farklı Bölüm Var!

### 1️⃣ Authorized JavaScript Origins
**SADECE domain + port (path YOK!)**

✅ **DOĞRU:**
```
http://127.0.0.1:8082
http://localhost:8082
```

❌ **YANLIŞ:**
```
http://127.0.0.1:8082/auth/callback  ← PATH VAR, HATA!
http://localhost:8082/              ← SONUNDA / VAR, HATA!
```

### 2️⃣ Authorized Redirect URIs
**Path İÇEREBİLİR**

✅ **DOĞRU:**
```
http://127.0.0.1:8082/auth/callback
http://localhost:8082/auth/callback
```

## 📋 Adım Adım

### Adım 1: Authorized JavaScript Origins
1. **Authorized JavaScript origins** bölümüne git
2. **SADECE şunları ekle (path YOK!):**
   ```
   http://127.0.0.1:8082
   http://localhost:8082
   ```
3. ✅ Her biri sadece domain + port olmalı

### Adım 2: Authorized Redirect URIs
1. **Authorized redirect URIs** bölümüne git
2. **Path'li URI'leri ekle:**
   ```
   http://127.0.0.1:8082/auth/callback
   http://localhost:8082/auth/callback
   ```
3. ✅ Burada path olabilir

### Adım 3: SAVE
- **SAVE** butonuna tıkla
- 1-2 dakika bekle
- Test et

## 🔍 Hata Mesajı Görürsen
**"Invalid Origin: URIs must not contain a path"**

→ **Authorized JavaScript origins** bölümündesin
→ Path'i kaldır, sadece `http://127.0.0.1:8082` yaz

## ✅ Kontrol Listesi

**Authorized JavaScript Origins:**
- [ ] `http://127.0.0.1:8082` (path YOK)
- [ ] `http://localhost:8082` (path YOK)
- [ ] Hiçbirinde `/` veya path yok

**Authorized Redirect URIs:**
- [ ] `http://127.0.0.1:8082/auth/callback` (path VAR)
- [ ] `http://localhost:8082/auth/callback` (path VAR)
