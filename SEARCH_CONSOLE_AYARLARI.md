# Google Search Console - novitskyarchive.com Ekleme

## 📋 Adımlar

### 1. Property Tipi Seçimi

**✅ Seçilecek:** **"Alan adı (Domain property)"** (Sol taraftaki seçenek)

**Neden?**
- Tüm alt domain'leri kapsar (`api.novitskyarchive.com`, `www.novitskyarchive.com`, vb.)
- Hem HTTP hem HTTPS protokollerini kapsar
- Cloud Run'da kullanacağımız tüm alt domain'ler için çalışır

### 2. Domain Adını Girin

**Input alanına:**
```
novitskyarchive.com
```

**Not:** `www` veya `https://` eklemeyin, sadece `novitskyarchive.com` yazın.

### 3. "DEVAM" Butonuna Tıklayın

Devam butonuna tıkladıktan sonra, Google size DNS doğrulama yöntemi gösterecek.

---

## 🔐 DNS Doğrulama (Search Console için)

Search Console, domain'i doğrulamak için bir **TXT kaydı** isteyecek. Bu kayıt Cloud Run domain mapping'i için farklı olabilir.

### Doğrulama Adımları:

1. **Search Console doğrulama TXT kaydını kopyalayın**
   - Format: `google-site-verification=ABC123...`

2. **Google Domains'e TXT kaydı ekleyin**
   - https://domains.google.com → `novitskyarchive.com` → DNS
   - "Custom resource records" bölümünde yeni TXT kaydı ekleyin
   - **Not:** Bu, Cloud Run doğrulama TXT kaydından farklı olabilir - her ikisini de ekleyin!

3. **Doğrulamayı tamamlayın**
   - Search Console'da "Doğrula" butonuna tıklayın
   - DNS yayılımı 5-10 dakika sürebilir

---

## ⚠️ Önemli Not

**Search Console doğrulama ≠ Cloud Run domain mapping**

- **Search Console:** Domain'i Google'a web sitesi olarak tanıtmak için
- **Cloud Run Domain Mapping:** Domain'i Cloud Run servisine bağlamak için

İkisi de DNS TXT kaydı gerektirir ama **farklı değerler** kullanır. Her ikisini de Google Domains'e eklemeniz gerekebilir.

---

## 📝 Özet

1. **"Alan adı (Domain property)"** seçeneğini seçin
2. `novitskyarchive.com` yazın
3. **"DEVAM"** butonuna tıklayın
4. Doğrulama TXT kaydını Google Domains'e ekleyin

---

**✅ Search Console, domain'inizi Google aramalarında görünür yapmak için önemli. Ancak Cloud Run domain mapping için ayrı bir DNS kaydı gerekiyor.**
