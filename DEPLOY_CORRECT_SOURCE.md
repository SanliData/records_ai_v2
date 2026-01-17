# Doğru Source ile Deploy

## Sorun
Yanlış repository kullanılıyor. Cloud Build yanlış yerden dosya çekiyor olabilir.

## Çözüm: Local Source Deployment

### Cloud Shell'de Yapılacaklar

#### Adım 1: Dosyaları Cloud Shell'e Yükle

**Yöntem A: Cloud Shell Editor Kullan (Önerilen)**

1. Cloud Shell'de **"Open Editor"** butonuna tıklayın (sağ üstte kalem ikonu)
2. Dosyaları upload edin veya dosya sisteminden kopyalayın

**Yöntem B: Zip Upload**

1. Local'de klasörü zip'leyin (gereksiz dosyaları hariç tutun)
2. Cloud Shell'de Upload butonunu kullanın
3. Zip'i unzip edin

#### Adım 2: Doğru Dizinde Olun

```bash
# Cloud Shell'de
cd records_ai_v2  # veya upload ettiğiniz klasör adı

# Dosyaların olduğunu kontrol edin
ls -la
# backend/, frontend/, requirements.txt, Procfile görünmeli
```

#### Adım 3: Deploy Et

```bash
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080 \
  --project records-ai
```

## Önemli: `--source .` Parametresi

Bu parametre:
- ✅ **MEVCUT DİZİN** (`.`) kullanır
- ✅ GitHub repository'yi **BYPASS** eder
- ✅ **Local dosyaları** direkt kullanır
- ✅ En güncel kodları deploy eder

## Kontrol Listesi

Deploy öncesi kontrol edin:

- [ ] `backend/main.py` dosyası var mı?
- [ ] `requirements.txt` dosyası var mı?
- [ ] `Procfile` dosyası var mı?
- [ ] `frontend/` klasörü var mı?
- [ ] `dockerfile` dosyası var mı? (opsiyonel)

## Hızlı Test

```bash
# Dosya yapısını kontrol
ls -la
ls -la backend/
ls -la frontend/

# Procfile kontrolü
cat Procfile
# Çıktı: web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT

# Deployment
gcloud run deploy records-ai-v2 --source . --platform managed --region europe-west1 --allow-unauthenticated --port 8080
```

## Sonuç

**`--source .` ile deploy ettiğinizde:**
- GitHub repository kullanılmaz
- Local dosyalar direkt deploy edilir
- Repository bağlantısı önemli değil

Bu yöntem %100 güvenilir!



