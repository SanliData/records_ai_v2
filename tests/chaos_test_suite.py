#!/usr/bin/env python3
"""
CHAOS ENGINEERING TEST SUITE
Records_AI_V2 Destruction Tests

This suite attempts to BREAK the system under extreme conditions.
"""

import asyncio
import aiohttp
import json
import os
import random
import string
import time
import uuid
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
# BASE_URL = os.getenv("API_BASE_URL", "https://records-ai-v2-969278596906.us-central1.run.app")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "")
TEST_EMAIL = os.getenv("TEST_EMAIL", "test@example.com")

RESULTS = []


def log_result(phase: str, test: str, attack_vector: str, expected: str, actual: str, root_cause: str, fix: str, severity: int):
    """Log test result."""
    result = {
        "phase": phase,
        "test": test,
        "attack_vector": attack_vector,
        "expected": expected,
        "actual": actual,
        "root_cause": root_cause,
        "fix": fix,
        "severity": severity,
        "timestamp": time.time()
    }
    RESULTS.append(result)
    print(f"\n[{phase}] {test}")
    print(f"  Attack: {attack_vector}")
    print(f"  Expected: {expected}")
    print(f"  Actual: {actual}")
    print(f"  Severity: {severity}/10")
    if severity >= 7:
        print(f"  ⚠️  CRITICAL: {root_cause}")
        print(f"  Fix: {fix}")


# ============================================================
# PHASE 1: API TORTURE
# ============================================================

def generate_test_file(size_mb: float, content_type: str = "image/jpeg", corrupted: bool = False) -> bytes:
    """Generate test file."""
    size = int(size_mb * 1024 * 1024)
    if corrupted:
        # Generate random garbage
        return os.urandom(size)
    elif content_type.startswith("image/"):
        # Fake JPEG header + random data
        header = b"\xFF\xD8\xFF\xE0"
        return header + os.urandom(size - len(header))
    else:
        return os.urandom(size)


