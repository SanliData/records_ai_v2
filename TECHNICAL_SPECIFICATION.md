# RECORDS_AI
## Teknik Tanıtım Raporu

**Versiyon:** v2 (UPAP Tabanlı Mimari)  
**Durum:** Mimari Stabilizasyon Tamamlandı – Recognition Entegrasyonu Eksik  
**Date:** 2025-01-19  
**Pipeline Score:** 100/100 (UPAP Validation)  
**Fonksiyonellik:** ~80% tamamlanmış

---

## 1. Projenin Amacı

`records_ai`, dijital veya fiziksel medya varlıklarının (başlangıçta görsel, özellikle plak / arşiv materyali) yüklenmesi, analiz edilmesi, arşivlenmesi ve yayıma hazır hâle getirilmesi için tasarlanmış aşamalı (pipeline-based) bir arka uç sistemidir.

**Gerçek Durum:**
- ✅ Upload pipeline çalışıyor (image/audio kabul ediyor)
- ⚠️ Recognition servisleri mevcut ama upload flow'a bağlı değil (Phase 1'de düzeltilecek)
- ✅ Archive sistemi çalışıyor
- ⚠️ Marketplace entegrasyonu placeholder (in-memory, Phase 3'te gerçek API'ler eklenecek)

Sistem; bireysel kullanıcılar, arşivciler ve gelecekte pazar yeri entegrasyonları için kanıtlanabilir, izlenebilir ve genişletilebilir bir altyapı sunar.

---

## 2. Mimari Yaklaşım – UPAP Modeli

`records_ai`'nin çekirdeğinde **UPAP** adı verilen deterministik bir işlem hattı bulunur:

```
Upload → Process → Archive → Publish
```

Bu yapı tek seferlik scriptler veya monolitik endpoint'ler yerine, açık kontratlara sahip bağımsız aşamalar kullanır.

### UPAP'in Temel Özellikleri:

- ✅ **Aşama bazlı çalışır** (stage-based)
- ✅ **Her aşama bağımsız test edilebilir**
- ✅ **Girdi–çıktı kontratları nettir**
- ✅ **Hatalar sessizce yutulmaz, deterministiktir**
- ✅ **Geriye dönük uyumluluk korunur**

---

## 3. Aşama (Stage) Tanımı ve Standartları

Her UPAP aşaması aşağıdaki teknik sözleşmeye uyar:

- `StageInterface` üzerinden tanımlanır
- Zorunlu `name` attribute'u bulunur
- Tek giriş noktası: `run(context: dict)`
- Gerekli input'lar eksikse açık hata üretir
- Yan etkiler kontrollüdür
- Docstring ve imza standardı zorunludur

Bu yapı sayesinde sistemde:

- ❌ Gizli bağımlılık yoktur
- ✅ Aşamalar yer değiştirebilir
- ✅ Yeni aşamalar eklenebilir

---

## 4. UPAP Aşamalarının Teknik Rolü

### 4.1 Auth Stage

- Kullanıcıyı tanımlar / doğrular
- Pipeline'a kullanıcı bağlamını ekler

**Implementation:** `backend/services/upap/auth/auth_stage.py`

### 4.2 Upload Stage

- Dosya alımını yönetir
- Dosyayı kullanıcıya özel alana kaydeder
- Metadata (boyut, yol, tür) üretir
- Thumbnail gibi yan servisleri tetikleyebilir

**Implementation:** `backend/services/upap/upload/upload_stage.py`

### 4.3 Process Stage

- Analiz aşamasıdır
- OCR, görüntü analizi, AI servisleri burada çalışır
- Ham dosyadan "anlamlı veri" üretir
- Sonuçları standart bir `process_result` olarak döner

**Implementation:** `backend/services/upap/process/process_stage.py`

**Gerçek Durum:**
- ✅ Process stage çalışıyor (text normalization, fuzzy matching)
- ⚠️ OCR stage optional (env var ile aktif ediliyor, şu an placeholder)
- ⚠️ AI stage optional (env var ile aktif ediliyor, şu an placeholder)
- ✅ `novarchive_gpt_service.py` mevcut ve çalışıyor (OpenAI Vision) ama preview router'da kullanılıyor, upload flow'a bağlı değil

### 4.4 Archive Stage

- İşlenmiş veriyi kanonik arşiv kaydına dönüştürür
- Arşiv kaydı immutable mantıktadır
- Sistem için "gerçek kayıt" bu aşamada oluşur

**Implementation:** `backend/services/upap/archive/archive_stage.py`

### 4.5 Publish Stage

- Arşiv kaydını dış sistemlere hazır hâle getirir
- Pasif/kontrollü çalışır
- Marketplace, Discogs vb. entegrasyonlara açıktır

