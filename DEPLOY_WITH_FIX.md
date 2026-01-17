# Deploy with rapidfuzz Fix

## Problem Found

```
ModuleNotFoundError: No module named 'rapidfuzz'
```

## Fix Applied Locally

Added `rapidfuzz>=3.0.0` to local `requirements.txt`.

## Update Cloud Shell requirements.txt

Before deploying, update requirements.txt in Cloud Shell:

### Option 1: Quick Add (Cloud Shell)

```bash
cd ~/records_ai

# Add rapidfuzz if not already there
grep -q "rapidfuzz" requirements.txt || echo "rapidfuzz>=3.0.0" >> requirements.txt

# Verify
cat requirements.txt
```

### Option 2: Edit File

```bash
cd ~/records_ai
nano requirements.txt
# Add: rapidfuzz>=3.0.0
# Save and exit (Ctrl+X, Y, Enter)
```

### Option 3: Replace Entire File

```bash
cd ~/records_ai
cat > requirements.txt << 'EOF'
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
SQLAlchemy>=2.0.0
pydantic>=2.0.0
python-multipart>=0.0.6
Pillow>=10.0.0
python-dotenv>=1.0.0
jinja2>=3.1.0
openai>=1.0.0
rapidfuzz>=3.0.0
EOF
```

## Deploy After Update

```bash
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080 \
  --project records-ai
```

## Verify

After deployment, check if there are any other missing dependencies by checking logs if deployment fails again.



