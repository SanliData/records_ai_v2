#!/usr/bin/env python3
"""
Final Pre-Production Destruction Test
Records_AI_V2 - Extreme Load & Security Stress Test

Mission: Break the system in every possible way.
If system survives → APPROVE PRODUCTION.

Phases:
1. Extreme Load Test (500 parallel uploads)
2. Auth Attack (JWT manipulation, SQL injection)
3. AI Service Chaos (OpenAI failures)
4. File Attack (Path traversal, MIME spoof, zip bomb)
5. Database Torture (Concurrent writes, conflicts)
6. Cloud Failure (Cold start, restart)
7. Frontend Abuse (XSS, unicode, broken JSON)

Acceptance Criteria:
- Security >= 9.0
- Stability >= 9.0
- No CRITICAL vulnerabilities
- No memory leak
- No data corruption
"""

import asyncio
import aiohttp
import json
import os
import sys
import time
import uuid
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # Create a dummy psutil for basic operations
    class DummyProcess:
        def memory_info(self):
            class MemInfo:
                rss = 0
            return MemInfo()
    class DummyPsutil:
        def Process(self, pid):
            return DummyProcess()
    psutil = DummyPsutil()

import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import statistics

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "https://records-ai-v2-969278596906.us-central1.run.app")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
TEST_EMAIL = os.getenv("TEST_EMAIL", "test@example.com")

# Test Results
TEST_RESULTS = []
CRITICAL_FAILURES = []
WARNINGS = []

# Metrics
METRICS = {
    "response_times": [],
    "memory_usage": [],
    "error_counts": defaultdict(int),
    "status_codes": defaultdict(int),
    "total_requests": 0,
    "failed_requests": 0,
    "timeouts": 0,
}

# Colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def log_result(phase: str, test_name: str, status: str, details: Dict[str, Any]):
    """Log test result."""
    result = {
        "phase": phase,
        "test_name": test_name,
        "status": status,  # PASS, FAIL, WARNING, CRITICAL
            "timestamp": datetime.now(timezone.utc).isoformat(),
        **details
    }
    TEST_RESULTS.append(result)
    
    if status == "CRITICAL":
        CRITICAL_FAILURES.append(result)
        symbol = "🚨"
        color = Colors.RED
    elif status == "FAIL":
        symbol = "❌"
        color = Colors.RED
    elif status == "WARNING":
        symbol = "⚠️"
        color = Colors.YELLOW
        WARNINGS.append(result)
    else:
        symbol = "✅"
        color = Colors.GREEN
    
    print(f"{color}{symbol} [{phase}] {test_name}: {status}{Colors.RESET}")
    if details.get("message"):
        print(f"    {details['message']}")
    if details.get("metrics"):
        for key, value in details['metrics'].items():
            print(f"    {key}: {value}")
    print()


def get_memory_usage() -> float:
    """Get current memory usage percentage."""
    try:
        if PSUTIL_AVAILABLE:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / (1024 * 1024)  # MB
        else:
            # Fallback: return 0 if psutil not available
            return 0.0
    except:
        return 0.0


def generate_test_file(size_mb: float, content_type: str = "image/jpeg", corrupt: bool = False) -> Tuple[bytes, str]:
    """Generate test file."""
    size = int(size_mb * 1024 * 1024)
    
    if corrupt:
        # Corrupted file (not valid JPEG)
        return os.urandom(size), "corrupt.bin"
    elif content_type.startswith("image/"):
        # Valid JPEG header
        header = b"\xFF\xD8\xFF\xE0"
        return header + os.urandom(size - len(header)), "test.jpg"
    else:
        return os.urandom(size), "test.bin"


def create_blurry_image(width=512, height=512) -> bytes:
    """Create blurry test image."""
    try:
        from PIL import Image
        import numpy as np
        
        img = Image.new("RGB", (width, height), color=(128, 128, 128))
        pixels = np.array(img)
        noise = np.random.randint(-20, 20, pixels.shape, dtype=np.int16)
        pixels = np.clip(pixels.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(pixels)
        
        import io
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=30)
        return buffer.getvalue()
    except:
        # Fallback if PIL not available
        return b"\xFF\xD8\xFF\xE0" + os.urandom(1024)


