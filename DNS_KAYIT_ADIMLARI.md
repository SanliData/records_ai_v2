# 🚀 novitskyarchive.com DNS Kayıt Ekleme - Adım Adım

## ✅ Durum
- ✅ Domain: Google Domains'te yönetiliyor
- ✅ Nameserver'lar: `ns-cloud-a*.googledomains.com`
- ❌ Squarespace'e gerek yok

---

## 📋 ADIM 1: Cloud Console'dan DNS Kayıtlarını Al

### 1.1 Cloud Console'a gidin
```
https://console.cloud.google.com/run/domains?project=records-ai
```

### 1.2 Domain mapping oluşturun
1. **"+ Add mapping"** butonuna tıklayın
2. **Service:** `records-ai-v2 (us-central1)` seçili olmalı
3. **Domain:** `novitskyarchive.com` yazın
4. **"Continue"** butonuna tıklayın

### 1.3 DNS kayıtlarını kopyalayın
Cloud Console size şu kayıtları gösterecek:

**A) TXT Kaydı (Doğrulama için):**
```
Tür: TXT
Name: @
Value: google-site-verification=ABC123xyz... (bu değeri kopyalayın)
```

**B) CNAME veya A Kaydı (Mapping için):**
Cloud Console size CNAME veya A kaydı gösterecek. Örnek:

**CNAME ise:**
```
Tür: CNAME
Name: @
Value: ghs.googlehosted.com (veya başka bir değer)
```

**A kaydı ise:**
```
Tür: A
Name: @
Value: 216.239.32.21 (IP adresi)
```

---

## 📋 ADIM 2: Google Domains'e DNS Kayıtlarını Ekle

### 2.1 Google Domains'e giriş
1. **https://domains.google.com** adresine gidin
2. Google hesabınızla giriş yapın (`ismail@novitskyarchive.com` veya `ednovitsky@novitskyarchive.com`)
3. **`novitskyarchive.com`** domain'ini seçin

### 2.2 DNS Ayarlarına gidin
1. Sol menüden **"DNS"** sekmesine tıklayın
2. **"Custom resource records"** (Özel kaynak kayıtları) bölümünü bulun

### 2.3 TXT Kaydını Ekleyin
1. **"Create new record"** veya **"+ Add"** butonuna tıklayın
2. Form alanlarını doldurun:
   - **Name:** `@` (veya boş bırakın)
   - **Type:** `TXT` seçin
   - **TTL:** `3600` (varsayılan)
   - **Data:** Cloud Console'dan kopyaladığınız TXT değerini yapıştırın
3. **"Save"** veya **"Add"** butonuna tıklayın

⚠️ **Not:** Mevcut SPF TXT kaydı (`v=spf1 include:_spf.google.com ~all`) varsa, onu silmeyin. Yeni TXT kaydını ekleyin.

---

## 📋 ADIM 3: Bekleme (Doğrulama)

1. **10-15 dakika bekleyin** (DNS yayılımı için)
2. Cloud Console'da domain sayfasına geri dönün
3. Domain'in yanında **yeşil tik** görünene kadar bekleyin
4. Durum **"Active"** veya **"Verified"** olmalı

---

## 📋 ADIM 4: CNAME veya A Kaydını Ekleyin

### Doğrulama tamamlandıktan sonra:

1. **Cloud Console'da mapping sayfasına gidin**
2. **CNAME veya A kaydını görüntüleyin** (doğrulama sonrası gösterilecek)
3. **Kaydı kopyalayın**

### Google Domains'e ekleyin:

**Eğer CNAME kaydı ise:**
1. Google Domains DNS sayfasında **"Create new record"** butonuna tıklayın
2. Form alanlarını doldurun:
   - **Name:** `@`
   - **Type:** `CNAME` seçin
   - **TTL:** `3600`
   - **Data:** `ghs.googlehosted.com` (Cloud Console'dan kopyaladığınız değer)
3. **"Save"** butonuna tıklayın

**VEYA**

**Eğer A kaydı ise:**
1. Google Domains DNS sayfasında **"Create new record"** butonuna tıklayın
2. Form alanlarını doldurun:
   - **Name:** `@`
   - **Type:** `A` seçin
   - **TTL:** `3600`
   - **Data:** `216.239.32.21` (Cloud Console'dan kopyaladığınız IP)
3. **"Save"** butonuna tıklayın

⚠️ **ÖNEMLİ:** 
- Mevcut A kaydı (`34.27.124.176`) varsa ve Cloud Run için yeni bir A kaydı ekliyorsanız, eski kaydı kaldırmanız gerekebilir.
- Ya da Cloud Run size CNAME vermişse, CNAME ekleyin (root domain için CNAME bazı sistemlerde desteklenmez, bu durumda A kullanılır).

---

## 📋 ADIM 5: Son Kontrol

1. **30 dakika bekleyin** (DNS yayılımı için)
2. **Cloud Console'da kontrol:**
   - Domain mapping sayfasına gidin
   - `novitskyarchive.com` yanında **yeşil tik** görmeli
   - Durum **"Active"** olmalı

3. **Tarayıcıda test:**
   ```powershell
   # PowerShell'de test
   Invoke-WebRequest -Uri "https://novitskyarchive.com/" -UseBasicParsing
   ```

   Veya tarayıcıda açın:
   - `https://novitskyarchive.com/`
   - `https://novitskyarchive.com/ui/`

---

## 🎯 Hızlı Özet

| Adım | Nerede | Ne Yapılacak |
|------|--------|--------------|
| 1 | Cloud Console | Domain mapping oluştur, TXT kaydını kopyala |
| 2 | Google Domains | TXT kaydını ekle |
| 3 | Bekle | 10-15 dakika (doğrulama) |
| 4 | Cloud Console | CNAME/A kaydını kopyala |
| 5 | Google Domains | CNAME/A kaydını ekle |
| 6 | Bekle | 30 dakika (DNS yayılımı) |
| 7 | Test | https://novitskyarchive.com çalışmalı ✅ |

---

## 🔗 Hızlı Linkler

- **Google Domains:** https://domains.google.com
- **Cloud Run Domain Mappings:** https://console.cloud.google.com/run/domains?project=records-ai
- **DNS Kontrol:** https://dnschecker.org/#A/novitskyarchive.com

---

## 💡 Sorun Giderme

### TXT kaydı doğrulanmıyor?
- TXT değerinin tam kopyalandığından emin olun
- Google Domains'te kaydın göründüğünü kontrol edin
- 24 saat bekleyip tekrar deneyin

### CNAME kaydı eklenemiyor?
- Root domain (`@`) için CNAME bazı sistemlerde desteklenmez
- Bu durumda **A kaydı** kullanın (Cloud Console size IP verecek)

### Domain hala çalışmıyor?
- DNS yayılımını kontrol edin: https://dnschecker.org/#A/novitskyarchive.com
- Google Domains'te kayıtların doğru eklendiğini kontrol edin
- 24-48 saat bekleyin (nadir durum)

---

**🎉 Başarılar! Adım adım ilerleyin, her adımı tamamladıktan sonra bir sonrakine geçin.**