async def torture_upload(session: aiohttp.ClientSession, file_data: bytes, filename: str, content_type: str, token: str) -> Dict:
    """Single upload request."""
    try:
        form = aiohttp.FormData()
        form.add_field('file', file_data, filename=filename, content_type=content_type)
        form.add_field('email', TEST_EMAIL)
        
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        start = time.time()
        async with session.post(
            f"{BASE_URL}/api/v1/upap/upload",
            data=form,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as response:
            elapsed = time.time() - start
            text = await response.text()
            return {
                "status": response.status,
                "elapsed": elapsed,
                "response": text[:500],  # Truncate
                "filename": filename,
                "size": len(file_data)
            }
    except asyncio.TimeoutError:
        return {"status": "timeout", "elapsed": 60, "error": "Request timeout"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def phase1_api_torture():
    """Phase 1: API Torture Tests"""
    print("\n" + "="*60)
    print("PHASE 1: API TORTURE")
    print("="*60)
    
    if not AUTH_TOKEN:
        print("⚠️  No AUTH_TOKEN provided. Some tests will fail authentication.")
        return
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        # Test 1: Valid images (10x)
        print("\n[1.1] Sending 10 valid image uploads...")
        for i in range(10):
            file_data = generate_test_file(1.0, "image/jpeg")
            tasks.append(torture_upload(session, file_data, f"test_{i}.jpg", "image/jpeg", AUTH_TOKEN))
        
        # Test 2: Corrupted images (10x)
        print("[1.2] Sending 10 corrupted image uploads...")
        for i in range(10):
            file_data = generate_test_file(1.0, "image/jpeg", corrupted=True)
            tasks.append(torture_upload(session, file_data, f"corrupt_{i}.jpg", "image/jpeg", AUTH_TOKEN))
        
        # Test 3: 50MB files (5x)
        print("[1.3] Sending 5 large (50MB) file uploads...")
        for i in range(5):
            file_data = generate_test_file(50.0, "image/jpeg")
            tasks.append(torture_upload(session, file_data, f"large_{i}.jpg", "image/jpeg", AUTH_TOKEN))
        
        # Test 4: Various formats
        print("[1.4] Sending various format uploads...")
        formats = [
            ("test.png", "image/png"),
            ("test.webp", "image/webp"),
            ("test.bmp", "image/bmp"),
            ("test.tiff", "image/tiff"),
            ("test.exe", "application/x-msdownload"),  # Wrong type
        ]
        for filename, content_type in formats:
            file_data = generate_test_file(1.0, content_type)
            tasks.append(torture_upload(session, file_data, filename, content_type, AUTH_TOKEN))
        
        # Test 5: Empty file
        print("[1.5] Sending empty file...")
        tasks.append(torture_upload(session, b"", "empty.jpg", "image/jpeg", AUTH_TOKEN))
        
        # Test 6: Random binary
        print("[1.6] Sending random binary file...")
        tasks.append(torture_upload(session, os.urandom(1024*1024), "random.bin", "application/octet-stream", AUTH_TOKEN))
        
        # Execute all
        print(f"\nExecuting {len(tasks)} requests in parallel...")
        start = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.time() - start
        
        # Analyze results
        success = sum(1 for r in results if isinstance(r, dict) and r.get("status") == 200)
        errors = sum(1 for r in results if isinstance(r, Exception) or (isinstance(r, dict) and r.get("status") not in [200, 400, 413]))
        timeouts = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "timeout")
        
        print(f"\nResults: {len(results)} total, {success} success, {errors} errors, {timeouts} timeouts")
        print(f"Total time: {elapsed:.2f}s")
        print(f"Avg time per request: {elapsed/len(results):.2f}s")
        
        # Log failures
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                log_result(
                    "Phase 1",
                    f"Request {i}",
                    "Parallel request",
                    "Should handle gracefully",
                    f"Exception: {result}",
                    "Unhandled exception in upload handler",
                    "Add try/except wrapper",
                    8
                )
            elif isinstance(result, dict) and result.get("status") == "timeout":
                log_result(
                    "Phase 1",
                    f"Request {i}",
                    "Slow/large file upload",
                    "Should timeout gracefully",
                    "Request timeout (60s)",
                    "No timeout handling",
                    "Add timeout handling",
                    7
                )


# ============================================================
# PHASE 2: AUTH BREAKING
# ============================================================

async def phase2_auth_breaking():
    """Phase 2: Auth Breaking Tests"""
    print("\n" + "="*60)
    print("PHASE 2: AUTH BREAKING")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Expired token
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.invalid"
        async with session.get(
            f"{BASE_URL}/api/v1/upap/upload",
            headers={"Authorization": f"Bearer {expired_token}"}
        ) as resp:
            if resp.status not in [401, 403]:
                log_result(
                    "Phase 2",
                    "Expired token",
                    "Expired JWT token",
                    "401 Unauthorized",
                    f"{resp.status}",
                    "auth_middleware.py:30 - token validation not strict enough",
                    "Add exp claim validation",
                    6
                )
        
        # Test 2: Random token
        random_token = ''.join(random.choices(string.ascii_letters + string.digits, k=100))
        async with session.get(
            f"{BASE_URL}/api/v1/upap/upload",
            headers={"Authorization": f"Bearer {random_token}"}
        ) as resp:
            if resp.status not in [401, 403]:
                log_result(
                    "Phase 2",
                    "Random token",
                    "Random string as token",
                    "401 Unauthorized",
                    f"{resp.status}",
                    "auth_middleware.py:28 - decode_token doesn't validate format",
                    "Add token format validation before decode",
                    7
                )
        
        # Test 3: SQL injection in token
        sql_token = "'; DROP TABLE users; --"
        async with session.get(
            f"{BASE_URL}/api/v1/upap/upload",
            headers={"Authorization": f"Bearer {sql_token}"}
        ) as resp:
            if resp.status == 500:
                log_result(
                    "Phase 2",
                    "SQL injection attempt",
                    "SQL injection in token",
                    "401 Unauthorized (no crash)",
                    "500 Internal Server Error",
                    "auth_middleware.py - SQL injection vulnerability",
                    "Use parameterized queries (already using ORM, but verify)",
                    9
                )
        
        # Test 4: Missing header
        async with session.get(f"{BASE_URL}/api/v1/upap/upload") as resp:
            if resp.status != 401:
                log_result(
                    "Phase 2",
                    "Missing auth header",
                    "No Authorization header",
                    "401 Unauthorized",
                    f"{resp.status}",
                    "auth_middleware.py:19 - check is correct",
                    "N/A - working correctly",
                    0
                )
        
        # Test 5: Malformed JWT
        malformed = "not.a.jwt.token"
        async with session.get(
            f"{BASE_URL}/api/v1/upap/upload",
            headers={"Authorization": f"Bearer {malformed}"}
        ) as resp:
            if resp.status not in [401, 403]:
                log_result(
                    "Phase 2",
                    "Malformed JWT",
                    "Invalid JWT format",
                    "401 Unauthorized",
                    f"{resp.status}",
                    "auth_middleware.py:28 - decode_token should catch JWTError",
                    "Already handled, verify exception catching",
                    3
                )


# ============================================================
# PHASE 3: AI FAILURE SCENARIOS
# ============================================================

async def phase3_ai_failures():
    """Phase 3: AI Failure Scenarios"""
    print("\n" + "="*60)
    print("PHASE 3: AI FAILURE SCENARIOS")
    print("="*60)
    
    # This requires mocking OpenAI API or testing with invalid key
    # For now, we test if system handles OpenAI errors gracefully
    
    async with aiohttp.ClientSession() as session:
        file_data = generate_test_file(1.0, "image/jpeg")
        form = aiohttp.FormData()
        form.add_field('file', file_data, filename='test.jpg', content_type='image/jpeg')
        form.add_field('email', TEST_EMAIL)
        
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"} if AUTH_TOKEN else {}
        
        # Test: Upload with potentially failing AI
        async with session.post(
            f"{BASE_URL}/api/v1/upap/upload",
            data=form,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as resp:
            text = await resp.text()
            
            # Check if response contains fallback data when AI fails
            if resp.status == 200:
                try:
                    data = json.loads(text)
                    if data.get("recognition_error"):
                        print("✅ System handles AI failure gracefully")
                    else:
                        print("ℹ️  AI succeeded or not called")
                except:
                    pass
            
            # Check timeout
            if resp.status == 504 or "timeout" in text.lower():
                log_result(
                    "Phase 3",
                    "AI timeout",
                    "OpenAI API timeout (10s+)",
                    "Should return fallback (no timeout)",
                    "Request timeout or 504",
                    "novarchive_gpt_service.py:129 - no timeout on OpenAI call",
                    "Add timeout to OpenAI API call",
                    8
                )


# ============================================================
# PHASE 4: FRONTEND DESTRUCTION
# ============================================================

async def phase4_frontend_destruction():
    """Phase 4: Frontend Destruction Tests"""
    print("\n" + "="*60)
    print("PHASE 4: FRONTEND DESTRUCTION")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}", "Content-Type": "application/json"} if AUTH_TOKEN else {"Content-Type": "application/json"}
        
        # Test 1: Empty JSON
        async with session.post(
            f"{BASE_URL}/api/v1/upap/archive/add",
            json={},
            headers=headers
        ) as resp:
            if resp.status == 500:
                log_result(
                    "Phase 4",
                    "Empty JSON",
                    "Empty JSON body",
                    "400 Bad Request",
                    "500 Internal Server Error",
                    "upap_archive_add_router.py:49 - missing error handling",
                    "Add validation for required fields",
                    7
                )
        
        # Test 2: Missing fields
        async with session.post(
            f"{BASE_URL}/api/v1/upap/archive/add",
            json={"record_id": None},
            headers=headers
        ) as resp:
            if resp.status == 500:
                log_result(
                    "Phase 4",
                    "Missing required fields",
                    "Null record_id",
                    "400 Bad Request",
                    "500 Internal Server Error",
                    "upap_archive_add_router.py:69 - validation too late",
                    "Validate earlier",
                    6
                )
        
        # Test 3: Extremely long string
        long_string = "A" * 10000
        async with session.post(
            f"{BASE_URL}/api/v1/upap/archive/add",
            json={
                "record_id": str(uuid.uuid4()),
                "artist": long_string,
                "album": long_string
            },
            headers=headers
        ) as resp:
            if resp.status == 500:
                log_result(
                    "Phase 4",
                    "Extremely long string",
                    "10k char string",
                    "400 Bad Request or 413",
                    "500 Internal Server Error",
                    "No length validation on fields",
                    "Add max_length validation",
                    5
                )
        
        # Test 4: Script injection attempt
        xss_payload = "<script>alert('XSS')</script>"
        async with session.post(
            f"{BASE_URL}/api/v1/upap/archive/add",
            json={
                "record_id": str(uuid.uuid4()),
                "artist": xss_payload,
                "album": xss_payload
            },
            headers=headers
        ) as resp:
            # Should accept (sanitization is frontend responsibility)
            # But check if it causes crash
            if resp.status == 500:
                log_result(
                    "Phase 4",
                    "XSS attempt",
                    "Script tags in data",
                    "200 OK (sanitize on display)",
                    "500 Internal Server Error",
                    "Backend crashes on script tags",
                    "Sanitize or escape on storage",
                    8
                )


# ============================================================
# PHASE 5: DB CORRUPTION
# ============================================================

async def phase5_db_corruption():
    """Phase 5: DB Corruption Tests"""
    print("\n" + "="*60)
    print("PHASE 5: DB CORRUPTION")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}", "Content-Type": "application/json"} if AUTH_TOKEN else {"Content-Type": "application/json"}
        
        # Test 1: Invalid year (future)
        async with session.post(
            f"{BASE_URL}/api/v1/upap/archive/add",
            json={
                "record_id": str(uuid.uuid4()),
                "year": "2099"
            },
            headers=headers
        ) as resp:
            # Should validate year range
            if resp.status == 200:
                log_result(
                    "Phase 5",
                    "Invalid year (future)",
                    "Year 2099",
                    "400 Bad Request",
                    "200 OK (accepted)",
                    "No year validation",
                    "Add year range validation (1900-2025)",
                    4
                )
        
        # Test 2: Unicode edge cases
        unicode_payload = "👽🚀" * 1000
        async with session.post(
            f"{BASE_URL}/api/v1/upap/archive/add",
            json={
                "record_id": str(uuid.uuid4()),
                "artist": unicode_payload,
                "album": unicode_payload
            },
            headers=headers
        ) as resp:
            if resp.status == 500:
                log_result(
                    "Phase 5",
                    "Unicode edge cases",
                    "Heavy emoji use",
                    "Should handle gracefully",
                    "500 Internal Server Error",
                    "Unicode encoding issues",
                    "Ensure UTF-8 encoding everywhere",
                    6
                )


