# UPAP Uyumluluk Notları

## Önemli: UPAP İleride Ayrı Bir Uygulama Olacak

UPAP (Upload → Process → Archive → Publish) pipeline'ı ileride bağımsız bir servis olarak çalışacak. Bu nedenle tüm frontend ve backend entegrasyonları UPAP endpoint'lerini doğrudan kullanmalı.

## Mevcut UPAP Uyumluluk Durumu

### ✅ Frontend (UPAP Uyumlu)

1. **upload.html**
   - Endpoint: `/upap/process/process/preview`
   - UPAP Pipeline: Upload → Process (Preview mode, Archive ve Publish öncesi durur)
   - Anonymous access: ✅ Evet
   - UPAP uyumlu: ✅ Evet

2. **results.html**
   - PreviewRecord gösterimi
   - Archive linki: `/upap/archive/add` endpoint'ine yönlendirir
   - UPAP uyumlu: ✅ Evet

3. **archive-save.html**
   - Endpoint: `/upap/archive/add`
   - UPAP Pipeline: Archive stage
   - Authentication: ✅ Gerekli
   - UPAP uyumlu: ✅ Evet

### ✅ Backend (UPAP Pipeline)

1. **UPAP Engine** (`backend/services/upap/engine/upap_engine.py`)
   - Stages: Upload, Process, Archive, Publish
   - Optional stages: OCR, AI (ENV ile kontrol edilir)

2. **UPAP Endpoints**
   - `/upap/upload` - Upload stage (email gerekli)
   - `/upap/process/process/preview` - Upload + Process (anonymous)
   - `/upap/archive/add` - Archive stage (auth gerekli)
   - `/upap/publish` - Publish stage (archive sonrası)

## UPAP Pipeline Sırası (Immutable)

```
1. Upload    → Dosya yükleme
2. Process   → OCR/AI analiz (opsiyonel)
3. Archive   → Arşive kaydetme (auth gerekli)
4. Publish   → Yayınlama (archive sonrası)
```

## Gelecek İçin Notlar

1. **UPAP Ayrı Uygulama Olunca:**
   - Frontend UPAP API'sine direkt bağlanacak
   - Backend UPAP'i dış servis olarak çağıracak
   - Endpoint URL'leri environment variable'lardan gelecek

2. **API Base URL Yapılandırması:**
   - Local: `http://127.0.0.1:8000`
   - Production: `https://api.zyagrolia.com`
   - UPAP Service (gelecekte): Environment variable'dan alınacak

3. **Preview Mode:**
   - Upload → Process sonrası durur
   - Archive ve Publish yapılmaz
   - Kullanıcı preview'dan sonra manuel olarak Archive yapar

## Migration Checklist (UPAP Ayrı App Olunca)

- [ ] UPAP service URL environment variable olarak ekle
- [ ] Frontend'de UPAP base URL'i config'den oku
- [ ] Backend'de UPAP service client wrapper oluştur
- [ ] Test endpoint'lerini UPAP service'e yönlendir
- [ ] Authentication token'ları UPAP service'e ilet



