# Fixes Applied - Archive & Image Serving

## Problems Fixed

### 1. 405 Method Not Allowed ✅
**Problem:** Frontend sent JSON but backend expected Form data.

**Fix:**
- Updated `backend/api/v1/upap_archive_add_router.py` to accept both JSON and Form data
- Backend now checks `Content-Type` header and parses accordingly
- JSON body is preferred, Form data is fallback for legacy support

### 2. 404 Image Not Found ✅
**Problem:** Images stored in `storage/` directory were not accessible via HTTP.

**Fix:**
- Added static file mount for `/storage` directory in `backend/main.py`
- Images are now served at `/storage/temp/{user_id}/{filename}`
- Updated upload router to return URL-accessible paths (starting with `/storage/`)

### 3. Wrong API Endpoint ✅
**Problem:** Frontend called `/upap/archive/add` but correct path is `/api/v1/upap/archive/add`.

**Fix:**
- Updated `frontend/preview.html` to use correct endpoint: `/api/v1/upap/archive/add`

### 4. Image Path Handling ✅
**Problem:** File paths were returned as relative paths, not URL-accessible.

**Fix:**
- Updated `backend/api/v1/upap_upload_router.py` to convert file paths to URL paths
- Paths like `storage/temp/...` are now converted to `/storage/temp/...`
- Added `thumbnail_url` and `canonical_image_path` fields to response

### 5. Archive Data Parsing ✅
**Problem:** Archive endpoint didn't handle JSON body correctly.

**Fix:**
- Added proper JSON body parsing with fallback to Form data
- Handles nested `record_data` object
- Extracts `record_id`, `preview_id`, `email` correctly
- Handles multiple field name variations (`file_path`, `canonical_image_path`, `thumbnail_url`)

## Files Changed

1. `backend/api/v1/upap_archive_add_router.py`
   - Added JSON body support
   - Improved error handling
   - Better field name handling

2. `backend/main.py`
   - Added `/storage` static file mount

3. `backend/api/v1/upap_upload_router.py`
   - Fixed image path URLs
   - Added multiple path field names

4. `frontend/preview.html`
   - Fixed API endpoint path

## Testing Checklist

- [ ] Upload image → Should return recognition data
- [ ] Preview page → Should display image correctly
- [ ] Add to archive → Should work with JSON body
- [ ] Image display → Should load from `/storage/` path
- [ ] Archive success → Should redirect to library

## Next Steps

1. Test full flow: upload → preview → archive → library
2. Verify recognition service is working
3. Test with real vinyl images
4. Check image serving in production (Cloud Run)