# ============================================================
# PHASE 6: RACE CONDITIONS
# ============================================================

async def phase6_race_conditions():
    """Phase 6: Race Condition Tests"""
    print("\n" + "="*60)
    print("PHASE 6: RACE CONDITIONS")
    print("="*60)
    
    if not AUTH_TOKEN:
        print("⚠️  Skipping - requires auth token")
        return
    
    async with aiohttp.ClientSession() as session:
        # Test: Same record archived multiple times simultaneously
        record_id = str(uuid.uuid4())
        archive_data = {
            "record_id": record_id,
            "artist": "Test Artist",
            "album": "Test Album"
        }
        
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}", "Content-Type": "application/json"}
        
        # Send 10 parallel archive requests
        tasks = []
        for i in range(10):
            tasks.append(session.post(
                f"{BASE_URL}/api/v1/upap/archive/add",
                json=archive_data,
                headers=headers
            ))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for r in results if isinstance(r, aiohttp.ClientResponse) and r.status == 200)
        
        if success_count > 1:
            log_result(
                "Phase 6",
                "Duplicate archive writes",
                "10 parallel archive requests for same record",
                "Only 1 should succeed",
                f"{success_count} succeeded",
                "No idempotency check",
                "Add idempotency key or check existing record",
                9
            )


# ============================================================
# PHASE 7: CLOUD FAILURE
# ============================================================

