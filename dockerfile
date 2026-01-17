FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for pytesseract and other packages
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

ENV PORT=8080

# Set entrypoint for Cloud Build
ENV GOOGLE_ENTRYPOINT="uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
