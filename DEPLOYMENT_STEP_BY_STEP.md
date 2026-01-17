# Değişiklikleri Uygulama Rehberi
Adım Adım Deployment Kılavuzu

## 📋 Özet

Bu rehber, yapılan tüm frontend ve backend değişikliklerini Google Cloud Run'a deploy etmek için gerekli adımları içerir.

## 🔍 Yapılan Değişiklikler

### Frontend (Yeni/Güncellenmiş Sayfalar)
- ✅ `frontend/index.html` - Yeni ana sayfa
- ✅ `frontend/upload.html` - Güncellenmiş (anonymous upload)
- ✅ `frontend/results.html` - Yeni results sayfası
- ✅ `frontend/archive-save.html` - Yeni archive save sayfası
- ✅ `frontend/login.html` - Güncellenmiş navigation

### Backend
- ✅ `backend/main.py` - Root redirect güncellendi

### Dokümantasyon
- ✅ `UPAP_COMPATIBILITY_NOTES.md`
- ✅ `GITHUB_SYNC_NOTES.md`
- ✅ `DEPLOYMENT_STATUS.md`
- ✅ `tree.txt`
- ✅ `live_book/records_ai_live_book_current.txt`

## 🚀 Deployment Adımları

### ADIM 1: Hazırlık Kontrolü

PowerShell'de şu komutları çalıştırın:

```powershell
# 1. Proje dizinine gidin (zaten orada olmalısınız)
cd C:\Users\issan\records_ai_v2

# 2. Google Cloud CLI kurulu mu kontrol edin
gcloud --version

# 3. Authenticate olun (eğer değilseniz)
gcloud auth login

# 4. Projeyi ayarlayın
gcloud config set project records-ai
```

### ADIM 2: Deployment Script'i Çalıştırma

#### Seçenek A: Otomatik Script (Önerilen)

```powershell
# Script'i çalıştırın
.\deploy_to_cloud_run.ps1
```

Script size adım adım rehberlik edecek ve onay isteyecek.

#### Seçenek B: Manuel Deployment

Eğer script çalışmazsa, komutları tek tek çalıştırın:

```powershell
# 1. Authenticate (gerekirse)
gcloud auth login

# 2. Projeyi seçin
gcloud config set project records-ai

# 3. Gerekli API'leri aktif edin (ilk seferde gerekli olabilir)
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# 4. Deploy edin
gcloud run deploy records-ai-v2 `
  --source . `
  --platform managed `
  --region europe-west1 `
  --allow-unauthenticated `
  --port 8080
```

### ADIM 3: Deployment İzleme

Deployment başladıktan sonra:

1. **Build süreci** (5-10 dakika sürebilir):
   - Docker image build edilir
   - Dependencies yüklenir
   - Cloud Run'a deploy edilir

2. **Progress** görebilirsiniz:
   ```
   Building Container...
   Uploading sources...
   Creating Revision...
   Routing traffic...
   ```

3. **Tamamlandığında** service URL alırsınız:
   ```
   Service URL: https://records-ai-v2-[hash].europe-west1.run.app
   ```

### ADIM 4: Doğrulama

Deployment tamamlandıktan sonra test edin:

```powershell
# 1. Service URL'ini alın
$serviceUrl = gcloud run services describe records-ai-v2 --region europe-west1 --format "value(status.url)"
Write-Host "Service URL: $serviceUrl"

# 2. Health check
Invoke-WebRequest -Uri "$serviceUrl/health" -UseBasicParsing

# 3. Tarayıcıda test edin
Write-Host "Test URL'leri:"
Write-Host "  Ana Sayfa: $serviceUrl/ui/index.html"
Write-Host "  Upload: $serviceUrl/ui/upload.html"
```

### ADIM 5: Browser Cache Temizleme

**ÖNEMLİ:** Yeni değişiklikleri görmek için cache temizleyin!

#### Chrome/Edge:
1. `Ctrl + Shift + Delete` (veya `Cmd + Shift + Delete` Mac'te)
2. "Cached images and files" seçin
3. "Clear data" tıklayın

#### VEYA Hard Refresh:
- **Windows:** `Ctrl + Shift + R` veya `Ctrl + F5`
- **Mac:** `Cmd + Shift + R`

#### VEYA Gizli Pencere:
- Yeni gizli/incognito pencere açın ve test edin

### ADIM 6: Test Checklist

Deployment sonrası şunları test edin:

- [ ] **Ana Sayfa:** `https://[SERVICE_URL]/ui/index.html`
  - UPAP pipeline açıklaması görünüyor mu?
  - Navigation çalışıyor mu?
  
