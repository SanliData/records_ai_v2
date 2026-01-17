# Hızlı Navigasyon Rehberi

## 🎯 Şu Anda Neredesiniz?
**Cloud Build → Repositories** sayfasındasınız

## 🚀 Gitmek İstediğiniz Yer: Cloud Run

### En Hızlı Yol: Doğrudan Link
Bu linki açın (yeni sekmede):
```
https://console.cloud.google.com/run?project=records-ai
```

### Alternatif: Sol Menü
1. Sol menüde yukarı/aşağı scroll edin
2. **"Run"** veya **"Cloud Run"** bulun
   - "Serverless" bölümü altında olabilir
3. Tıklayın

### Alternatif: Arama
1. Üstteki arama çubuğuna tıklayın
2. "Cloud Run" yazın
3. İlk sonuca tıklayın

## 📋 Tüm Önemli Linkler

| Sayfa | Link |
|-------|------|
| **Cloud Run** | https://console.cloud.google.com/run?project=records-ai |
| **Build History** | https://console.cloud.google.com/cloud-build/builds?project=records-ai |
| **Service Details** | https://console.cloud.google.com/run/detail/europe-west1/records-ai-v2?project=records-ai |
| **IAM** | https://console.cloud.google.com/iam-admin/iam?project=records-ai |

## ⚡ Cloud Shell'den Deploy (En Kolay)

Eğer Cloud Shell kullanmak isterseniz:

1. Üstteki **terminal ikonuna** tıklayın (Cloud Shell'i aç)
2. Şu komutu çalıştırın:
```bash
gcloud run deploy records-ai-v2 --source . --platform managed --region europe-west1 --allow-unauthenticated --port 8080
```

## ✅ Sonuç

**Seçenek 1:** Cloud Run linkini aç → Service'e tıkla → Deploy  
**Seçenek 2:** Cloud Shell aç → Komutu çalıştır



