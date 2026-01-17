# Cloud Shell Build Hatası Çözümü

Build loglarını kontrol edin:

## Build Loglarını Görüntüleme

Cloud Shell'de:

```bash
# Son build ID'yi al
gcloud builds list --limit 1 --format="value(id)"

# Logları göster (yukarıdaki ID'yi kullan)
gcloud builds log [BUILD_ID]
```

VEYA Cloud Console:
https://console.cloud.google.com/cloud-build/builds?project=records-ai

## Yapılan Düzeltmeler

### 1. Dockerfile Güncellendi
- `tesseract-ocr` ve `libtesseract-dev` eklendi
- `pytesseract` için gerekli sistem bağımlılıkları kuruluyor

### 2. .gcloudignore Eklendi
- Gereksiz dosyalar build'e dahil edilmiyor
- Build hızlanır ve boyutu küçülür

## Yeniden Deploy

Düzeltmelerden sonra tekrar deploy edin:

```bash
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080
```

## Alternatif: pytesseract Olmadan

Eğer hala sorun varsa, `pytesseract`'i requirements.txt'ten kaldırabilirsiniz:

```bash
# requirements.txt'ten pytesseract satırını kaldırın
# OCR opsiyonel olduğu için sorun olmaz
```

Sonra tekrar deploy edin.

## Hızlı Test

Build'in çalışıp çalışmadığını test etmek için:

```bash
# Local'de test (Cloud Shell'de)
docker build -t test-image .
```

Eğer local build çalışırsa, Cloud Run deployment da çalışır.



