#!/bin/bash

echo "=== Testing Auth Endpoints ==="
echo ""

EMAIL="test$(date +%s)@example.com"
PASSWORD="test123"

echo "1. Register new user ($EMAIL):"
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}"
echo ""
echo ""

echo "2. Login with email/password:"
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" | grep -o '"token":"[^"]*' | cut -d'"' -f4)
echo "Token received: ${TOKEN:0:50}..."
echo ""

echo "3. Test wrong password (should fail):"
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"wrong\"}"
echo ""
echo ""

echo "4. Health check:"
curl -X GET http://127.0.0.1:8000/health
echo ""
echo ""
