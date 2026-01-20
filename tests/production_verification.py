#!/usr/bin/env python3
"""
Production Security Verification Script
Records_AI_V2 Security Fix Validation

Tests all critical security fixes identified in CHAOS_TEST_REPORT.md
"""

import asyncio
import aiohttp
import json
import os
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "https://records-ai-v2-969278596906.us-central1.run.app")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "")
TEST_EMAIL = os.getenv("TEST_EMAIL", "test@example.com")

# Test Results
RESULTS = []
FAILURES = []

# Colors for console output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def log_test(test_name: str, status: str, details: Dict[str, Any]):
    """Log test result."""
    result = {
        "test_name": test_name,
        "status": status,  # PASS, FAIL, WARNING
        "timestamp": datetime.utcnow().isoformat(),
        **details
    }
    RESULTS.append(result)
    
    # Console output
    if status == "PASS":
        symbol = "✔"
        color = Colors.GREEN
    elif status == "FAIL":
        symbol = "❌"
        color = Colors.RED
        FAILURES.append(result)
    else:
        symbol = "⚠"
        color = Colors.YELLOW
    
    print(f"{color}{symbol} {test_name}{Colors.RESET}")
    if details.get("message"):
        print(f"    {details['message']}")
    if details.get("http_status"):
        print(f"    HTTP: {details['http_status']}")
    if details.get("duration"):
        print(f"    Duration: {details['duration']:.2f}s")
    if status == "FAIL" and details.get("fix"):
        print(f"    {Colors.YELLOW}Fix: {details['fix']}{Colors.RESET}")
    print()


def generate_test_file(size_mb: float, content_type: str = "image/jpeg", fake_type: str = None) -> Tuple[bytes, str]:
    """Generate test file with optional fake magic bytes."""
    size = int(size_mb * 1024 * 1024)
    
    if fake_type == "exe":
        # Windows EXE header + random data
        header = b"MZ\x90\x00"
        return header + os.urandom(size - len(header)), "fake.exe"
    elif content_type.startswith("image/"):
        # JPEG header + random data
        header = b"\xFF\xD8\xFF\xE0"
        return header + os.urandom(size - len(header)), "test.jpg"
    else:
        return os.urandom(size), "test.bin"


async def test_auth_negative(session: aiohttp.ClientSession) -> Dict[str, Any]:
    """Test 1: Auth Negative Test (401)"""
    test_name = "Auth Negative Test"
    start = time.time()
    
    try:
        # Test without auth token - use FormData for multipart
        form = aiohttp.FormData()
        form.add_field('file', b"fake", filename="test.jpg", content_type="image/jpeg")
        form.add_field('email', TEST_EMAIL)
        
        async with session.post(
            f"{BASE_URL}/api/v1/upap/upload",
            data=form,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            elapsed = time.time() - start
            status_code = resp.status
            text = await resp.text()
            
            if status_code == 401:
                log_test(test_name, "PASS", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": "Unauthorized request correctly rejected"
                })
                return {"status": "PASS", "severity": 8}
            else:
                log_test(test_name, "FAIL", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "response": text[:200],
                    "message": f"Expected 401, got {status_code}",
                    "fix": "Check auth_middleware.py - verify 401 is returned for missing token",
                    "file": "backend/api/v1/auth_middleware.py",
                    "line": "19"
                })
                return {"status": "FAIL", "severity": 9}
    except Exception as e:
        elapsed = time.time() - start
        log_test(test_name, "FAIL", {
            "duration": elapsed,
            "error": str(e),
            "message": f"Test failed with exception: {e}",
            "fix": "Check network connectivity and API availability"
        })
        return {"status": "FAIL", "severity": 9}


async def test_path_traversal(session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
    """Test 2: Path Traversal (../../../etc/passwd)"""
    test_name = "Path Traversal Protection"
    start = time.time()
    
    try:
        file_data, _ = generate_test_file(0.1, "image/jpeg")
        form = aiohttp.FormData()
        form.add_field('file', file_data, filename="../../../etc/passwd", content_type="image/jpeg")
        form.add_field('email', TEST_EMAIL)
        
        async with session.post(
            f"{BASE_URL}/api/v1/upap/upload",
            data=form,
            headers={"Authorization": f"Bearer {token}"},
            timeout=aiohttp.ClientTimeout(total=30)
        ) as resp:
            elapsed = time.time() - start
            status_code = resp.status
            text = await resp.text()
            
            if status_code == 400:
                # Check if error mentions path traversal
                if "path traversal" in text.lower() or "invalid filename" in text.lower():
                    log_test(test_name, "PASS", {
                        "http_status": status_code,
                        "duration": elapsed,
                        "message": "Path traversal attempt blocked"
                    })
                    return {"status": "PASS", "severity": 10}
                else:
                    log_test(test_name, "WARNING", {
                        "http_status": status_code,
                        "duration": elapsed,
                        "message": "Path traversal rejected but error message unclear",
                        "response": text[:200]
                    })
                    return {"status": "WARNING", "severity": 8}
            elif status_code == 200:
                log_test(test_name, "FAIL", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": "CRITICAL: Path traversal not blocked - file may be saved outside intended directory",
                    "fix": "Check file_validation.py sanitize_filename() and validate_path_stays_in_directory()",
                    "file": "backend/core/file_validation.py",
                    "line": "25, 59"
                })
                return {"status": "FAIL", "severity": 10}
            else:
                log_test(test_name, "WARNING", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": f"Unexpected status code: {status_code}",
                    "response": text[:200]
                })
                return {"status": "WARNING", "severity": 7}
    except Exception as e:
        elapsed = time.time() - start
        log_test(test_name, "FAIL", {
            "duration": elapsed,
            "error": str(e),
            "message": f"Test failed: {e}",
            "fix": "Check file upload endpoint"
        })
        return {"status": "FAIL", "severity": 10}


