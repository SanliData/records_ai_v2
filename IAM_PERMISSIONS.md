# Google Cloud IAM İzinleri ve Rolleri
Cloud Run Deployment için Gerekli İzinler

## 🔐 Gerekli IAM Rolleri

Cloud Run'a deploy edebilmek için aşağıdaki rollerden en az birine sahip olmanız gerekir:

### Minimum Gerekli Rol
- **Cloud Run Admin** (`roles/run.admin`)
  - Servis oluşturma, güncelleme ve silme
  - Revision yönetimi
  - Traffic yönetimi

### Önerilen Roller (Geliştirme için)
- **Cloud Run Admin** (`roles/run.admin`)
- **Service Account User** (`roles/iam.serviceAccountUser`)
- **Cloud Build Editor** (`roles/cloudbuild.builds.editor`)
- **Storage Admin** (`roles/storage.admin`) - Container Registry için

### Owner/Editor Rolü (Tüm İzinler)
- **Owner** (`roles/owner`) veya **Editor** (`roles/editor`)
  - Tüm işlemleri yapabilir
  - En geniş kapsamlı izinler

## 📋 IAM Kontrol Listesi

### 1. IAM Sayfasında Kontrol

Google Cloud Console'da IAM sayfasına gidin:
https://console.cloud.google.com/iam-admin/iam?project=records-ai

**Kontrol edin:**
- [ ] Email adresinizin listelendiğini görün
- [ ] En azından **Cloud Run Admin** rolünüz olduğunu kontrol edin
- [ ] Veya **Owner/Editor** rolünüz olduğunu kontrol edin

### 2. Komut Satırından Kontrol

```powershell
# Mevcut kullanıcının rollerini kontrol et
gcloud projects get-iam-policy records-ai `
  --flatten="bindings[].members" `
  --format="table(bindings.role)" `
  --filter="bindings.members:YOUR_EMAIL@example.com"
```

### 3. Cloud Run Servis İzinlerini Kontrol

```powershell
# Cloud Run servis IAM policy'sini kontrol et
gcloud run services get-iam-policy records-ai-v2 `
  --region europe-west1
```

## 🚀 İzin Ekleme (Owner/Admin Gerekli)

Eğer izinleriniz yoksa, proje Owner'ı şu komutu çalıştırabilir:

```powershell
# Cloud Run Admin rolü ekle
gcloud projects add-iam-policy-binding records-ai `
  --member="user:YOUR_EMAIL@example.com" `
  --role="roles/run.admin"

# Service Account User rolü ekle
gcloud projects add-iam-policy-binding records-ai `
  --member="user:YOUR_EMAIL@example.com" `
  --role="roles/iam.serviceAccountUser"

# Cloud Build Editor rolü ekle (source deployment için)
gcloud projects add-iam-policy-binding records-ai `
  --member="user:YOUR_EMAIL@example.com" `
  --role="roles/cloudbuild.builds.editor"

# Storage Admin rolü ekle (Container Registry için)
gcloud projects add-iam-policy-binding records-ai `
  --member="user:YOUR_EMAIL@example.com" `
  --role="roles/storage.admin"
```

## 🔍 İzin Sorunları ve Çözümleri

### Problem: "Permission denied on service"
**Hata:** `Permission denied on service or resource`

**Çözüm:**
1. IAM sayfasında rollerinizi kontrol edin
2. Cloud Run Admin rolü ekleyin (yukarıdaki komutlar)
3. Birkaç dakika bekleyin (izinlerin yayılması için)

### Problem: "IAM permission denied"
**Hata:** `User does not have permission to access project`

**Çözüm:**
```powershell
# Mevcut kullanıcıyı kontrol et
gcloud auth list

# Farklı bir hesap ile login ol
gcloud auth login

# Projeyi seç
gcloud config set project records-ai
```

### Problem: "Service account permission"
**Hata:** `Permission denied: service account`

**Çözüm:**
```powershell
# Service Account User rolü ekleyin (yukarıdaki komutlar)
# Veya default service account'u kullanın
```

## 📊 Rol Detayları

### Cloud Run Admin (`roles/run.admin`)
**İzinler:**
- `run.services.create`
- `run.services.update`
- `run.services.delete`
- `run.revisions.create`
- `run.revisions.update`
- `run.services.setIamPolicy`

### Service Account User (`roles/iam.serviceAccountUser`)
**İzinler:**
- Service account'ları kullanma
- Impersonation izni

### Cloud Build Editor (`roles/cloudbuild.builds.editor`)
**İzinler:**
- Build oluşturma ve yönetme
- `--source` ile deployment için gerekli

### Storage Admin (`roles/storage.admin`)
**İzinler:**
- Container Registry erişimi
- Image push/pull

## 🔐 Service Account İzinleri

Cloud Run, default service account kullanır:
- **Default:** `PROJECT_NUMBER-compute@developer.gserviceaccount.com`
- **Custom:** İstediğiniz service account'u belirtebilirsiniz

```powershell
# Service account ile deploy
gcloud run deploy records-ai-v2 `
  --source . `
  --service-account YOUR_SERVICE_ACCOUNT@records-ai.iam.gserviceaccount.com `
  --region europe-west1
```

## ✅ İzin Testi

İzinlerinizi test etmek için:

```powershell
# 1. Proje erişimi test et
gcloud projects describe records-ai

# 2. Cloud Run servisleri listele
gcloud run services list --region europe-west1

# 3. Servis bilgisi al (okuma izni test)
gcloud run services describe records-ai-v2 --region europe-west1

# 4. Deployment deneme (yazma izni test)
# Bu komut çalışırsa izinler tamam demektir
gcloud run deploy records-ai-v2 --source . --region europe-west1 --dry-run
```

## 🎯 Hızlı İzin Kontrolü

```powershell
# Tek komut ile mevcut izinleri görüntüle
gcloud projects get-iam-policy records-ai `
  --flatten="bindings[].members" `
  --format="table(bindings.role,bindings.members)" `
  --filter="bindings.members:$(gcloud config get-value account)"
```

## 📝 Notlar

1. **İzin Yayılması:** Yeni eklenen izinler 1-2 dakika içinde aktif olur
2. **Cache:** Bazen `gcloud auth application-default login` gerekebilir
3. **Organization Policies:** Bazı organizasyonlarda ek kısıtlamalar olabilir
4. **Billing:** Projede aktif billing account olmalı

## 🔗 İlgili Linkler

- **IAM Sayfası:** https://console.cloud.google.com/iam-admin/iam?project=records-ai
- **Cloud Run:** https://console.cloud.google.com/run?project=records-ai
- **Service Accounts:** https://console.cloud.google.com/iam-admin/serviceaccounts?project=records-ai

---

**Önemli:** IAM izinleri proje seviyesinde atanır. Eğer izinleriniz yoksa, proje Owner'ından talep edin.



