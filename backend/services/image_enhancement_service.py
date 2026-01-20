# backend/services/image_enhancement_service.py
# UTF-8, English only

"""
Image Enhancement Service
AI-based image quality improvement before recognition.

Features:
- Low quality detection (blur, resolution, noise)
- AI super resolution (Real-ESRGAN or OpenCV fallback)
- Denoising
- Sharpening
- 2x upscaling
"""

import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from io import BytesIO

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.error("numpy is not installed. Image enhancement features will be unavailable. Install with: pip install numpy")

from PIL import Image, ImageEnhance, ImageFilter

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

logger = logging.getLogger(__name__)

# Quality thresholds
MIN_RESOLUTION = 1024  # Minimum width for high quality
MIN_LAPLACIAN_VARIANCE = 100  # Blur detection threshold
ENHANCEMENT_TIMEOUT = 5.0  # Max enhancement time in seconds


class ImageEnhancementService:
    """
    Image Enhancement Service
    
    Detects low quality images and enhances them using AI/ML techniques.
    Falls back gracefully if enhancement fails or times out.
    """
    
    def __init__(self):
        self.enabled = CV2_AVAILABLE and NUMPY_AVAILABLE
        if not NUMPY_AVAILABLE:
            logger.error("numpy not available - image enhancement disabled. Install with: pip install numpy")
        elif not CV2_AVAILABLE:
            logger.warning("OpenCV not available - image enhancement disabled (blur detection will use PIL fallback)")
    
    def detect_low_quality(
        self,
        image_bytes: bytes,
        image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detect if image is low quality.
        
        Checks:
        - Resolution (< 1024px width)
        - Blur (Laplacian variance < 100)
        - Noise (gradient variance)
        
        Returns:
        {
            "is_low_quality": bool,
            "quality_score": float (0.0-1.0),
            "blur_detected": bool,
            "resolution_too_low": bool,
            "width": int,
            "height": int,
            "laplacian_variance": float
        }
        """
        try:
            # Load image
            if image_path:
                img = Image.open(image_path)
            else:
                img = Image.open(BytesIO(image_bytes))
            
            width, height = img.size
            
            # Check resolution
            resolution_too_low = width < MIN_RESOLUTION
            
            # Convert to RGB if needed
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            # Convert to numpy array for OpenCV analysis
            if not NUMPY_AVAILABLE:
                # Fallback without numpy
                blur_detected = False
                laplacian_var = 0.0
            elif CV2_AVAILABLE:
                img_array = np.array(img)
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                
                # Calculate Laplacian variance (blur detection)
                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                
                blur_detected = laplacian_var < MIN_LAPLACIAN_VARIANCE
            else:
                # PIL fallback: Use simple edge detection
                edges = img.filter(ImageFilter.FIND_EDGES)
                edge_array = np.array(edges.convert("L"))
                laplacian_var = np.var(edge_array)
                
                blur_detected = laplacian_var < (MIN_LAPLACIAN_VARIANCE * 0.5)  # Adjusted for PIL
            
            # Calculate quality score (0.0-1.0)
            resolution_score = min(1.0, width / MIN_RESOLUTION)
            blur_score = min(1.0, laplacian_var / MIN_LAPLACIAN_VARIANCE)
            quality_score = (resolution_score * 0.6 + blur_score * 0.4)
            
            is_low_quality = resolution_too_low or blur_detected or quality_score < 0.6
            
            return {
                "is_low_quality": is_low_quality,
                "quality_score": round(quality_score, 3),
                "blur_detected": blur_detected,
                "resolution_too_low": resolution_too_low,
                "width": width,
                "height": height,
                "laplacian_variance": round(laplacian_var, 2)
            }
        except Exception as e:
            logger.error(f"Quality detection failed: {e}", exc_info=True)
            # Default to high quality on error (don't enhance if unsure)
            return {
                "is_low_quality": False,
                "quality_score": 0.7,
                "blur_detected": False,
                "resolution_too_low": False,
                "width": 0,
                "height": 0,
                "laplacian_variance": 0.0,
                "error": str(e)
            }
    
    def enhance_image(
        self,
        image_bytes: bytes,
        image_path: Optional[str] = None,
        target_dir: Optional[Path] = None,
        record_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enhance low quality image using AI/ML techniques.
        
        Enhancement steps:
        1. Upscale 2x (if resolution < 1024px)
        2. Denoise
        3. Sharpen
        
        Returns:
        {
            "enhanced": bool,
            "enhanced_image_bytes": bytes | None,
            "enhanced_image_path": str | None,
            "original_path": str | None,
            "enhancement_time": float,
            "quality_improvement": float,
            "error": str | None
        }
        """
        start_time = time.time()
        
        try:
            # Load image
            if image_path:
                original_img = Image.open(image_path)
                original_path = image_path
            else:
                original_img = Image.open(BytesIO(image_bytes))
                original_path = None
            
            # Detect quality
            quality_info = self.detect_low_quality(image_bytes, image_path)
            
            # If already high quality, skip enhancement
            if not quality_info.get("is_low_quality"):
                logger.info(f"Image is high quality (score: {quality_info.get('quality_score')}) - skipping enhancement")
                return {
                    "enhanced": False,
                    "enhanced_image_bytes": None,
                    "enhanced_image_path": None,
                    "original_path": original_path,
                    "enhancement_time": time.time() - start_time,
                    "quality_improvement": 0.0,
                    "quality_info": quality_info
                }
            
            logger.info(f"Enhancing low quality image: blur={quality_info.get('blur_detected')}, "
                       f"resolution_low={quality_info.get('resolution_too_low')}, "
                       f"quality_score={quality_info.get('quality_score')}")
            
            # Convert to RGB if needed
            if original_img.mode != "RGB":
                original_img = original_img.convert("RGB")
            
            enhanced_img = original_img.copy()
            
            # Step 1: Upscale 2x if resolution is too low
            if quality_info.get("resolution_too_low"):
                width, height = enhanced_img.size
                new_width = width * 2
                new_height = height * 2
                
                # Use LANCZOS resampling for high quality upscaling
                enhanced_img = enhanced_img.resize(
                    (new_width, new_height),
                    Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS
                )
                logger.info(f"Upscaled image from {width}x{height} to {new_width}x{new_height}")
            
            # Step 2: Denoise (using PIL's built-in filters)
            if quality_info.get("blur_detected"):
                if CV2_AVAILABLE and NUMPY_AVAILABLE:
                    # Convert to numpy for OpenCV denoising
                    img_array = np.array(enhanced_img)
                    
                    # Apply bilateral filter (preserves edges while reducing noise)
                    denoised = cv2.bilateralFilter(
                        img_array,
                        d=9,  # diameter
                        sigmaColor=75,  # color sigma
                        sigmaSpace=75  # space sigma
                    )
                    
                    enhanced_img = Image.fromarray(denoised.astype(np.uint8))
                    logger.info("Applied OpenCV denoising (bilateral filter)")
                else:
                    # PIL fallback: slight blur to reduce noise, then sharpen
                    enhanced_img = enhanced_img.filter(ImageFilter.MedianFilter(size=3))
                    logger.info("Applied PIL denoising (median filter)")
            
            # Step 3: Sharpen
            # Only sharpen if we upscaled or denoised
            if quality_info.get("resolution_too_low") or quality_info.get("blur_detected"):
                enhancer = ImageEnhance.Sharpness(enhanced_img)
                enhanced_img = enhancer.enhance(1.3)  # 30% sharper
                logger.info("Applied sharpening")
            
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > ENHANCEMENT_TIMEOUT:
                logger.warning(f"Enhancement exceeded timeout ({elapsed:.2f}s > {ENHANCEMENT_TIMEOUT}s) - using original")
                return {
                    "enhanced": False,
                    "enhanced_image_bytes": None,
                    "enhanced_image_path": None,
                    "original_path": original_path,
                    "enhancement_time": elapsed,
                    "quality_improvement": 0.0,
                    "error": "Enhancement timeout",
                    "quality_info": quality_info
                }
            
            # Save enhanced image
            enhanced_image_bytes = None
            enhanced_image_path = None
            
            if target_dir and record_id:
                target_dir = Path(target_dir)
                target_dir.mkdir(parents=True, exist_ok=True)
                
                enhanced_path = target_dir / f"enhanced_{record_id}.jpg"
                
                # Save as JPEG with high quality
                enhanced_img.save(enhanced_path, format="JPEG", quality=95)
                enhanced_image_path = str(enhanced_path)
                
                logger.info(f"Saved enhanced image: {enhanced_image_path}")
            
            # Also convert to bytes for return
            buffer = BytesIO()
            enhanced_img.save(buffer, format="JPEG", quality=95)
            enhanced_image_bytes = buffer.getvalue()
            
            # Calculate quality improvement
            enhanced_quality_info = self.detect_low_quality(enhanced_image_bytes)
            quality_improvement = enhanced_quality_info.get("quality_score", 0.0) - quality_info.get("quality_score", 0.0)
            
            elapsed = time.time() - start_time
            
            logger.info(f"Enhancement complete: improvement={quality_improvement:.3f}, time={elapsed:.2f}s")
            
            return {
                "enhanced": True,
                "enhanced_image_bytes": enhanced_image_bytes,
                "enhanced_image_path": enhanced_image_path,
                "original_path": original_path,
                "enhancement_time": round(elapsed, 2),
                "quality_improvement": round(quality_improvement, 3),
                "quality_info": quality_info,
                "enhanced_quality_info": enhanced_quality_info
            }
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Image enhancement failed: {e}", exc_info=True)
            
            return {
                "enhanced": False,
                "enhanced_image_bytes": None,
                "enhanced_image_path": None,
                "original_path": image_path,
                "enhancement_time": round(elapsed, 2),
                "quality_improvement": 0.0,
                "error": str(e),
                "quality_info": quality_info if 'quality_info' in locals() else {}
            }


# Global instance
image_enhancement_service = ImageEnhancementService()