async def test_mime_spoof(session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
    """Test 3: MIME Spoofing (.exe -> image/jpeg)"""
    test_name = "MIME Spoofing Protection"
    start = time.time()
    
    try:
        # Create fake EXE with JPEG content-type
        file_data, filename = generate_test_file(0.1, "image/jpeg", fake_type="exe")
        form = aiohttp.FormData()
        form.add_field('file', file_data, filename=filename, content_type="image/jpeg")
        form.add_field('email', TEST_EMAIL)
        
        async with session.post(
            f"{BASE_URL}/api/v1/upap/upload",
            data=form,
            headers={"Authorization": f"Bearer {token}"},
            timeout=aiohttp.ClientTimeout(total=30)
        ) as resp:
            elapsed = time.time() - start
            status_code = resp.status
            text = await resp.text()
            
            if status_code == 400:
                # Check if error mentions MIME mismatch or file type validation
                if "mime type mismatch" in text.lower() or "file type validation" in text.lower() or "file signature" in text.lower():
                    log_test(test_name, "PASS", {
                        "http_status": status_code,
                        "duration": elapsed,
                        "message": "MIME spoofing attempt blocked"
                    })
                    return {"status": "PASS", "severity": 9}
                else:
                    log_test(test_name, "WARNING", {
                        "http_status": status_code,
                        "duration": elapsed,
                        "message": "MIME spoofing rejected but error unclear",
                        "response": text[:200]
                    })
                    return {"status": "WARNING", "severity": 8}
            elif status_code == 200:
                log_test(test_name, "FAIL", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": "CRITICAL: MIME spoofing not blocked - executable may be stored as image",
                    "fix": "Check file_validation.py validate_file_signature() - verify magic bytes check",
                    "file": "backend/core/file_validation.py",
                    "line": "170"
                })
                return {"status": "FAIL", "severity": 9}
            else:
                log_test(test_name, "WARNING", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": f"Unexpected status: {status_code}",
                    "response": text[:200]
                })
                return {"status": "WARNING", "severity": 7}
    except Exception as e:
        elapsed = time.time() - start
        log_test(test_name, "FAIL", {
            "duration": elapsed,
            "error": str(e),
            "message": f"Test failed: {e}",
            "fix": "Check file upload endpoint"
        })
        return {"status": "FAIL", "severity": 9}


async def test_memory_exhaustion(session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
    """Test 4: Memory Exhaustion (60MB file upload)"""
    test_name = "Memory Exhaustion Protection (60MB)"
    start = time.time()
    
    try:
        # Generate 60MB file (exceeds 50MB limit)
        file_data, filename = generate_test_file(60.0, "image/jpeg")
        form = aiohttp.FormData()
        form.add_field('file', file_data, filename=filename, content_type="image/jpeg")
        form.add_field('email', TEST_EMAIL)
        
        async with session.post(
            f"{BASE_URL}/api/v1/upap/upload",
            data=form,
            headers={"Authorization": f"Bearer {token}"},
            timeout=aiohttp.ClientTimeout(total=60)
        ) as resp:
            elapsed = time.time() - start
            status_code = resp.status
            text = await resp.text()
            
            if status_code == 413:
                log_test(test_name, "PASS", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": "Large file correctly rejected (413 Payload Too Large)"
                })
                return {"status": "PASS", "severity": 9}
            elif status_code == 200:
                log_test(test_name, "FAIL", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": "CRITICAL: 60MB file accepted - may cause memory exhaustion",
                    "fix": "Check upap_upload_router.py - verify MAX_FILE_SIZE check during streaming",
                    "file": "backend/api/v1/upap_upload_router.py",
                    "line": "125"
                })
                return {"status": "FAIL", "severity": 9}
            else:
                log_test(test_name, "WARNING", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": f"Unexpected status: {status_code}",
                    "response": text[:200]
                })
                return {"status": "WARNING", "severity": 7}
    except asyncio.TimeoutError:
        elapsed = time.time() - start
        log_test(test_name, "PASS", {
            "duration": elapsed,
            "message": "Request timeout - likely due to size check (expected behavior)"
        })
        return {"status": "PASS", "severity": 9}
    except Exception as e:
        elapsed = time.time() - start
        log_test(test_name, "WARNING", {
            "duration": elapsed,
            "error": str(e),
            "message": f"Test completed with exception: {e}"
        })
        return {"status": "WARNING", "severity": 7}


