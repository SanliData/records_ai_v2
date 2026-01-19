# OAuth Client URI Düzeltme Rehberi
## "no registered origin" Hatasını Çözme

### 🔴 Hata:
```
no registered origin
Error 401: invalid_client
```

### ✅ Çözüm:

OAuth Client ayarlarına uygulama URL'lerini eklemeniz gerekiyor.

---

## ADIM ADIM ÇÖZÜM

### ADIM 1: OAuth Client'ı Düzenle

1. **Google Cloud Console** → **Google Auth Platform** → **Clients**
2. **"Records AI Web Client"** satırında **kalem (edit) ikonuna** tıklayın

---

### ADIM 2: Authorized JavaScript origins Ekleyin

1. **"Authorized JavaScript origins"** bölümünde **"+ Add URI"** butonuna tıklayın
2. Şu URL'yi ekleyin:
   ```
   https://records-ai-v2-969278596906.europe-west1.run.app
   ```
3. Enter'a basın veya ekleme butonuna tıklayın

---

### ADIM 3: Authorized redirect URIs Ekleyin (Opsiyonel ama önerilir)

1. **"Authorized redirect URIs"** bölümünde **"+ Add URI"** butonuna tıklayın
2. Şu URL'yi ekleyin:
   ```
   https://records-ai-v2-969278596906.europe-west1.run.app/auth/callback
   ```
3. Eğer farklı bir callback URL kullanıyorsanız, onu da ekleyin

---

### ADIM 4: Kaydedin

1. **"SAVE"** veya **"UPDATE"** butonuna tıklayın
2. Ayarların etkili olması 5 dakika kadar sürebilir

---

## Özel Domain Kullanıyorsanız

Eğer `api.zyagrolia.com` gibi özel bir domain kullanıyorsanız, onu da ekleyin:

**Authorized JavaScript origins:**
```
https://api.zyagrolia.com
```

**Authorized redirect URIs:**
```
https://api.zyagrolia.com/auth/callback
```

---

## ✅ Kontrol Listesi

- [ ] OAuth Client edit sayfası açıldı
- [ ] Authorized JavaScript origins'e URL eklendi
- [ ] Authorized redirect URIs'e URL eklendi (opsiyonel)
- [ ] Değişiklikler kaydedildi
- [ ] 5 dakika beklenildi (ayarların aktif olması için)

---

## Not

- Değişikliklerin etkili olması 5 dakika - birkaç saat sürebilir
- Ayarların hemen aktif olması garanti değildir
- Test etmeden önce biraz bekleyin

---

**Son Güncelleme:** 2026-01-18
