# Google Cloud Console - Adım Adım Yönlendirme

## Cloud Run Deployment Sayfasına Gitme

### Yöntem 1: Doğrudan Link (En Hızlı)

1. Bu linki tarayıcınızda açın:
   ```
   https://console.cloud.google.com/run?project=records-ai
   ```

### Yöntem 2: Console'dan Navigasyon

#### Adım 1: Cloud Run Servisleri Listesi
1. Sol menüden **"Run"** veya **"Cloud Run"** seçin
   - Bulamazsanız: **"☰" (Hamburger menü)** → **"Serverless"** → **"Cloud Run"**

#### Adım 2: Service Detayları
1. **"records-ai-v2"** servisine tıklayın
2. Servis detay sayfası açılacak

#### Adım 3: Yeni Revision Deploy Etme
1. Üstte **"EDIT & DEPLOY NEW REVISION"** butonuna tıklayın
2. VEYA **"DEPLOY NEW REVISION"** butonuna tıklayın

#### Adım 4: Source Deployment
1. **"Continuously deploy new revisions from a source repository"** sekmesine gidin
2. **"Source"** bölümünde:
   - **"Cloud Source Repositories"** yerine
   - **"Upload from your local machine"** seçin
   - VEYA **"Cloud Storage"** kullanın

## Build Loglarını Görüntüleme

### Cloud Build Sayfası
1. Sol menüden **"Cloud Build"** seçin
   - Bulamazsanız: **"☰"** → **"CI/CD"** → **"Cloud Build"**
2. **"History"** sekmesine gidin
3. Son build'e tıklayın
4. **"Build log"** sekmesinden detayları görün

**Doğrudan Link:**
```
https://console.cloud.google.com/cloud-build/builds?project=records-ai
```

## IAM İzinlerini Kontrol

### IAM Sayfası
1. Sol menüden **"IAM & Admin"** → **"IAM"** seçin
2. Email adresinizi (`ednovitsky@novitskyarchive.com`) bulun
3. Rolleri kontrol edin

**Doğrudan Link:**
```
https://console.cloud.google.com/iam-admin/iam?project=records-ai
```

## Service URL'i ve Durum

### Cloud Run Overview
1. Sol menüden **"Cloud Run"** seçin
2. **"records-ai-v2"** servisine tıklayın
3. Üst kısımda **"URL"** görünecek
4. **"Revisions"** sekmesinden revision geçmişini görebilirsiniz

**Doğrudan Link:**
```
https://console.cloud.google.com/run/detail/europe-west1/records-ai-v2?project=records-ai
```

## Hızlı Erişim Linkleri

### Cloud Run Servisleri
```
https://console.cloud.google.com/run?project=records-ai
```

### Cloud Build History
```
https://console.cloud.google.com/cloud-build/builds?project=records-ai
```

### IAM & Permissions
```
https://console.cloud.google.com/iam-admin/iam?project=records-ai
```

### Service Details
```
https://console.cloud.google.com/run/detail/europe-west1/records-ai-v2?project=records-ai
```

### Cloud Storage (Source Files)
```
https://console.cloud.google.com/storage/browser?project=records-ai&prefix=run-sources
```

## Önemli Notlar

1. **Project Seçimi:** Üstte "records-ai" projesi seçili olmalı
2. **Region:** `europe-west1` bölgesinde çalışıyor
3. **Service Name:** `records-ai-v2`

## Sorun Giderme

### Cloud Run bulunamıyor?
→ Sol menüden "☰" → "Serverless" → "Cloud Run"

### Build logları bulunamıyor?
→ "Cloud Build" → "History" → Son build'e tıklayın

### İzin sorunu?
→ "IAM & Admin" → "IAM" → Rollerinizi kontrol edin



