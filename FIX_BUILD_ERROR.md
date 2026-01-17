# Build Hatası Çözümü

Build loglarını kontrol edin ve hatayı bulun.

## Build Loglarını Görüntüleme

Cloud Shell'de şu komutu çalıştırın:

```bash
# Son build logunu göster
gcloud builds list --limit 1 --format="value(id)"

# Log detaylarını göster (ID'yi yukarıdaki komuttan alın)
gcloud builds log [BUILD_ID]
```

VEYA Cloud Console'dan:
https://console.cloud.google.com/cloud-build/builds?project=records-ai

## Yaygın Build Hataları ve Çözümleri

### 1. Requirements.txt Hatası
**Hata:** `ERROR: Could not find a version that satisfies the requirement`

**Çözüm:**
```bash
# requirements.txt'i kontrol edin
cat requirements.txt

# Geçersiz paketleri kaldırın veya düzeltin
```

### 2. Python Version Hatası
**Hata:** `Python version not found`

**Çözüm:**
- Dockerfile'da Python version belirtin
- Veya `runtime.txt` dosyası ekleyin

### 3. Dosya Bulunamadı
**Hata:** `File not found: backend/main.py`

**Çözüm:**
- Dosya yapısını kontrol edin
- `.gcloudignore` dosyası kontrol edin

### 4. Port Hatası
**Hata:** `Port configuration error`

**Çözüm:**
- Dockerfile'da PORT environment variable kullanın
- CMD'de port 8080 olmalı

## Hızlı Düzeltme

### Dockerfile Kontrolü
Dockerfile şöyle olmalı:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
```

### .gcloudignore Kontrolü
`.gcloudignore` dosyası oluşturun:

```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
.env
.venv
venv/
*.db
*.log
.git/
.gitignore
```

## Build'i Yeniden Deneme

Düzeltmelerden sonra tekrar deploy edin:

```bash
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080
```



