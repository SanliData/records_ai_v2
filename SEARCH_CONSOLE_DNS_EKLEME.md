# Search Console DNS Kaydı Ekleme - novitskyarchive.com

## 📋 TXT Kaydı Bilgileri

**Search Console Doğrulama TXT Kaydı:**
```
google-site-verification=BHCAjtNXtH8orf0B04TIlYecCbZ1RKMjyS6a_TAOEVE
```

---

## 🔧 Google Domains'e TXT Kaydı Ekleme

### ADIM 1: Google Domains'e Giriş
1. **https://domains.google.com** adresine gidin
2. Google hesabınızla giriş yapın
3. **`novitskyarchive.com`** domain'ini seçin

### ADIM 2: DNS Ayarlarına Gidin
1. Sol menüden **"DNS"** sekmesine tıklayın
2. **"Custom resource records"** (Özel kaynak kayıtları) bölümünü bulun

### ADIM 3: TXT Kaydını Ekleyin
1. **"Create new record"** veya **"+ Add"** butonuna tıklayın
2. Form alanlarını doldurun:

   | Alan | Değer |
   |------|-------|
   | **Name** | `@` (veya boş bırakın) |
   | **Type** | `TXT` |
   | **TTL** | `3600` (varsayılan) |
   | **Data** | `google-site-verification=BHCAjtNXtH8orf0B04TIlYecCbZ1RKMjyS6a_TAOEVE` |

3. **"Save"** veya **"Add"** butonuna tıklayın

⚠️ **Not:** 
- Mevcut SPF TXT kaydı (`v=spf1 include:_spf.google.com ~all`) varsa, onu silmeyin.
- Search Console TXT kaydını **ayrı bir kayıt** olarak ekleyin.
- Birden fazla TXT kaydı olabilir.

---

## ⏱️ Bekleme Süresi

1. **DNS kaydını ekledikten sonra 5-10 dakika bekleyin**
2. Google Search Console sayfasına geri dönün
3. **"DOĞRULA"** butonuna tıklayın

---

## ✅ Doğrulama Kontrolü

### PowerShell'de kontrol:
```powershell
# TXT kayıtlarını kontrol et
Resolve-DnsName novitskyarchive.com -Type TXT
```

Google-site-verification kaydını görmeli.

### Online kontrol:
- https://dnschecker.org/#TXT/novitskyarchive.com

---

## 🎯 Özet

| Adım | Nerede | Ne Yapılacak |
|------|--------|--------------|
| 1 | Google Domains | DNS sekmesine git |
| 2 | Google Domains | TXT kaydı ekle (`google-site-verification=BHCAjtNXtH8orf0B04TIlYecCbZ1RKMjyS6a_TAOEVE`) |
| 3 | Bekle | 5-10 dakika (DNS yayılımı) |
| 4 | Search Console | "DOĞRULA" butonuna tıkla |

---

## 📝 Notlar

- Bu TXT kaydı **sadece Search Console doğrulaması** için.
- **Cloud Run domain mapping** için ayrı bir TXT kaydı gerekecek (Cloud Console'dan alınacak).
- Her iki TXT kaydını da aynı anda Google Domains'e ekleyebilirsiniz.

---

## 🔗 Hızlı Linkler

- **Google Domains:** https://domains.google.com
- **Search Console:** https://search.google.com/search-console
- **DNS Kontrol:** https://dnschecker.org/#TXT/novitskyarchive.com
