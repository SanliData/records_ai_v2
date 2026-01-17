#!/bin/bash
# HIZLI DEPLOY - Cloud Shell'de Copy-Paste edin

cd ~/records_ai_v2 2>/dev/null || cd ~ || pwd

# main.py oluştur
cat > main.py << 'EOF'
"""
Root entrypoint wrapper for Cloud Run buildpacks.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from backend.main import app
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
EOF

# Procfile oluştur
echo "web: uvicorn backend.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# runtime.txt oluştur
echo "python-3.11" > runtime.txt

# Deploy
gcloud config set project records-ai && \
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080



