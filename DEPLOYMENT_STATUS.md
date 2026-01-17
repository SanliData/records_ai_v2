# Deployment Durumu ve Senaryo Notları

## Mevcut Durum

### Local Development
- **Path**: `C:\Users\issan\records_ai_v2`
- **Frontend**: `frontend/` klasörü
- **Backend**: `backend/` klasörü
- **API Base**: `http://127.0.0.1:8000`

### Production Deployment
- **Domain**: `zyagrolia.com`
- **API**: `api.zyagrolia.com`
- **Frontend URL**: `https://zyagrolia.com/ui/`
- **Platform**: Google Cloud Run
- **Static Files**: FastAPI `/ui` mount point'inden servis ediliyor

### GitHub Repository
- **URL**: https://github.com/SanliData/records_ai
- **Status**: Public repository
- **Branch**: main

## Son Yapılan Değişiklikler

### Frontend Refactoring (UPAP Uyumlu)
1. ✅ **index.html** - Ana sayfa eklendi
2. ✅ **upload.html** - Anonymous upload, UPAP uyumlu
3. ✅ **results.html** - Results preview sayfası
4. ✅ **archive-save.html** - Archive kaydetme (auth gerekli)
5. ✅ **login.html** - Navigation güncellendi

### Backend
1. ✅ **main.py** - Root redirect `/ui/index.html` olarak güncellendi

### UPAP Uyumluluk
- ✅ Tüm frontend sayfaları UPAP endpoint'lerini kullanıyor
- ✅ Upload → Process → Archive → Publish pipeline'ı korunuyor
- ✅ Preview mode: Upload + Process (Archive öncesi durur)

## GitHub Senkronizasyon

### Push Gereken Dosyalar
```
frontend/
  - index.html (YENİ)
  - upload.html (GÜNCELLENDİ)
  - results.html (YENİ)
  - archive-save.html (YENİ)
  - login.html (GÜNCELLENDİ)

backend/
  - main.py (GÜNCELLENDİ)

UPAP_COMPATIBILITY_NOTES.md (YENİ)
GITHUB_SYNC_NOTES.md (YENİ)
DEPLOYMENT_STATUS.md (YENİ)
```

### Git Komutları (Git Kuruluysa)
```bash
git add .
git commit -m "feat: UPAP uyumlu frontend refactoring

- Anonymous upload/analysis support
- New pages: index, results, archive-save
- UPAP pipeline compliance
- Navigation consistency
- GPT ownership footer"

git push origin main
```

## Production Deployment Notları

### Mevcut Durum
- Production'da eski `upload.html` görünüyor olabilir (cache sorunu)
- Hard refresh (Ctrl+F5) gerekli
- Server restart gerekebilir

### Yeni Deployment Gerekiyorsa
```powershell
# Cloud Run'a deploy
gcloud run deploy records-ai-v2 `
  --source . `
  --region europe-west1 `
  --platform managed `
  --allow-unauthenticated
```

### Deployment Sonrası
1. Cache temizleme (hard refresh)
2. Test: `https://zyagrolia.com/ui/index.html`
3. Test: `https://zyagrolia.com/ui/upload.html`
4. API test: `https://api.zyagrolia.com/health`

## UPAP Gelecek Senaryosu

### UPAP Ayrı Uygulama Olunca

**Frontend Değişiklikleri:**
- UPAP service URL environment variable'dan alınacak
- Config dosyası: `config.js` veya environment variable
- Fallback: `api.zyagrolia.com` (mevcut)

**Backend Değişiklikleri:**
- UPAP service client wrapper
- Service discovery için config
- Authentication token forwarding

**Migration Checklist:**
- [ ] UPAP service URL environment variable
- [ ] Frontend config system
- [ ] Backend UPAP client
- [ ] Test endpoints migration
- [ ] Documentation update

## Önemli Notlar

1. **Cache Sorunları:**
   - Frontend static files cache'lenebilir
   - Hard refresh gerekebilir
   - Production deploy sonrası server restart önerilir

2. **API Endpoint'leri:**
   - Local: `http://127.0.0.1:8000`
   - Production: `https://api.zyagrolia.com`
   - UPAP Service (gelecek): Environment variable

3. **UPAP Pipeline:**
   - Upload → Process → Archive → Publish (immutable order)
   - Preview mode: Upload + Process (Archive öncesi durur)
   - Anonymous: Upload + Process
   - Authenticated: Archive + Publish



