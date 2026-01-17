# Records_AI v2 - İşlem Akışı ve Mimarisi

## 📊 Genel Bakış

**Records_AI v2**, plak arşivi (vinyl record archive) için geliştirilmiş bir FastAPI tabanlı UPAP (Upload → Process → Archive → Publish) pipeline sistemidir.

---

## 🎯 UPAP Pipeline: Ana İşlem Akışı

### UPAP = Upload → Process → Archive → Publish

```
┌─────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│ UPLOAD  │ ───> │ PROCESS  │ ───> │ ARCHIVE  │ ───> │ PUBLISH  │
│ (Yükle) │      │ (İşle)   │      │ (Arşivle)│      │ (Yayınla)│
└─────────┘      └──────────┘      └──────────┘      └──────────┘
```

---

## 🔄 Detaylı İşlem Akışı

### 1️⃣ UPLOAD STAGE (Yükleme Aşaması)

**Ne Yapar:**
- Kullanıcıdan dosya (resim/video) alır
- Dosyayı diske kaydeder: `storage/uploads/{user_id}/{filename}`
- `record_id` oluşturur (UUID)

**Endpoint:**
- `/upap/upload` (standart upload)
- `/upap/process/process/preview` (preview mode - anonymous)

**Kimler Kullanabilir:**
- ✅ **Anonymous users** (preview mode)
- ✅ **Authenticated users** (full upload)

**Input:**
```json
{
  "file": "image.jpg",
  "email": "user@example.com" (opsiyonel - preview mode'da yok)
}
```

**Output:**
```json
{
  "record_id": "uuid-here",
  "saved_to": "storage/uploads/user_id/image.jpg",
  "stage": "upload"
}
```

---

### 2️⃣ PROCESS STAGE (İşleme Aşaması)

**Ne Yapar:**
- OCR çalıştırır (text extraction)
- AI analizi yapar (NovArchive GPT service)
- Metadata çıkarır (artist, album, year, label, vb.)
- Fuzzy matching yapar (archived records ile eşleştirme)

**Opsiyonel Modüller (ENV ile kontrol):**
- **OCR Stage:** `UPAP_ENABLE_OCR=true` → Tesseract OCR çalışır
- **AI Stage:** `UPAP_ENABLE_AI=true` → AI metadata extraction

**Endpoint:**
- `/upap/process` (standart process)
- `/upap/process/process/preview` (upload + process birleşik)

**Output:**
```json
{
  "record_id": "uuid-here",
  "stage": "process",
  "ocr_text": "extracted text...",
  "ai_metadata": {
    "artist": "Pink Floyd",
    "album": "The Wall",
    "year": "1979",
    "label": "Harvest Records",
    "catalog_number": "SHVL 815"
  },
  "archive_match": false,
  "candidates": []
}
```

---

### 3️⃣ ARCHIVE STAGE (Arşivleme Aşaması)

**Ne Yapar:**
- Record'u kalıcı arşive kaydeder
- Kullanıcı ile record'u ilişkilendirir
- Archive store'a yazar (SQLite/JSON)

**⚠️ AUTHENTICATION GEREKLİ:**
- Archive stage için kullanıcı girişi zorunlu
- Anonymous kullanıcılar archive yapamaz

**Endpoint:**
- `/upap/archive/add` (POST - record_id ile)

**Input:**
```json
{
  "record_id": "uuid-here",
  "user_id": "authenticated-user-id"
}
```

**Output:**
```json
{
  "status": "archived",
  "record_id": "uuid-here",
  "archive": { ... archived record data ... }
}
```

---

### 4️⃣ PUBLISH STAGE (Yayınlama Aşaması)

**Ne Yapar:**
- Archive edilmiş record'u yayınlar
- Kullanıcı kütüphanesinde görünür yapar
- Query/search için hazır hale getirir

**⚠️ ÖNKOŞUL:**
- Record önce **Archive** edilmiş olmalı
- `is_archived=True` kontrolü yapılır

**Endpoint:**
- `/upap/publish` (POST - record_id ile)

**Input:**
```json
{
  "record_id": "uuid-here"
}
```

**Output:**
```json
{
  "status": "published",
  "record_id": "uuid-here",
  "stage": "publish"
}
```

---

## 👤 Kullanıcı Senaryoları

### Senaryo 1: Anonymous Kullanıcı (Keşfetme Modu)

```
1. Kullanıcı upload.html'ye gider
2. Dosya seçer (email gerekmez)
3. Upload → Process çalışır (preview mode)
4. Sonuçları görür (results.html)
5. Archive yapmak isterse → login gerekir
```

**Endpoint Kullanımı:**
- `POST /upap/process/process/preview` (anonymous)

**Akış:**
```
User → Upload File → Preview Results → [Login Required] → Archive
```

---

### Senaryo 2: Authenticated Kullanıcı (Tam Akış)

```
1. Kullanıcı login olur
2. Upload yapar
3. Process otomatik çalışır
4. Archive eder
5. Publish eder
```

**Endpoint Kullanımı:**
- `POST /upap/upload`
- `POST /upap/process`
- `POST /upap/archive/add`
- `POST /upap/publish`

**Akış:**
```
User → Upload → Process → Archive → Publish → Library'de Görünür
```

---

## 🌐 Frontend Sayfaları ve Akışları

### `/ui/index.html` - Ana Sayfa
- UPAP pipeline açıklaması
- Anonymous access bilgisi
- Navigation menüsü

### `/ui/upload.html` - Yükleme Sayfası
- **Anonymous access:** ✅
- Dosya seçimi (resim/video/ZIP)
- Preview mode: `/upap/process/process/preview`
- Sonuçlar `results.html`'e yönlendirilir

