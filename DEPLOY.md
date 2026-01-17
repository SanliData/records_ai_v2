# Deployment Guide - Records AI V2

## Değişiklikleri Canlıya Alma

### 1. Yerel Test
```powershell
# Virtual environment aktif et
.\.venv\Scripts\Activate.ps1

# Bağımlılıkları güncelle
pip install -r requirements.txt

# Yerel olarak çalıştır
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Sonra tarayıcıda: `http://127.0.0.1:8000/ui/upload.html`

### 2. Production Deployment (Google Cloud Run)

#### A. Docker Image Build
```powershell
# Docker image oluştur
docker build -t gcr.io/YOUR_PROJECT_ID/records-ai-v2:latest .

# Veya tag ile
docker build -t records-ai-v2:latest .
```

#### B. Cloud Run'a Deploy
```powershell
# Google Cloud'a push
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/records-ai-v2:latest

# Cloud Run'a deploy
gcloud run deploy records-ai-v2 \
  --image gcr.io/YOUR_PROJECT_ID/records-ai-v2:latest \
  --platform managed \
  --region YOUR_REGION \
  --allow-unauthenticated
```

#### C. Environment Variables
Cloud Run'da şu environment variable'ları ayarlayın:
- `OPENAI_API_KEY` (NovArchive GPT için)
- `UPAP_ENABLE_OCR=true` (opsiyonel)
- `UPAP_ENABLE_AI=true` (opsiyonel)

### 3. Frontend Dosyalarını Güncelleme

Frontend dosyaları (`frontend/` klasörü) Docker image içinde olduğu için:
- Docker image rebuild edildiğinde otomatik güncellenir
- Veya ayrı bir static hosting kullanılıyorsa oraya da deploy edilmeli

### 4. Değişiklikleri Kontrol Etme

Deployment sonrası:
1. `https://zyagrolia.com/ui/upload.html` - Yeni upload sayfası
2. `https://zyagrolia.com/ui/preview.html` - Preview sayfası
3. `https://zyagrolia.com/ui/library.html` - Library sayfası
4. `https://api.zyagrolia.com/upap/upload/preview` - Preview API endpoint

### 5. Hızlı Deployment Script

```powershell
# deploy.ps1
$PROJECT_ID = "YOUR_PROJECT_ID"
$SERVICE_NAME = "records-ai-v2"
$REGION = "YOUR_REGION"

# Build ve push
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

# Deploy
gcloud run deploy $SERVICE_NAME `
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --set-env-vars "OPENAI_API_KEY=$env:OPENAI_API_KEY"
```

### Notlar

- **Frontend değişiklikleri**: Docker image rebuild edildiğinde otomatik güncellenir
- **Backend değişiklikleri**: Docker image rebuild + Cloud Run deploy gerekir
- **Environment variables**: Cloud Run console'dan veya gcloud CLI ile ayarlanabilir
- **Cache**: Tarayıcı cache'ini temizleyin (Ctrl+Shift+R veya Ctrl+F5)




