# Domain Mapping Region Güncelleme
## zyagrolia.com - us-central1'den europe-west1'e Güncelleme

### 📍 Mevcut Durum
- **Domain:** `zyagrolia.com` 
- **Eski mapping:** `records-ai-v2 (us-central1)`
- **Yeni deployment:** `records-ai-v2 (europe-west1)`
- **Sorun:** Domain hala eski region'daki service'e işaret ediyor

---

## Çözüm 1: Service'i europe-west1'de Kontrol Et

Önce `europe-west1` region'ında service'in çalıştığından emin olalım:

### PowerShell'de:
```powershell
# europe-west1'deki service'i kontrol et
gcloud run services describe records-ai-v2 --region europe-west1
```

---

## Çözüm 2: Domain Mapping'i Güncelleme

### Cloud Console'dan:

1. **Domain mappings sayfasında** `zyagrolia.com` satırını bulun
2. Sağdaki **üç nokta (⋮)** veya **edit ikonuna** tıklayın
3. **"Edit mapping"** veya **"Update"** seçeneğini seçin
4. **Region** veya **Service** dropdown'ından `europe-west1` region'ını seçin
   - VEYA service seçiminde `records-ai-v2` service'inin `europe-west1` versiyonunu seçin
5. **"SAVE"** veya **"UPDATE"** butonuna tıklayın

---

## Çözüm 3: Eski Mapping'i Sil ve Yeniden Oluştur (Alternatif)

Eğer güncelleme çalışmazsa:

### ADIM 1: Eski Mapping'i Sil

1. `zyagrolia.com` satırında **üç nokta (⋮)** menüsüne tıklayın
2. **"Delete"** veya **"Remove"** seçeneğini seçin
3. Silme işlemini onaylayın

### ADIM 2: Yeni Mapping Oluştur

1. **"+ Add mapping"** butonuna tıklayın
2. **Domain:** `zyagrolia.com` yazın
3. **Service:** `records-ai-v2` seçin
4. **Region:** `europe-west1` seçin (önemli!)
5. **"CONTINUE"** veya **"CREATE"** butonuna tıklayın

---

## Önemli Notlar

1. **Region önemli:** Domain mapping, belirli bir region'daki service'e bağlanır
2. **DNS değişmez:** Mapping güncellendiğinde DNS kayıtları genellikle aynı kalır
3. **Yayılma süresi:** Değişikliklerin aktif olması 5-15 dakika sürebilir

---

## Kontrol

Mapping güncellemesi sonrası:

1. **Cloud Console'da:**
   - `zyagrolia.com` yanında yeşil tik görünmeli
   - "Mapped to" kolonunda `records-ai-v2 (europe-west1)` görünmeli

2. **Tarayıcıda test:**
   - https://zyagrolia.com
   - Yeni deployment'ınızın çalıştığını doğrulayın

---

**Son Güncelleme:** 2026-01-18
