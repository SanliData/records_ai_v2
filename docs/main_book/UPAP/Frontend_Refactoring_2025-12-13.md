# Frontend Refactoring - December 2025
Design Decision Record (DDR-UPAP-002)

**Status:** Completed  
**Date:** 2025-12-13  
**Related:** DDR-UPAP-001 (Archive Stage Lock)

---

## Overview

Complete frontend refactoring to support:
1. Anonymous access for exploration (Upload + Process)
2. Authentication gate at Archive stage
3. UPAP pipeline compliance
4. Consistent navigation and user experience

---

## Pages Created/Updated

### 1. index.html (NEW)
**Purpose:** Home page with explore-first design

**Features:**
- UPAP pipeline explanation
- Anonymous access information
- Clear call-to-action buttons
- Navigation header/footer

**Key Messages:**
- "No account required" for exploration
- "Sign in required" only for archive/publish

### 2. upload.html (UPDATED)
**Purpose:** Upload and analyze records

**Changes:**
- ❌ Removed: Email input field
- ✅ Added: Anonymous upload support
- ✅ Updated: Endpoint to `/upap/process/process/preview`
- ✅ Added: "No account required" messaging
- ✅ Added: Navigation header/footer

**Flow:**
1. User selects file
2. Uploads to UPAP preview endpoint
3. Receives analysis results
4. Can view results or save to archive (requires auth)

### 3. results.html (NEW)
**Purpose:** Display analysis results

**Features:**
- Shows preview record data
- Displays metadata (artist, album, label, year, etc.)
- OCR text display
- Archive save link (requires auth)
- Raw data view (collapsible)

**Authentication:**
- View: Anonymous allowed
- Save to Archive: Authentication required

### 4. archive-save.html (NEW)
**Purpose:** Save records to personal archive

**Features:**
- Authentication check
- Record preview
- UPAP Archive stage execution
- Success/error handling
- Redirect to library on success

**Authentication:**
- ✅ Required (redirects to login if not authenticated)

### 5. login.html (UPDATED)
**Purpose:** Sign in / Sign up

**Changes:**
- ✅ Added: Navigation header/footer
- ✅ Added: GPT ownership footer
- ✅ Updated: API base URL (dynamic)
- ✅ Added: Return URL support

---

## UPAP Compliance

### Endpoints Used

| Page | Endpoint | Stage | Auth |
|------|----------|-------|------|
| upload.html | `/upap/process/process/preview` | Upload + Process | No |
| results.html | (displays preview data) | - | No |
| archive-save.html | `/upap/archive/add` | Archive | Yes |
| (future) | `/upap/publish` | Publish | Yes |

### Pipeline Flow

```
Anonymous User:
  Upload → Process → [View Results] → [Sign In] → Archive → Publish

Authenticated User:
  Upload → Process → Archive → Publish
```

---

## Authentication Model

### Tier 1: Anonymous (No Account Required)
- ✅ Access homepage
- ✅ Upload record images
- ✅ View preliminary results
- ✅ Navigate between steps
- ❌ Save to archive
- ❌ Publish records

### Tier 2: Authenticated (Sign In Required)
- ✅ All anonymous features
- ✅ Save records to archive
- ✅ View personal archives
- ✅ Edit metadata
- ✅ Publish records

---

## Navigation Structure

All pages include:

**Header:**
- RECORDS_AI logo/title
- Home link
- Upload & Analyze link
- Sign In / Sign Up link

**Footer:**
- Records_AI ownership information
- GPT guidance interface notice
- System prompt reference

---

## API Base URL Configuration

Dynamic API base URL based on environment:

```javascript
const apiBase = window.location.hostname === 'localhost' || 
                window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000'
    : 'https://api.zyagrolia.com';
```

**Future:** Will use environment variable for UPAP service URL when separated.

---

## User Experience Improvements

### Before
- ❌ Email required for upload
- ❌ Forced authentication
- ❌ Unclear pipeline explanation
- ❌ No home page

### After
- ✅ Anonymous exploration
- ✅ Clear authentication gates
- ✅ UPAP pipeline explanation
- ✅ Consistent navigation
- ✅ Professional design

---

## Technical Details

### Session Storage
- Preview results stored in `sessionStorage`
- Key format: `result_{record_id}`
- Used to pass data between pages

### Error Handling
- Clear error messages
- Loading states
- Success confirmations
- Graceful fallbacks

### Responsive Design
- Mobile-friendly layout
- Flexible grid systems
- Media queries for small screens

---

## Testing Checklist

- [x] Anonymous upload works
- [x] Results page displays correctly
- [x] Archive save requires authentication
- [x] Navigation works across all pages
- [x] API endpoints correct
- [x] Error handling works
- [x] Mobile responsive

---

## Migration Notes

### Production Deployment
1. Deploy updated frontend files
2. Clear browser cache (hard refresh)
3. Restart server (if needed)
4. Test anonymous flow
5. Test authenticated flow

### Backward Compatibility
- Legacy endpoints still exist (not broken)
- Old upload.html can be deprecated
- No breaking API changes

---

## Future Enhancements

1. **UPAP Service Separation:**
   - Environment variable for UPAP service URL
   - Service discovery
   - Health checks

2. **Enhanced Preview:**
   - Image thumbnails
   - Better metadata display
   - Comparison view

3. **Authentication:**
   - Social login options
   - Token refresh
   - Session management

---

## References

- `frontend/index.html` - Home page
- `frontend/upload.html` - Upload page
- `frontend/results.html` - Results page
- `frontend/archive-save.html` - Archive save page
- `UPAP_COMPATIBILITY_NOTES.md` - UPAP compliance
- `DEPLOYMENT_STATUS.md` - Deployment information