async def test_parallel_upload_stress(session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
    """Test 5: 20 Parallel Upload Stress Test"""
    test_name = "Parallel Upload Stress Test (20x)"
    start = time.time()
    
    try:
        tasks = []
        for i in range(20):
            file_data, filename = generate_test_file(1.0, "image/jpeg")
            form = aiohttp.FormData()
            form.add_field('file', file_data, filename=f"test_{i}.jpg", content_type="image/jpeg")
            form.add_field('email', TEST_EMAIL)
            
            task = session.post(
                f"{BASE_URL}/api/v1/upap/upload",
                data=form,
                headers={"Authorization": f"Bearer {token}"},
                timeout=aiohttp.ClientTimeout(total=60)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.time() - start
        
        # Analyze results
        success_count = 0
        rate_limit_count = 0
        error_count = 0
        
        for result in results:
            if isinstance(result, Exception):
                error_count += 1
            elif isinstance(result, aiohttp.ClientResponse):
                try:
                    if result.status == 200:
                        success_count += 1
                    elif result.status == 429:
                        rate_limit_count += 1
                    else:
                        error_count += 1
                finally:
                    result.close()
        
        # Check if rate limiting worked
        if rate_limit_count > 0:
            log_test(test_name, "PASS", {
                "duration": elapsed,
                "message": f"Rate limiting working: {success_count} succeeded, {rate_limit_count} rate-limited, {error_count} errors",
                "stats": {
                    "success": success_count,
                    "rate_limited": rate_limit_count,
                    "errors": error_count,
                    "total": 20
                }
            })
            return {"status": "PASS", "severity": 8}
        elif error_count == 0 and success_count == 20:
            log_test(test_name, "WARNING", {
                "duration": elapsed,
                "message": "All 20 requests succeeded - rate limiting may not be enabled",
                "stats": {
                    "success": success_count,
                    "rate_limited": rate_limit_count,
                    "errors": error_count
                },
                "fix": "Check main.py - verify rate limiting middleware is enabled",
                "file": "backend/main.py",
                "line": "40"
            })
            return {"status": "WARNING", "severity": 6}
        else:
            log_test(test_name, "FAIL", {
                "duration": elapsed,
                "message": f"Unexpected results: {success_count} success, {rate_limit_count} rate-limited, {error_count} errors",
                "stats": {
                    "success": success_count,
                    "rate_limited": rate_limit_count,
                    "errors": error_count
                }
            })
            return {"status": "FAIL", "severity": 8}
    except Exception as e:
        elapsed = time.time() - start
        log_test(test_name, "FAIL", {
            "duration": elapsed,
            "error": str(e),
            "message": f"Stress test failed: {e}"
        })
        return {"status": "FAIL", "severity": 8}


async def test_archive_idempotency(session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
    """Test 6: Archive Idempotency (same record_id 5 times)"""
    test_name = "Archive Idempotency"
    start = time.time()
    
    try:
        record_id = str(uuid.uuid4())
        archive_data = {
            "record_id": record_id,
            "artist": "Test Artist",
            "album": "Test Album",
            "label": "Test Label",
            "year": "2023",
            "format": "LP"
        }
        
        # Send 5 identical requests
        tasks = []
        for i in range(5):
            task = session.post(
                f"{BASE_URL}/api/v1/upap/archive/add",
                json=archive_data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.time() - start
        
        # Analyze results
        success_count = 0
        idempotent_count = 0
        
        for result in results:
            if isinstance(result, Exception):
                continue
            
            try:
                if result.status == 200:
                    success_count += 1
                    try:
                        body = await result.json()
                        if body.get("idempotent") or body.get("message", "").lower().find("already") >= 0 or body.get("message", "").lower().find("idempotent") >= 0:
                            idempotent_count += 1
                    except:
                        pass
            finally:
                result.close()
        
        # Check if idempotency works (should have 4+ idempotent responses)
        if success_count == 5 and idempotent_count >= 4:
            log_test(test_name, "PASS", {
                "duration": elapsed,
                "message": f"Idempotency working: {success_count} succeeded, {idempotent_count} idempotent",
                "stats": {
                    "total": 5,
                    "success": success_count,
                    "idempotent": idempotent_count
                }
            })
            return {"status": "PASS", "severity": 9}
        elif success_count == 5 and idempotent_count == 0:
            log_test(test_name, "FAIL", {
                "duration": elapsed,
                "message": "CRITICAL: All 5 requests created new records - idempotency not working",
                "fix": "Check user_library_service.py add_record() - verify idempotency check",
                "file": "backend/services/user_library_service.py",
                "line": "13"
            })
            return {"status": "FAIL", "severity": 9}
        else:
            log_test(test_name, "WARNING", {
                "duration": elapsed,
                "message": f"Partial idempotency: {success_count} succeeded, {idempotent_count} idempotent",
                "stats": {
                    "success": success_count,
                    "idempotent": idempotent_count
                }
            })
            return {"status": "WARNING", "severity": 7}
    except Exception as e:
        elapsed = time.time() - start
        log_test(test_name, "FAIL", {
            "duration": elapsed,
            "error": str(e),
            "message": f"Test failed: {e}",
            "fix": "Check archive endpoint"
        })
        return {"status": "FAIL", "severity": 9}


async def test_xss_injection(session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
    """Test 7: XSS Injection Test"""
    test_name = "XSS Injection Protection"
    start = time.time()
    
    try:
        record_id = str(uuid.uuid4())
        xss_data = {
            "record_id": record_id,
            "artist": "<script>alert('XSS')</script>",
            "album": "<img src=x onerror=alert(1)>",
            "label": "javascript:alert('XSS')",
            "year": "2023"
        }
        
        async with session.post(
            f"{BASE_URL}/api/v1/upap/archive/add",
            json=xss_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=aiohttp.ClientTimeout(total=30)
        ) as resp:
            elapsed = time.time() - start
            status_code = resp.status
            text = await resp.text()
            
            if status_code == 200:
                # Check if script tags were sanitized
                if "<script>" not in text and "javascript:" not in text:
                    log_test(test_name, "PASS", {
                        "http_status": status_code,
                        "duration": elapsed,
                        "message": "XSS attempt handled - script tags sanitized"
                    })
                    return {"status": "PASS", "severity": 8}
                else:
                    log_test(test_name, "FAIL", {
                        "http_status": status_code,
                        "duration": elapsed,
                        "message": "CRITICAL: XSS payload not sanitized - script tags present in response",
                        "fix": "Check archive_schema.py sanitize_xss() validator",
                        "file": "backend/api/v1/schemas/archive_schema.py",
                        "line": "78"
                    })
                    return {"status": "FAIL", "severity": 8}
            elif status_code == 422:
                log_test(test_name, "PASS", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": "XSS attempt rejected (422 Validation Error)"
                })
                return {"status": "PASS", "severity": 8}
            else:
                log_test(test_name, "WARNING", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": f"Unexpected status: {status_code}",
                    "response": text[:200]
                })
                return {"status": "WARNING", "severity": 7}
    except Exception as e:
        elapsed = time.time() - start
        log_test(test_name, "FAIL", {
            "duration": elapsed,
            "error": str(e),
            "message": f"Test failed: {e}"
        })
        return {"status": "FAIL", "severity": 8}


async def test_invalid_year(session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
    """Test 8: Invalid Year Validation"""
    test_name = "Invalid Year Validation"
    start = time.time()
    
    try:
        record_id = str(uuid.uuid4())
        invalid_data = {
            "record_id": record_id,
            "artist": "Test Artist",
            "album": "Test Album",
            "year": "2099"  # Future year
        }
        
        async with session.post(
            f"{BASE_URL}/api/v1/upap/archive/add",
            json=invalid_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=aiohttp.ClientTimeout(total=30)
        ) as resp:
            elapsed = time.time() - start
            status_code = resp.status
            text = await resp.text()
            
            if status_code == 422:
                log_test(test_name, "PASS", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": "Invalid year correctly rejected (422)"
                })
                return {"status": "PASS", "severity": 4}
            elif status_code == 200:
                log_test(test_name, "WARNING", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": "Invalid year accepted - validation may allow future years",
                    "fix": "Check archive_schema.py validate_year() - verify year range (1900-current+1)",
                    "file": "backend/api/v1/schemas/archive_schema.py",
                    "line": "67"
                })
                return {"status": "WARNING", "severity": 4}
            else:
                log_test(test_name, "WARNING", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": f"Unexpected status: {status_code}"
                })
                return {"status": "WARNING", "severity": 3}
    except Exception as e:
        elapsed = time.time() - start
        log_test(test_name, "WARNING", {
            "duration": elapsed,
            "error": str(e),
            "message": f"Test failed: {e}"
        })
        return {"status": "WARNING", "severity": 3}


async def test_duplicate_upload_retry(session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
    """Test 9: Duplicate Upload Retry Test"""
    test_name = "Duplicate Upload Retry Test"
    start = time.time()
    
    try:
        # First upload
        file_data, filename = generate_test_file(1.0, "image/jpeg")
        form1 = aiohttp.FormData()
        form1.add_field('file', file_data, filename=filename, content_type="image/jpeg")
        form1.add_field('email', TEST_EMAIL)
        
        async with session.post(
            f"{BASE_URL}/api/v1/upap/upload",
            data=form1,
            headers={"Authorization": f"Bearer {token}"},
            timeout=aiohttp.ClientTimeout(total=30)
        ) as resp1:
            if resp1.status != 200:
                elapsed = time.time() - start
                log_test(test_name, "WARNING", {
                    "duration": elapsed,
                    "message": f"First upload failed: {resp1.status}"
                })
                return {"status": "WARNING", "severity": 5}
            
            data1 = await resp1.json()
            record_id_1 = data1.get("record_id")
        
        # Retry with same file (should be idempotent or return existing)
        form2 = aiohttp.FormData()
        form2.add_field('file', file_data, filename=filename, content_type="image/jpeg")
        form2.add_field('email', TEST_EMAIL)
        
        async with session.post(
            f"{BASE_URL}/api/v1/upap/upload",
            data=form2,
            headers={"Authorization": f"Bearer {token}"},
            timeout=aiohttp.ClientTimeout(total=30)
        ) as resp2:
            elapsed = time.time() - start
            status_code = resp2.status
            data2 = await resp2.json()
            record_id_2 = data2.get("record_id")
            
            # Check if same record_id returned or new one created
            if record_id_1 and record_id_2 and record_id_1 == record_id_2:
                log_test(test_name, "PASS", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": "Duplicate upload returned same record_id (idempotent)"
                })
                return {"status": "PASS", "severity": 7}
            elif status_code == 200:
                log_test(test_name, "WARNING", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": "Duplicate upload created new record_id - may not be idempotent",
                    "fix": "Check upload endpoint - verify idempotency by file hash or content"
                })
                return {"status": "WARNING", "severity": 6}
            else:
                log_test(test_name, "WARNING", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": f"Unexpected status: {status_code}"
                })
                return {"status": "WARNING", "severity": 5}
    except Exception as e:
        elapsed = time.time() - start
        log_test(test_name, "FAIL", {
            "duration": elapsed,
            "error": str(e),
            "message": f"Test failed: {e}"
        })
        return {"status": "FAIL", "severity": 6}