**Implementation:** `backend/services/upap/publish/publish_stage.py`

**Gerçek Durum:**
- ✅ Publish stage çalışıyor (archive kontrolü yapıyor)
- ⚠️ Marketplace entegrasyonu placeholder (in-memory storage)
- ✅ Pricing service çalışıyor (Discogs API entegre)

---

## 5. Router ve Service Ayrımı

`records_ai`, router–logic ayrımını katı biçimde uygular:

**Router:**
- Sadece HTTP / API sorumluluğu
- Validation
- UPAP engine çağrısı

**Service / Stage:**
- İş mantığı
- Dosya sistemi
- Analiz
- Arşivleme

Bu sayede:

- ✅ API değişse bile iş mantığı bozulmaz
- ✅ Test edilebilirlik artar
- ✅ Cloud / local ortam farkları minimize edilir

---

## 6. Validation ve Güvenilirlik

Sistem, kendi kendini doğrulayan bir **UPAP Validation Engine** içerir.

Bu motor:

- Her aşamanın kontratını kontrol eder
- Runtime davranışı test eder
- Eksik veya hatalı aşamayı raporlar
- Pipeline bütünlüğünü puanlar

**Güncel Durum:**
```
OVERALL PIPELINE SCORE: 100 / 100
```

Bu skor:

- ✅ Tüm aşamaların doğru tanımlandığını
- ✅ Standartlara tam uyum olduğunu
- ✅ Deploy için teknik engel kalmadığını gösterir

**Validation Implementation:** `backend/services/upap/engine/upap_validation.py`

---

## 7. Teknoloji Yığını

- **Dil:** Python 3.11+
- **Framework:** FastAPI
- **ASGI Server:** Uvicorn
- **Mimari:** Stage-based pipeline (UPAP)
- **Database:** PostgreSQL (production) / SQLite (local dev)
- **ORM:** SQLAlchemy
- **Authentication:** JWT + bcrypt
- **Dosya Sistemi:** Local / Cloud uyumlu
- **Image Processing:** Pillow
- **OCR:** OpenAI Vision API (via `novarchive_gpt_service`) - **Mevcut ama upload flow'a bağlı değil**
- **AI Analysis:** OpenAI GPT-4 Vision (via `novarchive_gpt_service`) - **Mevcut ama upload flow'a bağlı değil**
- **Legacy OCR:** Filename-based placeholder (`ocr_engine.py`) - **Kullanılmıyor, deprecated**
- **Validation:** Custom UPAP Validator
- **Encoding Standardı:** UTF-8 (BOM-free)
- **Deployment:** Google Cloud Run

---

## 8. Ölçeklenebilirlik ve Gelecek Planı

`records_ai`:

- ✅ Local Windows ortamında stabil çalışır
- ✅ Docker / Cloud Run uyumludur
- ✅ Küçük dataset'lerle (1–2K kayıt) başlayıp
- ✅ Aşama bazlı yatay ölçeklenmeye uygundur

### Mevcut Durum (v2.0):

**Çalışan Özellikler:**
- ✅ File upload (image/audio)
- ✅ User authentication (JWT + bcrypt, PostgreSQL)
- ✅ Archive storage (PostgreSQL)
- ✅ Preview flow (novarchive_gpt_service entegre)
- ✅ Pricing service (Discogs API - gerçek entegrasyon)
- ✅ Multi-record detection (Sherlock Holmes mode)

**Eksik/Broken Özellikler:**
- ⚠️ Recognition upload flow'a bağlı değil (Phase 1)
- ⚠️ Marketplace API'leri placeholder (Phase 3)
- ⚠️ OCR/AI stages optional ve placeholder (env var ile aktif)

### Planlanan Genişlemeler:

**Phase 1: Recognition Integration (1-2 hafta)**
- Wire `novarchive_gpt_service` into upload flow
- Upload endpoint'ten gerçek recognition data döndür
- Test accuracy with real vinyl images

**Phase 2: Admin Moderation (2-3 hafta)**
- Admin review interface
- Quality control workflow
- Manual correction before archive

**Phase 3: Marketplace Automation (4-6 hafta)**
- Discogs API integration (listing creation)
- eBay API integration
- Etsy API integration
- Cross-platform sync

**Phase 4: Scaling & Monetization (8-12 hafta)**
- Performance optimization
- Caching layer (Redis)
- Background job processing
- Subscription tiers
- Mobile app (React Native)

---

## 9. Mimari Prensipler

`records_ai`, klasik CRUD tabanlı sistemlerden farklı olarak:

