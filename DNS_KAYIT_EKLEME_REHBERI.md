# novitskyarchive.com DNS Kayıt Ekleme Rehberi

## Google Workspace DNS Ayarlarına Erişim

### 1. Google Admin Console'a Giriş
- URL: https://admin.google.com
- Giriş: `ednovitsky@novitskyarchive.com` ile giriş yapın

### 2. Domain Ayarlarına Gitme
1. Sol menüden **"Hesap"** bölümünü genişletin
2. **"Alanlar"** altında **"Alanları yönetin"** seçeneğine tıklayın
3. `novitskyarchive.com` domain'ine tıklayın
4. **"DNS kayıtlarını göster"** veya **"DNS Ayarları"** sekmesine gidin

---

## DNS Kayıt Türleri ve Nasıl Eklenir

### A) Domain Doğrulama Kaydı (TXT)

**Ne zaman gerekir:** Cloud Console'da domain doğrulama adımında

**Kayıt bilgileri:**
- **Tür:** TXT
- **Ad/İsim:** `@` (veya boş bırakılabilir)
- **Değer:** Cloud Console'da gösterilen doğrulama metni (örnek: `google-site-verification=ABC123...`)

**Ekleme adımları:**
1. Google Workspace Admin → Domain Settings → DNS Records
2. **"+ Kayıt ekle"** veya **"Add record"** butonuna tıklayın
3. Tür olarak **TXT** seçin
4. İsim alanına `@` yazın (veya boş bırakın)
5. Değer alanına Cloud Console'dan kopyaladığınız TXT değerini yapıştırın
6. TTL (Time To Live) varsayılan değerde bırakılabilir (örn: 3600)
7. **Kaydet** butonuna tıklayın

---

### B) Domain Mapping Kaydı (CNAME veya A)

**Ne zaman gerekir:** Domain doğrulandıktan sonra, Cloud Console size gösterir

#### Seçenek 1: CNAME Kaydı (Önerilen)

**Kayıt bilgileri:**
- **Tür:** CNAME
- **Ad/İsim:** `@` (root domain için)
- **Değer/Hedef:** Cloud Console'da gösterilen hedef (örnek: `ghs.googlehosted.com` veya benzeri)

**Ekleme adımları:**
1. Google Workspace Admin → Domain Settings → DNS Records
2. **"+ Kayıt ekle"** butonuna tıklayın
3. Tür olarak **CNAME** seçin
4. İsim alanına `@` yazın (root domain için)
5. Değer alanına Cloud Console'dan verilen hedef adresi yazın
6. **Kaydet** butonuna tıklayın

**Not:** Bazı DNS sağlayıcıları root domain (`@`) için CNAME kabul etmez. Bu durumda **A kaydı** kullanılmalıdır.

---

#### Seçenek 2: A Kaydı (CNAME desteklenmiyorsa)

**Kayıt bilgileri:**
- **Tür:** A
- **Ad/İsim:** `@` (root domain için)
- **Değer/IP Adresi:** Cloud Console'da gösterilen IP adresi (örnek: `216.239.32.21`)

**Ekleme adımları:**
1. Google Workspace Admin → Domain Settings → DNS Records
2. **"+ Kayıt ekle"** butonuna tıklayın
3. Tür olarak **A** seçin
4. İsim alanına `@` yazın
5. IP adresi alanına Cloud Console'dan verilen IP'yi yazın
6. **Kaydet** butonuna tıklayın

---

## Önemli Notlar

### DNS Yayılımı Süresi
- DNS kayıtları genellikle **5-30 dakika** içinde yayılır
- Bazen **24-48 saat** sürebilir (nadir)
- Yayılımı kontrol etmek için: https://dnschecker.org

### Doğrulama Kontrolü
1. Cloud Console'da domain mapping sayfasına gidin
2. Domain'in yanında **yeşil tik** görünene kadar bekleyin
3. Durum "Active" olmalı

### Hata Durumları

**Eğer CNAME hatası alırsanız:**
- Root domain için CNAME bazı sağlayıcılarda desteklenmez
- A kaydı kullanın (Cloud Console size IP verecek)

**Eğer doğrulama başarısız olursa:**
- TXT kaydının doğru kopyalandığından emin olun
- Tırnak işaretleri varsa onları dahil edin
- 24 saat bekleyip tekrar deneyin

---

## Cloud Console'dan DNS Bilgilerini Alma

1. **Cloud Console → Cloud Run → Domain Mappings** sayfasına gidin
2. Domain'inizi seçin (veya "Add mapping" adımında gösterilir)
3. DNS kayıtları otomatik olarak gösterilir:
   - **TXT kaydı** (doğrulama için)
   - **CNAME veya A kaydı** (mapping için)
4. Bu bilgileri Google Workspace DNS ayarlarına ekleyin

---

## Test Etme

DNS kayıtlarını ekledikten sonra:

```powershell
# PowerShell'de DNS sorgusu
nslookup novitskyarchive.com

# veya
Resolve-DnsName novitskyarchive.com -Type A
Resolve-DnsName novitskyarchive.com -Type CNAME
Resolve-DnsName novitskyarchive.com -Type TXT
```

**Online test:**
- https://dnschecker.org/#A/novitskyarchive.com
- https://dnschecker.org/#TXT/novitskyarchive.com

---

## Özet Checklist

- [ ] Google Admin Console'a giriş yapıldı
- [ ] Domain Settings → DNS Records açıldı
- [ ] Cloud Console'dan TXT kaydı kopyalandı
- [ ] TXT kaydı Google Workspace'e eklendi
- [ ] Domain doğrulandı (Cloud Console'da yeşil tik)
- [ ] Cloud Console'dan CNAME/A kaydı alındı
- [ ] CNAME veya A kaydı Google Workspace'e eklendi
- [ ] 5-30 dakika beklendi (DNS yayılımı için)
- [ ] Domain mapping "Active" durumuna geçti
- [ ] https://novitskyarchive.com test edildi

---

## Yardımcı Linkler

- **Google Admin Console:** https://admin.google.com
- **Cloud Run Domain Mappings:** https://console.cloud.google.com/run/domains?project=records-ai
- **DNS Checker:** https://dnschecker.org
- **Google Workspace DNS Yardım:** https://support.google.com/a/answer/48090
