# ✅ novitskyarchive.com DNS Kayıt Ekleme - Google Domains

## 🎯 Tespit Edildi!

Domain'iniz **Google Domains** üzerinden yönetiliyor:
- Nameserver'lar: `ns-cloud-a*.googledomains.com`
- Mevcut A kaydı: `34.27.124.176`
- DNS yönetimi: **Google Domains** panelinden yapılmalı

---

## 📋 ADIM ADIM: Google Domains'te DNS Kayıt Ekleme

### ADIM 1: Google Domains'e Giriş

1. **Google Domains'e gidin:**
   ```
   https://domains.google.com
   ```

2. **Google hesabınızla giriş yapın:**
   - `ismail@novitskyarchive.com` veya `ednovitsky@novitskyarchive.com` ile giriş

3. **Domain'i seçin:**
   - `novitskyarchive.com` üzerine tıklayın

---

### ADIM 2: DNS Ayarlarına Erişim

1. Sol menüden **"DNS"** sekmesine tıklayın
2. **"Custom resource records"** (Özel kaynak kayıtları) bölümüne gidin

---

### ADIM 3: Cloud Console'dan DNS Kayıtlarını Kopyalayın

1. **Cloud Console'a gidin:**
   ```
   https://console.cloud.google.com/run/domains?project=records-ai
   ```

2. **"+ Add mapping"** butonuna tıklayın

3. **Domain girin:**
   - Base domain to verify: `novitskyarchive.com`
   - Continue butonuna tıklayın

4. **DNS kayıtlarını görüntüleyin:**
   - **TXT kaydı** (doğrulama için)
   - **CNAME veya A kaydı** (mapping için)

5. **Kayıtları kopyalayın** - Örnek format:
   ```
   TXT kaydı:
   @    TXT    google-site-verification=ABC123xyz...
   
   CNAME kaydı:
   @    CNAME    ghs.googlehosted.com
   ```

---

### ADIM 4: Google Domains'e TXT Kaydını Ekleyin

1. Google Domains DNS sayfasında **"Custom resource records"** bölümüne gidin

2. **"Create new record"** veya **"+ Add"** butonuna tıklayın

3. **TXT kaydı ekleyin:**
   | Alan | Değer |
   |------|-------|
   | **Name** | `@` (veya boş bırakın) |
   | **Type** | `TXT` |
   | **TTL** | `3600` (varsayılan) |
   | **Data** | Cloud Console'dan kopyaladığınız TXT değeri |

4. **"Add"** veya **"Save"** butonuna tıklayın

✅ **Not:** Mevcut TXT kaydı (`v=spf1 include:_spf.google.com ~all`) varsa, onu silmeyin. Yeni TXT kaydını ekleyin.

---

### ADIM 5: Bekleyin (Doğrulama için)

- **5-10 dakika bekleyin** (DNS yayılımı için)
- Cloud Console'da domain'in doğrulandığını kontrol edin (yeşil tik görünmeli)

---

### ADIM 6: Google Domains'e CNAME veya A Kaydını Ekleyin

**Doğrulama tamamlandıktan sonra:**

1. Cloud Console'da mapping için gösterilen **CNAME veya A kaydını** kopyalayın

2. Google Domains DNS sayfasında **"Create new record"** butonuna tıklayın

3. **CNAME kaydı ekleyin (eğer gösteriliyorsa):**
   | Alan | Değer |
   |------|-------|
   | **Name** | `@` |
   | **Type** | `CNAME` |
   | **TTL** | `3600` |
   | **Data** | `ghs.googlehosted.com` (Cloud Console'dan kopyaladığınız değer) |

   **VEYA**

   **A kaydı ekleyin (eğer CNAME desteklenmiyorsa):**
   | Alan | Değer |
   |------|-------|
   | **Name** | `@` |
   | **Type** | `A` |
   | **TTL** | `3600` |
   | **Data** | `216.239.32.21` (Cloud Console'dan kopyaladığınız IP) |

4. **"Add"** veya **"Save"** butonuna tıklayın

⚠️ **ÖNEMLİ:** Eğer `@` için mevcut bir A kaydı varsa (örn: `34.27.124.176`), onu silmeniz gerekebilir. Önce Cloud Run mapping'i için yeni kaydı ekleyin, sonra eski kaydı kaldırın.

---

### ADIM 7: Son Kontrol

1. **30 dakika bekleyin** (DNS yayılımı için)

2. **Cloud Console'da kontrol:**
   - Domain mapping sayfasına gidin
   - `novitskyarchive.com` yanında **yeşil tik** görmeli
   - Durum **"Active"** olmalı

3. **Tarayıcıda test:**
   - `https://novitskyarchive.com/` açılmalı
   - `https://novitskyarchive.com/ui/` çalışmalı

---

## 🎯 Özet Checklist

- [ ] Google Domains'e giriş yaptım (`https://domains.google.com`)
- [ ] `novitskyarchive.com` domain'ini seçtim
- [ ] DNS sekmesine gittim
- [ ] Cloud Console'dan TXT kaydını kopyaladım
- [ ] Google Domains'e TXT kaydını ekledim
- [ ] 10 dakika bekledim (doğrulama için)
- [ ] Cloud Console'da doğrulandığını kontrol ettim
- [ ] Cloud Console'dan CNAME/A kaydını kopyaladım
- [ ] Google Domains'e CNAME/A kaydını ekledim
- [ ] 30 dakika bekledim (DNS yayılımı için)
- [ ] https://novitskyarchive.com test ettim - ÇALIŞIYOR! ✅

---

## 🔗 Hızlı Linkler

- **Google Domains:** https://domains.google.com
- **Cloud Run Domain Mappings:** https://console.cloud.google.com/run/domains?project=records-ai
- **DNS Kontrol:** https://dnschecker.org/#A/novitskyarchive.com

---

## 💡 İpuçları

1. **Mevcut A kaydı:** `34.27.124.176` şu anda kayıtlı. Cloud Run mapping için yeni kayıt eklerken, eski kaydı kaldırmayı unutmayın (veya yeni kayıt otomatik olarak öncelikli olacak).

2. **CNAME vs A:** Root domain (`@`) için CNAME bazı sistemlerde desteklenmez. Bu durumda A kaydı kullanın.

3. **Çoklu TXT kayıtları:** Google Workspace SPF kaydı (`v=spf1...`) ile Cloud Run doğrulama TXT kaydı birlikte olabilir. Her ikisini de tutun.

---

**🎉 Artık DNS kayıtlarını doğru yerde (Google Domains) ekleyebilirsiniz!**