- ✅ **Pipeline-first** - İşlemler aşamalı pipeline üzerinden
- ✅ **Contract-driven** - Açık sözleşmeler ve validasyon
- ✅ **Deterministic** - Aynı input → aynı output
- ✅ **Future-proof** - Yeni aşamalar eklenebilir, mevcut kod bozulmaz

### Tasarım Kararları:

1. **Stage Independence:** Her stage bağımsız test edilebilir
2. **Context Passing:** Stage'ler arası veri aktarımı context dict ile
3. **Error Propagation:** Hatalar sessizce yutulmaz, açıkça raporlanır
4. **Backward Compatibility:** Yeni aşamalar eski pipeline'ı bozmaz

---

## 10. Dosya Yapısı

```
backend/
├── api/v1/              # HTTP routers (API layer)
├── services/            # Business logic
│   ├── upap/           # UPAP pipeline stages
│   │   ├── auth/       # AuthStage
│   │   ├── upload/     # UploadStage
│   │   ├── process/    # ProcessStage
│   │   ├── archive/    # ArchiveStage
│   │   └── publish/    # PublishStage
│   └── ...             # Supporting services
├── models/              # SQLAlchemy models
├── db.py               # Database configuration
└── main.py            # FastAPI app entry point

frontend/               # Static HTML/JS frontend
alembic/               # Database migrations
```

---

## 11. API Endpoints

### Production Endpoints:

- `POST /api/v1/upap/upload` - File upload (image/audio) - **Çalışıyor, recognition placeholder**
- `POST /upap/process/preview` - Process file and return preview - **Çalışıyor, novarchive_gpt_service kullanıyor**
- `POST /upap/archive/add` - Archive a preview record - **Çalışıyor**
- `POST /upap/publish` - Publish archived record - **Çalışıyor (pasif)**

### Authentication:

- `POST /auth/register` - User registration
- `POST /auth/login` - Email/password login
- `POST /auth/login/google` - Google OAuth login

### Internal/Diagnostic:

- `POST /upap/upload` - Upload-only (bypasses full pipeline)
- `POST /upap/process` - Process-only (placeholder)
- `POST /upap/archive` - Archive-only
- `POST /upap/publish` - Publish-only

---

## 12. Deployment

### Local Development:

```bash
python -m venv .venv
.venv/Scripts/Activate.ps1  # Windows
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Cloud Run:

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/records-ai-v2
gcloud run deploy records-ai-v2 \
  --image gcr.io/PROJECT_ID/records-ai-v2 \
  --platform managed \
  --region us-central1
```

### Environment Variables:

- `DATABASE_URL` - PostgreSQL connection string (required for production)
- `SECRET_KEY` - JWT secret key (required for production)
- `OPENAI_API_KEY` - OpenAI API key (for recognition)
- `DISCOGS_TOKEN` - Discogs API token (for pricing)
- `UPAP_ENABLE_OCR` - Enable OCR stage (optional)
- `UPAP_ENABLE_AI` - Enable AI stage (optional)

---

## 13. Mevcut Durum ve Sonuç

`records_ai v2`, **pipeline-first**, **contract-driven**, **deterministic** ve **future-proof** bir mimariyle inşa edilmiştir.

**UPAP Pipeline Validation Score: 100/100** - Pipeline mimarisi deploy için hazırdır.

### Gerçek Durum Özeti:

**✅ Çalışan:**
- UPAP pipeline mimarisi (100/100 validation)
- File upload (image/audio)
- User authentication (PostgreSQL + JWT)
- Archive storage
- Preview flow (novarchive_gpt_service entegre)
- Pricing service (Discogs API)

**⚠️ Eksik/Broken:**
- Recognition servisleri upload flow'a bağlı değil (Phase 1)
- Marketplace API'leri placeholder (Phase 3)
- OCR/AI stages optional ve placeholder

**📊 Sistem Durumu:**
- Mimari: %100 uyumlu (UPAP gold standard)
- Fonksiyonellik: %80 tamamlanmış
- Kritik eksik: Recognition wiring (1-2 hafta)

### Next Steps (Öncelik Sırası):

1. **Phase 1 (Kritik):** Wire `novarchive_gpt_service` into upload flow
2. **Phase 2:** Admin moderation interface
3. **Phase 3:** Real marketplace APIs
4. **Phase 4:** Scaling & monetization

**Deploy Readiness:** ✅ Mimari hazır, ⚠️ Recognition entegrasyonu eksik

---

**Documentation:**
- `UPAP_ENGINE_CONTRACT.md` - Engine public interface
- `ARCHITECTURAL_ALIGNMENT_REPORT.md` - Alignment with gold standard
- `PROJECT_ANALYSIS_REPORT.md` - Current state analysis
