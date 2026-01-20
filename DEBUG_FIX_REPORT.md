# Debug Fix Report - Preview Flow

## Root Cause Analysis

### Problem 1: Response Structure Mismatch ✅ FIXED
**Location:** `backend/api/v1/upap_upload_router.py:161-170`

**Issue:**
- Backend returned nested structure: `{ "record": { "artist": "..." }, "file_path": "..." }`
- Frontend expected flat structure: `{ "artist": "...", "file_path": "..." }`
- Frontend accessed `record.artist` but data was in `record.record.artist`

**Fix:**
- Flattened response: Fields now appear at both top level AND nested `record` for compatibility
- Added `full_image_url` and `label_image_url` fields

### Problem 2: Image URL Handling ✅ FIXED
**Location:** `frontend/preview.html:446`

**Issue:**
- Relative image paths not converted to absolute URLs
- Browser couldn't resolve `/storage/temp/...` paths

**Fix:**
- Added absolute URL conversion: `window.location.origin + imageUrl`
- Added fallback for multiple field names: `full_image_url`, `label_image_url`, `thumbnail_url`, `file_path`

### Problem 3: Missing Logging ✅ FIXED
**Location:** All files

**Issue:**
- No logs to trace data flow
- Hard to debug production issues

**Fix:**
- Added `console.log()` in frontend for all data transformations
- Added `logger.info()` in backend for upload processing
- Logs include: incoming data, recognition results, response payload

## Files Changed

### 1. `backend/api/v1/upap_upload_router.py`
**Changes:**
- Added logging import
- Flattened response structure (fields at top level + nested)
- Added `full_image_url` and `label_image_url` fields
- Added comprehensive logging

**Key Code:**
```python
# Flatten to top level
response.update(record_data)
response["full_image_url"] = image_url
response["label_image_url"] = image_url
logger.info(f"[UPLOAD] Response prepared: artist={response.get('artist')}, file_path={image_url}")
```

### 2. `frontend/preview.html`
**Changes:**
- Handle both nested and flat record structures
- Convert relative image URLs to absolute
- Added comprehensive logging
- Support multiple image field names

**Key Code:**
```javascript
const recordData = record.record || record;
const imageUrl = record.full_image_url || record.label_image_url || record.thumbnail_url || ...;
const fullImageUrl = imageUrl.startsWith('http') ? imageUrl : window.location.origin + imageUrl;
console.log('[PREVIEW] Full preview data:', JSON.stringify(previewData, null, 2));
```

### 3. `frontend/upload.html`
**Changes:**
- Added logging for backend response
- Added logging for stored preview data

**Key Code:**
```javascript
console.log('[UPLOAD] Backend response:', data);
console.log('[UPLOAD] Storing preview data:', previewData);
```

## Response Format (Now)

```json
{
  "status": "ok",
  "record_id": "uuid",
  "artist": "Artist Name",          // TOP LEVEL
  "album": "Album Name",            // TOP LEVEL
  "label": "Label Name",            // TOP LEVEL
  "year": "2023",                   // TOP LEVEL
  "catalog_number": "CAT123",       // TOP LEVEL
  "format": "LP",                   // TOP LEVEL
  "confidence": 0.87,               // TOP LEVEL
  "record": {                       // NESTED (backward compat)
    "artist": "Artist Name",
    "album": "Album Name",
    ...
  },
  "file_path": "/storage/temp/user_id/filename.jpg",
  "thumbnail_url": "/storage/temp/user_id/filename.jpg",
  "canonical_image_path": "/storage/temp/user_id/filename.jpg",
  "full_image_url": "/storage/temp/user_id/filename.jpg",
  "label_image_url": "/storage/temp/user_id/filename.jpg"
}
```

## Testing Checklist

- [ ] Upload image via upload.html
- [ ] Check browser console for logs
- [ ] Verify preview.html loads with data
- [ ] Verify images display correctly
- [ ] Verify metadata fields populated (not "-")
- [ ] Verify "Add to Archive" button works
- [ ] Check Cloud Run logs for backend processing

## Expected Console Output

**Frontend (upload.html):**
```
[UPLOAD] Backend response: {status: "ok", artist: "...", ...}
[UPLOAD] Storing preview data: {artist: "...", ...}
```

**Frontend (preview.html):**
```
[PREVIEW] Loaded from localStorage: {artist: "...", ...}
[PREVIEW] Full preview data: {...}
[PREVIEW] displayRecord called with: {...}
[PREVIEW] Image URL: /storage/temp/...
[PREVIEW] Full image URL: https://records-ai-v2-...us-central1.run.app/storage/temp/...
[PREVIEW] Metadata: {artist: "...", album: "...", ...}
```

**Backend (Cloud Run logs):**
```
[UPLOAD] Processing image: storage/temp/user_id/filename.jpg, user_id: ..., record_id: ...
[UPLOAD] Recognition result: artist=..., album=..., confidence=...
[UPLOAD] Response prepared: artist=..., file_path=/storage/temp/...
```

## Verification Steps

1. **Upload Test:**
   - Go to upload.html
   - Upload a vinyl image
   - Open browser console (F12)
   - Should see `[UPLOAD] Backend response:` with populated fields

2. **Preview Test:**
   - After redirect to preview.html
   - Should see `[PREVIEW] Loaded from localStorage:` with same data
   - Should see `[PREVIEW] Image URL:` with correct path
   - Should see `[PREVIEW] Metadata:` with artist, album, etc.
   - Images should display
   - Fields should NOT show "-"

3. **404 Check:**
   - Network tab in browser
   - Should NOT see 404 for image requests
   - Image URL should be absolute (https://...)

4. **Backend Logs:**
   - Cloud Run logs
   - Should see `[UPLOAD] Processing image:` messages
   - Should see `[UPLOAD] Recognition result:` with data
   - Should see `[UPLOAD] Response prepared:` confirmation

## Deployment

Commit and push:
```bash
git add -A
git commit -m "fix: flatten upload response, fix image URLs, add logging"
git push origin main
```

Deploy to Cloud Run:
```bash
gcloud run deploy records-ai-v2 --source . --platform managed --region us-central1
```