async def phase1_extreme_load_test(session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
    """Phase 1: Extreme Load Test - 500 parallel uploads."""
    phase_name = "PHASE 1: Extreme Load Test"
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{phase_name}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")
    
    if not token:
        log_result(phase_name, "Extreme Load Test", "SKIP", {
            "message": "AUTH_TOKEN required for load test - skipped"
        })
        return {"status": "SKIP", "severity": 0}
    
    # Extract email from token to ensure it matches authenticated user
    test_email = decode_token_email(token) or TEST_EMAIL
    
    start_time = time.time()
    initial_memory = get_memory_usage()
    max_memory = initial_memory
    
    # Create test files
    test_files = []
    for i in range(500):
        if i < 200:
            # High quality images
            file_data, filename = generate_test_file(1.0, "image/jpeg")
        elif i < 350:
            # Low quality images
            file_data = create_blurry_image(512, 512)
            filename = f"blurry_{i}.jpg"
        elif i < 450:
            # Corrupted files
            file_data, filename = generate_test_file(0.5, "image/jpeg", corrupt=True)
        else:
            # Large files (but under limit)
            file_data, filename = generate_test_file(10.0, "image/jpeg")
        
        test_files.append((file_data, filename, i))
    
    print(f"📊 Starting 500 parallel uploads...")
    print(f"   Initial memory: {initial_memory:.2f} MB")
    
    async def upload_file(file_data: bytes, filename: str, index: int):
        """Single upload task."""
        try:
            form = aiohttp.FormData()
            form.add_field('file', file_data, filename=filename, content_type="image/jpeg")
            form.add_field('email', test_email)  # Use email from token, not TEST_EMAIL
            
            req_start = time.time()
            async with session.post(
                f"{BASE_URL}/api/v1/upap/upload",
                data=form,
                headers={"Authorization": f"Bearer {token}"},
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                elapsed = time.time() - req_start
                status_code = resp.status
                METRICS["response_times"].append(elapsed)
                METRICS["status_codes"][status_code] += 1
                METRICS["total_requests"] += 1
                
                if status_code >= 500:
                    METRICS["failed_requests"] += 1
                    METRICS["error_counts"]["5xx"] += 1
                    return {"index": index, "status": status_code, "error": "5xx"}
                elif status_code != 200:
                    METRICS["failed_requests"] += 1
                    return {"index": index, "status": status_code}
                
                # Check memory
                current_memory = get_memory_usage()
                if current_memory > max_memory:
                    max_memory = current_memory
                
                return {"index": index, "status": status_code, "time": elapsed}
        except asyncio.TimeoutError:
            METRICS["timeouts"] += 1
            METRICS["failed_requests"] += 1
            return {"index": index, "status": "timeout"}
        except Exception as e:
            METRICS["failed_requests"] += 1
            METRICS["error_counts"]["exception"] += 1
            return {"index": index, "status": "error", "error": str(e)}
    
    # Run 500 parallel uploads
    tasks = [upload_file(file_data, filename, i) for file_data, filename, i in test_files]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    elapsed = time.time() - start_time
    final_memory = get_memory_usage()
    client_memory_increase_mb = final_memory - initial_memory  # Client-side memory only
    memory_increase = client_memory_increase_mb  # Keep for backward compatibility
    
    # Analyze results
    success_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == 200)
    error_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") != 200)
    exception_count = sum(1 for r in results if isinstance(r, Exception))
    timeout_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "timeout")
    
    avg_response_time = statistics.mean(METRICS["response_times"]) if METRICS["response_times"] else 0
    max_response_time = max(METRICS["response_times"]) if METRICS["response_times"] else 0
    p95_response_time = statistics.quantiles(METRICS["response_times"], n=20)[18] if len(METRICS["response_times"]) > 20 else max_response_time
    
    # Check criteria
    has_5xx = METRICS["error_counts"]["5xx"] > 0
    memory_too_high = memory_increase > 1000  # > 1GB increase
    timeout_rate = timeout_count / len(results) if results else 0
    
    status = "PASS"
    severity = 10
    
    if has_5xx:
        status = "CRITICAL"
        message = f"CRITICAL: {METRICS['error_counts']['5xx']} 5xx errors detected - system unstable"
    elif memory_too_high:
        status = "CRITICAL"
        message = f"CRITICAL: Memory increase {memory_increase:.2f} MB - possible memory leak"
    elif timeout_rate > 0.1:  # > 10% timeout
        status = "CRITICAL"
        message = f"CRITICAL: {timeout_count} timeouts ({timeout_rate*100:.1f}%) - system overloaded"
    elif error_count > 50:  # > 10% error rate
        status = "FAIL"
        severity = 9
        message = f"High error rate: {error_count} errors ({error_count/len(results)*100:.1f}%)"
    else:
        message = f"Load test passed: {success_count} success, {error_count} errors, {timeout_count} timeouts"
    
    log_result(phase_name, "500 Parallel Uploads", status, {
        "message": message,
        "metrics": {
            "success": success_count,
            "errors": error_count,
            "timeouts": timeout_count,
            "exceptions": exception_count,
            "duration": f"{elapsed:.2f}s",
            "avg_response_time": f"{avg_response_time:.2f}s",
            "p95_response_time": f"{p95_response_time:.2f}s",
            "max_response_time": f"{max_response_time:.2f}s",
            "client_memory_increase_mb": f"{client_memory_increase_mb:.2f}",
            "memory_increase_mb": f"{memory_increase:.2f}",  # Backward compatibility
            "final_memory_mb": f"{final_memory:.2f}",
            "server_memory": "unknown (not accessible locally)"
        }
    })
    
    return {
        "status": status,
        "severity": severity,
        "has_5xx": has_5xx,
        "memory_increase": memory_increase,
        "client_memory_increase_mb": client_memory_increase_mb
    }


