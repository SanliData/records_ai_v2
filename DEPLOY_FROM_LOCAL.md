# Local Dosyalardan Deploy (Doğru Yöntem)

## Sorun
Yanlış repository kullanılıyor. Cloud Build GitHub'dan çekmeye çalışıyor olabilir.

## Çözüm: Local Source Deployment

### Cloud Shell'den (Önerilen)

1. **Cloud Shell'i açın** (üstteki terminal ikonuna tıklayın)

2. **Dosyaları yükleyin:**
   - Cloud Shell'de "Düzenleyiciyi Aç" (Open Editor) butonuna tıklayın
   - VEYA dosyaları zip olarak yükleyin

3. **Deploy komutu:**
```bash
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080
```

### Alternatif: Dosyaları Cloud Shell'e Kopyala

```bash
# 1. Cloud Shell'de klasör oluştur
mkdir records_ai_v2
cd records_ai_v2

# 2. Dosyaları yükle (Cloud Shell Editor veya zip upload)

# 3. Deploy et
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080
```

## Önemli: `--source .` Parametresi

Bu parametre:
- ✅ Local dizindeki dosyaları kullanır
- ✅ GitHub repository'ye bağlı değildir
- ✅ En güncel local dosyaları deploy eder

## GitHub Repository Senkronizasyonu (Sonra)

Deployment başarılı olduktan sonra, GitHub'ı güncellemek isterseniz:

```bash
# Git kuruluysa
git add .
git commit -m "feat: UPAP uyumlu frontend refactoring"
git push origin main
```

## Hızlı Özet

**Şimdi Yapılacak:**
1. Cloud Shell aç
2. Dosyaları yükle (Editor veya zip)
3. `gcloud run deploy records-ai-v2 --source . --platform managed --region europe-west1 --allow-unauthenticated --port 8080`

Bu yöntem GitHub repository'yi bypass eder ve direkt local dosyaları kullanır!