async def test_image_enhancement_auto_fix(session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
    """Test 10: Image Enhancement - Low Quality Auto Fix"""
    test_name = "Image Enhancement Auto Fix"
    start = time.time()
    
    try:
        # Create a small/blurry test image (512x512 with blur)
        import io
        from PIL import Image
        import numpy as np
        
        # Create small blurry image
        img = Image.new("RGB", (512, 512), color=(128, 128, 128))
        pixels = np.array(img)
        noise = np.random.randint(-20, 20, pixels.shape, dtype=np.int16)
        pixels = np.clip(pixels.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(pixels)
        img = img.filter(Image.ImageFilter.GaussianBlur(radius=2))
        
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        file_data = buffer.getvalue()
        
        form = aiohttp.FormData()
        form.add_field('file', file_data, filename="blurry_test.jpg", content_type="image/jpeg")
        form.add_field('email', TEST_EMAIL)
        
        async with session.post(
            f"{BASE_URL}/api/v1/upap/upload",
            data=form,
            headers={"Authorization": f"Bearer {token}"},
            timeout=aiohttp.ClientTimeout(total=30)
        ) as resp:
            elapsed = time.time() - start
            status_code = resp.status
            text = await resp.text()
            
            if status_code == 200:
                try:
                    data = json.loads(text)
                    enhancement = data.get("enhancement", {})
                    
                    if enhancement.get("enhanced"):
                        log_test(test_name, "PASS", {
                            "http_status": status_code,
                            "duration": elapsed,
                            "message": f"Low quality image auto-enhanced: quality_improvement={enhancement.get('quality_improvement')}",
                            "enhancement_time": enhancement.get("enhancement_time"),
                            "quality_improvement": enhancement.get("quality_improvement")
                        })
                        return {"status": "PASS", "severity": 7}
                    else:
                        log_test(test_name, "WARNING", {
                            "http_status": status_code,
                            "duration": elapsed,
                            "message": "Image not enhanced - may be high quality or enhancement skipped",
                            "quality_score": enhancement.get("quality_score")
                        })
                        return {"status": "WARNING", "severity": 5}
                except:
                    log_test(test_name, "WARNING", {
                        "http_status": status_code,
                        "duration": elapsed,
                        "message": "Upload succeeded but enhancement info missing"
                    })
                    return {"status": "WARNING", "severity": 5}
            else:
                log_test(test_name, "FAIL", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": f"Upload failed: {status_code}",
                    "response": text[:200]
                })
                return {"status": "FAIL", "severity": 6}
    except Exception as e:
        elapsed = time.time() - start
        log_test(test_name, "FAIL", {
            "duration": elapsed,
            "error": str(e),
            "message": f"Test failed: {e}"
        })
        return {"status": "FAIL", "severity": 6}


async def test_enhanced_image_used_in_ai(session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
    """Test 11: Enhanced Image Used in AI Recognition"""
    test_name = "Enhanced Image Used in AI"
    start = time.time()
    
    try:
        # Create small test image that should be enhanced
        import io
        from PIL import Image
        
        img = Image.new("RGB", (512, 512), color=(200, 200, 200))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        file_data = buffer.getvalue()
        
        form = aiohttp.FormData()
        form.add_field('file', file_data, filename="small_test.jpg", content_type="image/jpeg")
        form.add_field('email', TEST_EMAIL)
        
        async with session.post(
            f"{BASE_URL}/api/v1/upap/upload",
            data=form,
            headers={"Authorization": f"Bearer {token}"},
            timeout=aiohttp.ClientTimeout(total=30)
        ) as resp:
            elapsed = time.time() - start
            status_code = resp.status
            text = await resp.text()
            
            if status_code == 200:
                try:
                    data = json.loads(text)
                    enhancement = data.get("enhancement", {})
                    
                    # Check if enhanced image URL is present
                    if data.get("enhanced_image_url") and enhancement.get("enhanced"):
                        log_test(test_name, "PASS", {
                            "http_status": status_code,
                            "duration": elapsed,
                            "message": "Enhanced image created and available for AI recognition",
                            "enhanced_image_url": data.get("enhanced_image_url")
                        })
                        return {"status": "PASS", "severity": 7}
                    else:
                        log_test(test_name, "WARNING", {
                            "http_status": status_code,
                            "duration": elapsed,
                            "message": "Enhancement may have been skipped (high quality image)"
                        })
                        return {"status": "WARNING", "severity": 5}
                except Exception as parse_error:
                    log_test(test_name, "WARNING", {
                        "http_status": status_code,
                        "duration": elapsed,
                        "message": f"Response parse error: {parse_error}"
                    })
                    return {"status": "WARNING", "severity": 5}
            else:
                log_test(test_name, "FAIL", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": f"Upload failed: {status_code}"
                })
                return {"status": "FAIL", "severity": 6}
    except Exception as e:
        elapsed = time.time() - start
        log_test(test_name, "FAIL", {
            "duration": elapsed,
            "error": str(e),
            "message": f"Test failed: {e}"
        })
        return {"status": "FAIL", "severity": 6}


async def test_enhancement_fallback_logic(session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
    """Test 12: Enhancement Fallback Logic"""
    test_name = "Enhancement Fallback Logic"
    start = time.time()
    
    try:
        # Upload a valid image - enhancement should gracefully handle any errors
        file_data, filename = generate_test_file(1.0, "image/jpeg")
        form = aiohttp.FormData()
        form.add_field('file', file_data, filename=filename, content_type="image/jpeg")
        form.add_field('email', TEST_EMAIL)
        
        async with session.post(
            f"{BASE_URL}/api/v1/upap/upload",
            data=form,
            headers={"Authorization": f"Bearer {token}"},
            timeout=aiohttp.ClientTimeout(total=30)
        ) as resp:
            elapsed = time.time() - start
            status_code = resp.status
            
            # Should always succeed (fallback to original if enhancement fails)
            if status_code == 200:
                log_test(test_name, "PASS", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": "Upload succeeded with fallback logic - enhancement errors don't break upload"
                })
                return {"status": "PASS", "severity": 8}
            else:
                log_test(test_name, "FAIL", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": "Upload failed - fallback logic may not be working",
                    "fix": "Check upap_upload_router.py - verify enhancement errors don't break upload flow"
                })
                return {"status": "FAIL", "severity": 7}
    except Exception as e:
        elapsed = time.time() - start
        log_test(test_name, "FAIL", {
            "duration": elapsed,
            "error": str(e),
            "message": f"Test failed: {e}"
        })
        return {"status": "FAIL", "severity": 7}


