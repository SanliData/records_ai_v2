# Upload Pipeline Fix - Summary

## Problem
Backend rejected image uploads with 400 error: "Only audio files allowed... Got: image/jpeg"
Frontend upload.html already sends images (jpeg/png), but backend only accepted audio files.

## Solution
Updated `/api/v1/upap/upload` endpoint to accept both audio and image files with mode-based routing.

## Files Changed

### `backend/api/v1/upap_upload_router.py`

**Changes:**
1. Added `ALLOWED_IMAGE_TYPES` set with image/jpeg, image/jpg, image/png, image/webp, image/heic
2. Renamed `ALLOWED_MIME_TYPES` to `ALLOWED_AUDIO_TYPES` for clarity
3. Combined into `ALLOWED_MIME_TYPES = ALLOWED_AUDIO_TYPES | ALLOWED_IMAGE_TYPES`
4. Updated `validate_mime_type()` to accept both `audio/*` and `image/*`
5. Added mode detection: `cover_recognition` for images, `audio_metadata` for audio
6. Updated response to include `mode`, `content_type`, and `record` structure for image mode
7. Updated error message to mention both audio and image types

## Response Format

### Image Mode (cover_recognition):
```json
{
  "status": "ok",
  "stage": "upload",
  "record_id": "...",
  "filename": "...",
  "email": "...",
  "size_bytes": 12345,
  "timestamp": "...",
  "mode": "cover_recognition",
  "content_type": "image/jpeg",
  "record": {
    "artist": null,
    "album": null,
    "label": null,
    "catalog_number": null,
    "confidence": null
  },
  "message": "Cover image received. Recognition queued or processed."
}
```

### Audio Mode (audio_metadata) - Backward Compatible:
```json
{
  "status": "ok",
  "stage": "upload",
  "record_id": "...",
  "filename": "...",
  "email": "...",
  "size_bytes": 12345,
  "timestamp": "...",
  "mode": "audio_metadata",
  "content_type": "audio/mpeg"
}
```

## Test Commands

### 1. Test Image Upload (should succeed):
```bash
# First, get a token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' | \
  grep -o '"token":"[^"]*' | cut -d'"' -f4)

# Test image upload
curl -X POST http://127.0.0.1:8000/api/v1/upap/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_image.jpg" \
  -F "email=test@example.com"
```

### 2. Test Invalid Type (should fail with 400):
```bash
curl -X POST http://127.0.0.1:8000/api/v1/upap/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.txt" \
  -F "email=test@example.com"
```

### 3. Test Audio Upload (backward compatibility):
```bash
curl -X POST http://127.0.0.1:8000/api/v1/upap/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_audio.mp3" \
  -F "email=test@example.com"
```

## Cloud Run Deploy

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/records-ai-v2
gcloud run deploy records-ai-v2 \
  --image gcr.io/PROJECT_ID/records-ai-v2 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Verification

After deployment, test with:
1. Image upload should return 200 with `mode: "cover_recognition"`
2. Text file upload should return 400 with clear error message
3. Audio upload should return 200 with `mode: "audio_metadata"` (backward compatible)
