# Static Files Serving Solution

## Problem
Frontend tries to load images like `https://records-ai-v2-...run.app/<uuid>.JPEG` but gets 404 because FastAPI doesn't serve static files by default.

## DEV Solution (Temporary)

### Implementation
Added `/files` mount in `backend/main.py` (after line 486):

```python
# DEV ONLY: Mount /files as alias for /storage (temporary solution)
if os.getenv("ENVIRONMENT", "dev").lower() == "dev":
    app.mount("/files", StaticFiles(directory=str(STORAGE_DIR)), name="files")
```

### Folder Structure
```
storage/
├── uploads/
│   └── {user_id}/
│       └── {filename}
├── archive/
│   └── {user_id}/
│       └── {record_id}.jpg
└── temp/
    └── {user_id}/
        └── {record_id}_{filename}
```

### Frontend URL Changes

**Before (broken):**
```javascript
// ❌ This fails with 404
const imageUrl = `/${record_id}.JPEG`;
```

**After (DEV):**
```javascript
// ✅ Use /files path
const imageUrl = `/files/archive/${user_id}/${record_id}.jpg`;
// Or if using API response:
const imageUrl = record.file_path || record.canonical_image_path;
// API returns: /storage/archive/{user_id}/{record_id}.jpg
```

### Files Modified
- `backend/main.py`: Added `/files` mount (DEV only, line ~490)

---

## PRODUCTION Solution (Recommended)

### Architecture

**Current Flow:**
```
Upload → Save to local disk → Return file path → Frontend requests file → 404
```

**Production Flow:**
```
Upload → Save to GCS → Generate signed URL → Return URL → Frontend uses GCS URL directly
```

### Implementation Steps

#### 1. Create GCS Bucket
```bash
gsutil mb -p records-ai -l us-central1 gs://records-ai-v2-uploads
gsutil iam ch allUsers:objectViewer gs://records-ai-v2-uploads  # Public read (or use signed URLs)
```

#### 2. Add GCS Dependencies
```python
# requirements.txt
google-cloud-storage>=2.10.0
```

#### 3. Create GCS Service
```python
# backend/services/gcs_service.py
from google.cloud import storage
import os
from pathlib import Path

class GCSService:
    def __init__(self):
        self.bucket_name = os.getenv("GCS_BUCKET", "records-ai-v2-uploads")
        self.client = storage.Client()
        self.bucket = self.client.bucket(self.bucket_name)
    
    def upload_file(self, file_bytes: bytes, blob_name: str, content_type: str = "image/jpeg") -> str:
        """Upload file to GCS and return public URL."""
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(file_bytes, content_type=content_type)
        blob.make_public()  # Or use signed URLs for security
        return blob.public_url
    
    def get_signed_url(self, blob_name: str, expiration_hours: int = 24) -> str:
        """Generate signed URL (more secure than public)."""
        blob = self.bucket.blob(blob_name)
        return blob.generate_signed_url(expiration=expiration_hours * 3600)
```

#### 4. Update Upload Router
```python
# backend/api/v1/upap_upload_router.py

# After saving file locally:
if os.getenv("ENVIRONMENT") == "production":
    from backend.services.gcs_service import gcs_service
    gcs_url = gcs_service.upload_file(
        file_bytes=content,
        blob_name=f"archive/{current_user.id}/{record_id}.jpg",
        content_type="image/jpeg"
    )
    response["file_path"] = gcs_url
    response["canonical_image_path"] = gcs_url
else:
    # DEV: Use local file path
    response["file_path"] = f"/files/archive/{current_user.id}/{record_id}.jpg"
```

#### 5. Environment Variables
```bash
# Cloud Run env vars
GCS_BUCKET=records-ai-v2-uploads
ENVIRONMENT=production
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json  # Auto-set in Cloud Run
```

### Security Considerations

**Option A: Public Bucket (Simple)**
- Set bucket IAM: `allUsers:objectViewer`
- Files accessible via public URLs
- ⚠️ No access control

**Option B: Signed URLs (Recommended)**
- Keep bucket private
- Generate signed URLs with expiration (24h default)
- ✅ Access control + expiration
- Requires service account with Storage Admin role

**Option C: Cloud CDN (Advanced)**
- Use Cloud CDN in front of GCS
- Better performance + caching
- More complex setup

### Migration Path

1. **Phase 1 (Now)**: Implement DEV `/files` mount
2. **Phase 2**: Add GCS service, test in staging
3. **Phase 3**: Deploy to production with GCS
4. **Phase 4**: Remove local file storage, use GCS only

### Cost Estimate

- **GCS Storage**: ~$0.020/GB/month
- **GCS Operations**: ~$0.05/10k operations
- **Bandwidth**: First 1GB free, then ~$0.12/GB

For 1000 images (avg 2MB each = 2GB):
- Storage: $0.04/month
- Operations: ~$0.01/month
- **Total: ~$0.05/month** (very cheap)

---

## Summary

**DEV (Immediate):**
- ✅ `/files` mount added
- ✅ Frontend should use `/files/archive/{user_id}/{record_id}.jpg`
- ✅ Or use API response `file_path` field

**PROD (Next Phase):**
- Upload to GCS instead of local disk
- Return GCS URLs (public or signed)
- Frontend uses GCS URLs directly
- No FastAPI static file serving needed
