# Cloud Shell'de direkt bu komutları çalıştırın (Copy-Paste)

# 1. Dosyaların olduğu dizine gidin
cd ~/records_ai_v2 2>/dev/null || {
    echo "records_ai_v2 dizini bulunamadı. Lütfen dosyaların olduğu dizine gidin:"
    echo "  cd ~/dizin_adi"
    exit 1
}

# 2. main.py oluştur
cat > main.py << 'EOF'
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from backend.main import app
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
EOF

# 3. Procfile oluştur
echo "web: uvicorn backend.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# 4. runtime.txt oluştur
echo "python-3.11" > runtime.txt

# 5. Deploy
gcloud config set project records-ai && \
gcloud run deploy records-ai-v2 \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080



