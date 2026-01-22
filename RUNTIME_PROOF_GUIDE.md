# Runtime Proof Guide - AI Pipeline Verification

## 🎯 CEO-Level Accountability

Her adımın çalıştığını **KANITLA** doğrula.

## ✅ Runtime Proof Checklist

### 1. Upload Sonrası - Server Console'da Görülmeli

```
[UPLOAD_V2] ⚡ AI PIPELINE TRIGGERED: preview_id=abc123
[UPLOAD_V2] 📋 AI TASK CREATED: preview_id=abc123
[AI_PIPELINE] 🚀 STARTING: preview_id=abc123
```

**Eğer bu loglar YOKSA:**
→ AI pipeline hiç başlamamış
→ `asyncio.create_task()` çalışmıyor

### 2. AI Pipeline Execution - Server Console'da Görülmeli

```
[AI_PIPELINE] 🎯 ENTRY: run_ai_pipeline called with preview_id=abc123
[AI_PIPELINE] 📥 Preview loaded: preview_id=abc123, state=uploaded
[AI_PIPELINE] 🔍 LEVEL_1_START: preview_id=abc123
[AI_PIPELINE] 📝 OCR extracted: preview_id=abc123, text_length=50
[AI_PIPELINE] 💾 Updating DB: preview_id=abc123, confidence=0.65, artist=Beatles
[AI_PIPELINE] ✅ DB UPDATED: preview_id=abc123, state=ai_analyzed, artist=Beatles, album=Abbey Road
[AI_PIPELINE] ✅ COMPLETED: preview_id=abc123, state=ai_analyzed
```

**Eğer bu loglar YOKSA:**
→ AI pipeline başlamış ama çalışmamış
→ Exception olmuş olabilir

### 3. Database Verification

**SQL Query:**
```sql
SELECT 
    preview_id,
    state,
    artist,
    album,
    confidence,
    model_used,
    ai_analyzed_at
FROM preview_records
WHERE preview_id = 'your-preview-id';
```

**Beklenen:**
- `state` = `ai_analyzed`
- `artist` = dolu (null değil)
- `album` = dolu (null değil)
- `ai_analyzed_at` = timestamp var
- `confidence` > 0

**Eğer boşsa:**
→ AI pipeline çalışmamış veya başarısız olmuş

### 4. Pipeline Logs Verification

**Log File:**
```bash
cat logs/pipeline.log | grep "your-preview-id"
```

**Beklenen:**
```json
{"preview_id": "abc123", "step": "LEVEL_1_START", "state": "UPLOADED", ...}
{"preview_id": "abc123", "step": "AI_PIPELINE_COMPLETE", "state": "AI_ANALYZED", ...}
```

**Eğer log yoksa:**
→ `pipeline_logger.log_step()` çağrılmamış

### 5. Debug Endpoint - Runtime Proof

**API Call:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://127.0.0.1:8082/api/v1/upap/debug/preview/abc123/status
```

**Response Kontrol:**
```json
{
  "runtime_proof": {
    "preview_exists": true,
    "state_in_db": "ai_analyzed",
    "ai_analyzed_at": "2024-01-01T12:00:00Z",
    "has_ai_execution_logs": true,
    "log_count": 5,
    "ai_log_count": 3
  },
  "metadata_proof": {
    "artist": "Beatles",
    "album": "Abbey Road",
    "has_metadata": true
  }
}
```

**Eğer `has_ai_execution_logs: false`:**
→ AI pipeline hiç çalışmamış

## 🔍 Troubleshooting

### Loglar Yok
1. Server console'u kontrol et
2. `logger.warning()` ve `print()` çıktılarını ara
3. Exception var mı kontrol et

### Database Boş
1. `preview_records` tablosunu kontrol et
2. `state` field'ı `uploaded` mi kaldı?
3. `ai_analyzed_at` null mu?

### Pipeline Logs Yok
1. `logs/pipeline.log` dosyası var mı?
2. Write permission var mı?
3. `pipeline_logger.log_step()` çağrılıyor mu?

## ✅ Success Criteria

**AI Pipeline çalıştığının kanıtı:**
1. ✅ Server console'da `[AI_PIPELINE] 🚀 STARTING` görünüyor
2. ✅ Server console'da `[AI_PIPELINE] ✅ DB UPDATED` görünüyor
3. ✅ Database'de `state = ai_analyzed`
4. ✅ Database'de `artist` ve `album` dolu
5. ✅ `logs/pipeline.log` dosyasında log var
6. ✅ Debug endpoint `has_ai_execution_logs: true` döndürüyor

**Hepsi ✅ ise:** AI pipeline çalışıyor, kanıt var.

**Herhangi biri ❌ ise:** AI pipeline çalışmıyor, debug et.
