# Cloud Shell'de Copy-Paste Komutları

## ❗ ÖNEMLİ: Dosyalar Cloud Shell'de Olmalı

Eğer dosyalar Cloud Shell'de değilse, önce yükleyin:

### Dosyaları Yükleme:

1. **Cloud Shell Editor ile:**
   - Sağ üstte **"Open Editor"** (kalem ikonu) tıklayın
   - Local `records_ai_v2` klasörünü Cloud Shell'e yükleyin

2. **VEYA Upload butonu ile:**
   - Cloud Shell terminalinde **"Upload"** butonuna tıklayın
   - Dosyaları seçin

## 🚀 Deploy Komutları (Copy-Paste)

### Adım 1: Dosyaların Olduğu Dizine Gidin

```bash
# Eğer records_ai_v2 klasörü varsa
cd ~/records_ai_v2

# VEYA dosyaları yüklediğiniz dizine gidin
# Örnek: cd ~/your_folder_name
```

### Adım 2: Dosyaları Oluştur ve Deploy Et

**Tüm komutları tek seferde çalıştırın:**

```bash
# main.py oluştur
cat > main.py << 'EOF'
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from backend.main import app
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
EOF

# Procfile oluştur
echo "web: uvicorn backend.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# runtime.txt oluştur
echo "python-3.11" > runtime.txt

# Deploy et
gcloud config set project records-ai && \
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080
```

## ✅ Alternatif: Script Oluştur

```bash
# Script'i oluştur
cat > deploy_now.sh << 'ENDOFSCRIPT'
#!/bin/bash
cd ~/records_ai_v2 2>/dev/null || pwd

cat > main.py << 'EOF'
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from backend.main import app
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
EOF

echo "web: uvicorn backend.main:app --host 0.0.0.0 --port \$PORT" > Procfile
echo "python-3.11" > runtime.txt

gcloud config set project records-ai && \
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080
ENDOFSCRIPT

# Çalıştırılabilir yap
chmod +x deploy_now.sh

# Çalıştır
bash deploy_now.sh
```

## ⚠️ Hata Alırsanız

### "backend/main.py bulunamadı"
- Dosyalar Cloud Shell'de değil
- Doğru dizinde olduğunuzdan emin olun: `ls -la backend/main.py`

### "No such file or directory"
- Dosyaları Cloud Shell'e yükleyin (Editor veya Upload)

### Build hatası
- Build loglarını kontrol edin:
```bash
gcloud builds list --limit=1 --format="value(id)" | xargs -I {} gcloud builds log {} --project=records-ai
```



