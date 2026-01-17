# Build Hatası Debug Rehberi

## Adım 1: Build Loglarını Kontrol Et

Cloud Shell'de şu komutları çalıştırın:

```bash
# Son build ID'yi al
BUILD_ID=$(gcloud builds list --limit 1 --format="value(id)")
echo "Build ID: $BUILD_ID"

# Build loglarını göster
gcloud builds log $BUILD_ID
```

VEYA direkt Cloud Console'dan:
https://console.cloud.google.com/cloud-build/builds?project=records-ai

## Adım 2: Hata Mesajlarını Filtrele

```bash
# Sadece hataları göster
gcloud builds log $(gcloud builds list --limit 1 --format="value(id)") | grep -i "error\|failed\|exception"
```

## Yaygın Hatalar ve Çözümler

### 1. Import Hatası
**Hata:** `ModuleNotFoundError: No module named 'X'`

**Çözüm:** 
- requirements.txt'te paket eksik
- Veya import path yanlış

### 2. Python Version Hatası
**Hata:** `Python version mismatch`

**Çözüm:**
- Dockerfile'da Python 3.11 kullanıyoruz
- Eğer sorun varsa `runtime.txt` ekleyin

### 3. Tesseract Hatası
**Hata:** `tesseract not found`

**Çözüm:**
- Dockerfile'da tesseract-ocr kuruluyor
- Eğer hala sorun varsa pytesseract'i requirements.txt'ten kaldırın (opsiyonel)

### 4. Syntax Hatası
**Hata:** `SyntaxError`

**Çözüm:**
- Python dosyalarında syntax hatası olabilir
- Local'de test edin: `python -m py_compile backend/main.py`

## Hızlı Düzeltme: Minimal Requirements

Eğer hala sorun varsa, minimal requirements.txt deneyin:

```bash
# Minimal requirements.txt oluştur
cat > requirements_minimal.txt << EOF
fastapi
uvicorn[standard]
pydantic
python-multipart
EOF

# Dockerfile'ı güncelle (requirements_minimal.txt kullan)
# Sonra tekrar deploy et
```

## Build'i Test Et (Local)

Cloud Shell'de Docker varsa:

```bash
# Dockerfile ile build test et
docker build -t test-build .

# Eğer local build çalışırsa, Cloud Run da çalışır
```

## Son Çare: Build Loglarını Paylaş

Build loglarını tam olarak görebilirsek, tam çözümü verebiliriz.

Logları şu şekilde alabilirsiniz:
```bash
gcloud builds log $(gcloud builds list --limit 1 --format="value(id)") > build_log.txt
cat build_log.txt
```



