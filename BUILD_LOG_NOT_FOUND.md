# Build Log Bulunamadı - Çözüm

## ❌ SORUN:
"Unable to find the resource you requested" hatası

Build ID: `9b0bd0c2-b6a5-47d4-93cc-d7998b971249` bulunamıyor.

## 🔍 Olası Nedenler:

1. **Build silinmiş olabilir** (retention policy)
2. **Farklı region'da build yapılmış** olabilir
3. **Build ID yanlış** olabilir
4. **Permission problemi** olabilir

## ✅ ÇÖZÜM:

### 1. Son Build'leri Bul

Cloud Shell'de çalıştırın:

```bash
# Tüm region'larda build ara
bash FIND_BUILD.sh

# VEYA manuel olarak:
gcloud builds list --project=records-ai --limit=10

# Europe-west1 region için:
gcloud builds list --project=records-ai --region=europe-west1 --limit=10
```

### 2. Build History'yi Kontrol Et

Console'da:
```
https://console.cloud.google.com/cloud-build/builds?project=records-ai
```

### 3. Farklı Region'ları Kontrol Et

Build farklı bir region'da olabilir:
- `europe-west1` (default)
- `us-central1`
- `us-east1`
- `europe-west4`

Her region için kontrol edin.

### 4. Build Status Kontrolü

```bash
# Son 5 build'i göster
gcloud builds list \
  --project=records-ai \
  --limit=5 \
  --format="table(id,status,createTime,region,logUrl)"
```

### 5. Yeni Build Yap

Eğer eski build'i bulamıyorsanız, yeni bir build başlatın:

```bash
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080 \
  --project records-ai
```

## 🎯 Hızlı Kontrol

```bash
# Proje ayarla
gcloud config set project records-ai

# Son build'i bul
gcloud builds list --limit=1 --format="value(id,status,createTime)"

# Build log'unu göster (yukarıdaki ID'yi kullanın)
gcloud builds log <BUILD_ID> --project=records-ai
```

## 📋 Build History Console Linki

Tüm build'leri görmek için:
```
https://console.cloud.google.com/cloud-build/builds?project=records-ai
```

Bu sayfada:
- Tüm build'ler listelenir
- Status (SUCCESS, FAILURE, WORKING) görünür
- Log'lara erişebilirsiniz