def phase7_cloud_failure():
    """Phase 7: Cloud Failure Tests"""
    print("\n" + "="*60)
    print("PHASE 7: CLOUD FAILURE")
    print("="*60)
    print("ℹ️  Cloud failure tests require Cloud Run deployment")
    print("    - Cold start delay: Test with first request")
    print("    - Memory limits: Test with 50MB+ files")
    print("    - Region latency: Test from different regions")
    
    # These would need actual Cloud Run deployment
    # For now, just document expected behavior


# ============================================================
# PHASE 8: SECURITY ATTACK
# ============================================================

async def phase8_security_attacks():
    """Phase 8: Security Attack Tests"""
    print("\n" + "="*60)
    print("PHASE 8: SECURITY ATTACKS")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        if not AUTH_TOKEN:
            print("⚠️  Skipping - requires auth token")
            return
        
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        
        # Test 1: Path traversal
        path_traversal = "../../../etc/passwd"
        form = aiohttp.FormData()
        form.add_field('file', b"fake", filename=path_traversal, content_type='image/jpeg')
        form.add_field('email', TEST_EMAIL)
        
        async with session.post(
            f"{BASE_URL}/api/v1/upap/upload",
            data=form,
            headers=headers
        ) as resp:
            if resp.status == 200:
                # Check if file was saved outside intended directory
                log_result(
                    "Phase 8",
                    "Path traversal",
                    "Filename: ../../../etc/passwd",
                    "400 Bad Request or sanitized path",
                    "200 OK (potential vulnerability)",
                    "upap_upload_router.py:151 - filename not sanitized",
                    "Sanitize filename, use Path.resolve() to check",
                    10
                )
        
        # Test 2: Huge filename
        huge_filename = "A" * 1000 + ".jpg"
        form2 = aiohttp.FormData()
        form2.add_field('file', b"fake", filename=huge_filename, content_type='image/jpeg')
        form2.add_field('email', TEST_EMAIL)
        
        async with session.post(
            f"{BASE_URL}/api/v1/upap/upload",
            data=form2,
            headers=headers
        ) as resp:
            if resp.status == 500:
                log_result(
                    "Phase 8",
                    "Huge filename",
                    "1000 char filename",
                    "400 Bad Request",
                    "500 Internal Server Error",
                    "Filename length not validated",
                    "Add filename length validation (max 255)",
                    7
                )
        
        # Test 3: MIME spoofing
        # Upload .exe as image/jpeg
        form3 = aiohttp.FormData()
        exe_content = b"MZ\x90\x00"  # Windows EXE header
        form3.add_field('file', exe_content, filename='malware.exe', content_type='image/jpeg')
        form3.add_field('email', TEST_EMAIL)
        
        async with session.post(
            f"{BASE_URL}/api/v1/upap/upload",
            data=form3,
            headers=headers
        ) as resp:
            if resp.status == 200:
                log_result(
                    "Phase 8",
                    "MIME spoofing",
                    "EXE file with image/jpeg content-type",
                    "400 Bad Request",
                    "200 OK (accepted)",
                    "Content-type not verified against file content",
                    "Add file magic number validation",
                    9
                )


