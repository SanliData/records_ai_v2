#!/bin/bash
# P0-3: Idempotency Test
# Verifies that duplicate archive requests don't create duplicates

set -e

API_BASE="${API_BASE_URL:-http://127.0.0.1:8000}"
AUTH_TOKEN="${AUTH_TOKEN:-}"

if [ -z "$AUTH_TOKEN" ]; then
    echo "ERROR: AUTH_TOKEN not set"
    echo "Usage: AUTH_TOKEN='your-token' bash scripts/test_idempotency.sh"
    exit 1
fi

echo "=========================================="
echo "P0-3: Idempotency Test"
echo "=========================================="

# Generate a unique record_id
RECORD_ID=$(uuidgen 2>/dev/null || python3 -c "import uuid; print(uuid.uuid4())" 2>/dev/null || echo "test-$(date +%s)")

# Test data
ARCHIVE_DATA=$(cat <<EOF
{
  "record_id": "$RECORD_ID",
  "artist": "Test Artist",
  "album": "Test Album",
  "label": "Test Label",
  "year": "2023",
  "format": "LP"
}
EOF
)

echo ""
echo "Using record_id: $RECORD_ID"
echo ""

# Send 5 identical archive requests
echo "[TEST] Sending 5 identical archive requests..."
SUCCESS_COUNT=0
IDEMPOTENT_COUNT=0

for i in {1..5}; do
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
        "${API_BASE}/api/v1/upap/archive/add" \
        -H "Authorization: Bearer ${AUTH_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "$ARCHIVE_DATA")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" == "200" ]; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        if echo "$BODY" | grep -q "idempotent.*true"; then
            IDEMPOTENT_COUNT=$((IDEMPOTENT_COUNT + 1))
            echo "  Request $i: ✅ Accepted (idempotent)"
        else
            echo "  Request $i: ✅ Accepted (new record)"
        fi
    else
        echo "  Request $i: ❌ Failed (HTTP $HTTP_CODE)"
        echo "  Response: $BODY"
    fi
done

echo ""
echo "Results:"
echo "  Total successful: $SUCCESS_COUNT/5"
echo "  Idempotent responses: $IDEMPOTENT_COUNT"

if [ "$SUCCESS_COUNT" == "5" ] && [ "$IDEMPOTENT_COUNT" -ge "4" ]; then
    echo ""
    echo "✅ PASS: Idempotency working (4+ duplicate requests handled)"
else
    echo ""
    echo "⚠️  Expected all 5 to succeed with 4+ idempotent"
fi

echo ""
echo "=========================================="
echo "Test complete"
echo "=========================================="
