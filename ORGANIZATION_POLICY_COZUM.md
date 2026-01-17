# Organization Policy Engeli - Çözüm

## ❌ SORUN:
"Domain Restricted Sharing" organization policy `allUsers` eklemeye izin vermiyor.

## ✅ ÇÖZÜM 1: Service Authentication Ayarını Değiştir (ÖNERİLEN)

### Adımlar:

1. **Cloud Run Services sayfasına gidin:**
   ```
   https://console.cloud.google.com/run?project=records-ai
   ```

2. **"records-ai-v2" service'ine tıklayın** (europe-west1 region)

3. **"EDIT & DEPLOY NEW REVISION" butonuna tıklayın**

4. **"SECURITY" sekmesine gidin** (veya "Networking" sekmesi)

5. **"Authentication" bölümünü bulun**

6. **"Allow unauthenticated invocations" seçeneğini işaretleyin**

7. **"DEPLOY" butonuna tıklayın**

Bu yöntem IAM policy'yi otomatik olarak ayarlar ve organization policy'yi bypass edebilir.

## ✅ ÇÖZÜM 2: Deployment Sırasında Flag Kullan

Yeniden deploy ederken `--allow-unauthenticated` flag'i kullanın:

```powershell
.\QUICK_DEPLOY.ps1
```

VEYA Cloud Shell'den:
```bash
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080 \
  --project records-ai
```

## ✅ ÇÖZÜM 3: Organization Admin ile İletişim

Organization policy'yi değiştirmek için organization admin yetkisi gerekir. Eğer bu yetkiniz varsa:

1. Organization Policy sayfasına gidin
2. `iam.allowedPolicyMemberDomains` constraint'ini bulun
3. `allUsers` için exception ekleyin

## ⚠️ NOT:

Sol tarafta iki service görünüyor:
- **us-central1**: "Public access" ✅ (çalışıyor)
- **europe-west1**: "Require authentication" ❌ (403 hatası)

Europe-west1 service'ini "Public access" yapmamız gerekiyor.



