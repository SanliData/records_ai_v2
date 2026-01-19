# Deploy - Logging Middleware Kaldırıldı

## 1. Git Commit & Push (Windows PowerShell)

```powershell
# Değişiklikleri ekle
git add backend/main.py

# Commit
git commit -m "fix: remove LoggingMiddleware import and usage"

# Push
git push origin main
```

## 2. Cloud Shell'de Deploy

Cloud Shell'de çalıştır:

```bash
cd ~/records_ai_v2
git pull origin main

gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --project records-ai
```

## Beklenen Sonuç

- Container başlar (LoggingMiddleware hatası olmaz)
- Port 8080 dinlenir
- `/health` endpoint çalışır
- Root URL (`/`) upload UI gösterir