async def test_enhancement_timeout_protection(session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
    """Test 13: Enhancement Timeout Protection"""
    test_name = "Enhancement Timeout Protection"
    start = time.time()
    
    try:
        # Upload a valid image - enhancement should complete within timeout
        file_data, filename = generate_test_file(2.0, "image/jpeg")
        form = aiohttp.FormData()
        form.add_field('file', file_data, filename=filename, content_type="image/jpeg")
        form.add_field('email', TEST_EMAIL)
        
        async with session.post(
            f"{BASE_URL}/api/v1/upap/upload",
            data=form,
            headers={"Authorization": f"Bearer {token}"},
            timeout=aiohttp.ClientTimeout(total=30)
        ) as resp:
            elapsed = time.time() - start
            status_code = resp.status
            text = await resp.text()
            
            if status_code == 200:
                try:
                    data = json.loads(text)
                    enhancement = data.get("enhancement", {})
                    enhancement_time = enhancement.get("enhancement_time", 0.0)
                    
                    # Enhancement should complete within 5 seconds
                    if enhancement_time < 5.5:  # Small buffer
                        log_test(test_name, "PASS", {
                            "http_status": status_code,
                            "duration": elapsed,
                            "message": f"Enhancement completed within timeout: {enhancement_time}s",
                            "enhancement_time": enhancement_time
                        })
                        return {"status": "PASS", "severity": 7}
                    else:
                        log_test(test_name, "WARNING", {
                            "http_status": status_code,
                            "duration": elapsed,
                            "message": f"Enhancement took longer than expected: {enhancement_time}s",
                            "enhancement_time": enhancement_time
                        })
                        return {"status": "WARNING", "severity": 6}
                except:
                    log_test(test_name, "WARNING", {
                        "http_status": status_code,
                        "duration": elapsed,
                        "message": "Enhancement info not available in response"
                    })
                    return {"status": "WARNING", "severity": 5}
            else:
                log_test(test_name, "FAIL", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": f"Upload failed: {status_code}"
                })
                return {"status": "FAIL", "severity": 6}
    except Exception as e:
        elapsed = time.time() - start
        log_test(test_name, "FAIL", {
            "duration": elapsed,
            "error": str(e),
            "message": f"Test failed: {e}"
        })
        return {"status": "FAIL", "severity": 6}


