# Cloud Console'dan Manuel Deploy - Hızlı Rehber

## En Kolay Yöntem: Cloud Run'dan Deploy

### 1. Cloud Run Console'a Git
👉 https://console.cloud.google.com/run?project=records-ai

### 2. Servis Seç veya Oluştur
- Mevcut **records-ai-v2** servisini seç
- Veya **"Create Service"** butonuna tıkla

### 3. Deployment Ayarları

#### Container:
- **Container image URL:** (önce build etmen gerekiyor)
  - Ya Cloud Build ile build et
  - Ya da GitHub'dan direkt deploy seçeneğini kullan

#### GitHub'dan Deploy (ÖNERİLEN):
- **Source:** **"Continuously deploy new revisions from a source repository"** seç
- **Repository:** `SanliData/records_ai_v2` (bağla)
- **Branch:** `main`
- **Build type:** `Dockerfile` veya `Buildpacks`
- **Dockerfile path:** `dockerfile` (veya boş bırak)

#### Container Image'den Deploy:
1. Önce Cloud Build ile build et:
   - https://console.cloud.google.com/cloud-build/builds?project=records-ai
   - "Create Build" > GitHub seç > `cloudbuild.yaml` kullan
2. Build tamamlandıktan sonra image URL'ini kullan:
   ```
   gcr.io/records-ai/records-ai-v2:latest
   ```

### 4. Runtime Ayarları

**Container:**
- **Port:** `8080`
- **Memory:** `1 GiB`
- **CPU:** `1`
- **Timeout:** `300 seconds`
- **Max instances:** `10`
- **Min instances:** `0`

**Connections:**
- **VPC:** (boş bırak)

**Security:**
- **Authentication:** **"Allow unauthenticated invocations"** ✅

**Environment variables:** (gerekirse ekle)
- `UPAP_ENABLE_OCR=false`
- `UPAP_ENABLE_AI=false`

### 5. Deploy
- **"Deploy"** butonuna tıkla
- 5-10 dakika bekle

### 6. Test
Deploy tamamlandıktan sonra servis URL'i gösterilecek:
- Health check: `https://[SERVICE-URL]/health`
- API Docs: `https://[SERVICE-URL]/docs`

---

## Alternatif: Cloud Build ile Tek Seferde

### Adımlar:

1. **Cloud Build Console:**
   👉 https://console.cloud.google.com/cloud-build/builds?project=records-ai

2. **"Create Build"** tıkla

3. **Source seç:**
   - **Repository:** GitHub
   - **Name:** `SanliData/records_ai_v2`
   - **Branch:** `main`
   - **Configuration:** `cloudbuild.yaml` (file) seç

4. **"Run"** tıkla

5. **Build ve deploy otomatik tamamlanır!**

---

## GitHub Trigger Kur (Otomatik Deploy)

Her push'ta otomatik deploy için:

1. **Cloud Build Triggers:**
   👉 https://console.cloud.google.com/cloud-build/triggers?project=records-ai

2. **"Create Trigger"** tıkla

3. **Ayarlar:**
   - **Name:** `auto-deploy-records-ai-v2`
   - **Event:** Push to a branch
   - **Source:** GitHub bağla (`SanliData/records_ai_v2`)
   - **Branch:** `^main$`
   - **Configuration:** `cloudbuild.yaml`
   - **Service account:** Default

4. **"Create"** tıkla

Artık her `main` branch'e push'ta otomatik deploy olacak! 🚀

---

## Özet Komutlar (Terminal'den)

```bash
# Build ve deploy
gcloud builds submit --config cloudbuild.yaml

# Veya direkt Cloud Run'a
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1
```

---

## Sorun Çıkarsa

1. **Build logs:** Cloud Build > Build history > Build detayları
2. **Run logs:** Cloud Run > Service > Logs
3. **Check:** Dockerfile ve requirements.txt doğru mu?
