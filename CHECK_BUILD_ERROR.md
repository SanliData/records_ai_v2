# Build Hatası Kontrol ve Çözüm

## Cloud Build History Sayfasından

### Adım 1: Son Build'i Açın
1. En üstteki build'e tıklayın (Build ID: `47c9446f`)
   - Mavi link olarak görünecek
   - "Created: 1/5/26, 4:46 PM" olan

### Adım 2: Build Detaylarını Görün
1. Build detay sayfası açılacak
2. **"Build log"** sekmesine tıklayın (varsayılan olarak açık olabilir)
3. Logları scroll edin ve hata mesajlarını bulun

### Adım 3: Hata Mesajını Bulun
Hata mesajları genellikle şu şekillerde görünür:
- `ERROR: ...`
- `failed to build`
- `ModuleNotFoundError`
- `SyntaxError`

## Doğrudan Build Log Linki

En son build loglarına doğrudan gitmek için:

```
https://console.cloud.google.com/cloud-build/builds/47c9446f-5c6d-43f6-bae5-cf8c11069249?project=records-ai
```

VEYA

```
https://console.cloud.google.com/cloud-build/builds?project=records-ai
```
Sonra en üstteki build'e tıklayın.

## Yaygın Hatalar ve Çözümler

### 1. "Python Missing Entrypoint" Hatası
**Çözüm:** Procfile zaten eklendi, tekrar deploy edin

### 2. "ModuleNotFoundError"
**Çözüm:** requirements.txt'te paket eksik olabilir

### 3. "SyntaxError"
**Çözüm:** Python dosyasında syntax hatası var

### 4. "ImportError"
**Çözüm:** Import path yanlış veya dosya eksik

## Hızlı Düzeltme

Eğer hata mesajını paylaşırsanız, tam çözümü verebilirim.

## Yeniden Deploy

Hata düzeltildikten sonra Cloud Shell'de:

```bash
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080
```



