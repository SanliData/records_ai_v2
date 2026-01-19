# USA Region Deployment - us-central1
## Kayıtlar USA'den Yüklenecek - En Uygun Region

### 📍 Yeni Region Seçimi
- **Önerilen:** `us-central1` (Iowa, USA)
- **Neden:** 
  - ✅ USA içinde en ucuz region (Tier 1)
  - ✅ USA'den yükleme için ideal latency
  - ✅ Google'ın en büyük veri merkezlerinden biri
  - ✅ Yüksek performans

---

## ADIM ADIM: us-central1'e Deployment

### ADIM 1: Yeni Region'da Deploy Et

**PowerShell'de:**

```powershell
cd C:\Users\issan\records_ai_v2

# us-central1'e deploy et
gcloud run deploy records-ai-v2 `
  --source . `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --port 8080
```

**Bu işlem 5-10 dakika sürebilir.**

---

### ADIM 2: Domain Mapping'i Güncelle

**Cloud Console'dan:**

1. **Cloud Console** → **Cloud Run** → **Domain mappings**
   - https://console.cloud.google.com/run/domains?project=records-ai

2. **`zyagrolia.com`** satırında **üç nokta (⋮)** menüsüne tıklayın

3. **"Edit"** veya **"Update"** seçeneğini seçin

4. **Region:** `us-central1` seçin (şu an `us-central1` zaten seçili olabilir ama kontrol edin)

5. **"SAVE"** veya **"UPDATE"** butonuna tıklayın

**VEYA** Eğer mapping yoksa veya güncellenmiyorsa:

1. **"+ Add mapping"** butonuna tıklayın
2. **Domain:** `zyagrolia.com`
3. **Service:** `records-ai-v2`
4. **Region:** `us-central1` seçin (önemli!)
5. **"CREATE"** butonuna tıklayın

---

### ADIM 3: DNS Kayıtları (Gerekirse)

Eğer domain mapping yeni oluşturulduysa:

1. Cloud Console size **DNS kayıtlarını** gösterecek
2. Domain sağlayıcınızda (Google Domains, vb.) bu kayıtları ekleyin/güncelleyin

**Not:** Eğer mapping sadece güncellendi ise, DNS kayıtları genellikle aynı kalır.

---

### ADIM 4: Test

Deployment tamamlandıktan sonra:

1. **Service URL:**
   ```
   https://records-ai-v2-[hash].us-central1.run.app
   ```

2. **Domain URL:**
   ```
   https://zyagrolia.com
   https://zyagrolia.com/ui/upload.html
   ```

3. **Health Check:**
   ```
   https://zyagrolia.com/health
   ```

---

## Maliyet Karşılaştırması

### us-central1 (Iowa) Avantajları:
- ✅ **En ucuz USA region'u** (Tier 1)
- ✅ USA kullanıcıları için **düşük latency** (~20-50ms)
- ✅ Google'ın **en büyük veri merkezi** - yüksek kapasite
- ✅ **Trafik maliyeti düşük** (USA içi)

### Fiyat Farkı:
- `us-central1`: ~$0.08287 / saat (instance)
- `europe-west1`: ~$0.09-0.10 / saat
- **Tasarruf:** %10-20 (trafiğe bağlı)

---

## Eski Region'ı Temizleme (Opsiyonel)

Eğer `europe-west1`'deki eski service'i silmek isterseniz:

```powershell
# DİKKAT: Bu komut service'i siler!
gcloud run services delete records-ai-v2 --region europe-west1
```

**Önce yeni service'in çalıştığından emin olun!**

---

## Özet

1. ✅ `us-central1` region'u seçildi (USA için ideal)
2. 🔄 Deployment yapılacak
3. 🔄 Domain mapping güncellenecek
4. ✅ USA'den yükleme için optimize edildi

---

**Son Güncelleme:** 2026-01-18
