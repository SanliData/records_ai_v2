# Cloud Run Deployment Configuration

## ✅ Otomatik Ayarlar (Script ile)

Deployment script'leri şu ayarları otomatik yapar:
- **Port:** 8082
- **Min Instances:** 0
- **Max Instances:** 10
- **Memory:** 1Gi
- **CPU:** 1
- **Timeout:** 300s
- **Max Requests per Container:** 200
- **Allow Unauthenticated:** ✅

## 📋 Manuel Deploy İçin Ayarlar

Cloud Console'dan manuel deploy yaparken şu ayarları kullanın:

### Container Configuration
- **Port:** `8082`
- **Container image URL:** `gcr.io/records-ai/records-ai-v2:latest` (Cloud Build otomatik günceller)

### Environment Variables
Aşağıdaki environment variables'ı ekleyin:

| Variable | Value | Açıklama |
|----------|-------|----------|
| `PORT` | `8082` | Container port |
| `ENVIRONMENT` | `production` | Environment type |
| `UPAP_ENABLE_OCR` | `false` | OCR stage'i devre dışı |
| `UPAP_ENABLE_AI` | `false` | AI stage'i devre dışı |

### Resources
- **Memory:** `1 GiB`
- **CPU:** `1 CPU`

### Requests
- **Maximum requests per container:** `200`
- **Minimum number of container instances:** `0` ⚠️ **ÖNEMLİ: 10 değil, 0 olmalı!**
- **Maximum number of container instances:** `10`

### Autoscaling
- **Minimum number of instances:** `0`
- **Maximum number of instances:** `10`
- **Scale to 0 CPU based:** ✅ İşaretli

### Security
- **Allow unauthenticated invocations:** ✅ **MUTLAKA İŞARETLİ OLMALI**

## 🚀 Deploy Komutu (gcloud CLI)

```bash
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8082 \
  --max-instances 10 \
  --min-instances 0 \
  --timeout 300 \
  --memory 1Gi \
  --cpu 1 \
  --set-env-vars PORT=8082,ENVIRONMENT=production,UPAP_ENABLE_OCR=false,UPAP_ENABLE_AI=false \
  --max-requests-per-container 200 \
  --project records-ai
```

## ⚠️ Önemli Notlar

1. **Minimum Instances:** Mutlaka `0` olmalı. `10` yaparsanız sürekli 10 container çalışır ve maliyet çok yüksek olur.

2. **Port:** `8082` olarak ayarlayın. Dockerfile artık `$PORT` environment variable'ını kullanıyor.

3. **Security:** "Allow unauthenticated invocations" mutlaka işaretli olmalı, yoksa 403 hatası alırsınız.

4. **Container Image:** Cloud Build trigger otomatik olarak yeni image'lar oluşturur. Manuel deploy yaparsanız eski image kullanılabilir.

## 🔍 Kontrol Listesi

Deploy öncesi kontrol edin:
- [ ] Port: 8082
- [ ] Min Instances: 0
- [ ] Max Instances: 10
- [ ] Allow Unauthenticated: ✅
- [ ] Environment Variables: PORT, ENVIRONMENT, UPAP_ENABLE_OCR, UPAP_ENABLE_AI
- [ ] Memory: 1Gi
- [ ] CPU: 1
- [ ] Timeout: 300s
