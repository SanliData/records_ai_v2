# 🚀 novitskyarchive.com DNS Kayıt Ekleme - Basit Rehber

## ⚡ Hızlı Başlangıç

Bu rehber sadece **3 adım** içeriyor. Her adımda **sadece kopyala-yapıştır** yapacaksınız!

---

## 📋 ADIM 1: Cloud Console'dan DNS Kayıtlarını Kopyalayın

### 1.1. Cloud Console'a gidin
```
https://console.cloud.google.com/run/domains?project=records-ai
```

### 1.2. "+ Add mapping" butonuna tıklayın

### 1.3. Domain'i girin
- **Base domain to verify:** `novitskyarchive.com` yazın
- **Continue** butonuna tıklayın

### 1.4. DNS kayıtlarını görüntüleyin
- Ekranda **iki tür kayıt** göreceksiniz:
  1. **TXT kaydı** (doğrulama için) - Bunu kopyalayın
  2. **CNAME veya A kaydı** (mapping için) - Bunu da kopyalayın

**⚠️ ÖNEMLİ:** Bu kayıtları **bir not defterine kopyalayın**. Örnek format:

```
TXT kaydı:
@    TXT    google-site-verification=ABC123xyz...

CNAME kaydı:
@    CNAME    ghs.googlehosted.com
```

---

## 📋 ADIM 2: Squarespace'e Giriş Yapın

### 2.1. Google Admin Console'dan Squarespace'e geçiş
1. Google Admin Console'da `novitskyarchive.com` detaylarına gidin
2. **"ALANI YÖNET (Squarespace üzerinden)"** linkine tıklayın
3. Google hesabınızla (`ismail@novitskyarchive.com`) oturum açın

### 2.2. DNS Yönetim Sayfasını Bulun
- Squarespace panelinde **"Settings"** veya **"DNS Settings"** menüsüne gidin
- Veya **"Advanced"** → **"DNS Settings"** seçeneğini bulun

**Not:** Squarespace arayüzü değişebilir. Eğer bulamazsanız, Squarespace arama kutusuna **"DNS"** yazın.

---

## 📋 ADIM 3: DNS Kayıtlarını Ekleyin (Kopyala-Yapıştır)

### 3.1. TXT Kaydını Ekleyin (Doğrulama için)

1. Squarespace DNS sayfasında **"+ Add Record"** veya **"Add DNS Record"** butonuna tıklayın

2. Aşağıdaki bilgileri girin (Cloud Console'dan kopyaladığınız değerler):

   | Alan | Değer |
   |------|-------|
   | **Tür/Type** | `TXT` |
   | **Host/Name** | `@` (veya boş bırakın) |
   | **Value/Data** | `Cloud Console'dan kopyaladığınız TXT değeri` |
   | **TTL** | Varsayılan (değiştirmeyin) |

3. **"Save"** veya **"Add Record"** butonuna tıklayın

**✅ Kontrol:** Kayıt listede görünmeli!

---

### 3.2. CNAME veya A Kaydını Ekleyin (Mapping için)

**Önce TXT kaydının doğrulandığını bekleyin (5-10 dakika).**

1. Cloud Console'da domain mapping sayfasına geri dönün
2. Mapping için gösterilen **CNAME veya A kaydını** kopyalayın

3. Squarespace'te **yeni bir kayıt** ekleyin:

   **Eğer CNAME kaydı ise:**
   | Alan | Değer |
   |------|-------|
   | **Tür/Type** | `CNAME` |
   | **Host/Name** | `@` |
   | **Target/Value** | `ghs.googlehosted.com` (Cloud Console'dan kopyaladığınız değer) |
   | **TTL** | Varsayılan |

   **Eğer A kaydı ise (CNAME desteklenmiyorsa):**
   | Alan | Değer |
   |------|-------|
   | **Tür/Type** | `A` |
   | **Host/Name** | `@` |
   | **IP Address** | `216.239.32.21` (Cloud Console'dan kopyaladığınız IP) |
   | **TTL** | Varsayılan |

4. **"Save"** butonuna tıklayın

---

## ⏱️ Bekleme Süresi

- **TXT kaydı doğrulama:** 5-10 dakika
- **CNAME/A kaydı yayılım:** 10-30 dakika
- **Toplam:** Maksimum 1 saat (genellikle daha kısa)

---

## ✅ Kontrol Etme

### Cloud Console'da kontrol:
1. Domain mappings sayfasına gidin
2. `novitskyarchive.com` yanında **yeşil tik** görmeli
3. Durum **"Active"** olmalı

### Tarayıcıda test:
- `https://novitskyarchive.com/` açılmalı
- `https://novitskyarchive.com/ui/` çalışmalı

---

## 🆘 Sorun Giderme

### Problem: TXT kaydı doğrulanmıyor
- **Çözüm:** 
  - TXT değerini tekrar kontrol edin (tam kopyalandığından emin olun)
  - 24 saat bekleyip tekrar deneyin
  - Squarespace DNS kayıtlarında kaydın göründüğünü kontrol edin

### Problem: CNAME kaydı eklenemiyor
- **Çözüm:**
  - Root domain (`@`) için CNAME bazı sağlayıcılarda desteklenmez
  - Bu durumda **A kaydı** kullanın (Cloud Console size IP verecek)

### Problem: Domain hala çalışmıyor
- **Çözüm:**
  - DNS yayılımını kontrol edin: https://dnschecker.org
  - 24-48 saat bekleyin (nadir durum)
  - Squarespace'te kayıtların doğru eklendiğini kontrol edin

---

## 📞 Yardım Gerekiyorsa

Eğer takıldığınız bir adım varsa:
1. Hangi adımda takıldığınızı belirtin
2. Cloud Console'dan kopyaladığınız DNS kayıt değerlerini paylaşın
3. Squarespace ekran görüntüsü paylaşabilirseniz daha iyi yardımcı olabilirim

---

## 🎯 Özet Checklist

- [ ] Cloud Console'dan TXT kaydını kopyaladım
- [ ] Cloud Console'dan CNAME/A kaydını kopyaladım
- [ ] Squarespace'e giriş yaptım
- [ ] TXT kaydını Squarespace'e ekledim
- [ ] 10 dakika bekledim (doğrulama için)
- [ ] CNAME/A kaydını Squarespace'e ekledim
- [ ] 30 dakika bekledim (DNS yayılımı için)
- [ ] Cloud Console'da domain "Active" durumuna geçti
- [ ] https://novitskyarchive.com test ettim - ÇALIŞIYOR! ✅

---

**💡 İpucu:** En kolay yol, her adımda Cloud Console'daki değerleri **kopyala-yapıştır** yapmak. Hiçbir şey yazmanıza gerek yok!
