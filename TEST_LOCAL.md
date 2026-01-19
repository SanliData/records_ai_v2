# Local Test Guide

## Quick Start

### 1. Activate Virtual Environment

**Windows PowerShell:**
```powershell
cd C:\Users\issan\records_ai_v2
.\.venv\Scripts\Activate.ps1
```

**Windows Git Bash:**
```bash
cd /c/Users/issan/records_ai_v2
source .venv/Scripts/activate
```

### 2. Install Dependencies (if needed)

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables

Create `.env` file in project root:

```env
DATABASE_URL=sqlite:///./records_ai_v2.db
SECRET_KEY=dev-secret-key-change-in-production
OPENAI_API_KEY=your-openai-key-here
DISCOGS_TOKEN=your-discogs-token-here
```

### 4. Initialize Database

```bash
# Run Alembic migrations
alembic upgrade head

# Or create tables directly
python -c "from backend.db import init_db; init_db()"
```

### 5. Start Server

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### 6. Test Endpoints

**Health Check:**
```bash
curl http://127.0.0.1:8000/health
```

**Login:**
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

**Upload (with token):**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/upap/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test_image.jpg" \
  -F "email=test@example.com"
```

## Frontend Testing

1. Open browser: `http://127.0.0.1:8000`
2. Go to `/login.html`
3. Sign in
4. Go to `/upload.html`
5. Upload a test image
6. Check `/preview.html` for results

## Common Issues

### Port Already in Use
```bash
# Find process using port 8000
netstat -ano | findstr :8000
# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Database Locked
- Close any DB browser tools
- Restart server

### Module Not Found
```bash
pip install -r requirements.txt
```

### CORS Errors
- Backend CORS is configured for localhost
- Should work automatically

## Test Checklist

- [ ] Server starts without errors
- [ ] `/health` returns `{"status":"ok"}`
- [ ] `/login.html` loads
- [ ] Can register/login
- [ ] Can upload image
- [ ] Preview shows recognition results
- [ ] Can add to archive
- [ ] Library shows archived records
