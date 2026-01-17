# 🚀 Hemen Deploy Et - Adım Adım

## ⚡ Hızlı Komut (Tek Satır)

PowerShell'de şu komutu çalıştırın:

```powershell
gcloud auth login; gcloud config set project records-ai; gcloud run deploy records-ai-v2 --source . --platform managed --region europe-west1 --allow-unauthenticated --port 8080
```

## 📝 Detaylı Adımlar

### ADIM 1: Authentication (2 dakika)

PowerShell'de çalıştırın:
```powershell
gcloud auth login
```

- Tarayıcı otomatik açılacak
- Google hesabınızla giriş yapın (ednovitsky@novitskyarchive.com)
- İzinleri onaylayın

### ADIM 2: Projeyi Ayarlayın (5 saniye)

```powershell
gcloud config set project records-ai
```

### ADIM 3: Deploy Edin (5-10 dakika)

```powershell
gcloud run deploy records-ai-v2 `
  --source . `
  --platform managed `
  --region europe-west1 `
  --allow-unauthenticated `
  --port 8080
```

Bu komut:
- Docker image build eder
- Cloud Run'a deploy eder
- Service URL'i gösterir

### ADIM 4: Sonuçları Kontrol Edin

Deployment tamamlandığında şöyle bir çıktı göreceksiniz:

```
Service URL: https://records-ai-v2-xxxxx.europe-west1.run.app
```

## ✅ Deployment Sonrası

1. **Browser cache temizle:** `Ctrl + Shift + R`
2. **Test et:**
   - Ana Sayfa: `https://[SERVICE_URL]/ui/index.html`
   - Upload: `https://[SERVICE_URL]/ui/upload.html`

## 🔄 Alternatif: Script Kullan

Eğer authentication yaptıysanız:

```powershell
.\QUICK_DEPLOY.ps1
```

## ❓ Sorun mu var?

### "Permission denied" hatası
→ IAM sayfasından rol ekleyin:
https://console.cloud.google.com/iam-admin/iam?project=records-ai

Gerekli roller:
- Cloud Run Admin
- Cloud Build Editor

### "Authentication failed"
→ `gcloud auth login` tekrar çalıştırın

### "Project not found"
→ `gcloud config set project records-ai`

---

**Özet:** Sadece `gcloud auth login` yapın, sonra deployment komutunu çalıştırın!



