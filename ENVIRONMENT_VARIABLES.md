# Environment Variables - records_ai_v2

## Required Configuration

All secrets must be set via Cloud Run environment variables or Secret Manager.

---

## Core Configuration

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `DATABASE_URL` | No | Database connection string | `sqlite:///./records_ai_v2.db` |

---

## Service-Specific Secrets

### ChatGPT App Integration
| Variable | Required | Description |
|----------|----------|-------------|
| `SERVICE_TOKEN` | Conditional | Bearer token for ChatGPT App endpoints (`/api/routes/*`) |

**Note**: Required only if ChatGPT App integration is enabled.

---

### External APIs
| Variable | Required | Description |
|----------|----------|-------------|
| `DISCOGS_TOKEN` | Conditional | Discogs API token for vinyl pricing |
| `OPENAI_API_KEY` | Conditional | OpenAI API key for AI/OCR features |

**Note**: These are optional. Services will fail gracefully if not set.

---

### OAuth (Google Sign-In)
| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_CLIENT_ID` | No | Google OAuth Client ID (currently in frontend HTML) |

**Note**: Currently hardcoded in `frontend/login.html`. Will be migrated to env var.

---

## UPAP Pipeline Flags

| Variable | Required | Description |
|----------|----------|-------------|
| `UPAP_ENABLE_OCR` | No | Enable OCR stage (`"true"` to enable) |
| `UPAP_ENABLE_AI` | No | Enable AI stage (`"true"` to enable) |

---

## Cloud Run Setup

### Using Environment Variables (Direct)

```bash
gcloud run services update records-ai-v2 \
    --set-env-vars "DISCOGS_TOKEN=your_token,SERVICE_TOKEN=your_service_token" \
    --region us-central1
```

### Using Secret Manager (Recommended)

1. Create secrets:
```bash
echo -n "your_discogs_token" | gcloud secrets create discogs-token --data-file=-
echo -n "your_service_token" | gcloud secrets create service-token --data-file=-
```

2. Grant access:
```bash
gcloud secrets add-iam-policy-binding discogs-token \
    --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

3. Mount secrets in Cloud Run:
```bash
gcloud run services update records-ai-v2 \
    --update-secrets "DISCOGS_TOKEN=discogs-token:latest,SERVICE_TOKEN=service-token:latest" \
    --region us-central1
```

---

## Validation

At startup, the application validates required secrets. If any required secret is missing, the service will fail to start with a clear error message.

---

## Migration Notes

### Before (Hardcoded - REMOVED)
- `DISCOGS_TOKEN` had fallback: `"LSZAwZzoglUrbLSkoyFijkxGqQfZ1RKMjyS6a"` ❌
- `SERVICE_TOKEN` was hardcoded: `"recordsai-chatgpt-app-token"` ❌

### After (Environment Variables - CURRENT)
- `DISCOGS_TOKEN` must be set via env var ✅
- `SERVICE_TOKEN` must be set via env var ✅

---

## Security Notes

1. Never commit secrets to Git (already excluded via `.gitignore`)
2. Use Secret Manager for production
3. Rotate secrets regularly
4. Monitor secret access via Cloud Audit Logs