### `/ui/results.html` - Sonuçlar Sayfası
- PreviewRecord gösterimi
- Archive butonu (login gerektirir)
- `/upap/archive/add` endpoint'ine yönlendirir

### `/ui/archive-save.html` - Arşiv Kaydetme
- **Authentication required:** ✅
- `/upap/archive/add` endpoint'i çağrılır
- Kullanıcı kütüphanesine kaydedilir

### `/ui/library.html` - Kullanıcı Kütüphanesi
- **Authentication required:** ✅
- Kullanıcının archived records'ları gösterilir
- Published records query edilir

### `/ui/login.html` - Giriş Sayfası
- Kullanıcı girişi/kaydı
- JWT token management

---

## 🏗️ Mimari Yapı

### Backend Katmanları

```
backend/
├── api/v1/              # FastAPI routers
│   ├── upap_upload_router.py
│   ├── upap_process_router.py
│   ├── upap_preview_router.py    # Preview mode (anonymous)
│   ├── upap_archive_router.py
│   ├── upap_archive_add_router.py
│   └── upap_publish_router.py
│
├── services/upap/       # UPAP pipeline stages
│   ├── engine/
│   │   └── upap_engine.py        # Pipeline orchestrator
│   ├── upload/
│   │   └── upload_stage.py       # Stage 1
│   ├── process/
│   │   ├── process_stage.py      # Stage 2
│   │   └── adapters/             # Domain adapters
│   ├── archive/
│   │   ├── archive_stage.py      # Stage 3
│   │   └── archive_store.py      # Persistence layer
│   └── publish/
│       ├── publish_stage.py      # Stage 4
│       └── publish_store.py
│
└── models/              # Data models
    └── preview_record.py
```

### UPAP Engine Yapısı

```python
UPAPEngine:
  ├── Zorunlu Stages:
  │   ├── ArchiveStage
  │   └── PublishStage
  │
  └── Opsiyonel Stages (ENV ile):
      ├── OCRStage (UPAP_ENABLE_OCR=true)
      └── AIStage (UPAP_ENABLE_AI=true)
```

---

## 📡 API Endpoint Özeti

### UPAP Endpoints

| Endpoint | Method | Auth | Açıklama |
|----------|--------|------|----------|
| `/upap/upload` | POST | Optional | Standart upload |
| `/upap/process` | POST | Optional | Standart process |
| `/upap/process/process/preview` | POST | **No** | Upload + Process (anonymous) |
| `/upap/archive/add` | POST | **Required** | Archive stage |
| `/upap/publish` | POST | **Required** | Publish stage |

### Diğer Endpoints

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/` | GET | Health check |
| `/ui/*` | GET | Frontend static files |
| `/docs` | GET | Swagger UI |

---

## 🔐 Authentication & Authorization

### Anonymous Access (Preview Mode)
- ✅ Upload + Process yapabilir
- ❌ Archive yapamaz
- ❌ Publish yapamaz

### Authenticated Access
- ✅ Tüm UPAP stages'i kullanabilir
- ✅ Kendi kütüphanesini görüntüleyebilir
- ✅ Records'ları archive/publish edebilir

**Authentication Gate:**
- Archive stage'de zorunlu
- Library'de zorunlu
- Preview mode'da yok

---

## 💾 Veri Akışı

### 1. Preview Mode (Anonymous)

```
File Upload
    ↓
storage/uploads/preview/{filename}
    ↓
OCR/AI Processing
    ↓
PreviewRecord (in-memory, non-authoritative)
    ↓
Frontend Display
    ↓
[User must login for Archive]
```

### 2. Full Pipeline (Authenticated)

```
File Upload
    ↓
storage/uploads/{user_id}/{filename}
    ↓
OCR/AI Processing
    ↓
Archive Store (persistent)
    ↓
Publish Store (queryable)
    ↓
User Library (visible)
```

---

## 🎨 Frontend → Backend İletişimi

### Upload Page Flow

```javascript
// upload.html
1. User selects file
2. FormData oluşturulur
3. POST /upap/process/process/preview
4. Response: PreviewRecord[]
5. Redirect to results.html
```

### Archive Flow

```javascript
// archive-save.html (after login)
1. User clicks "Archive" button
2. POST /upap/archive/add { record_id }
3. Response: { status: "archived" }
4. Redirect to library.html
```

---

## 🚀 Deployment

### Production Environment
- **Platform:** Google Cloud Run
- **Service:** `records-ai-v2`
- **Region:** `us-central1`
- **Domain:** `zyagrolia.com` (temporary), `novitskyarchive.com` (in progress)

### Environment Variables

```bash
UPAP_ENABLE_OCR=true    # OCR stage'i etkinleştir
UPAP_ENABLE_AI=true     # AI stage'i etkinleştir
```

---

## 📝 Özet: İşlem Akışı

### Basit Kullanım (Anonymous)
```
1. /ui/upload.html → Dosya seç
2. Preview mode → Sonuçları gör
3. Login → Archive yap
4. Library'de görüntüle
```

### Tam Kullanım (Authenticated)
```
1. Login
2. Upload → Process → Archive → Publish
3. Library'de görüntüle
4. Query/Search yap
```

---

## 🔄 UPAP Pipeline Sırası (Immutable)

**Pipeline sırası değiştirilemez:**
1. **Upload** (zorunlu - başlangıç)
2. **Process** (opsiyonel - OCR/AI)
3. **Archive** (zorunlu - authentication gerekli)
4. **Publish** (zorunlu - archive sonrası)

**Bypass edilemez, atlanamaz!**

---

**📚 Daha fazla bilgi için:**
- `UPAP_COMPATIBILITY_NOTES.md` - UPAP uyumluluk notları
- `docs/main_book/UPAP/` - Detaylı dokümantasyon
