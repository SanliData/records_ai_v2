# Quick Log Check Commands

## Current Situation

- Revision: `records-ai-v2-00046-c2h`
- Region: `us-central1` (NOTE: We deployed to `europe-west1`!)
- Status: Failed to start

## Check Error Logs

### In Cloud Shell, run:

```bash
# Check for ERROR level logs
gcloud logging read \
  "resource.type=\"cloud_run_revision\"
   resource.labels.service_name=\"records-ai-v2\"
   resource.labels.revision_name=\"records-ai-v2-00046-c2h\"
   resource.labels.location=\"us-central1\"
   severity>=ERROR" \
  --limit=20 \
  --format="table(timestamp,severity,textPayload)" \
  --project=records-ai
```

### Check Application Startup Logs

```bash
# Look for uvicorn, errors, tracebacks
gcloud logging read \
  "resource.type=\"cloud_run_revision\"
   resource.labels.service_name=\"records-ai-v2\"
   resource.labels.revision_name=\"records-ai-v2-00046-c2h\"
   resource.labels.location=\"us-central1\"
   (textPayload=~\"uvicorn\" OR textPayload=~\"Error\" OR textPayload=~\"Traceback\" OR textPayload=~\"Exception\" OR textPayload=~\"ModuleNotFound\")" \
  --limit=30 \
  --format="table(timestamp,severity,textPayload)" \
  --project=records-ai
```

### Check All Logs

```bash
# All logs for this revision
gcloud logging read \
  "resource.type=\"cloud_run_revision\"
   resource.labels.service_name=\"records-ai-v2\"
   resource.labels.revision_name=\"records-ai-v2-00046-c2h\"
   resource.labels.location=\"us-central1\"" \
  --limit=50 \
  --format="table(timestamp,severity,textPayload)" \
  --project=records-ai
```

## Important Note

**Region Mismatch:**
- Failed revision is in `us-central1`
- We deployed to `europe-west1`
- These are different services/regions!

Check which region you're actually deploying to.



