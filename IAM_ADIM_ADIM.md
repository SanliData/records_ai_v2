# Cloud Run Service IAM - Adım Adım

## ŞU ANDA: Proje IAM Sayfasındasınız ❌
## GİTMENİZ GEREKEN: Cloud Run Service IAM ✅

## ADIMLAR:

### 1️⃣ Cloud Run Services Sayfasına Gidin
**Link:**
```
https://console.cloud.google.com/run?project=records-ai
```

**VEYA** sol menüden:
- "Cloud Run" tıklayın (sol menüde)
- "Services" tıklayın
- "records-ai-v2" service'ine tıklayın

### 2️⃣ Service Details Sayfasında
Üstte şu sekmeler görünecek:
- Overview
- Observability
- Revisions
- Source
- Triggers
- **PERMISSIONS** ← BU SEKMEYE TIKLAYIN
- Networking
- Security
- YAML

### 3️⃣ PERMISSIONS Sekmesinde
"ADD PRINCIPAL" butonuna tıklayın

### 4️⃣ Formu Doldurun:
- **New principals:** `allUsers`
- **Select a role:** `Cloud Run Invoker`
- **Save** butonuna tıklayın

### 5️⃣ Onay
"Allow unauthenticated invocations?" sorusuna **"Allow"** diyin

## ✅ BAŞARILI!
Artık `/ui/index.html` çalışmalı.

## Direkt Link (Service IAM):
```
https://console.cloud.google.com/run/detail/europe-west1/records-ai-v2/permissions?project=records-ai
```



