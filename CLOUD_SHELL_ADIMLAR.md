# Cloud Shell'de Deployment - Adım Adım

## SORUNLAR:
1. ❌ Build hatası: `Dockerfile` bulunamıyor
2. ❌ IAM policy: `allUsers` eklenemiyor (organization policy)

## ✅ ÇÖZÜM ADIMLARI:

### ADIM 1: Cloud Shell'de Dosyaları Hazırlayın

```bash
# Mevcut dizini kontrol et
pwd
ls -la

# Eğer dosyalar yoksa, GitHub'dan çekin VEYA Cloud Shell Editor'den yükleyin
# GitHub'dan:
# git clone https://github.com/SanliData/records_ai.git records_ai_v2
# cd records_ai_v2

# Dockerfile'ı kontrol et
ls -la | grep -i dockerfile

# Eğer dockerfile (küçük d) varsa, Dockerfile (büyük D) olarak değiştir
if [ -f "dockerfile" ] && [ ! -f "Dockerfile" ]; then
    mv dockerfile Dockerfile
    echo "✓ dockerfile -> Dockerfile"
fi

# Dockerfile içeriğini kontrol et
head Dockerfile
```

### ADIM 2: Deploy Script'ini Çalıştırın

```bash
# Script'i çalıştırılabilir yap
chmod +x CLOUD_SHELL_DEPLOY_FIX.sh

# Çalıştır
bash CLOUD_SHELL_DEPLOY_FIX.sh
```

### ADIM 3: Eğer IAM Hatası Alırsanız

Build başarılı ama 403 hatası alıyorsanız, Console'dan yapın:

1. **Cloud Console'a gidin:**
   ```
   https://console.cloud.google.com/run/detail/europe-west1/records-ai-v2?project=records-ai
   ```

2. **"EDIT & DEPLOY NEW REVISION" butonuna tıklayın**

3. **"SECURITY" sekmesine gidin**

4. **"Allow unauthenticated invocations" seçeneğini işaretleyin**

5. **"DEPLOY" butonuna tıklayın**

## MANUEL DEPLOY (Alternatif)

```bash
# Proje ayarla
gcloud config set project records-ai

# Deploy et
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080 \
  --project records-ai
```

## BUILD HATASI KONTROLÜ

Eğer hala build hatası alıyorsanız:

```bash
# Son build loglarını göster
gcloud builds list --limit=1 --format="value(id)" | xargs -I {} gcloud builds log {}

# VEYA Console'dan:
# https://console.cloud.google.com/cloud-build/builds?project=records-ai
```

## TEST

Deploy başarılı olduktan sonra:

```
https://records-ai-v2-969278596906.europe-west1.run.app/ui/index.html
```



