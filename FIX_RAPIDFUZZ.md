# Fix: ModuleNotFoundError - rapidfuzz

## Problem Found

```
ModuleNotFoundError: No module named 'rapidfuzz'
```

**Error Chain:**
1. Container starts
2. Uvicorn tries to load application
3. `backend/main.py` imports `upap_preview_router`
4. Which imports `ProcessStage`
5. Which imports `FuzzyMatcher`
6. `FuzzyMatcher` tries to import `rapidfuzz` → **FAILS**

## Root Cause

The `rapidfuzz` module is imported in:
- `backend/services/upap/process/fuzzy_matcher.py`

But `rapidfuzz` is **NOT** in `requirements.txt`.

## Solution Applied

Added `rapidfuzz>=3.0.0` to `requirements.txt`.

## Next Steps

1. The fix has been applied locally
2. Deploy again with updated requirements.txt:

```bash
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080 \
  --project records-ai
```

## Verification

After deployment, check if there are any other missing dependencies by checking logs again.

## Files Updated

- `requirements.txt` - Added `rapidfuzz>=3.0.0`



