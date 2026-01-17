# Build Hatası Çözümü

## ❌ SORUN:
Build log'unda görülen hata:
```
unable to evaluate symlinks in Dockerfile path: lstat /workspace/Dockerfile: no such file or directory
```

**Neden:** Cloud Build `Dockerfile` (büyük D) arıyor, ama dosya `dockerfile` (küçük d) olabilir.

## ✅ ÇÖZÜM:

### 1. Local'de Dockerfile'ı kontrol edin

PowerShell'de:
```powershell
# Dockerfile'ı kontrol et
Get-ChildItem -Filter "*ockerfile*"

# Eğer dockerfile varsa, Dockerfile olarak yeniden adlandır
Rename-Item -Path "dockerfile" -NewName "Dockerfile"
```

### 2. Cloud Shell'de dosyaları yükleyin

**Seçenek A: Cloud Shell Editor**
1. Cloud Shell'de sağ üstte **"Open Editor"** butonuna tıklayın
2. Dosyaları drag & drop ile yükleyin

**Seçenek B: Upload butonu**
1. Cloud Shell terminalinde **"Upload"** butonuna tıklayın
2. `records_ai_v2` klasörünü zip'leyip yükleyin
3. Zip'i açın: `unzip records_ai_v2.zip`

**Seçenek C: GitHub'dan çek**
```bash
git clone https://github.com/SanliData/records_ai.git records_ai_v2
cd records_ai_v2
# Dockerfile'ı kontrol et ve düzelt
```

### 3. Dockerfile'ı düzeltin

Cloud Shell'de:
```bash
cd records_ai_v2

# Dockerfile var mı kontrol et
ls -la | grep -i dockerfile

# Eğer dockerfile varsa, Dockerfile olarak yeniden adlandır
if [ -f "dockerfile" ] && [ ! -f "Dockerfile" ]; then
    mv dockerfile Dockerfile
    echo "✓ dockerfile -> Dockerfile"
fi

# Dockerfile içeriğini kontrol et
cat Dockerfile
```

### 4. Deploy edin

```bash
bash CLOUD_SHELL_DEPLOY_FIX.sh
```

VEYA manuel:
```bash
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080 \
  --project records-ai
```

## ⚠️ ÖNEMLİ:

1. **Dockerfile** dosyası repository root'unda olmalı
2. İsmi **tam olarak "Dockerfile"** olmalı (büyük D, geri kalan küçük)
3. Dosya `.gcloudignore` içinde ignore edilmemeli



