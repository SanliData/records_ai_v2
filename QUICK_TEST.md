# Quick Local Test

## One-Line Start (PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1; uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

## Test Endpoints

### 1. Health Check
```bash
curl http://127.0.0.1:8000/health
```

### 2. Register User
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

### 3. Login
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

Save the token from response.

### 4. Upload Image (with token)
```bash
curl -X POST http://127.0.0.1:8000/api/v1/upap/upload \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@test_image.jpg" \
  -F "email=test@example.com"
```

### 5. Add to Archive
```bash
curl -X POST http://127.0.0.1:8000/upap/archive/add \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "record_id": "test-123",
    "email": "test@example.com",
    "record_data": "{\"artist\":\"Test\",\"album\":\"Test Album\"}"
  }'
```

## Browser Test

1. Open: http://127.0.0.1:8000
2. Go to: http://127.0.0.1:8000/login.html
3. Register/Login
4. Go to: http://127.0.0.1:8000/upload.html
5. Upload test image
6. Check preview and archive

## Expected Results

✅ Server starts on port 8000  
✅ Health endpoint returns `{"status":"ok"}`  
✅ Can register/login  
✅ Can upload images  
✅ Recognition works (if OPENAI_API_KEY set)  
✅ Can add to archive  
✅ No CORS errors (same origin)