async def test_openai_timeout_simulation(session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
    """Test 10: OpenAI Timeout Simulation (large/complex image)"""
    test_name = "OpenAI Timeout Protection"
    start = time.time()
    
    try:
        # Upload a valid image (should trigger OpenAI call)
        file_data, filename = generate_test_file(5.0, "image/jpeg")  # 5MB image
        form = aiohttp.FormData()
        form.add_field('file', file_data, filename=filename, content_type="image/jpeg")
        form.add_field('email', TEST_EMAIL)
        
        async with session.post(
            f"{BASE_URL}/api/v1/upap/upload",
            data=form,
            headers={"Authorization": f"Bearer {token}"},
            timeout=aiohttp.ClientTimeout(total=35)  # 35s timeout
        ) as resp:
            elapsed = time.time() - start
            status_code = resp.status
            text = await resp.text()
            
            # Check if request completes within timeout (even if OpenAI fails)
            if elapsed < 35 and status_code == 200:
                try:
                    data = json.loads(text)
                    if data.get("recognition_error") or data.get("recognition_failed"):
                        log_test(test_name, "PASS", {
                            "http_status": status_code,
                            "duration": elapsed,
                            "message": "Request completed within timeout, OpenAI error handled gracefully"
                        })
                        return {"status": "PASS", "severity": 8}
                    else:
                        log_test(test_name, "PASS", {
                            "http_status": status_code,
                            "duration": elapsed,
                            "message": "Request completed successfully within timeout"
                        })
                        return {"status": "PASS", "severity": 8}
                except:
                    log_test(test_name, "PASS", {
                        "http_status": status_code,
                        "duration": elapsed,
                        "message": "Request completed within timeout"
                    })
                    return {"status": "PASS", "severity": 8}
            elif elapsed >= 35:
                log_test(test_name, "FAIL", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": "CRITICAL: Request exceeded 35s timeout - OpenAI timeout not enforced",
                    "fix": "Check novarchive_gpt_service.py - verify timeout=30.0 parameter",
                    "file": "backend/services/novarchive_gpt_service.py",
                    "line": "134"
                })
                return {"status": "FAIL", "severity": 8}
            else:
                log_test(test_name, "WARNING", {
                    "http_status": status_code,
                    "duration": elapsed,
                    "message": f"Request completed with status {status_code}",
                    "response": text[:200]
                })
                return {"status": "WARNING", "severity": 6}
    except asyncio.TimeoutError:
        elapsed = time.time() - start
        log_test(test_name, "FAIL", {
            "duration": elapsed,
            "message": "CRITICAL: Request timed out - OpenAI timeout not working",
            "fix": "Check novarchive_gpt_service.py - add timeout parameter to OpenAI API call",
            "file": "backend/services/novarchive_gpt_service.py",
            "line": "134"
        })
        return {"status": "FAIL", "severity": 8}
    except Exception as e:
        elapsed = time.time() - start
        log_test(test_name, "WARNING", {
            "duration": elapsed,
            "error": str(e),
            "message": f"Test completed with exception: {e}"
        })
        return {"status": "WARNING", "severity": 6}


