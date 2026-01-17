# Find Actual Error in Logs

## Current Log Status

The log you shared is just an INFO message saying "Starting new instance". This is normal system logging, not the actual error.

## What We Need

We need to find ERROR level logs or application crash logs that show WHY the container failed to start.

## Method 1: Filter for Errors Only

In Cloud Shell, run:

```bash
gcloud logging read \
  "resource.type=\"cloud_run_revision\"
   resource.labels.service_name=\"records-ai-v2\"
   resource.labels.revision_name=\"records-ai-v2-00046-c2h\"
   resource.labels.location=\"us-central1\"
   severity>=ERROR" \
  --limit=50 \
  --project=records-ai
```

## Method 2: Check Application Logs

```bash
gcloud logging read \
  "resource.type=\"cloud_run_revision\"
   resource.labels.service_name=\"records-ai-v2\"
   resource.labels.revision_name=\"records-ai-v2-00046-c2h\"
   resource.labels.location=\"us-central1\"
   (textPayload=~\"Traceback\" OR textPayload=~\"Exception\" OR textPayload=~\"Error\" OR textPayload=~\"Failed\" OR textPayload=~\"ModuleNotFound\" OR textPayload=~\"FileNotFound\" OR textPayload=~\"uvicorn\")" \
  --limit=50 \
  --project=records-ai
```

## Method 3: All Logs for This Revision

```bash
gcloud logging read \
  "resource.type=\"cloud_run_revision\"
   resource.labels.service_name=\"records-ai-v2\"
   resource.labels.revision_name=\"records-ai-v2-00046-c2h\"
   resource.labels.location=\"us-central1\"" \
  --limit=100 \
  --format="table(timestamp,severity,textPayload)" \
  --project=records-ai | grep -i -E "(error|exception|traceback|failed|uvicorn|starting|listening)"
```

## What to Look For

Common error patterns:
- `ModuleNotFoundError: No module named 'xxx'`
- `FileNotFoundError: [Errno 2] No such file or directory`
- `Traceback (most recent call last):`
- `Exception: ...`
- `Error: ...`
- `uvicorn: error: ...`
- `Address already in use`
- `Permission denied`

## Region Note

The failed revision is in `us-central1`, but we deployed to `europe-west1`. 
- Check if you're deploying to the correct region
- Or check the europe-west1 service status

## Quick Check: Compare Regions

```bash
# Check europe-west1 (where we deployed)
gcloud run services describe records-ai-v2 \
  --region=europe-west1 \
  --project=records-ai

# Check us-central1 (where error occurred)
gcloud run services describe records-ai-v2 \
  --region=us-central1 \
  --project=records-ai
```



