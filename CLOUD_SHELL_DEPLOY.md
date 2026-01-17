# Cloud Shell'de Deploy - Adım Adım

## ✅ Local Dosyalar Hazır!

Local'de şu dosyalar hazırlandı:
- ✅ `main.py` (root wrapper)
- ✅ `Procfile` (web: uvicorn backend.main:app ...)
- ✅ `runtime.txt` (python-3.11)
- ✅ `Dockerfile` (manuel build için)
- ✅ `app.yaml` (runtime config)

## 🚀 Cloud Shell'de Yapılacaklar:

### Seçenek 1: Hazır Script ile (ÖNERİLEN)

1. **Dosyaları Cloud Shell'e yükleyin:**
   - Cloud Shell Editor'ü açın (sağ üstte kalem ikonu)
   - Local `records_ai_v2` klasörünü Cloud Shell'e yükleyin
   - VEYA Cloud Shell terminalinde `Upload` butonuna tıklayın

2. **Script'i çalıştırılabilir yapın:**
   ```bash
   chmod +x DEPLOY_NOW.sh
   ```

3. **Script'i çalıştırın:**
   ```bash
   bash DEPLOY_NOW.sh
   ```

### Seçenek 2: Manuel Deploy

1. **Proje dizinine gidin:**
   ```bash
   cd ~/records_ai_v2
   # VEYA dosyaları yüklediğiniz dizine
   ```

2. **Dosyaları kontrol edin:**
   ```bash
   ls -la main.py Procfile runtime.txt backend/main.py
   ```

3. **Eğer main.py yoksa, oluşturun:**
   ```bash
   cat > main.py << 'EOF'
   """
   Root entrypoint wrapper for Cloud Run buildpacks.
   """
   import sys
   import os
   sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
   from backend.main import app
   if __name__ == "__main__":
       import uvicorn
       port = int(os.environ.get("PORT", 8080))
       uvicorn.run(app, host="0.0.0.0", port=port)
   EOF
   ```

4. **Deploy edin:**
   ```bash
   gcloud run deploy records-ai-v2 \
     --source . \
     --platform managed \
     --region europe-west1 \
     --allow-unauthenticated \
     --port 8080 \
     --project records-ai
   ```

## ⚠️ IAM Hatası Alırsanız:

Build başarılı ama 403 hatası varsa:

1. Console'a gidin:
   ```
   https://console.cloud.google.com/run/detail/europe-west1/records-ai-v2?project=records-ai
   ```

2. "EDIT & DEPLOY NEW REVISION" → "SECURITY" → "Allow unauthenticated invocations" → "DEPLOY"

## 📋 Dosya Kontrolü

Deploy'dan önce bu dosyaların olduğundan emin olun:
- ✅ `main.py` (root'ta)
- ✅ `Procfile` (root'ta)
- ✅ `runtime.txt` (root'ta)
- ✅ `backend/main.py` (gerçek uygulama)
- ✅ `requirements.txt` (dependencies)

## 🎯 Başarı Kriterleri

1. ✅ Build başarılı (STATUS: SUCCESS)
2. ✅ Service URL çalışıyor
3. ✅ `/health` endpoint 200 dönüyor
4. ✅ `/ui/index.html` erişilebilir (403 olmamalı)