# ============================================================
# MAIN
# ============================================================

async def main():
    """Run all chaos tests."""
    print("="*60)
    print("CHAOS ENGINEERING TEST SUITE")
    print("Records_AI_V2 Destruction Tests")
    print("="*60)
    print(f"Target: {BASE_URL}")
    print(f"Auth: {'✅ Set' if AUTH_TOKEN else '❌ Not set'}")
    print()
    
    try:
        await phase1_api_torture()
        await phase2_auth_breaking()
        await phase3_ai_failures()
        await phase4_frontend_destruction()
        await phase5_db_corruption()
        await phase6_race_conditions()
        phase7_cloud_failure()
        await phase8_security_attacks()
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Generate report
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    critical = [r for r in RESULTS if r["severity"] >= 7]
    warnings = [r for r in RESULTS if 4 <= r["severity"] < 7]
    info = [r for r in RESULTS if r["severity"] < 4]
    
    print(f"\nCritical Issues (Severity >= 7): {len(critical)}")
    for r in critical:
        print(f"  [{r['phase']}] {r['test']} - {r['root_cause']}")
    
    print(f"\nWarnings (Severity 4-6): {len(warnings)}")
    for r in warnings:
        print(f"  [{r['phase']}] {r['test']} - {r['root_cause']}")
    
    print(f"\nInfo (Severity < 4): {len(info)}")
    
    # Save report
    report_file = Path("CHAOS_TEST_REPORT.json")
    with open(report_file, "w") as f:
        json.dump(RESULTS, f, indent=2)
    
    print(f"\n📄 Full report saved to: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())
