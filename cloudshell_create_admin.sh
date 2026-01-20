#!/bin/bash
# Cloud Shell script to create admin user in Cloud Run PostgreSQL
# Run in Google Cloud Shell

set -e

echo "=========================================="
echo "Create Admin User - Cloud Run Database"
echo "=========================================="
echo ""

# Get project ID from gcloud
PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "records-ai")
echo "Project ID: $PROJECT_ID"
echo ""

# Set default values
EMAIL="${1:-ednovitsky@novitskyarchive.com}"
PASSWORD="${2:-}"
BASE_URL="${3:-https://records-ai-v2-969278596906.us-central1.run.app}"

# Prompt for password if not provided
if [ -z "$PASSWORD" ]; then
    echo -n "Enter password for $EMAIL: "
    read -s PASSWORD
    echo ""
fi

echo "Email: $EMAIL"
echo "Password: ${PASSWORD:0:3}***"
echo "Base URL: $BASE_URL"
echo ""

# Check if gcloud is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "ERROR: Not authenticated. Please run: gcloud auth login"
    exit 1
fi

echo "Step 1: Getting identity token for authentication..."
IDENTITY_TOKEN=$(gcloud auth print-identity-token)

if [ -z "$IDENTITY_TOKEN" ]; then
    echo "ERROR: Failed to get identity token"
    exit 1
fi

echo "[OK] Identity token obtained"
echo ""

# Try to login first to check if user exists
echo "Step 2: Checking if user exists..."
LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

HTTP_CODE=$(echo "$LOGIN_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$LOGIN_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" == "200" ]; then
    echo "[OK] User already exists and can login"
    TOKEN=$(echo "$RESPONSE_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])" 2>/dev/null || echo "")
    if [ -n "$TOKEN" ]; then
        echo "[OK] Token obtained: ${TOKEN:0:50}..."
        echo "$TOKEN" > .admin_token.txt
        echo "[OK] Token saved to .admin_token.txt"
        exit 0
    fi
elif [ "$HTTP_CODE" == "401" ]; then
    echo "[INFO] User does not exist or password is incorrect. Need to create user."
else
    echo "[WARN] Unexpected response: HTTP $HTTP_CODE"
    echo "Response: $RESPONSE_BODY"
fi

echo ""

# If user doesn't exist, we need to bootstrap
# But we need an admin token first. Try to use identity token to call bootstrap endpoint
echo "Step 3: Attempting to bootstrap user via /admin/bootstrap-user..."

BOOTSTRAP_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/admin/bootstrap-user" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $IDENTITY_TOKEN" \
    -d "{\"email\":\"$EMAIL\",\"is_admin\":true}")

BOOTSTRAP_HTTP_CODE=$(echo "$BOOTSTRAP_RESPONSE" | tail -n1)
BOOTSTRAP_BODY=$(echo "$BOOTSTRAP_RESPONSE" | sed '$d')

if [ "$BOOTSTRAP_HTTP_CODE" == "200" ]; then
    echo "[OK] User bootstrapped successfully"
    echo "$BOOTSTRAP_BODY" | python3 -m json.tool 2>/dev/null || echo "$BOOTSTRAP_BODY"
    echo ""
    
    # Now try to login with password
    echo "Step 4: Logging in with password..."
    LOGIN_RESPONSE2=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
    
    HTTP_CODE2=$(echo "$LOGIN_RESPONSE2" | tail -n1)
    RESPONSE_BODY2=$(echo "$LOGIN_RESPONSE2" | sed '$d')
    
    if [ "$HTTP_CODE2" == "200" ]; then
        TOKEN=$(echo "$RESPONSE_BODY2" | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])" 2>/dev/null || echo "")
        if [ -n "$TOKEN" ]; then
            echo "[OK] Login successful"
            echo "[OK] Token obtained: ${TOKEN:0:50}..."
            echo "$TOKEN" > .admin_token.txt
            echo "[OK] Token saved to .admin_token.txt"
            echo ""
            echo "=========================================="
            echo "SUCCESS: Admin user ready"
            echo "=========================================="
            exit 0
        fi
    else
        echo "[WARN] Login failed after bootstrap: HTTP $HTTP_CODE2"
        echo "Note: User created but password may need to be set separately"
    fi
elif [ "$BOOTSTRAP_HTTP_CODE" == "401" ] || [ "$BOOTSTRAP_HTTP_CODE" == "403" ]; then
    echo "[ERROR] Bootstrap endpoint requires admin authentication"
    echo "You need to:"
    echo "  1. Get an admin token first (from another admin user)"
    echo "  2. Or create the user manually in the database"
    exit 1
else
    echo "[ERROR] Bootstrap failed: HTTP $BOOTSTRAP_HTTP_CODE"
    echo "Response: $BOOTSTRAP_BODY"
    exit 1
fi
