#!/usr/bin/env python3
"""
Test bootstrap flow: whoami → bootstrap → whoami
Verifies endpoints exist and bootstrap flow works.
"""

import os
import requests
import base64
import json

API = os.getenv("API_BASE_URL", "http://127.0.0.1:8001")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")


def headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_whoami_exists():
    """Test that /auth/whoami endpoint exists (not 404)."""
    r = requests.get(f"{API}/auth/whoami")
    assert r.status_code != 404, "whoami endpoint NOT mounted (404)"
    print(f"✅ /auth/whoami exists (status: {r.status_code})")


def test_bootstrap_exists():
    """Test that /admin/bootstrap-user endpoint exists (not 404/405)."""
    r = requests.post(f"{API}/admin/bootstrap-user")
    assert r.status_code not in (404, 405), f"bootstrap endpoint NOT mounted (status: {r.status_code})"
    print(f"✅ /admin/bootstrap-user exists (status: {r.status_code})")


def test_bootstrap_flow():
    """Test complete bootstrap flow: whoami → bootstrap → whoami."""
    assert AUTH_TOKEN, "AUTH_TOKEN not set"
    assert ADMIN_TOKEN, "ADMIN_TOKEN not set"

    # 1) whoami
    print("\nStep 1: Testing /auth/whoami...")
    r = requests.get(f"{API}/auth/whoami", headers=headers(AUTH_TOKEN))

    if r.status_code == 200:
        print("✅ User already exists:", r.json())
        return

    assert r.status_code == 401, f"Expected 401, got {r.status_code}: {r.text}"
    body = r.json()
    print(f"   Status: {r.status_code}")
    print(f"   Response: {body}")
    
    # Check for user_not_found (may be in detail or error_type)
    detail = body.get("detail", "")
    if "user not found" in detail.lower() or "bootstrap" in detail.lower():
        print("   ✅ User not found (expected)")
    else:
        print(f"   ⚠️  Unexpected detail: {detail}")

    # 2) decode email from jwt (no verify)
    print("\nStep 2: Extracting email from AUTH_TOKEN...")
    payload = AUTH_TOKEN.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    email = json.loads(base64.urlsafe_b64decode(payload))["email"]
    print(f"   Email: {email}")

    # 3) bootstrap user
    print("\nStep 3: Bootstrapping user via /admin/bootstrap-user...")
    rb = requests.post(
        f"{API}/admin/bootstrap-user",
        headers=headers(ADMIN_TOKEN),
        json={"email": email, "is_admin": False}
    )

    assert rb.status_code == 200, f"Bootstrap failed: {rb.status_code} - {rb.text}"
    bootstrap_result = rb.json()
    print(f"   ✅ Bootstrap successful: {bootstrap_result}")

    # 4) retry whoami
    print("\nStep 4: Retrying /auth/whoami after bootstrap...")
    r2 = requests.get(f"{API}/auth/whoami", headers=headers(AUTH_TOKEN))
    assert r2.status_code == 200, f"Whoami failed after bootstrap: {r2.status_code} - {r2.text}"
    whoami_result = r2.json()
    print(f"   ✅ Whoami after bootstrap: {whoami_result}")
    print("\n✅ Bootstrap flow completed successfully!")


if __name__ == "__main__":
    print("=" * 70)
    print("Bootstrap Flow Test")
    print("=" * 70)
    print(f"API: {API}")
    print(f"AUTH_TOKEN: {'Set' if AUTH_TOKEN else 'Not set'}")
    print(f"ADMIN_TOKEN: {'Set' if ADMIN_TOKEN else 'Not set'}")
    print("=" * 70)
    print()
    
    try:
        # Test 1: Endpoints exist
        print("Test 1: Verifying endpoints exist...")
        test_whoami_exists()
        test_bootstrap_exists()
        print()
        
        # Test 2: Bootstrap flow (if tokens available)
        if AUTH_TOKEN and ADMIN_TOKEN:
            print("Test 2: Testing bootstrap flow...")
            test_bootstrap_flow()
        else:
            print("⚠️  Skipping bootstrap flow test (tokens not set)")
            print("   Set AUTH_TOKEN and ADMIN_TOKEN to test full flow")
        
        print()
        print("=" * 70)
        print("✅ All tests passed!")
        print("=" * 70)
        
    except AssertionError as e:
        print()
        print("=" * 70)
        print(f"❌ Test failed: {e}")
        print("=" * 70)
        exit(1)
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 70)
        exit(1)
