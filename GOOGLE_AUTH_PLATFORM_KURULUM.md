# Google Auth Platform Kurulum Rehberi
## Records AI Projesi için OAuth Yapılandırması

### 📍 Mevcut Durum
- Proje: `records-ai`
- Google Auth Platform henüz yapılandırılmamış
- OAuth client hatası alınıyor

---

## ADIM ADIM KURULUM

### ADIM 1: Get Started Butonuna Tıklayın

Cloud Console'da (https://console.cloud.google.com/auth/overview?authuser=1&project=records-ai):
1. Ana sayfada **"Get started"** mavi butonuna tıklayın

---

### ADIM 2: App Information (Uygulama Bilgileri)

**App name (Uygulama Adı):**
```
Records AI
```

**User support email:**
```
ednovitsky@novitskyarchive.com
```

**App logo (Opsiyonel):**
- Logo ekleyebilirsiniz veya boş bırakabilirsiniz

**App domain (Opsiyonel):**
```
zyagrolia.com
```

**Developer contact information:**
```
ednovitsky@novitskyarchive.com
```

**"SAVE AND CONTINUE" butonuna tıklayın**

---

### ADIM 3: Scopes (API İzinleri)

**Scopes Nedir?**
- Scopes, uygulamanızın kullanıcı verilerine nasıl erişebileceğini belirler
- Örnek: Email adresi, profil fotoğrafı, isim gibi bilgilere erişim izni

**Ne Yapmalısınız?**
- **Varsayılan ayarları koruyun** - Genellikle yeterlidir
- **"ADD OR REMOVE SCOPES" butonuna tıklamayın** (eğer gerekmezse)
- Direkt **"SAVE AND CONTINUE"** butonuna tıklayın

**Varsayılan Scopes (Otomatik Eklenir):**
- `openid` - Kullanıcının kim olduğunu doğrulama
- `.../auth/userinfo.email` - Email adresine erişim
- `.../auth/userinfo.profile` - Profil bilgilerine erişim (isim, fotoğraf)

**Bu yeterli mi?** 
✅ Evet! Records AI için bu yeterli. Başka bir şey gerekmez.

**"SAVE AND CONTINUE" butonuna tıklayın**

---

### ADIM 4: Test Users (Test Kullanıcıları)

Eğer "Internal" veya "Testing" modundaysanız:

1. **"ADD USERS"** butonuna tıklayın
2. Test kullanıcılarını ekleyin:
   ```
   ednovitsky@novitskyarchive.com
   isanli058@gmail.com
   ```
3. **"ADD"** butonuna tıklayın
4. **"SAVE AND CONTINUE"** butonuna tıklayın

---

### ADIM 5: Summary ve Publish

1. Yapılandırmayı kontrol edin
2. **"BACK TO DASHBOARD"** veya **"PUBLISH APP"** butonuna tıklayın

Eğer production için gerekliyse:
- **"PUBLISH APP"** butonuna tıklayın
- Verification gerekebilir (çoğunlukla gerekmez)

---

### ADIM 6: OAuth Client ID Oluşturma

1. Sol menüden **"Clients"** sekmesine gidin
2. **"CREATE CLIENT"** butonuna tıklayın
3. **Application type:** `Web application` seçin
4. **Name:** `Records AI Web Client`
5. **Authorized redirect URIs** (gerekirse ekleyin):
   ```
   https://records-ai-v2-969278596906.europe-west1.run.app/auth/callback
   https://api.zyagrolia.com/auth/callback
   ```
6. **"CREATE"** butonuna tıklayın
7. **Client ID** ve **Client Secret** kaydedin (güvenli yerde saklayın)

---

## ✅ Kontrol Listesi

- [ ] ADIM 1: Get started butonuna tıklandı
- [ ] ADIM 2: App information dolduruldu
- [ ] ADIM 3: Scopes ayarlandı
- [ ] ADIM 4: Test users eklendi (gerekirse)
- [ ] ADIM 5: Yapılandırma kaydedildi
- [ ] ADIM 6: OAuth Client ID oluşturuldu

---

## 🔍 Alternatif: API & Services Üzerinden

Eğer yukarıdaki yöntem çalışmazsa:

1. **APIs & Services** → **Credentials** (https://console.cloud.google.com/apis/credentials)
2. **"CREATE CREDENTIALS"** → **"OAuth client ID"**
3. Yeni bir OAuth client oluşturun

---

## 📝 Notlar

1. **OAuth client hatası** genellikle Client ID'nin yanlış yapılandırılması veya eksik olmasından kaynaklanır
2. **Test users** sadece Internal/Testing modunda gereklidir
3. **Production** için verification gerekebilir (çoğunlukla gerekmez)

---

**Son Güncelleme:** 2026-01-18
