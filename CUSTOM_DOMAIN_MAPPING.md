# Custom Domain Mapping - zyagrolia.com
## Cloud Run Service'ine Domain Bağlama Rehberi

### 📍 Mevcut Durum
- **Service:** `records-ai-v2`
- **Mevcut URL:** `https://records-ai-v2-969278596906.europe-west1.run.app`
- **Hedef Domain:** `zyagrolia.com`
- **API Domain:** `api.zyagrolia.com` (opsiyonel)

---

## ADIM ADIM DOMAIN MAPPING

### ADIM 1: Cloud Run Service'i Kontrol Et

Service'in çalıştığını doğrulayın:
```powershell
gcloud run services describe records-ai-v2 --region europe-west1
```

---

### ADIM 2: Domain Mapping Oluştur

**Cloud Console'dan (Kolay Yöntem):**

1. **Google Cloud Console** → **Cloud Run** (https://console.cloud.google.com/run)
2. **`records-ai-v2`** service'ine tıklayın
3. Üstte **"MANAGE CUSTOM DOMAINS"** veya **"MAPPINGS"** sekmesine gidin
4. **"ADD MAPPING"** veya **"MAP NEW DOMAIN"** butonuna tıklayın
5. Domain'i girin: `zyagrolia.com`
6. **"CONTINUE"** butonuna tıklayın

**VEYA PowerShell'den:**

```powershell
# Domain mapping oluştur (beta komutu gerekli)
gcloud beta run domain-mappings create `
  --service records-ai-v2 `
  --domain zyagrolia.com `
  --region europe-west1
```

---

### ADIM 3: Domain Doğrulama

Cloud Console domain'i doğrulamaya çalışacak:

1. **Domain sahipliğini doğrula** - Google Workspace veya DNS kayıtları ile
2. Eğer doğrulama başarısız olursa, **manuel DNS kayıtları** gerekebilir

---

### ADIM 4: DNS Kayıtları Ekleme

Cloud Console size DNS kayıtlarını gösterecek. Domain sağlayıcınızda (Google Domains, GoDaddy, vb.) şu kayıtları ekleyin:

#### A Record (IPv4):
```
Type: A
Name: @ (veya zyagrolia.com)
Value: [Cloud Run tarafından verilen IP adresi]
TTL: 3600
```

#### CNAME Record (Eğer gerekirse):
```
Type: CNAME
Name: @ (veya zyagrolia.com)
Value: [Cloud Run tarafından verilen CNAME]
TTL: 3600
```

**VEYA** (Önerilen - Cloud Run'un yeni yöntemi):

Google Cloud'un size verdiği **tam DNS kayıtlarını** kullanın. Genellikle şöyle görünür:

```
Type: A
Name: @
Value: [IPv4 adresi - örnek: 216.239.32.21]
TTL: 3600

Type: AAAA
Name: @  
Value: [IPv6 adresi]
TTL: 3600
```

---

### ADIM 5: DNS Değişikliklerinin Yayılmasını Bekleyin

DNS kayıtlarının yayılması **5 dakika - 48 saat** sürebilir (genellikle 1-2 saat).

Kontrol etmek için:
```powershell
nslookup zyagrolia.com
```

---

### ADIM 6: SSL Sertifikası (Otomatik)

Cloud Run **otomatik olarak SSL sertifikası** sağlar. Google, Let's Encrypt üzerinden ücretsiz SSL verir.

SSL aktif olması **15-60 dakika** sürebilir.

---

### ADIM 7: Test Etme

DNS yayıldıktan sonra:

1. **Ana domain:** https://zyagrolia.com
2. **Upload sayfası:** https://zyagrolia.com/ui/upload.html
3. **Health check:** https://zyagrolia.com/health

---

## API Subdomain (Opsiyonel)

Eğer `api.zyagrolia.com` kullanmak isterseniz:

### ADIM 1: Subdomain Mapping

```powershell
gcloud beta run domain-mappings create `
  --service records-ai-v2 `
  --domain api.zyagrolia.com `
  --region europe-west1
```

### ADIM 2: DNS CNAME Kaydı

Domain sağlayıcınızda:
```
Type: CNAME
Name: api
Value: [Cloud Run tarafından verilen CNAME]
TTL: 3600
```

---

## Troubleshooting

### Problem: "Domain verification failed"
**Çözüm:** 
- DNS kayıtlarının doğru eklendiğinden emin olun
- 24 saat bekleyin ve tekrar deneyin

### Problem: "SSL certificate pending"
**Çözüm:**
- 1-2 saat bekleyin (Let's Encrypt işlemi)
- DNS'in tamamen yayıldığından emin olun

### Problem: "404 Not Found"
**Çözüm:**
- Domain mapping'in tamamlandığından emin olun
- Service'in çalıştığını kontrol edin:
  ```powershell
  gcloud run services describe records-ai-v2 --region europe-west1
  ```

---

## PowerShell Komutları (Özet)

```powershell
# 1. Service bilgisi
gcloud run services describe records-ai-v2 --region europe-west1

# 2. Domain mapping oluştur (beta komutu)
gcloud beta run domain-mappings create `
  --service records-ai-v2 `
  --domain zyagrolia.com `
  --region europe-west1

# 3. Domain mapping listesi
gcloud beta run domain-mappings list --region europe-west1

# 4. Domain mapping detayları
gcloud beta run domain-mappings describe zyagrolia.com --region europe-west1
```

---

## Önemli Notlar

1. **DNS yayılması zaman alır** - Sabırlı olun
2. **SSL otomatiktir** - Ekstra işlem gerekmez
3. **HTTPS zorunludur** - Cloud Run otomatik olarak HTTPS yönlendirir
4. **Domain sahipliği** - Domain'in sizin adınıza kayıtlı olduğundan emin olun

---

**Son Güncelleme:** 2026-01-18
