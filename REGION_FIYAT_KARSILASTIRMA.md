# Cloud Run Region Fiyat Karşılaştırması
## En Uygun Region Seçimi - 2026

### 📍 Mevcut Durum
- **Şu anki region:** `europe-west1` (Belgium)
- **Service:** `records-ai-v2`

---

## 💰 Cloud Run Fiyatlandırması (2026)

Cloud Run fiyatlandırması **üç ana bileşenden** oluşur:

1. **CPU Time** - İşlem süresi
2. **Memory** - Bellek kullanımı
3. **Requests** - İstek sayısı

### Region Bazlı Fiyat Farkları:

**Önemli:** Cloud Run fiyatlandırması region'a göre **çok az değişir**. Ana farklar:

- **Avrupa bölgeleri:** Genellikle benzer fiyatlar
- **ABD bölgeleri:** Bazen biraz daha ucuz olabilir
- **Asya bölgeleri:** Genellikle benzer veya biraz daha pahalı

---

## 🌍 Önerilen Bölgeler (Fiyat ve Performans)

### 1. **us-central1 (Iowa, USA)** ⭐ ÖNERİLEN
- **Fiyat:** En ucuz bölgelerden biri
- **Performans:** Yüksek
- **Latency (Türkiye):** ~150-200ms
- **Not:** Google'ın en büyük veri merkezlerinden biri

### 2. **europe-west1 (Belgium)** ⚡ ŞU ANKİ
- **Fiyat:** Orta
- **Performans:** Yüksek
- **Latency (Türkiye):** ~50-100ms (daha yakın)
- **Not:** Avrupa'daki kullanıcılar için ideal

### 3. **us-east1 (South Carolina, USA)**
- **Fiyat:** Ucuz
- **Performans:** Yüksek
- **Latency (Türkiye):** ~150-200ms

### 4. **asia-south1 (Mumbai, India)**
- **Fiyat:** Orta
- **Performans:** İyi
- **Latency (Türkiye):** ~100-150ms

---

## 💡 Öneri

### Eğer **maliyet** öncelikliyse:
→ **`us-central1`** (Iowa) - En ucuz seçenek

### Eğer **performans + maliyet** dengesi önemliyse:
→ **`europe-west1`** (Belgium) - Şu anki seçim iyi
   - Türkiye'ye yakın
   - Fiyat/performans dengesi iyi

### Eğer **sadece maliyet** önemliyse ve latency önemli değilse:
→ **`us-central1`** - En uygun fiyat

---

## 📊 Maliyet Karşılaştırması (Yaklaşık)

**Örnek:** 1 milyon request, 100GB memory-hours, 50 vCPU-hours

| Region | Tahmini Aylık Maliyet |
|--------|----------------------|
| us-central1 | ~$15-20 |
| europe-west1 | ~$18-23 |
| us-east1 | ~$15-20 |
| asia-south1 | ~$20-25 |

**Not:** Farklar genellikle %10-20 arasında değişir.

---

## 🔄 Region Değiştirme Adımları

Eğer region değiştirmek isterseniz:

### ADIM 1: Yeni Region'da Deploy Et

```powershell
# us-central1'e deploy et
gcloud run deploy records-ai-v2 `
  --source . `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --port 8080
```

### ADIM 2: Domain Mapping'i Güncelle

Cloud Console'da:
- Domain mappings → `zyagrolia.com` → Edit
- Region: `us-central1` seçin
- Save

---

## 🎯 Sonuç ve Öneri

**Şu anki durum (`europe-west1`):**
- ✅ Türkiye'ye yakın (düşük latency)
- ✅ Fiyat/performans dengesi iyi
- ✅ Avrupa kullanıcıları için ideal

**Eğer maliyet çok önemliyse:**
- `us-central1`'e geçebilirsiniz (%10-15 tasarruf)
- Ancak latency biraz artacak (150-200ms)

**Önerim:** Şu anki `europe-west1` seçimi **iyi bir denge**. Eğer aylık maliyet $5-10 tasarruf etmek kritikse, `us-central1` düşünülebilir.

---

## 📝 Notlar

1. **Cloud Run fiyatlandırması region'a göre çok az değişir** - Ana maliyet kullanım miktarınıza bağlı
2. **Latency önemliyse:** `europe-west1` daha iyi
3. **Maliyet önemliyse:** `us-central1` biraz daha ucuz
4. **Trafik yüksek değilse:** Fiyat farkı çok küçük olacak

---

**Son Güncelleme:** 2026-01-18