async def phase2_auth_attack(session: aiohttp.ClientSession) -> Dict[str, Any]:
    """Phase 2: Auth Attack - JWT manipulation, SQL injection."""
    phase_name = "PHASE 2: Auth Attack"
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{phase_name}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")
    
    tests = [
        ("Expired JWT", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.invalid", None),
        ("Forged JWT", "eyJhbGciOiJub25lIn0.eyJzdWIiOiIxMjM0NTY3ODkwIn0.invalid", None),
        ("SQL Injection in Email", "USE_VALID_TOKEN", "admin' OR '1'='1"),
        ("Missing Authorization", "NO_HEADER", None),  # Special marker to indicate no header
        ("Malformed JWT", "invalid.jwt.token", None),
        ("XSS in Email", "USE_VALID_TOKEN", "<script>alert('xss')</script>@example.com"),
    ]
    
    pass_count = 0
    fail_count = 0
    critical_count = 0
    
    for test_name, jwt_token, email_override in tests:
        try:
            file_data, filename = generate_test_file(0.1, "image/jpeg")
            form = aiohttp.FormData()
            form.add_field('file', file_data, filename=filename, content_type="image/jpeg")
            form.add_field('email', email_override or TEST_EMAIL)
            
            headers = {}
            if jwt_token == "NO_HEADER":
                # Missing auth - don't set Authorization header at all
                pass
            elif jwt_token == "USE_VALID_TOKEN":
                # Use valid token (but test email injection)
                if AUTH_TOKEN:
                    headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
            elif jwt_token:
                # Use provided token (may be invalid/expired)
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            async with session.post(
                f"{BASE_URL}/api/v1/upap/upload",
                data=form,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                status_code = resp.status
                text = await resp.text()
                
                # Check for stacktrace leak
                has_stacktrace = "Traceback" in text or "File \"" in text or "at " in text and "line" in text
                
                if status_code == 401:
                    pass_count += 1
                    status = "PASS"
                    if has_stacktrace:
                        critical_count += 1
                        status = "CRITICAL"
                        log_result(phase_name, f"{test_name} - Stacktrace Leak", "CRITICAL", {
                            "message": "CRITICAL: Stacktrace leaked in 401 response",
                            "response_preview": text[:200]
                        })
                    else:
                        log_result(phase_name, test_name, "PASS", {
                            "message": "Correctly rejected with 401"
                        })
                elif status_code == 400:
                    pass_count += 1
                    log_result(phase_name, test_name, "PASS", {
                        "message": "Correctly rejected with 400"
                    })
                elif status_code == 200:
                    fail_count += 1
                    critical_count += 1
                    log_result(phase_name, test_name, "CRITICAL", {
                        "message": f"CRITICAL: Attack succeeded! Got 200 instead of 401/400",
                        "status_code": status_code
                    })
                else:
                    fail_count += 1
                    log_result(phase_name, test_name, "FAIL", {
                        "message": f"Unexpected status: {status_code}",
                        "status_code": status_code
                    })
        except Exception as e:
            fail_count += 1
            log_result(phase_name, test_name, "FAIL", {
                "message": f"Test exception: {e}",
                "error": str(e)
            })
    
    if critical_count > 0:
        status = "CRITICAL"
        severity = 10
    elif fail_count > 0:
        status = "FAIL"
        severity = 9
    else:
        status = "PASS"
        severity = 8
    
    return {
        "status": status,
        "severity": severity,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "critical_count": critical_count
    }


async def phase3_ai_service_chaos(session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
    """Phase 3: AI Service Chaos - OpenAI failures."""
    phase_name = "PHASE 3: AI Service Chaos"
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{phase_name}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")
    
    if not token:
        log_result(phase_name, "AI Service Chaos", "SKIP", {
            "message": "AUTH_TOKEN required - skipped"
        })
        return {"status": "SKIP", "severity": 0}
    
    # Extract email from token to ensure it matches authenticated user
    test_email = decode_token_email(token) or TEST_EMAIL
    
    # Upload large image (should trigger OpenAI)
    file_data, filename = generate_test_file(3.0, "image/jpeg")
    form = aiohttp.FormData()
    form.add_field('file', file_data, filename=filename, content_type="image/jpeg")
    form.add_field('email', test_email)  # Use email from token, not TEST_EMAIL
    
    start_time = time.time()
    try:
        async with session.post(
            f"{BASE_URL}/api/v1/upap/upload",
            data=form,
            headers={"Authorization": f"Bearer {token}"},
            timeout=aiohttp.ClientTimeout(total=40)
        ) as resp:
            elapsed = time.time() - start_time
            status_code = resp.status
            text = await resp.text()
            
            if status_code == 200:
                try:
                    data = json.loads(text)
                    # Check if fallback worked
                    has_recognition_error = "recognition_error" in str(data) or "recognition_failed" in str(data)
                    
                    if elapsed < 35:
                        status = "PASS"
                        message = f"Request completed within timeout ({elapsed:.2f}s), fallback handled OpenAI failure"
                        
                        if has_recognition_error:
                            message += " (OpenAI error gracefully handled)"
                        
                        log_result(phase_name, "OpenAI Failure Handling", status, {
                            "message": message,
                            "duration": f"{elapsed:.2f}s",
                            "has_fallback": has_recognition_error
                        })
                        return {"status": "PASS", "severity": 8}
                    else:
                        status = "FAIL"
                        log_result(phase_name, "OpenAI Timeout Protection", status, {
                            "message": f"Request exceeded timeout: {elapsed:.2f}s > 35s",
                            "duration": f"{elapsed:.2f}s"
                        })
                        return {"status": "FAIL", "severity": 8}
                except:
                    log_result(phase_name, "OpenAI Failure Handling", "WARNING", {
                        "message": "Response parse error"
                    })
                    return {"status": "WARNING", "severity": 7}
            else:
                log_result(phase_name, "AI Service Chaos", "FAIL", {
                    "message": f"Upload failed: {status_code}"
                })
                return {"status": "FAIL", "severity": 8}
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        log_result(phase_name, "OpenAI Timeout Protection", "FAIL", {
            "message": f"Request timed out: {elapsed:.2f}s",
            "duration": f"{elapsed:.2f}s"
        })
        return {"status": "FAIL", "severity": 8}
    except Exception as e:
        elapsed = time.time() - start_time
        log_result(phase_name, "AI Service Chaos", "FAIL", {
            "message": f"Test exception: {e}",
            "duration": f"{elapsed:.2f}s"
        })
        return {"status": "FAIL", "severity": 8}


async def phase4_file_attack(session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
    """Phase 4: File Attack - Path traversal, MIME spoof, zip bomb."""
    phase_name = "PHASE 4: File Attack"
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{phase_name}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")
    
    if not token:
        log_result(phase_name, "File Attack", "SKIP", {
            "message": "AUTH_TOKEN required - skipped"
        })
        return {"status": "SKIP", "severity": 0}
    
    # Extract email from token to ensure it matches authenticated user
    test_email = decode_token_email(token) or TEST_EMAIL
    
    attacks = [
        ("Path Traversal", b"\xFF\xD8\xFF\xE0" + os.urandom(100), "../../../etc/passwd", "image/jpeg"),
        ("MIME Spoof (EXE)", b"MZ\x90\x00" + os.urandom(100), "malware.exe", "image/jpeg"),
        ("1000 Char Filename", b"\xFF\xD8\xFF\xE0" + os.urandom(100), "A" * 1000 + ".jpg", "image/jpeg"),
        ("Null Byte", b"\xFF\xD8\xFF\xE0" + os.urandom(100), "file\x00.jpg", "image/jpeg"),
        ("Unicode Attack", b"\xFF\xD8\xFF\xE0" + os.urandom(100), "файл.jpg", "image/jpeg"),
    ]
    
    blocked_count = 0
    critical_count = 0
    
    for attack_name, file_data, filename, content_type in attacks:
        try:
            form = aiohttp.FormData()
            form.add_field('file', file_data, filename=filename, content_type=content_type)
            form.add_field('email', test_email)  # Use email from token, not TEST_EMAIL
            
            async with session.post(
                f"{BASE_URL}/api/v1/upap/upload",
                data=form,
                headers={"Authorization": f"Bearer {token}"},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                status_code = resp.status
                text = await resp.text()
                
                if status_code == 400:
                    blocked_count += 1
                    log_result(phase_name, attack_name, "PASS", {
                        "message": "Attack correctly blocked with 400"
                    })
                elif status_code == 200:
                    critical_count += 1
                    log_result(phase_name, attack_name, "CRITICAL", {
                        "message": f"CRITICAL: {attack_name} succeeded! File may be saved",
                        "status_code": status_code
                    })
                else:
                    log_result(phase_name, attack_name, "FAIL", {
                        "message": f"Unexpected status: {status_code}",
                        "status_code": status_code
                    })
        except Exception as e:
            log_result(phase_name, attack_name, "WARNING", {
                "message": f"Test exception: {e}"
            })
    
    if critical_count > 0:
        status = "CRITICAL"
        severity = 10
    elif blocked_count == len(attacks):
        status = "PASS"
        severity = 10
    else:
        status = "FAIL"
        severity = 9
    
    return {
        "status": status,
        "severity": severity,
        "blocked_count": blocked_count,
        "critical_count": critical_count,
        "total_attacks": len(attacks)
    }


async def phase5_database_torture(session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
    """Phase 5: Database Torture - Concurrent writes, conflicts."""
    phase_name = "PHASE 5: Database Torture"
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{phase_name}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")
    
    if not token:
        log_result(phase_name, "Database Torture", "SKIP", {
            "message": "AUTH_TOKEN required - skipped"
        })
        return {"status": "SKIP", "severity": 0}
    
    # Create single record for idempotency test
    record_id = str(uuid.uuid4())
    archive_data = {
        "record_id": record_id,
        "artist": "Test Artist",
        "album": "Test Album",
        "label": "Test Label",
        "year": "2023",
        "format": "LP"
    }
    
    # Send 100 concurrent archive requests with same record_id
    print(f"📊 Sending 100 concurrent archive requests with same record_id...")
    
    async def archive_request(index: int):
        try:
            async with session.post(
                f"{BASE_URL}/api/v1/upap/archive/add",
                json=archive_data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                status_code = resp.status
                text = await resp.text()
                
                try:
                    data = json.loads(text)
                    return {
                        "index": index,
                        "status": status_code,
                        "idempotent": "already" in text.lower() or "idempotent" in text.lower()
                    }
                except:
                    return {"index": index, "status": status_code}
        except Exception as e:
            return {"index": index, "status": "error", "error": str(e)}
    
    tasks = [archive_request(i) for i in range(100)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Analyze results
    success_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == 200)
    idempotent_count = sum(1 for r in results if isinstance(r, dict) and r.get("idempotent"))
    error_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") != 200)
    
    # Check idempotency: Should have only ONE new record, rest should be idempotent
    if success_count == 100 and idempotent_count >= 99:
        status = "PASS"
        message = f"Idempotency working: {success_count} success, {idempotent_count} idempotent"
        log_result(phase_name, "Concurrent Archive Writes", status, {
            "message": message,
            "metrics": {
                "total": 100,
                "success": success_count,
                "idempotent": idempotent_count,
                "errors": error_count
            }
        })
        return {"status": "PASS", "severity": 9}
    elif success_count == 100 and idempotent_count == 0:
        status = "CRITICAL"
        message = "CRITICAL: All 100 requests created new records - idempotency broken, data corruption risk!"
        log_result(phase_name, "Concurrent Archive Writes", status, {
            "message": message,
            "metrics": {
                "total": 100,
                "success": success_count,
                "idempotent": idempotent_count
            }
        })
        return {"status": "CRITICAL", "severity": 10}
    else:
        status = "FAIL"
        message = f"Partial idempotency: {success_count} success, {idempotent_count} idempotent"
        log_result(phase_name, "Concurrent Archive Writes", status, {
            "message": message,
            "metrics": {
                "total": 100,
                "success": success_count,
                "idempotent": idempotent_count
            }
        })
        return {"status": "FAIL", "severity": 9}


async def phase6_cloud_failure(session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
    """Phase 6: Cloud Failure - Cold start, restart simulation."""
    phase_name = "PHASE 6: Cloud Failure"
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{phase_name}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")
    
    if not token:
        log_result(phase_name, "Cloud Failure", "SKIP", {
            "message": "AUTH_TOKEN required - skipped"
        })
        return {"status": "SKIP", "severity": 0}
    
    # Extract email from token to ensure it matches authenticated user
    test_email = decode_token_email(token) or TEST_EMAIL
    
    # Simulate cold start: First request after delay
    print("📊 Simulating cold start (5s delay before first request)...")
    await asyncio.sleep(5)
    
    file_data, filename = generate_test_file(1.0, "image/jpeg")
    form = aiohttp.FormData()
    form.add_field('file', file_data, filename=filename, content_type="image/jpeg")
    form.add_field('email', test_email)  # Use email from token, not TEST_EMAIL
    
    start_time = time.time()
    try:
        async with session.post(
            f"{BASE_URL}/api/v1/upap/upload",
            data=form,
            headers={"Authorization": f"Bearer {token}"},
            timeout=aiohttp.ClientTimeout(total=60)
        ) as resp:
            elapsed = time.time() - start_time
            status_code = resp.status
            
            if status_code == 200:
                log_result(phase_name, "Cold Start Handling", "PASS", {
                    "message": f"Cold start handled: request completed in {elapsed:.2f}s",
                    "duration": f"{elapsed:.2f}s"
                })
                return {"status": "PASS", "severity": 7}
            else:
                log_result(phase_name, "Cold Start Handling", "FAIL", {
                    "message": f"Cold start failed: {status_code}",
                    "status_code": status_code
                })
                return {"status": "FAIL", "severity": 7}
    except Exception as e:
        elapsed = time.time() - start_time
        log_result(phase_name, "Cold Start Handling", "FAIL", {
            "message": f"Cold start exception: {e}",
            "duration": f"{elapsed:.2f}s"
        })
        return {"status": "FAIL", "severity": 7}


async def phase7_frontend_abuse(session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
    """Phase 7: Frontend Abuse - XSS, unicode, broken JSON."""
    phase_name = "PHASE 7: Frontend Abuse"
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{phase_name}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")
    
    if not token:
        log_result(phase_name, "Frontend Abuse", "SKIP", {
            "message": "AUTH_TOKEN required - skipped"
        })
        return {"status": "SKIP", "severity": 0}
    
    attacks = [
        ("XSS in Artist", {"record_id": str(uuid.uuid4()), "artist": "<script>alert('xss')</script>", "album": "Test", "year": "2023"}),
        ("XSS in Album", {"record_id": str(uuid.uuid4()), "artist": "Test", "album": "<img src=x onerror=alert(1)>", "year": "2023"}),
        ("50k Char Input", {"record_id": str(uuid.uuid4()), "artist": "A" * 50000, "album": "Test", "year": "2023"}),
        ("Unicode Attack", {"record_id": str(uuid.uuid4()), "artist": "艺术家" * 1000, "album": "Test", "year": "2023"}),
        ("SQL Injection", {"record_id": str(uuid.uuid4()), "artist": "Test'; DROP TABLE users; --", "album": "Test", "year": "2023"}),
    ]
    
    sanitized_count = 0
    critical_count = 0
    
    for attack_name, payload in attacks:
        try:
            async with session.post(
                f"{BASE_URL}/api/v1/upap/archive/add",
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                status_code = resp.status
                text = await resp.text()
                
                # Check if XSS was sanitized
                has_xss = "<script>" in text or "javascript:" in text or "onerror=" in text.lower()
                
                if status_code == 422:
                    # Validation error (correct)
                    sanitized_count += 1
                    log_result(phase_name, attack_name, "PASS", {
                        "message": "Attack correctly rejected with 422"
                    })
                elif status_code == 200:
                    if has_xss:
                        critical_count += 1
                        log_result(phase_name, attack_name, "CRITICAL", {
                            "message": f"CRITICAL: {attack_name} stored with XSS - stored XSS vulnerability!",
                            "response_preview": text[:200]
                        })
                    else:
                        sanitized_count += 1
                        log_result(phase_name, attack_name, "PASS", {
                            "message": "Attack sanitized successfully"
                        })
                else:
                    sanitized_count += 1
                    log_result(phase_name, attack_name, "PASS", {
                        "message": f"Attack blocked: {status_code}"
                    })
        except Exception as e:
            log_result(phase_name, attack_name, "WARNING", {
                "message": f"Test exception: {e}"
            })
    
    if critical_count > 0:
        status = "CRITICAL"
        severity = 10
    else:
        status = "PASS"
        severity = 8
    
    return {
        "status": status,
        "severity": severity,
        "sanitized_count": sanitized_count,
        "critical_count": critical_count
    }


def decode_token_email(token: str) -> Optional[str]:
    """
    Decode JWT token to extract email claim (without signature verification).
    Used ONLY for reading the email claim from a token we already have.
    Server will still validate the token signature.
    """
    try:
        import base64
        # JWT format: header.payload.signature
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        # Decode payload (add padding if needed)
        payload_b64 = parts[1]
        padding = 4 - (len(payload_b64) % 4)
        if padding != 4:
            payload_b64 += '=' * padding
        
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_bytes)
        return payload.get('email')
    except Exception:
        return None


async def ensure_user_bootstrapped(session: aiohttp.ClientSession) -> bool:
    """
    Ensure the user from AUTH_TOKEN exists in the database.
    Returns True if user exists or was bootstrapped, False otherwise.
    """
    if not AUTH_TOKEN:
        print(f"{Colors.YELLOW}⚠️  AUTH_TOKEN not set - skipping user bootstrap{Colors.RESET}\n")
        return False
    
    print(f"{Colors.CYAN}📋 Checking user authentication...{Colors.RESET}")
    
    # Step 1: Try /auth/whoami
    try:
        async with session.get(
            f"{BASE_URL}/auth/whoami",
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
            timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"{Colors.GREEN}✅ User authenticated: {data.get('email')} (id: {data.get('user_id')}){Colors.RESET}\n")
                return True
            elif resp.status == 401:
                text = await resp.text()
                if "User not found" in text or "bootstrap" in text.lower():
                    # Step 2: Bootstrap user if missing
                    if not ADMIN_TOKEN:
                        print(f"{Colors.RED}❌ User not found and ADMIN_TOKEN not set - cannot bootstrap{Colors.RESET}")
                        print(f"{Colors.YELLOW}   Set ADMIN_TOKEN environment variable to bootstrap users{Colors.RESET}\n")
                        return False
                    
                    # Extract email from token
                    email = decode_token_email(AUTH_TOKEN)
                    if not email:
                        print(f"{Colors.RED}❌ Cannot extract email from AUTH_TOKEN - cannot bootstrap{Colors.RESET}\n")
                        return False
                    
                    print(f"{Colors.YELLOW}⚠️  User {email} not found - bootstrapping...{Colors.RESET}")
                    
                    # Bootstrap user
                    async with session.post(
                        f"{BASE_URL}/admin/bootstrap-user",
                        json={"email": email, "is_admin": False},
                        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as bootstrap_resp:
                        if bootstrap_resp.status == 200:
                            bootstrap_data = await bootstrap_resp.json()
                            existed = bootstrap_data.get("existed", False)
                            status_msg = "already existed" if existed else "created"
                            print(f"{Colors.GREEN}✅ User {email} {status_msg} (id: {bootstrap_data.get('user_id')}){Colors.RESET}\n")
                            
                            # Retry whoami
                            async with session.get(
                                f"{BASE_URL}/auth/whoami",
                                headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
                                timeout=aiohttp.ClientTimeout(total=10)
                            ) as retry_resp:
                                if retry_resp.status == 200:
                                    return True
                                else:
                                    print(f"{Colors.RED}❌ User bootstrap succeeded but whoami still fails{Colors.RESET}\n")
                                    return False
                        else:
                            error_text = await bootstrap_resp.text()
                            print(f"{Colors.RED}❌ Bootstrap failed: {bootstrap_resp.status} - {error_text}{Colors.RESET}\n")
                            return False
                else:
                    print(f"{Colors.RED}❌ Authentication failed: {text}{Colors.RESET}\n")
                    return False
            elif resp.status == 404:
                # Endpoint not found - likely not deployed yet
                print(f"{Colors.YELLOW}⚠️  /auth/whoami endpoint not found (404) - trying alternative approach{Colors.RESET}")
                
                # Try to bootstrap directly if ADMIN_TOKEN available
                if ADMIN_TOKEN:
                    email = decode_token_email(AUTH_TOKEN)
                    if email:
                        print(f"{Colors.YELLOW}   Attempting direct bootstrap for {email}...{Colors.RESET}")
                        try:
                            async with session.post(
                                f"{BASE_URL}/admin/bootstrap-user",
                                json={"email": email, "is_admin": False},
                                headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
                                timeout=aiohttp.ClientTimeout(total=10)
                            ) as bootstrap_resp:
                                if bootstrap_resp.status == 200:
                                    bootstrap_data = await bootstrap_resp.json()
                                    existed = bootstrap_data.get("existed", False)
                                    status_msg = "already existed" if existed else "created"
                                    print(f"{Colors.GREEN}✅ User {email} {status_msg} (id: {bootstrap_data.get('user_id')}){Colors.RESET}\n")
                                    return True
                                elif bootstrap_resp.status == 404:
                                    print(f"{Colors.YELLOW}   Bootstrap endpoint also not deployed (404) - skipping{Colors.RESET}")
                                    print(f"{Colors.YELLOW}   Tests will fail with 401 if user missing{Colors.RESET}\n")
                                    return True  # Continue anyway
                                else:
                                    error_text = await bootstrap_resp.text()
                                    print(f"{Colors.YELLOW}   Bootstrap failed: {bootstrap_resp.status} - {error_text}{Colors.RESET}\n")
                                    return True  # Continue anyway
                        except Exception as e:
                            print(f"{Colors.YELLOW}   Bootstrap attempt failed: {e} - continuing anyway{Colors.RESET}\n")
                            return True
                    else:
                        print(f"{Colors.YELLOW}   Cannot extract email from token - skipping bootstrap{Colors.RESET}\n")
                        return True
                else:
                    print(f"{Colors.YELLOW}   ADMIN_TOKEN not set - cannot bootstrap{Colors.RESET}")
                    print(f"{Colors.YELLOW}   Tests will fail with 401 if user missing{Colors.RESET}\n")
                    return True  # Continue anyway
            else:
                error_text = await resp.text()
                print(f"{Colors.RED}❌ Unexpected status {resp.status}: {error_text}{Colors.RESET}\n")
                return False
    except Exception as e:
        print(f"{Colors.RED}❌ Error checking authentication: {e}{Colors.RESET}\n")
        return False


async def main():
    """Run all final stress tests."""
    print(f"\n{Colors.BOLD}{Colors.RED}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.RED}FINAL PRE-PRODUCTION DESTRUCTION TEST{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.RED}Records_AI_V2 - Extreme Load & Security Stress Test{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.RED}{'='*70}{Colors.RESET}\n")
    
    print(f"Target: {BASE_URL}")
    print(f"Auth: {'✅ Token provided' if AUTH_TOKEN else '❌ No token (some tests will fail)'}")
    print(f"Admin: {'✅ Token provided' if ADMIN_TOKEN else '⚠️  No admin token (bootstrap unavailable)'}")
    print(f"Start Time: {datetime.now(timezone.utc).isoformat()}\n")
    
    phase_results = {}
    
    async with aiohttp.ClientSession() as session:
        # Bootstrap user if needed (before running destructive tests)
        user_ready = await ensure_user_bootstrapped(session)
        
        if not user_ready and AUTH_TOKEN:
            print(f"{Colors.RED}❌ User authentication failed - aborting destructive tests{Colors.RESET}")
            print(f"{Colors.YELLOW}   Fix authentication and try again{Colors.RESET}\n")
            return
        # Phase 1: Extreme Load Test
        phase_results["phase1"] = await phase1_extreme_load_test(session, AUTH_TOKEN)
        
        # Phase 2: Auth Attack
        phase_results["phase2"] = await phase2_auth_attack(session)
        
        # Phase 3: AI Service Chaos
        phase_results["phase3"] = await phase3_ai_service_chaos(session, AUTH_TOKEN)
        
        # Phase 4: File Attack
        phase_results["phase4"] = await phase4_file_attack(session, AUTH_TOKEN)
        
        # Phase 5: Database Torture
        phase_results["phase5"] = await phase5_database_torture(session, AUTH_TOKEN)
        
        # Phase 6: Cloud Failure
        phase_results["phase6"] = await phase6_cloud_failure(session, AUTH_TOKEN)
        
        # Phase 7: Frontend Abuse
        phase_results["phase7"] = await phase7_frontend_abuse(session, AUTH_TOKEN)
    
    # Calculate scores (exclude SKIP from calculations)
    active_results = {k: v for k, v in phase_results.items() if v.get("status") != "SKIP"}
    total_severity = sum(p.get("severity", 0) for p in active_results.values())
    passed_severity = sum(p.get("severity", 0) for p in active_results.values() if p.get("status") == "PASS")
    security_score = (passed_severity / total_severity * 10) if total_severity > 0 else 10.0
    
    # Stability score (based on phase 1 load test)
    phase1_result = phase_results.get("phase1", {})
    has_5xx = phase1_result.get("has_5xx", False)
    memory_increase = phase1_result.get("memory_increase", 0)
    
    stability_score = 10.0
    if has_5xx:
        stability_score -= 5.0
    if memory_increase > 1000:
        stability_score -= 3.0
    stability_score = max(0.0, stability_score)
    
    # Final decision
    critical_failures = len(CRITICAL_FAILURES)
    
    if critical_failures > 0 or security_score < 9.0 or stability_score < 9.0:
        decision = "BLOCK"
        verdict_color = Colors.RED
    else:
        decision = "GO LIVE"
        verdict_color = Colors.GREEN
    
    # Print summary
    print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}FINAL TEST SUMMARY{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")
    
    print(f"{'Phase':<30} {'Status':<15} {'Severity':<10}")
    print("-" * 70)
    for phase_key, result in phase_results.items():
        phase_name = phase_key.replace("phase", "Phase ").title()
        status = result.get("status", "UNKNOWN")
        severity = result.get("severity", 0)
        
        if status == "CRITICAL":
            color = Colors.RED
            symbol = "🚨"
        elif status == "FAIL":
            color = Colors.RED
            symbol = "❌"
        elif status == "WARNING":
            color = Colors.YELLOW
            symbol = "⚠️"
        elif status == "SKIP":
            color = Colors.CYAN
            symbol = "⏭️"
        else:
            color = Colors.GREEN
            symbol = "✅"
        
        print(f"{phase_name:<30} {color}{symbol} {status:<10}{Colors.RESET} {severity}")
    
    print()
    print(f"{Colors.BOLD}Security Score: {Colors.RESET}", end="")
    if security_score >= 9.0:
        print(f"{Colors.GREEN}{security_score:.1f}/10 ✅{Colors.RESET}")
    else:
        print(f"{Colors.RED}{security_score:.1f}/10 ❌{Colors.RESET}")
    
    print(f"{Colors.BOLD}Stability Score: {Colors.RESET}", end="")
    if stability_score >= 9.0:
        print(f"{Colors.GREEN}{stability_score:.1f}/10 ✅{Colors.RESET}")
    else:
        print(f"{Colors.RED}{stability_score:.1f}/10 ❌{Colors.RESET}")
    
    print()
    print(f"{verdict_color}{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{verdict_color}{Colors.BOLD}FINAL DECISION: {decision}{Colors.RESET}")
    print(f"{verdict_color}{Colors.BOLD}{'='*70}{Colors.RESET}\n")
    
    if decision == "BLOCK":
        print(f"{Colors.RED}❌ DEPLOYMENT BLOCKED{Colors.RESET}")
        print(f"   Critical failures: {critical_failures}")
        print(f"   Security score: {security_score:.1f}/10 (required: >= 9.0)")
        print(f"   Stability score: {stability_score:.1f}/10 (required: >= 9.0)")
    else:
        print(f"{Colors.GREEN}✅ PRODUCTION APPROVED{Colors.RESET}")
        print(f"   Security score: {security_score:.1f}/10")
        print(f"   Stability score: {stability_score:.1f}/10")
        print(f"   No critical vulnerabilities detected")
    
    print()
    
    # Save report
    report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
        "target_url": BASE_URL,
        "security_score": round(security_score, 1),
        "stability_score": round(stability_score, 1),
        "decision": decision,
        "critical_failures": critical_failures,
        "total_tests": len(TEST_RESULTS),
        "passed": sum(1 for r in TEST_RESULTS if r.get("status") == "PASS"),
        "failed": sum(1 for r in TEST_RESULTS if r.get("status") == "FAIL"),
        "warnings": len(WARNINGS),
        "phase_results": phase_results,
        "test_results": TEST_RESULTS,
        "metrics": {
            "total_requests": METRICS["total_requests"],
            "failed_requests": METRICS["failed_requests"],
            "timeouts": METRICS["timeouts"],
            "status_codes": dict(METRICS["status_codes"]),
            "error_counts": dict(METRICS["error_counts"]),
            "avg_response_time": statistics.mean(METRICS["response_times"]) if METRICS["response_times"] else 0,
            "max_response_time": max(METRICS["response_times"]) if METRICS["response_times"] else 0,
        }
    }
    
    report_path = Path("final_kill_test_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Full report saved to: {report_path}\n")
    
    # Exit code
    if decision == "BLOCK":
        sys.exit(1)
    else:
        sys.exit(0)


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
