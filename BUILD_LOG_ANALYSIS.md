# Build Log Analysis Guide

## Build ID
`9b0bd0c2-b6a5-47d4-93cc-d7998b971249`

## Build Log'unu Görüntüleme

### 1. Cloud Shell'den (Önerilen)

```bash
gcloud builds log 9b0bd0c2-b6a5-47d4-93cc-d7998b971249 \
  --project=records-ai \
  --region=europe-west1
```

### 2. Console'dan

Direkt link:
```
https://console.cloud.google.com/cloud-build/builds/9b0bd0c2-b6a5-47d4-93cc-d7998b971249?project=records-ai&region=europe-west1
```

### 3. Tüm Build'leri Listele

```bash
gcloud builds list \
  --project=records-ai \
  --region=europe-west1 \
  --limit=5
```

## Yaygın Build Hataları ve Çözümleri

### 1. "Dockerfile not found"
**Hata:**
```
unable to evaluate symlinks in Dockerfile path: lstat /workspace/Dockerfile: no such file or directory
```

**Çözüm:**
```bash
# Local'de Dockerfile'ı kontrol et
ls -la | grep -i dockerfile

# Eğer dockerfile (küçük d) varsa
mv dockerfile Dockerfile
```

### 2. "Requirements installation failed"
**Hata:**
```
ERROR: Could not install packages due to an OSError
```

**Çözüm:**
- `requirements.txt` dosyasını kontrol et
- Versiyon conflict'leri düzelt
- `--no-cache-dir` flag'i kullan (zaten Dockerfile'da var)

### 3. "Module not found"
**Hata:**
```
ModuleNotFoundError: No module named 'xxx'
```

**Çözüm:**
- `requirements.txt`'e eksik modülü ekle
- Import path'lerini kontrol et

### 4. "Port binding failed"
**Hata:**
```
The user-provided container failed to start and listen on the port defined provided by the PORT=8080
```

**Çözüm:**
- `dockerfile`'da `ENV PORT=8080` olduğundan emin ol
- Uvicorn'un `--port ${PORT:-8080}` ile başladığından emin ol

## Build Log'unu Analiz Etme

### Önemli Bölümler:

1. **FETCHSOURCE**: Kaynak kodun nereden çekildiğini gösterir
   ```
   From https://github.com/SanliData/records_ai
   HEAD is now at a0c13c2
   ```

2. **BUILD**: Docker build sürecini gösterir
   ```
   Step #0 - "Build"
   Step #1 - "Push"
   ```

3. **ERROR**: Hata mesajı varsa burada görünür

### Log Formatı:

```
-------------------------------------------------------------------------------------------------------------
REMOTE BUILD OUTPUT
-------------------------------------------------------------------------------------------------------------
FETCHSOURCE
...
BUILD
Step #0 - "Build"
...
ERROR
ERROR: build step 0 "..." failed: step exited with non-zero status: 1
```

## Build'i Yeniden Çalıştırma

Eğer build başarısız olursa:

1. Hatayı düzelt (Dockerfile, requirements.txt, vb.)
2. Yeniden deploy et:
   ```bash
   gcloud run deploy records-ai-v2 \
     --source . \
     --platform managed \
     --region europe-west1 \
     --allow-unauthenticated \
     --port 8080 \
     --project records-ai
   ```

## Debug İpuçları

1. **Build'i local'de test et:**
   ```bash
   docker build -t records-ai-test .
   docker run -p 8080:8080 records-ai-test
   ```

2. **Container'ı kontrol et:**
   ```bash
   docker run -it records-ai-test /bin/bash
   ```

3. **Requirements'ı kontrol et:**
   ```bash
   docker run -it records-ai-test pip list
   ```



