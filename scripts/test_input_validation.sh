#!/bin/bash
# P2: Input Validation Test
# Verifies that invalid input is rejected

set -e

API_BASE="${API_BASE_URL:-http://127.0.0.1:8000}"
AUTH_TOKEN="${AUTH_TOKEN:-}"

if [ -z "$AUTH_TOKEN" ]; then
    echo "ERROR: AUTH_TOKEN not set"
    exit 1
fi

echo "=========================================="
echo "P2: Input Validation Test"
echo "=========================================="

RECORD_ID=$(uuidgen 2>/dev/null || python3 -c "import uuid; print(uuid.uuid4())" 2>/dev/null || echo "test-$(date +%s)")

# Test 1: Empty JSON (should fail)
echo ""
echo "[TEST 1] Empty JSON (should fail)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    "${API_BASE}/api/v1/upap/archive/add" \
    -H "Authorization: Bearer ${AUTH_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "422" ] || [ "$HTTP_CODE" == "400" ]; then
    echo "✅ PASS: Empty JSON rejected (HTTP $HTTP_CODE)"
else
    echo "❌ FAIL: Empty JSON not rejected (HTTP $HTTP_CODE)"
fi

# Test 2: Extremely long string (should fail)
echo ""
echo "[TEST 2] Extremely long string in artist field (should fail)"
LONG_STRING=$(head -c 10000 /dev/zero | tr '\0' 'A')

DATA=$(cat <<EOF
{
  "record_id": "$RECORD_ID",
  "artist": "$LONG_STRING"
}
EOF
)

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    "${API_BASE}/api/v1/upap/archive/add" \
    -H "Authorization: Bearer ${AUTH_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$DATA")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "422" ] || [ "$HTTP_CODE" == "400" ]; then
    echo "✅ PASS: Long string rejected (HTTP $HTTP_CODE)"
else
    echo "⚠️  Expected 422, got $HTTP_CODE"
fi

# Test 3: XSS attempt (should be sanitized, not rejected)
echo ""
echo "[TEST 3] XSS attempt (should be sanitized)"
XSS_DATA=$(cat <<EOF
{
  "record_id": "$(uuidgen 2>/dev/null || echo "xss-test-$(date +%s)")",
  "artist": "<script>alert('XSS')</script>",
  "album": "Test Album"
}
EOF
)

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    "${API_BASE}/api/v1/upap/archive/add" \
    -H "Authorization: Bearer ${AUTH_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$XSS_DATA")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" == "200" ]; then
    # Check if script tags were removed
    if echo "$BODY" | grep -q "<script>" || echo "$BODY" | grep -q "alert"; then
        echo "⚠️  WARNING: Script tags may not be sanitized"
    else
        echo "✅ PASS: XSS attempt handled (script tags sanitized or escaped)"
    fi
else
    echo "ℹ️  Request rejected (HTTP $HTTP_CODE) - validation may be too strict"
fi

# Test 4: Invalid year (should fail or be sanitized)
echo ""
echo "[TEST 4] Invalid year (future year 2099)"
INVALID_YEAR_DATA=$(cat <<EOF
{
  "record_id": "$(uuidgen 2>/dev/null || echo "year-test-$(date +%s)")",
  "year": "2099"
}
EOF
)

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    "${API_BASE}/api/v1/upap/archive/add" \
    -H "Authorization: Bearer ${AUTH_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$INVALID_YEAR_DATA")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "422" ] || [ "$HTTP_CODE" == "400" ]; then
    echo "✅ PASS: Invalid year rejected"
else
    echo "ℹ️  Year validation may allow future years (HTTP $HTTP_CODE)"
fi

echo ""
echo "=========================================="
echo "Test complete"
echo "=========================================="
