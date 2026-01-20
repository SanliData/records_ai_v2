#!/bin/bash
# P0-1: Path Traversal Test
# Verifies that path traversal attempts are blocked

set -e

API_BASE="${API_BASE_URL:-http://127.0.0.1:8000}"
AUTH_TOKEN="${AUTH_TOKEN:-}"

if [ -z "$AUTH_TOKEN" ]; then
    echo "ERROR: AUTH_TOKEN not set"
    echo "Usage: AUTH_TOKEN='your-token' bash scripts/test_path_traversal.sh"
    exit 1
fi

echo "=========================================="
echo "P0-1: Path Traversal Test"
echo "=========================================="

# Create a test image file
TEST_FILE="test.jpg"
echo -e "\xFF\xD8\xFF\xE0" > "$TEST_FILE"
dd if=/dev/zero of="$TEST_FILE" bs=1024 count=10 2>/dev/null || head -c 10240 /dev/zero > "$TEST_FILE"

# Test 1: Normal filename (should succeed)
echo ""
echo "[TEST 1] Normal filename (should succeed)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    "${API_BASE}/api/v1/upap/upload" \
    -H "Authorization: Bearer ${AUTH_TOKEN}" \
    -F "file=@${TEST_FILE};filename=test.jpg" \
    -F "email=test@example.com")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" == "200" ]; then
    echo "✅ PASS: Normal filename accepted"
else
    echo "❌ FAIL: Normal filename rejected (HTTP $HTTP_CODE)"
    echo "Response: $BODY"
    exit 1
fi

# Test 2: Path traversal attempt (should fail)
echo ""
echo "[TEST 2] Path traversal attempt (should fail)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    "${API_BASE}/api/v1/upap/upload" \
    -H "Authorization: Bearer ${AUTH_TOKEN}" \
    -F "file=@${TEST_FILE};filename=../../../etc/passwd" \
    -F "email=test@example.com")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" == "400" ]; then
    echo "✅ PASS: Path traversal blocked (HTTP 400)"
else
    echo "❌ FAIL: Path traversal not blocked (HTTP $HTTP_CODE)"
    echo "Response: $BODY"
    exit 1
fi

# Test 3: Nested path traversal (should fail)
echo ""
echo "[TEST 3] Nested path traversal (should fail)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    "${API_BASE}/api/v1/upap/upload" \
    -H "Authorization: Bearer ${AUTH_TOKEN}" \
    -F "file=@${TEST_FILE};filename=../../../../root/.ssh/id_rsa" \
    -F "email=test@example.com")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" == "400" ]; then
    echo "✅ PASS: Nested path traversal blocked"
else
    echo "❌ FAIL: Nested path traversal not blocked (HTTP $HTTP_CODE)"
    exit 1
fi

# Cleanup
rm -f "$TEST_FILE"

echo ""
echo "=========================================="
echo "✅ ALL TESTS PASSED"
echo "=========================================="
