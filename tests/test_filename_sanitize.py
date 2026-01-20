#!/usr/bin/env python3
"""
P0-1: Path Traversal Fix - Unit Test
Tests filename sanitization function
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.file_validation import sanitize_filename, validate_path_stays_in_directory


def test_sanitize_filename():
    """Test filename sanitization."""
    print("Testing filename sanitization...")
    
    # Test 1: Normal filename
    assert sanitize_filename("test.jpg") == "test.jpg"
    print("  ✅ Normal filename preserved")
    
    # Test 2: Path traversal
    assert sanitize_filename("../../../etc/passwd") == "etc_passwd"
    print("  ✅ Path traversal removed")
    
    # Test 3: Nested path
    assert sanitize_filename("../../root/.ssh/id_rsa") == "root_.ssh_id_rsa"
    print("  ✅ Nested path sanitized")
    
    # Test 4: Null bytes
    assert sanitize_filename("test\x00.jpg") == "test.jpg"
    print("  ✅ Null bytes removed")
    
    # Test 5: Empty filename
    assert sanitize_filename("") == "upload.bin"
    print("  ✅ Empty filename uses default")
    
    # Test 6: Long filename
    long_name = "A" * 200 + ".jpg"
    result = sanitize_filename(long_name)
    assert len(result) <= 120
    print(f"  ✅ Long filename truncated ({len(result)} chars)")
    
    # Test 7: Path separators
    assert sanitize_filename("path/to/file.jpg") == "file.jpg"
    print("  ✅ Path separators handled")
    
    print("✅ All sanitization tests passed!")


def test_path_validation():
    """Test path stays in directory validation."""
    print("\nTesting path validation...")
    
    from pathlib import Path
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        temp_dir = base_dir / "storage" / "temp" / "user123"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Test 1: Valid path
        valid_file = temp_dir / "test.jpg"
        is_safe, error = validate_path_stays_in_directory(temp_dir.resolve(), valid_file.resolve())
        assert is_safe, f"Valid path rejected: {error}"
        print("  ✅ Valid path accepted")
        
        # Test 2: Path traversal attempt
        traversal_file = temp_dir / "../../etc/passwd"
        is_safe, error = validate_path_stays_in_directory(temp_dir.resolve(), traversal_file.resolve())
        assert not is_safe, "Path traversal not detected"
        print("  ✅ Path traversal detected")
        
        # Test 3: Absolute path outside
        if sys.platform != "win32":  # Skip on Windows
            outside_file = Path("/etc/passwd")
            is_safe, error = validate_path_stays_in_directory(temp_dir.resolve(), outside_file)
            assert not is_safe, "Outside path not detected"
            print("  ✅ Outside path detected")
    
    print("✅ All path validation tests passed!")


if __name__ == "__main__":
    print("="*50)
    print("P0-1: Path Traversal Fix - Unit Tests")
    print("="*50)
    
    try:
        test_sanitize_filename()
        test_path_validation()
        
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED")
        print("="*50)
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
