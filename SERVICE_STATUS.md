# Records AI V2 - Service Status

## Mevcut Durum (5 Ocak 2026)

### ✅ ÇALIŞIYOR: europe-west1 Region

**Service URL:**
```
https://records-ai-v2-969278596906.europe-west1.run.app
```

**Durum:**
- ✅ Uvicorn başarıyla çalışıyor (port 8080)
- ✅ Health check başarılı
- ✅ Service aktif ve trafik alıyor
- ⚠️ Tek bir /health 403 hatası görüldü (25 Aralık - geçici olabilir)

**Son Deployment:**
- 5 Ocak 2026, 16:45 (CST)
- Region: europe-west1
- Status: Active

### ❌ BAŞARISIZ: us-central1 Region

**Hata:**
```
The user-provided container failed to start and listen on the port 
defined provided by the PORT=8080 environment variable within the 
allocated timeout.
```

**Not:** Bu muhtemelen eski bir deployment denemesi. europe-west1'de servis çalışıyor.

## Test Sayfaları

### Ana Sayfa
```
https://records-ai-v2-969278596906.europe-west1.run.app/ui/index.html
```

### Upload
```
https://records-ai-v2-969278596906.europe-west1.run.app/ui/upload.html
```

### Health Check
```
https://records-ai-v2-969278596906.europe-west1.run.app/health
```

### Login
```
https://records-ai-v2-969278596906.europe-west1.run.app/ui/login.html
```

## Önemli Notlar

1. **Region:** europe-west1 kullanılıyor (QUICK_DEPLOY.ps1'de ayarlı)
2. **Port:** 8080 (doğru yapılandırılmış)
3. **Health Endpoint:** `/health` public (auth gerektirmiyor)
4. **403 Hatası:** Tek bir 403 görüldü, muhtemelen geçici

## Cloud Console Linkleri

### Service Details (europe-west1)
```
https://console.cloud.google.com/run/detail/europe-west1/records-ai-v2?project=records-ai
```

### Logs
```
https://console.cloud.google.com/run/detail/europe-west1/records-ai-v2/observability/logs?project=records-ai
```

### Metrics
```
https://console.cloud.google.com/run/detail/europe-west1/records-ai-v2/observability/metrics?project=records-ai
```

## Yeni Deployment Yapmak İçin

Local PowerShell'den:
```powershell
.\QUICK_DEPLOY.ps1
```

VEYA Cloud Shell'den:
```bash
cd records_ai_v2
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080
```



