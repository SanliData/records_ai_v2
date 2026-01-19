#!/bin/bash

echo "=== Testing Upload Endpoint Fix ==="
echo ""

API_BASE="http://127.0.0.1:8000"
TOKEN="test_token_here"  # Replace with actual token from login

echo "1. Test image/jpeg upload (should succeed):"
curl -X POST "${API_BASE}/api/v1/upap/upload" \
  -H "Authorization: Bearer ${TOKEN}" \
  -F "file=@test_image.jpg" \
  -F "email=test@example.com" \
  2>&1 | head -20
echo ""
echo ""

echo "2. Test text/plain upload (should fail with 400):"
curl -X POST "${API_BASE}/api/v1/upap/upload" \
  -H "Authorization: Bearer ${TOKEN}" \
  -F "file=@test.txt" \
  -F "email=test@example.com" \
  2>&1 | head -20
echo ""
echo ""

echo "3. Test audio/mpeg upload (should succeed, backward compatible):"
curl -X POST "${API_BASE}/api/v1/upap/upload" \
  -H "Authorization: Bearer ${TOKEN}" \
  -F "file=@test_audio.mp3" \
  -F "email=test@example.com" \
  2>&1 | head -20
echo ""
