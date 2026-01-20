# -*- coding: utf-8 -*-
"""
File Validation Utilities
Security helpers for file uploads: path sanitization, magic bytes, etc.
"""

import re
from pathlib import Path
from typing import Tuple, Optional, Dict


def sanitize_filename(filename: Optional[str], default: str = "upload.bin") -> str:
    """
    Sanitize filename to prevent path traversal attacks.
    
    Rules:
    - Keep only basename (strip directory path)
    - Remove null bytes
    - Replace path separators with underscore
    - Strip ".." sequences (multiple passes)
    - Remove Unicode control characters
    - Limit length to 120 chars
    - If empty after sanitization -> use default
    
    Args:
        filename: Original filename (may contain path traversal attempts)
        default: Default filename if sanitization results in empty string
        
    Returns:
        Sanitized filename safe for filesystem operations
    """
    if not filename:
        return default
    
    # Remove null bytes and other control characters
    safe = filename.replace("\x00", "")
    safe = "".join(c for c in safe if ord(c) >= 32 or c in "\n\r\t")
    
    # Extract basename only (strip directory path) - do this BEFORE path replacement
    safe = Path(safe).name
    
    # Replace path separators with underscore
    safe = safe.replace("/", "_").replace("\\", "_")
    
    # Remove ".." sequences (multiple passes to catch nested attempts)
    old_safe = ""
    while safe != old_safe:
        old_safe = safe
        safe = safe.replace("..", "")
        safe = safe.replace("./", "").replace(".\\", "")
    
    # Remove leading/trailing dots, spaces, and underscores
    safe = safe.strip(". _")
    
    # Limit length to 120 chars (filesystem-safe)
    if len(safe) > 120:
        name, ext = Path(safe).stem[:110], Path(safe).suffix[:10]
        safe = name + ext
    
    # Final check: if still contains dangerous patterns, reject
    if ".." in safe or "/" in safe or "\\" in safe or safe.startswith("."):
        safe = default
    
    # If empty after sanitization, use default
    if not safe:
        safe = default
    
    return safe


def validate_path_stays_in_directory(
    base_dir: Path,
    target_path: Path
) -> Tuple[bool, Optional[str]]:
    """
    Verify that target_path stays within base_dir (no path traversal).
    
    Args:
        base_dir: Base directory (must be absolute)
        target_path: Target file path (may be relative or absolute)
        
    Returns:
        (is_safe, error_message)
        - is_safe: True if path is safe, False if traversal detected
        - error_message: Error description if not safe, None if safe
    """
    try:
        # Resolve both paths to absolute
        base_resolved = base_dir.resolve()
        target_resolved = target_path.resolve()
        
        # Check if target is within base directory
        # target_resolved.parents should include base_resolved
        try:
            target_resolved.relative_to(base_resolved)
            return True, None
        except ValueError:
            # Path is outside base directory
            return False, f"Path traversal detected: {target_path} escapes {base_dir}"
            
    except Exception as e:
        return False, f"Path validation error: {str(e)}"


# Magic bytes for common file types
MAGIC_BYTES = {
    # Images
    b"\xFF\xD8\xFF": "image/jpeg",  # JPEG
    b"\x89PNG\r\n\x1a\n": "image/png",  # PNG
    b"RIFF": "image/webp",  # WebP (need more bytes to confirm)
    b"BM": "image/bmp",  # BMP
    b"GIF87a": "image/gif",  # GIF87a
    b"GIF89a": "image/gif",  # GIF89a
    
    # Audio
    b"ID3": "audio/mpeg",  # MP3 with ID3 tag
    b"\xFF\xFB": "audio/mpeg",  # MP3 frame sync
    b"\xFF\xF3": "audio/mpeg",  # MP3 frame sync
    b"\xFF\xF2": "audio/mpeg",  # MP3 frame sync
    b"RIFF": "audio/wav",  # WAV (need more bytes to confirm)
    b"fLaC": "audio/flac",  # FLAC
    b"FORM": "audio/aiff",  # AIFF (need more bytes to confirm)
}


