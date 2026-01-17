# -*- coding: utf-8 -*-
"""
Multi-Record Detection Service
Sherlock Holmes mode: Detects multiple vinyl records in a single image/video.
Uses AI vision to find and isolate each record, even if partially visible.
"""

import cv2
import numpy as np
from PIL import Image
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import base64
import os
import uuid
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class MultiRecordDetectionService:
    """
    Service for detecting multiple vinyl records in images/videos.
    AI-powered detection with Sherlock Holmes mode for partial/incomplete records.
    """
    
    def __init__(self):
        self.min_record_size = 200  # Minimum expected record diameter in pixels
        self.max_overlap_ratio = 0.3  # Maximum overlap allowed between detections
    
    def detect_records_in_image(
        self, 
        image_path: str, 
        raw_bytes: Optional[bytes] = None
    ) -> List[Dict]:
        """
        Detect all vinyl records in an image using AI vision.
        
        Returns list of detected records with bounding boxes:
        [
            {
                "record_id": "uuid",
                "bbox": {"x": 0, "y": 0, "width": 100, "height": 100},
                "crop_path": "/path/to/cropped_image.jpg",
                "confidence": 0.95,
                "detection_method": "ai_vision"
            },
            ...
        ]
        """
        try:
            # Method 1: AI Vision Detection (Primary - Sherlock Holmes mode)
            ai_detections = self._detect_with_ai_vision(image_path, raw_bytes)
            
            # Method 2: Computer Vision Fallback (Hough Circles for circular records)
            cv_detections = self._detect_with_cv(image_path)
            
            # Merge and deduplicate detections (AI takes priority)
            merged = self._merge_detections(ai_detections, cv_detections)
            
            # Crop each detected record
            cropped_records = []
            for i, detection in enumerate(merged):
                crop_result = self._crop_record(image_path, detection, record_index=i)
                if crop_result:
                    detection.update(crop_result)
                    cropped_records.append(detection)
            
            return cropped_records
            
        except Exception as e:
            # Fallback: Return entire image as single record
            return [{
                "record_id": str(uuid.uuid4()) if 'uuid' in globals() else "fallback-1",
                "bbox": {"x": 0, "y": 0, "width": 0, "height": 0},  # Full image
                "crop_path": image_path,
                "confidence": 0.5,
                "detection_method": "fallback",
                "error": str(e)
            }]
    
    def _detect_with_ai_vision(
        self, 
        image_path: str, 
        raw_bytes: Optional[bytes] = None
    ) -> List[Dict]:
        """
        Use OpenAI Vision to detect multiple vinyl records.
        Sherlock Holmes mode: Finds records even if partially visible or incomplete.
        """
        try:
            # Encode image
            if raw_bytes:
                image_b64 = base64.b64encode(raw_bytes).decode("utf-8")
            else:
                with open(image_path, "rb") as f:
                    image_b64 = base64.b64encode(f.read()).decode("utf-8")
            
            prompt = (
                "You are Sherlock Holmes, an expert at finding vinyl records in images.\n"
                "Your task is to detect ALL vinyl records in this image, even if:\n"
                "- They are partially visible or cut off\n"
                "- They are at different angles or perspectives\n"
                "- They overlap with each other\n"
                "- The image quality is poor\n"
                "- Only labels or parts of records are visible\n\n"
                "For EACH record you find, return:\n"
                "- bbox: bounding box coordinates {x, y, width, height} in pixels\n"
                "- confidence: how confident you are (0.0-1.0)\n"
                "- notes: any visible text or distinguishing features\n\n"
                "Return a JSON array of detections:\n"
                "[{\"bbox\": {\"x\": 0, \"y\": 0, \"width\": 200, \"height\": 200}, \"confidence\": 0.95, \"notes\": \"label visible\"}, ...]\n"
                "If no records found, return empty array []."
            )
            
            response = client.chat.completions.create(
                model="gpt-4o",  # Use vision-capable model
                messages=[
                    {
                        "role": "system",
                        "content": "You respond ONLY with valid JSON array and no extra text."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_b64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1,  # Low temperature for consistent detection
                max_tokens=2000
            )
            
            import json
            raw = response.choices[0].message.content
            detections = json.loads(raw)
            
            if not isinstance(detections, list):
                detections = []
            
            # Add metadata to each detection
            for i, detection in enumerate(detections):
                detection["record_id"] = f"ai-{i}"
                detection["detection_method"] = "ai_vision_sherlock"
            
            return detections
            
        except Exception as e:
            print(f"AI vision detection error: {e}")
            return []
    
    def _detect_with_cv(self, image_path: str) -> List[Dict]:
        """
        Computer vision fallback: Detect circular objects (records) using Hough Circles.
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return []
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape
            
            # Detect circles (records are typically circular)
            circles = cv2.HoughCircles(
                gray,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=int(min(width, height) * 0.3),
                param1=50,
                param2=30,
                minRadius=self.min_record_size // 2,
                maxRadius=max(width, height) // 2
            )
            
            detections = []
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                for i, (x, y, r) in enumerate(circles):
                    detections.append({
                        "record_id": f"cv-{i}",
                        "bbox": {
                            "x": max(0, x - r),
                            "y": max(0, y - r),
                            "width": min(width - x + r, r * 2),
                            "height": min(height - y + r, r * 2)
                        },
                        "confidence": 0.7,
                        "detection_method": "hough_circles"
                    })
            
            return detections
            
        except Exception as e:
            print(f"CV detection error: {e}")
            return []
    
    def _merge_detections(
        self, 
        ai_detections: List[Dict], 
        cv_detections: List[Dict]
    ) -> List[Dict]:
        """
        Merge AI and CV detections, removing overlaps.
        AI detections take priority.
        """
        merged = list(ai_detections)  # Start with AI detections
        
        # Add CV detections that don't overlap significantly with AI
        for cv_det in cv_detections:
            overlaps = False
            for ai_det in ai_detections:
                if self._bboxes_overlap(cv_det["bbox"], ai_det["bbox"], self.max_overlap_ratio):
                    overlaps = True
                    break
            
            if not overlaps:
                merged.append(cv_det)
        
        # Sort by confidence (highest first)
        merged.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        return merged
    
    def _bboxes_overlap(self, bbox1: Dict, bbox2: Dict, max_ratio: float) -> bool:
        """Check if two bounding boxes overlap by more than max_ratio."""
        x1, y1, w1, h1 = bbox1["x"], bbox1["y"], bbox1["width"], bbox1["height"]
        x2, y2, w2, h2 = bbox2["x"], bbox2["y"], bbox2["width"], bbox2["height"]
        
        # Calculate intersection
        x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
        y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
        overlap_area = x_overlap * y_overlap
        
        # Calculate union
        area1 = w1 * h1
        area2 = w2 * h2
        union_area = area1 + area2 - overlap_area
        
        if union_area == 0:
            return False
        
        overlap_ratio = overlap_area / union_area
        return overlap_ratio > max_ratio
    
    def _crop_record(
        self, 
        image_path: str, 
        detection: Dict, 
        record_index: int
    ) -> Optional[Dict]:
        """
        Crop a detected record from the image.
        Returns dict with crop_path.
        """
        try:
            bbox = detection.get("bbox")
            if not bbox:
                return None
            
            x = bbox.get("x", 0)
            y = bbox.get("y", 0)
            width = bbox.get("width", 0)
            height = bbox.get("height", 0)
            
            # Load image
            img = Image.open(image_path).convert("RGB")
            img_width, img_height = img.size
            
            # Ensure bbox is within image bounds
            x = max(0, min(x, img_width))
            y = max(0, min(y, img_height))
            width = min(width, img_width - x)
            height = min(height, img_height - y)
            
            if width <= 0 or height <= 0:
                return None
            
            # Crop
            cropped = img.crop((x, y, x + width, y + height))
            
            # Save cropped image
            image_path_obj = Path(image_path)
            crop_path = image_path_obj.parent / f"{image_path_obj.stem}_record_{record_index}.jpg"
            cropped.save(str(crop_path), "JPEG", quality=90)
            
            return {
                "crop_path": str(crop_path),
                "crop_bbox": {"x": x, "y": y, "width": width, "height": height}
            }
            
        except Exception as e:
            print(f"Crop error: {e}")
            return None


# Global instance
multi_record_detection_service = MultiRecordDetectionService()
