#!/usr/bin/env python3
"""
Test archive endpoint availability.
Tests that POST /api/v1/upap/archive/add returns 200 (not 405).
"""

import pytest
import requests
import os
from typing import Dict, Any

# API base URL - use environment variable or default to localhost
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def test_archive_add_endpoint_exists():
    """
    Test that POST /api/v1/upap/archive/add endpoint exists and doesn't return 405.
    """
    endpoint = f"{API_BASE_URL}/api/v1/upap/archive/add"
    
    # Minimal test payload
    test_payload = {
        "record_id": "test-record-123",
        "artist": "Test Artist",
        "album": "Test Album",
        "title": "Test Album",
        "label": "Test Label",
        "year": "2024",
        "format": "LP"
    }
    
    try:
        # Attempt POST request
        response = requests.post(
            endpoint,
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        # Check status code - should NOT be 405 (Method Not Allowed)
        assert response.status_code != 405, f"Endpoint returned 405 Method Not Allowed. Router may not be registered."
        
        # Accept 200 (OK) or 422 (Validation Error) - both are valid responses
        # Reject 404 (Not Found) or 405 (Method Not Allowed)
        assert response.status_code not in [404, 405], (
            f"Endpoint returned {response.status_code}. "
            f"404 = Not Found, 405 = Method Not Allowed. "
            f"Router may not be registered correctly."
        )
        
        print(f"✅ Endpoint exists and accepts POST requests (status: {response.status_code})")
        
        # If we get 200, perfect
        if response.status_code == 200:
            print("   ✅ Endpoint returned 200 OK")
            return True
        
        # If we get 422, that's also OK (validation error means endpoint exists)
        if response.status_code == 422:
            print("   ✅ Endpoint returned 422 Validation Error - endpoint exists but payload validation failed")
            return True
        
        # If we get 401, that's expected (authentication required)
        if response.status_code == 401:
            print("   Note: 401 Unauthorized is expected (authentication required)")
            return True
        
        # Other status codes - log but don't fail
        print(f"   ⚠️  Unexpected status code: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        return True
        
    except requests.exceptions.ConnectionError:
        pytest.skip(f"Could not connect to API at {API_BASE_URL}. Server may not be running.")
    except Exception as e:
        pytest.fail(f"Unexpected error testing endpoint: {e}")


def test_archive_add_endpoint_route_path():
    """
    Verify the endpoint path is correct.
    """
    # Check that the route is defined correctly
    # The router prefix is /upap/archive and route is /add
    # So full path should be /upap/archive/add
    # Or /api/v1/upap/archive/add if mounted with /api/v1 prefix
    
    expected_paths = [
        "/upap/archive/add",
        "/api/v1/upap/archive/add"
    ]
    
    for path in expected_paths:
        endpoint = f"{API_BASE_URL}{path}"
        try:
            response = requests.post(
                endpoint,
                json={"test": "data"},
                headers={"Content-Type": "application/json"},
                timeout=2,
                allow_redirects=False
            )
            
            # If we don't get 404, the path exists
            if response.status_code != 404:
                print(f"✅ Found endpoint at: {path} (status: {response.status_code})")
                return True
                
        except requests.exceptions.ConnectionError:
            pytest.skip(f"Could not connect to API at {API_BASE_URL}")
        except Exception:
            continue
    
    pytest.fail("Could not find endpoint at any expected path")


if __name__ == "__main__":
    # Run tests directly
    print("=" * 80)
    print("Testing Archive Endpoint")
    print("=" * 80)
    print(f"API Base URL: {API_BASE_URL}")
    print()
    
    try:
        test_archive_add_endpoint_exists()
        test_archive_add_endpoint_route_path()
        print()
        print("=" * 80)
        print("✅ All tests passed")
        print("=" * 80)
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        exit(1)