def detect_file_type(content: bytes) -> Optional[str]:
    """
    Detect file type by magic bytes (file signature).
    
    Args:
        content: File content bytes (at least first 12 bytes recommended)
        
    Returns:
        Detected MIME type or None if unknown
    """
    if not content or len(content) < 4:
        return None
    
    # P0-2: Check for dangerous file types FIRST (EXE, DLL, etc.)
    # Windows EXE/DLL: MZ header
    if content[:2] == b"MZ":
        # This is a Windows executable - reject even if declared as image
        return "application/x-msdownload"  # EXE/DLL
    
    # ELF executable (Linux/Unix)
    if content[:4] == b"\x7fELF":
        return "application/x-executable"  # ELF executable
    
    # Mach-O executable (macOS)
    if content[:4] in [b"\xfe\xed\xfa\xce", b"\xce\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"\xcf\xfa\xed\xfe"]:
        return "application/x-mach-binary"  # Mach-O executable
    
    # Check magic bytes (ordered by specificity - longest first)
    checks = [
        (b"\x89PNG\r\n\x1a\n", "image/png"),
        (b"GIF89a", "image/gif"),
        (b"GIF87a", "image/gif"),
        (b"fLaC", "audio/flac"),
        (b"ID3", "audio/mpeg"),
    ]
    
    for magic, mime_type in checks:
        if content.startswith(magic):
            return mime_type
    
    # Check JPEG (variable length header)
    if content[:3] == b"\xFF\xD8\xFF":
        return "image/jpeg"
    
    # Check MP3 frame sync patterns
    if content[:2] in [b"\xFF\xFB", b"\xFF\xF3", b"\xFF\xF2"]:
        return "audio/mpeg"
    
    # Check BMP
    if content[:2] == b"BM":
        return "image/bmp"
    
    # Check RIFF-based formats (WAV, WebP)
    if len(content) >= 12 and content[:4] == b"RIFF":
        # Check format chunk
        format_type = content[8:12]
        if format_type == b"WAVE":
            return "audio/wav"
        elif format_type == b"WEBP":
            return "image/webp"
    
    # Check AIFF
    if len(content) >= 12 and content[:4] == b"FORM":
        if content[8:12] == b"AIFF":
            return "audio/aiff"
    
    return None


def validate_file_signature(
    content: bytes,
    declared_type: str
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate that file content matches declared MIME type.
    
    Args:
        content: File content bytes
        declared_type: MIME type declared in Content-Type header
        
    Returns:
        (is_valid, detected_type, error_message)
        - is_valid: True if signature matches declared type
        - detected_type: Detected MIME type from magic bytes
        - error_message: Error if mismatch, None if valid
    """
    if not content or len(content) < 4:
        return False, None, "File too small to detect type"
    
    detected_type = detect_file_type(content)
    
    # P0-2: Reject executable files immediately
    dangerous_types = [
        "application/x-msdownload",  # EXE/DLL
        "application/x-executable",  # ELF
        "application/x-mach-binary",  # Mach-O
    ]
    if detected_type in dangerous_types:
        return False, detected_type, (
            f"Dangerous file type detected: {detected_type}. "
            "Executable files are not allowed even if declared as image/audio."
        )
    
    if not detected_type:
        # Unknown file type - allow if declared type is in allowed list
        allowed_types = [
            "image/jpeg", "image/jpg", "image/png", "image/webp", "image/heic",
            "audio/mpeg", "audio/mp3", "audio/wav", "audio/flac", "audio/aiff"
        ]
        if declared_type in allowed_types:
            # Allow unknown signatures if declared type is allowed
            # (some formats may have variable headers)
            return True, None, None
        return False, None, f"Unknown file type. Declared: {declared_type}"
    
    # Normalize declared type for comparison
    declared_normalized = declared_type.lower().strip()
    detected_normalized = detected_type.lower().strip()
    
    # Allow if detected matches declared (with some flexibility)
    if detected_normalized == declared_normalized:
        return True, detected_type, None
    
    # Special cases: image/jpg vs image/jpeg, audio/mp3 vs audio/mpeg
    type_map = {
        "image/jpg": "image/jpeg",
        "audio/mp3": "audio/mpeg",
        "audio/wave": "audio/wav",
        "audio/x-wav": "audio/wav",
        "audio/x-flac": "audio/flac",
        "audio/x-aiff": "audio/aiff",
    }
    
    declared_mapped = type_map.get(declared_normalized, declared_normalized)
    
    if detected_normalized == declared_mapped:
        return True, detected_type, None
    
    # Mismatch detected
    return False, detected_type, (
        f"MIME type mismatch: declared '{declared_type}' "
        f"but file signature indicates '{detected_type}'. "
        "Possible MIME spoofing attempt."
    )
