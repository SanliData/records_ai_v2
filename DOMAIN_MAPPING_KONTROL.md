# Domain Mapping Kontrol ve Güncelleme
## zyagrolia.com - Eski Yayını Güncelleme

### 📍 Durum
- Domain: `zyagrolia.com`
- Eski bir domain mapping mevcut
- Yeni service: `records-ai-v2`

---

## ADIM 1: Mevcut Mapping'i Kontrol

### Cloud Console'dan:

1. **Cloud Console** → **Cloud Run** → **Domains**
   - URL: https://console.cloud.google.com/run/domains?project=records-ai

2. **`zyagrolia.com`** domain'ini arayın
   - Hangi service'e map edilmiş?
   - Status nedir? (Active/Inactive)

---

## ADIM 2: Eski Mapping'i Güncelleme

### Seçenek A: Mapping'i Güncelle (Önerilen)

1. **Cloud Console** → **Cloud Run** → **Domains**
2. **`zyagrolia.com`** satırında **edit (kalem) ikonuna** tıklayın
3. **Service** dropdown'ından **`records-ai-v2`** seçin
4. **Region:** `europe-west1` seçin
5. **"UPDATE"** veya **"SAVE"** butonuna tıklayın

### Seçenek B: Eski Mapping'i Sil ve Yeni Oluştur

Eğer güncelleme çalışmazsa:

1. **Eski mapping'i sil:**
   - `zyagrolia.com` satırında **delete (çöp kutusu) ikonuna** tıklayın
   - Silme işlemini onaylayın

2. **Yeni mapping oluştur:**
   - **"+ ADD MAPPING"** butonuna tıklayın
   - Domain: `zyagrolia.com`
   - Service: `records-ai-v2`
   - Region: `europe-west1`
   - **"CREATE"** butonuna tıklayın

---

## ADIM 3: DNS Kayıtlarını Kontrol

Eğer mapping başarılı olursa:

1. **DNS kayıtları** otomatik olarak güncellenir (genellikle)
2. Eğer manuel DNS yönetiyorsanız, Cloud Console'dan yeni kayıtları alın
3. Domain sağlayıcınızda DNS kayıtlarını güncelleyin

---

## ADIM 4: Test

Mapping güncellemesi 5-15 dakika sürebilir:

1. **Tarayıcıda test edin:**
   - https://zyagrolia.com
   - https://zyagrolia.com/ui/upload.html

2. **Health check:**
   - https://zyagrolia.com/health

---

## PowerShell Komutları (Alternatif)

Eğer Cloud Console çalışmazsa:

```powershell
# Mevcut mapping'leri listele
gcloud run domain-mappings list --region europe-west1

# Mapping detaylarını görüntüle (eğer beta kuruluysa)
gcloud beta run domain-mappings describe zyagrolia.com --region europe-west1
```

---

## Sorun Giderme

### "Domain already mapped" hatası
**Çözüm:** Önce mevcut mapping'i silin veya güncelleyin

### "Permission denied" hatası
**Çözüm:** Doğru hesap ile login olduğunuzdan emin olun

### DNS kayıtları güncellenmedi
**Çözüm:** Domain sağlayıcınızda manuel olarak DNS kayıtlarını güncelleyin

---

**Son Güncelleme:** 2026-01-18