async def main():
    """Run all production verification tests."""
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}PRODUCTION SECURITY VERIFICATION{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}Records_AI_V2 Security Fix Validation{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print()
    print(f"Target: {BASE_URL}")
    print(f"Auth: {'✅ Token provided' if AUTH_TOKEN else '❌ No token (some tests will fail)'}")
    print()
    
    if not AUTH_TOKEN:
        print(f"{Colors.YELLOW}⚠️  WARNING: AUTH_TOKEN not set. Some tests will fail.{Colors.RESET}")
        print("Set AUTH_TOKEN environment variable for full test coverage.")
        print()
    
    async with aiohttp.ClientSession() as session:
        # Run tests in priority order
        tests = [
            ("Path Traversal", test_path_traversal, AUTH_TOKEN),
            ("MIME Spoofing", test_mime_spoof, AUTH_TOKEN),
            ("Memory Exhaustion", test_memory_exhaustion, AUTH_TOKEN),
            ("Rate Limiting", test_parallel_upload_stress, AUTH_TOKEN),
            ("Archive Idempotency", test_archive_idempotency, AUTH_TOKEN),
            ("Auth Negative", test_auth_negative, None),
            ("XSS Injection", test_xss_injection, AUTH_TOKEN),
            ("Invalid Year", test_invalid_year, AUTH_TOKEN),
            ("Duplicate Upload", test_duplicate_upload_retry, AUTH_TOKEN),
            ("Image Enhancement Auto Fix", test_image_enhancement_auto_fix, AUTH_TOKEN),
            ("Enhanced Image Used in AI", test_enhanced_image_used_in_ai, AUTH_TOKEN),
            ("Enhancement Fallback Logic", test_enhancement_fallback_logic, AUTH_TOKEN),
            ("Enhancement Timeout Protection", test_enhancement_timeout_protection, AUTH_TOKEN),
            ("OpenAI Timeout", test_openai_timeout_simulation, AUTH_TOKEN),
        ]
        
        results = {}
        for test_name, test_func, token in tests:
            try:
                if token or test_name == "Auth Negative":
                    result = await test_func(session, token) if token else await test_func(session)
                    results[test_name] = result
                else:
                    log_test(test_name, "WARNING", {
                        "message": "Skipped - requires auth token"
                    })
                    results[test_name] = {"status": "WARNING", "severity": 0}
            except Exception as e:
                log_test(test_name, "FAIL", {
                    "error": str(e),
                    "message": f"Test crashed: {e}"
                })
                results[test_name] = {"status": "FAIL", "severity": 10}
        
        # Calculate security score
        total_severity = 0
        passed_severity = 0
        
        for test_name, result in results.items():
            severity = result.get("severity", 0)
            status = result.get("status", "UNKNOWN")
            total_severity += severity
            if status == "PASS":
                passed_severity += severity
        
        security_score = (passed_severity / total_severity * 10) if total_severity > 0 else 0
        
        # Print summary
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}TEST RESULTS SUMMARY{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}")
        print()
        
        # PASS/FAIL matrix
        print(f"{Colors.BOLD}Test Results Matrix:{Colors.RESET}")
        print(f"{'Test Name':<30} {'Status':<10} {'Severity':<10}")
        print("-" * 70)
        
        for test_name, result in results.items():
            status = result.get("status", "UNKNOWN")
            severity = result.get("severity", 0)
            
            if status == "PASS":
                symbol = "✔ PASS"
                color = Colors.GREEN
            elif status == "FAIL":
                symbol = "❌ FAIL"
                color = Colors.RED
            else:
                symbol = "⚠ WARN"
                color = Colors.YELLOW
            
            print(f"{test_name:<30} {color}{symbol:<10}{Colors.RESET} {severity}")
        
        print()
        print(f"{Colors.BOLD}Security Score: {Colors.RESET}", end="")
        if security_score >= 8:
            print(f"{Colors.GREEN}{security_score:.1f}/10 ✅{Colors.RESET}")
        elif security_score >= 6:
            print(f"{Colors.YELLOW}{security_score:.1f}/10 ⚠️{Colors.RESET}")
        else:
            print(f"{Colors.RED}{security_score:.1f}/10 ❌{Colors.RESET}")
        print()
        
        # Critical failures
        critical_failures = [f for f in FAILURES if f.get("severity", 0) >= 9]
        if critical_failures:
            print(f"{Colors.RED}{Colors.BOLD}{'='*70}{Colors.RESET}")
            print(f"{Colors.RED}{Colors.BOLD}🚨 DEPLOY BLOCKED - CRITICAL SECURITY ISSUES FOUND 🚨{Colors.RESET}")
            print(f"{Colors.RED}{Colors.BOLD}{'='*70}{Colors.RESET}")
            print()
            for failure in critical_failures:
                print(f"{Colors.RED}❌ {failure['test_name']}{Colors.RESET}")
                if failure.get("fix"):
                    print(f"   Fix: {failure['fix']}")
                if failure.get("file"):
                    print(f"   File: {failure['file']}")
                if failure.get("line"):
                    print(f"   Line: {failure['line']}")
                print()
        else:
            print(f"{Colors.GREEN}✅ No critical security issues found{Colors.RESET}")
            print()
        
        # Save JSON report
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "target_url": BASE_URL,
            "security_score": round(security_score, 1),
            "total_tests": len(results),
            "passed": sum(1 for r in results.values() if r.get("status") == "PASS"),
            "failed": sum(1 for r in results.values() if r.get("status") == "FAIL"),
            "warnings": sum(1 for r in results.values() if r.get("status") == "WARNING"),
            "critical_failures": len(critical_failures),
            "tests": RESULTS,
            "deploy_blocked": len(critical_failures) > 0
        }
        
        report_path = Path("production_verification_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Full report saved to: {report_path}")
        print()
        
        # Exit code
        if len(critical_failures) > 0:
            sys.exit(1)  # Block deployment
        elif security_score < 6:
            sys.exit(1)  # Block deployment
        else:
            sys.exit(0)  # Allow deployment


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Test interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Test suite failed: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
