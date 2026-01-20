#!/bin/bash
# Verification Script - Runs all security tests
# P0-1, P0-2, P0-3, P2

set -e

API_BASE="${API_BASE_URL:-http://127.0.0.1:8000}"
AUTH_TOKEN="${AUTH_TOKEN:-}"

if [ -z "$AUTH_TOKEN" ]; then
    echo "ERROR: AUTH_TOKEN environment variable is required"
    echo ""
    echo "Usage:"
    echo "  export AUTH_TOKEN='your-jwt-token'"
    echo "  export API_BASE_URL='http://127.0.0.1:8000'  # optional"
    echo "  bash scripts/verify_all.sh"
    exit 1
fi

echo "=========================================="
echo "SECURITY FIXES VERIFICATION"
echo "=========================================="
echo "API Base: $API_BASE"
echo "Auth: ✅ Token provided"
echo ""

PASS_COUNT=0
FAIL_COUNT=0

# Test P0-1: Path Traversal
echo "Running P0-1: Path Traversal Test..."
if bash scripts/test_path_traversal.sh 2>/dev/null; then
    echo "✅ P0-1 PASSED"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "❌ P0-1 FAILED"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi

echo ""

# Test P0-2: MIME Spoofing
echo "Running P0-2: MIME Spoofing Test..."
if bash scripts/test_mime_spoof.sh 2>/dev/null; then
    echo "✅ P0-2 PASSED"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "❌ P0-2 FAILED"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi

echo ""

# Test P0-3: Idempotency
echo "Running P0-3: Idempotency Test..."
if bash scripts/test_idempotency.sh 2>/dev/null; then
    echo "✅ P0-3 PASSED"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "❌ P0-3 FAILED"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi

echo ""

# Test P2: Input Validation
echo "Running P2: Input Validation Test..."
if bash scripts/test_input_validation.sh 2>/dev/null; then
    echo "✅ P2 PASSED"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "❌ P2 FAILED"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi

echo ""
echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo "Passed: $PASS_COUNT/4"
echo "Failed: $FAIL_COUNT/4"
echo ""

if [ "$FAIL_COUNT" -eq 0 ]; then
    echo "✅ ALL TESTS PASSED"
    exit 0
else
    echo "❌ SOME TESTS FAILED"
    exit 1
fi
