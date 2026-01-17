# ❌ YANLIŞ YER - PROJE IAM
# ✅ DOĞRU YER - CLOUD RUN SERVICE IAM

## Şu anda neredeyiz?
**❌ YANLIŞ:** `IAM & Admin > IAM` (PROJE seviyesi IAM)

## Nereye gitmeliyiz?
**✅ DOĞRU:** Cloud Run Service'in IAM sekmesi

## Adımlar:

### 1. Cloud Run Services sayfasına gidin:
```
https://console.cloud.google.com/run?project=records-ai
```

### 2. "records-ai-v2" service'ine tıklayın

### 3. Üstteki sekmelerden "PERMISSIONS" (veya "IAM") sekmesine tıklayın

### 4. VEYA direkt bu linke gidin:
```
https://console.cloud.google.com/run/detail/europe-west1/records-ai-v2/permissions?project=records-ai
```

### 5. "ADD PRINCIPAL" butonuna tıklayın

### 6. Principal: `allUsers`
### 7. Role: `Cloud Run Invoker`
### 8. Save

## Fark:
- **PROJE IAM:** Tüm proje için genel izinler
- **SERVICE IAM:** Sadece bu Cloud Run service için özel izinler

Bizim ihtiyacımız: **SERVICE IAM** (Cloud Run service seviyesi)