- [ ] **Upload Sayfası:** `https://[SERVICE_URL]/ui/upload.html`
  - Email alanı YOK mu? ✅
  - "Upload & Analyze" butonu var mı? ✅
  - "No account required" mesajı görünüyor mu? ✅

- [ ] **Upload Test:**
  - Resim yükleyebiliyor musunuz?
  - Analysis sonuçları geliyor mu?
  - Results sayfasına yönlendiriliyor mu?

- [ ] **Login Sayfası:** `https://[SERVICE_URL]/ui/login.html`
  - Navigation header var mı?
  - Footer var mı?

- [ ] **API Health:** `https://[SERVICE_URL]/health`
  - Status "ok" dönüyor mu?

## 🔧 Sorun Giderme

### Problem: "gcloud: command not found"
**Çözüm:** Google Cloud CLI kurun
- İndir: https://cloud.google.com/sdk/docs/install
- Kurulum sonrası PowerShell'i yeniden başlatın

### Problem: "Authentication required"
**Çözüm:**
```powershell
gcloud auth login
gcloud config set project records-ai
```

### Problem: "Permission denied"
**Çözüm:**
- Cloud Console'dan IAM izinlerinizi kontrol edin
- `Cloud Run Admin` rolüne ihtiyacınız var

### Problem: "Build failed"
**Çözüm:**
```powershell
# Logları kontrol edin
gcloud run logs read records-ai-v2 --region europe-west1 --limit 50

# Dockerfile'ı kontrol edin
cat dockerfile
```

### Problem: "Service URL çalışmıyor"
**Çözüm:**
```powershell
# Service durumunu kontrol edin
gcloud run services describe records-ai-v2 --region europe-west1

# Logları inceleyin
gcloud run logs read records-ai-v2 --region europe-west1
```

### Problem: "Eski sayfa görünüyor"
**Çözüm:**
1. Browser cache temizleyin (Adım 5)
2. Hard refresh yapın (`Ctrl+Shift+R`)
3. Gizli pencerede test edin
4. Farklı browser deneyin

## 📊 Deployment Sonrası Kontroller

### Cloud Console'da Kontrol

1. **Cloud Run Servisleri:**
   https://console.cloud.google.com/run?project=records-ai

2. **Deployment Geçmişi:**
   - Service'e tıklayın
   - "Revisions" sekmesinden geçmişi görün

3. **Loglar:**
   - "Logs" sekmesinden canlı logları izleyin

### Komut Satırından Kontrol

```powershell
# Service bilgisi
gcloud run services describe records-ai-v2 --region europe-west1

# Son loglar
gcloud run logs read records-ai-v2 --region europe-west1 --limit 20

# Revisions
gcloud run revisions list --service records-ai-v2 --region europe-west1
```

## ✅ Başarı Kriterleri

Deployment başarılı sayılır eğer:

1. ✅ Service URL erişilebilir
2. ✅ `/health` endpoint 200 dönüyor
3. ✅ `/ui/index.html` yeni tasarımı gösteriyor
4. ✅ `/ui/upload.html` email alanı YOK
5. ✅ Upload işlemi çalışıyor
6. ✅ Browser cache temizlendi

## 📝 Notlar

- **İlk deployment:** 10-15 dakika sürebilir (image build)
- **Sonraki deployment'lar:** 3-5 dakika (sadece değişiklikler)
- **Downtime:** Yok (zero-downtime deployment)
- **Rollback:** Gerekirse önceki revision'a dönebilirsiniz

## 🆘 Yardım

Sorun yaşarsanız:

1. `DEPLOYMENT_COMMANDS.md` dosyasına bakın
2. Cloud Run loglarını kontrol edin
3. `gcloud` komutlarına `--verbosity=debug` ekleyin

---

**Son Güncelleme:** 2026-01-05



