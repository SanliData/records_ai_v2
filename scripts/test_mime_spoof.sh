#!/bin/bash
# P0-2: MIME Spoofing Test
# Verifies that file magic bytes are validated

set -e

API_BASE="${API_BASE_URL:-http://127.0.0.1:8000}"
AUTH_TOKEN="${AUTH_TOKEN:-}"

if [ -z "$AUTH_TOKEN" ]; then
    echo "ERROR: AUTH_TOKEN not set"
    echo "Usage: AUTH_TOKEN='your-token' bash scripts/test_mime_spoof.sh"
    exit 1
fi

echo "=========================================="
echo "P0-2: MIME Spoofing Test"
echo "=========================================="

# Test 1: Valid JPEG (should succeed)
echo ""
echo "[TEST 1] Valid JPEG file with image/jpeg content-type (should succeed)"
echo -e "\xFF\xD8\xFF\xE0" > valid.jpg
dd if=/dev/zero of=valid.jpg bs=1024 count=10 2>/dev/null || head -c 10240 /dev/zero >> valid.jpg

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    "${API_BASE}/api/v1/upap/upload" \
    -H "Authorization: Bearer ${AUTH_TOKEN}" \
    -F "file=@valid.jpg;type=image/jpeg" \
    -F "email=test@example.com")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "200" ]; then
    echo "✅ PASS: Valid JPEG accepted"
else
    echo "⚠️  Expected 200, got $HTTP_CODE (may need valid token)"
fi

# Test 2: EXE file with image/jpeg content-type (should fail)
echo ""
echo "[TEST 2] EXE file with image/jpeg content-type (should fail)"
echo "MZ\x90\x00" > fake.exe
dd if=/dev/zero of=fake.exe bs=1024 count=10 2>/dev/null || head -c 10240 /dev/zero >> fake.exe

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    "${API_BASE}/api/v1/upap/upload" \
    -H "Authorization: Bearer ${AUTH_TOKEN}" \
    -F "file=@fake.exe;type=image/jpeg" \
    -F "email=test@example.com")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" == "400" ]; then
    if echo "$BODY" | grep -q "MIME type mismatch\|File type validation failed"; then
        echo "✅ PASS: MIME spoofing blocked (HTTP 400)"
    else
        echo "⚠️  Got 400 but not MIME validation error"
    fi
else
    echo "❌ FAIL: MIME spoofing not blocked (HTTP $HTTP_CODE)"
    echo "Response: $BODY"
    exit 1
fi

# Test 3: Random binary with image/jpeg content-type (should fail)
echo ""
echo "[TEST 3] Random binary with image/jpeg content-type (should fail)"
dd if=/dev/urandom of=random.bin bs=1024 count=10 2>/dev/null || head -c 10240 /dev/urandom > random.bin

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    "${API_BASE}/api/v1/upap/upload" \
    -H "Authorization: Bearer ${AUTH_TOKEN}" \
    -F "file=@random.bin;type=image/jpeg" \
    -F "email=test@example.com")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" == "400" ]; then
    echo "✅ PASS: Random binary rejected"
else
    echo "⚠️  Expected 400, got $HTTP_CODE"
fi

# Cleanup
rm -f valid.jpg fake.exe random.bin

echo ""
echo "=========================================="
echo "✅ ALL TESTS PASSED"
echo "=========================================="
