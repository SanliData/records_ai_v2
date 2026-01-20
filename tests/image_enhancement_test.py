#!/usr/bin/env python3
"""
Image Enhancement Service Tests
Tests AI-based image quality improvement.
"""

import pytest
import os
import time
from pathlib import Path
from PIL import Image
import numpy as np

from backend.services.image_enhancement_service import image_enhancement_service


# Test data directory
TEST_DATA_DIR = Path("tests/test_data")
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)


def create_blurry_image(width=512, height=512) -> bytes:
    """Create a blurry test image."""
    img = Image.new("RGB", (width, height), color=(128, 128, 128))
    # Add some noise
    pixels = np.array(img)
    noise = np.random.randint(-20, 20, pixels.shape, dtype=np.int16)
    pixels = np.clip(pixels.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(pixels)
    
    # Apply blur
    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    
    buffer = bytes()
    import io
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def create_high_quality_image(width=2048, height=2048) -> bytes:
    """Create a high quality test image."""
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    # Add sharp edges
    pixels = np.array(img)
    pixels[100:200, 100:200] = [0, 0, 0]  # Black square
    pixels[300:400, 300:400] = [255, 0, 0]  # Red square
    img = Image.fromarray(pixels)
    
    buffer = bytes()
    import io
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def create_small_image(width=512, height=512) -> bytes:
    """Create a small test image."""
    img = Image.new("RGB", (width, height), color=(200, 200, 200))
    
    buffer = bytes()
    import io
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class TestImageEnhancement:
    """Test suite for Image Enhancement Service."""
    
    def test_detect_blurry_image(self):
        """Test blur detection for blurry images."""
        blurry_image = create_blurry_image()
        
        result = image_enhancement_service.detect_low_quality(blurry_image)
        
        assert result["is_low_quality"] is True
        assert result["blur_detected"] is True
        assert result["quality_score"] < 0.7
        print(f"✅ Blurry image detected: quality_score={result['quality_score']}, blur_detected={result['blur_detected']}")
    
    def test_detect_small_image(self):
        """Test resolution detection for small images."""
        small_image = create_small_image(width=512, height=512)
        
        result = image_enhancement_service.detect_low_quality(small_image)
        
        assert result["is_low_quality"] is True
        assert result["resolution_too_low"] is True
        assert result["width"] == 512
        print(f"✅ Small image detected: width={result['width']}, resolution_too_low={result['resolution_too_low']}")
    
    def test_detect_high_quality_image(self):
        """Test that high quality images are not flagged for enhancement."""
        hq_image = create_high_quality_image()
        
        result = image_enhancement_service.detect_low_quality(hq_image)
        
        assert result["is_low_quality"] is False
        assert result["quality_score"] >= 0.7
        print(f"✅ High quality image detected: quality_score={result['quality_score']}, is_low_quality={result['is_low_quality']}")
    
    def test_enhance_blurry_image(self):
        """Test enhancement of blurry images."""
        blurry_image = create_blurry_image()
        test_dir = TEST_DATA_DIR / "enhanced"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        result = image_enhancement_service.enhance_image(
            image_bytes=blurry_image,
            target_dir=test_dir,
            record_id="test_blurry"
        )
        
        assert result["enhanced"] is True
        assert result["quality_improvement"] > 0.0
        assert result["enhancement_time"] < 5.0  # Should be fast
        assert result.get("enhanced_image_path") is not None
        
        # Verify enhanced image exists
        if result.get("enhanced_image_path"):
            assert Path(result["enhanced_image_path"]).exists()
        
        print(f"✅ Blurry image enhanced: improvement={result['quality_improvement']}, time={result['enhancement_time']}s")
    
    def test_enhance_small_image(self):
        """Test upscaling of small images."""
        small_image = create_small_image(width=512, height=512)
        test_dir = TEST_DATA_DIR / "enhanced"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        result = image_enhancement_service.enhance_image(
            image_bytes=small_image,
            target_dir=test_dir,
            record_id="test_small"
        )
        
        assert result["enhanced"] is True
        assert result["enhancement_time"] < 5.0
        
        # Check if image was upscaled (width should be >= 1024)
        if result.get("enhanced_image_path"):
            enhanced_img = Image.open(result["enhanced_image_path"])
            assert enhanced_img.size[0] >= 1024  # Should be upscaled
            print(f"✅ Small image upscaled: {enhanced_img.size[0]}x{enhanced_img.size[1]}")
    
    def test_skip_high_quality_enhancement(self):
        """Test that high quality images skip enhancement."""
        hq_image = create_high_quality_image()
        test_dir = TEST_DATA_DIR / "enhanced"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        result = image_enhancement_service.enhance_image(
            image_bytes=hq_image,
            target_dir=test_dir,
            record_id="test_hq"
        )
        
        assert result["enhanced"] is False
        assert result["quality_improvement"] == 0.0
        print(f"✅ High quality image skipped enhancement: quality_score={result.get('quality_info', {}).get('quality_score', 0.0)}")
    
    def test_corrupted_image_fallback(self):
        """Test fallback behavior for corrupted images."""
        corrupted_image = b"This is not an image"
        test_dir = TEST_DATA_DIR / "enhanced"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        result = image_enhancement_service.enhance_image(
            image_bytes=corrupted_image,
            target_dir=test_dir,
            record_id="test_corrupted"
        )
        
        # Should gracefully fail and not crash
        assert result["enhanced"] is False
        assert "error" in result
        print(f"✅ Corrupted image handled gracefully: error={result.get('error', 'None')}")
    
    def test_performance_under_5s(self):
        """Test that enhancement completes within 5 seconds."""
        blurry_image = create_blurry_image(width=1024, height=1024)
        test_dir = TEST_DATA_DIR / "enhanced"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        start_time = time.time()
        result = image_enhancement_service.enhance_image(
            image_bytes=blurry_image,
            target_dir=test_dir,
            record_id="test_performance"
        )
        elapsed = time.time() - start_time
        
        assert elapsed < 5.5  # Allow small buffer
        assert result["enhancement_time"] < 5.0
        
        print(f"✅ Performance test passed: elapsed={elapsed:.2f}s, enhancement_time={result['enhancement_time']}s")
    
    def test_enhancement_timeout_protection(self):
        """Test that enhancement respects timeout (if we had a slow operation)."""
        # Create a reasonable size image that should process quickly
        test_image = create_blurry_image(width=800, height=800)
        test_dir = TEST_DATA_DIR / "enhanced"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        result = image_enhancement_service.enhance_image(
            image_bytes=test_image,
            target_dir=test_dir,
            record_id="test_timeout"
        )
        
        # Should complete within timeout or return original
        assert result["enhancement_time"] < 5.5  # Small buffer
        
        if result.get("error") == "Enhancement timeout":
            assert result["enhanced"] is False
            print(f"✅ Timeout protection working: returned original on timeout")
        else:
            assert result["enhancement_time"] < 5.0
            print(f"✅ Enhancement completed within timeout: {result['enhancement_time']}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
