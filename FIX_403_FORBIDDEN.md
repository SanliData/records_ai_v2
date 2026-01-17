# 403 Forbidden Hatası - Çözüm

## Sorun
`/ui/index.html` ve diğer static files 403 Forbidden hatası veriyor.

## Olası Nedenler

1. **Cloud Run IAM Policy** - Service unauthenticated access'e izin vermiyor
2. **Static Files** - `frontend` klasörü Docker image'ine kopyalanmamış
3. **Deployment ayarları** - `--allow-unauthenticated` flag'i eksik

## Çözüm Adımları

### 1. IAM Policy'yi Düzelt (Cloud Console)

**Link:**
```
https://console.cloud.google.com/run/detail/europe-west1/records-ai-v2/iam?project=records-ai
```

**Yapılacaklar:**
1. Cloud Console'da service'in **"IAM"** sekmesine gidin
2. **"Add principal"** butonuna tıklayın
3. Principal: `allUsers`
4. Role: `Cloud Run Invoker`
5. Save

### 2. veya gcloud CLI ile

```bash
gcloud run services add-iam-policy-binding records-ai-v2 \
  --region=europe-west1 \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --project=records-ai
```

### 3. Dockerfile Kontrolü

`frontend` klasörünün Docker image'ine kopyalandığından emin olun.

### 4. Yeniden Deploy

```bash
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080 \
  --project records-ai
```

## Hızlı Test

Deploy'dan sonra:
```
https://records-ai-v2-969278596906.europe-west1.run.app/health
```

Bu çalışıyorsa ama `/ui/index.html` çalışmıyorsa, static files sorunu var demektir.



