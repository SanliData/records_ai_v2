# Cloud Console'dan Manuel Deploy Rehberi

## Yöntem 1: Cloud Build ile Deploy (Önerilen)

### Adımlar:

1. **Cloud Console'a gidin:**
   - https://console.cloud.google.com/cloud-build/builds?project=records-ai

2. **"Create Build" butonuna tıklayın**

3. **Build konfigürasyonunu seçin:**
   - **Source:** GitHub repository seçin
     - Repository: `SanliData/records_ai_v2`
     - Branch: `main`
   - **Configuration:** `cloudbuild.yaml` (Repository'de mevcut)

4. **"Run" butonuna tıklayın**

5. **Build başlar ve otomatik olarak Cloud Run'a deploy eder**

---

## Yöntem 2: Cloud Run'dan Direkt Deploy

### Adımlar:

1. **Cloud Run Console'a gidin:**
   - https://console.cloud.google.com/run?project=records-ai

2. **"records-ai-v2" servisini seçin** (veya "Create Service")

3. **"Edit & Deploy New Revision" tıklayın**

4. **Container image URL:**
   - Önce Cloud Build ile image build edin:
     ```
     gcr.io/records-ai/records-ai-v2:latest
     ```

5. **Ayarlar:**
   - **Memory:** 1Gi
   - **CPU:** 1
   - **Min instances:** 0
   - **Max instances:** 10
   - **Timeout:** 300
   - **Port:** 8080
   - **Authentication:** Allow unauthenticated

6. **"Deploy" butonuna tıklayın**

---

## Yöntem 3: GitHub'dan Otomatik Deploy (Trigger)

### Cloud Build Trigger Kurulumu:

1. **Cloud Build Triggers sayfasına gidin:**
   - https://console.cloud.google.com/cloud-build/triggers?project=records-ai

2. **"Create Trigger" tıklayın**

3. **Ayarlar:**
   - **Name:** `deploy-records-ai-v2`
   - **Event:** Push to a branch
   - **Source:** GitHub repository bağlayın (`SanliData/records_ai_v2`)
   - **Branch:** `^main$`
   - **Configuration:** `cloudbuild.yaml`
   - **Location:** `us-central1`

4. **"Create" butonuna tıklayın**

5. **Artık her GitHub push'unda otomatik deploy olacak**

---

## Yöntem 4: gcloud CLI ile (Terminal)

```bash
# Build ve deploy
gcloud builds submit --config cloudbuild.yaml

# Veya direkt deploy
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --clear-base-image
```

---

## Kontrol

Deploy sonrası servis URL'i:
```
https://records-ai-v2-XXXXX.us-central1.run.app
```

Test endpoint'leri:
- Health: `https://records-ai-v2-XXXXX.us-central1.run.app/health`
- Docs: `https://records-ai-v2-XXXXX.us-central1.run.app/docs`

---

## Sorun Giderme

### Build hatası varsa:
1. Cloud Build logs'u kontrol edin
2. Dockerfile'ı kontrol edin
3. `requirements.txt` eksik paket var mı kontrol edin

### Deploy hatası varsa:
1. Cloud Run logs'u kontrol edin
2. Environment variables eksik olabilir
3. Port ayarlarını kontrol edin
