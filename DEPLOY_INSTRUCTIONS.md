# Deployment Talimatları

## ✅ Docker Image Başarıyla Oluşturuldu!

Docker image hazır: `records-ai-v2:latest`

## 🔐 Google Cloud Authentication

Önce Google Cloud'a giriş yapın:

```powershell
gcloud auth login
```

## 🚀 Deployment Adımları

### 1. Google Container Registry'ye Push

```powershell
# Image'ı tag'le
docker tag records-ai-v2:latest gcr.io/records-ai/records-ai-v2:latest

# Docker'ı Google Cloud'a authenticate et
gcloud auth configure-docker

# Image'ı push et
docker push gcr.io/records-ai/records-ai-v2:latest
```

### 2. Cloud Run'a Deploy

```powershell
gcloud run deploy records-ai-v2 `
  --image gcr.io/records-ai/records-ai-v2:latest `
  --platform managed `
  --region europe-west1 `
  --allow-unauthenticated `
  --port 8080 `
  --set-env-vars "OPENAI_API_KEY=YOUR_OPENAI_API_KEY"
```

**Not:** `YOUR_OPENAI_API_KEY` yerine gerçek API key'inizi yazın.

### 3. Alternatif: Environment Variable'ları Sonra Ayarlama

Eğer API key'i sonra ayarlamak isterseniz:

```powershell
# Önce deploy et
gcloud run deploy records-ai-v2 `
  --image gcr.io/records-ai/records-ai-v2:latest `
  --platform managed `
  --region europe-west1 `
  --allow-unauthenticated `
  --port 8080

# Sonra environment variable ekle
gcloud run services update records-ai-v2 `
  --region europe-west1 `
  --set-env-vars "OPENAI_API_KEY=YOUR_OPENAI_API_KEY"
```

## 📍 Servis URL'ini Öğrenme

Deployment sonrası servis URL'ini öğrenmek için:

```powershell
gcloud run services describe records-ai-v2 --region europe-west1 --format "value(status.url)"
```

## ✅ Kontrol

Deployment sonrası şu sayfaları kontrol edin:

- `https://zyagrolia.com/ui/upload.html` - Yeni upload sayfası
- `https://zyagrolia.com/ui/preview.html` - Preview sayfası  
- `https://zyagrolia.com/ui/library.html` - Library sayfası
- `https://api.zyagrolia.com/health` - Health check

## 🔄 Hızlı Deployment (Tek Komut)

Tüm adımları tek seferde yapmak için:

```powershell
# 1. Tag
docker tag records-ai-v2:latest gcr.io/records-ai/records-ai-v2:latest

# 2. Auth
gcloud auth configure-docker

# 3. Push
docker push gcr.io/records-ai/records-ai-v2:latest

# 4. Deploy
gcloud run deploy records-ai-v2 `
  --image gcr.io/records-ai/records-ai-v2:latest `
  --platform managed `
  --region europe-west1 `
  --allow-unauthenticated `
  --port 8080
```

## ⚠️ Önemli Notlar

1. **Region**: Mevcut servisinizin region'ını kontrol edin:
   ```powershell
   gcloud run services list --platform managed
   ```

2. **Project ID**: Eğer farklı bir project kullanıyorsanız:
   ```powershell
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **API Key**: NovArchive GPT özelliği için `OPENAI_API_KEY` gerekli (opsiyonel)

4. **Cache**: Deployment sonrası tarayıcı cache'ini temizleyin (Ctrl+Shift+R)




