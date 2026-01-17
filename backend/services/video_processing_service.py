# -*- coding: utf-8 -*-
"""
Video Processing Service
Extracts best frame from video and converts to JPEG.
"""

import os
import cv2
import tempfile
import numpy as np
from uuid import uuid4
from pathlib import Path
from typing import Optional, Tuple
import io


class VideoProcessingService:
    """
    Service for processing video files.
    Extracts best frame and converts to JPEG for archive storage.
    """
    
    def __init__(self):
        self.storage_dir = Path("storage/uploads/videos")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_best_frame(
        self, 
        video_bytes: bytes, 
        video_filename: str = "video.mp4"
    ) -> Tuple[str, dict]:
        """
        Extract best frame from video using Laplacian variance (focus measure).
        Returns path to extracted JPEG and frame metadata.
        
        Args:
            video_bytes: Video file bytes
            video_filename: Original video filename (for extension detection)
            
        Returns:
            Tuple of (jpeg_path, metadata_dict)
        """
        # Create temporary video file
        temp_video = tempfile.NamedTemporaryFile(
            suffix=Path(video_filename).suffix or ".mp4",
            delete=False
        )
        temp_video.write(video_bytes)
        temp_video.close()
        
        try:
            # Open video
            cap = cv2.VideoCapture(temp_video.name)
            if not cap.isOpened():
                raise RuntimeError("Could not open video file")
            
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 30
            duration = total_frames / fps if fps > 0 else 0
            
            # Extract frames and calculate focus measure
            best_frame = None
            best_score = -1
            best_frame_number = 0
            frame_count = 0
            
            # Sample frames (every 0.5 seconds or at least 10 frames)
            frame_interval = max(1, int(fps * 0.5)) if fps > 0 else 1
            sample_count = min(30, total_frames // frame_interval) if total_frames > 0 else 30
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Sample frames for efficiency
                if frame_count % frame_interval == 0 or frame_count < 10:
                    # Calculate Laplacian variance (focus measure)
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                    
                    if laplacian_var > best_score:
                        best_score = laplacian_var
                        best_frame = frame.copy()
                        best_frame_number = frame_count
                
                frame_count += 1
                
                # Limit sampling
                if frame_count >= sample_count * frame_interval:
                    break
            
            cap.release()
            
            # If no frame found, try to read first frame
            if best_frame is None:
                cap = cv2.VideoCapture(temp_video.name)
                ret, best_frame = cap.read()
                cap.release()
                
                if not ret:
                    raise RuntimeError("Could not extract any frame from video")
            
            # Save best frame as JPEG
            jpeg_filename = f"{uuid4().hex}_frame.jpg"
            jpeg_path = self.storage_dir / jpeg_filename
            cv2.imwrite(str(jpeg_path), best_frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            
            metadata = {
                "video_filename": video_filename,
                "video_size_bytes": len(video_bytes),
                "total_frames": total_frames,
                "fps": fps,
                "duration_seconds": duration,
                "best_frame_number": best_frame_number,
                "focus_score": float(best_score),
                "jpeg_path": str(jpeg_path),
                "jpeg_size_bytes": os.path.getsize(jpeg_path)
            }
            
            return str(jpeg_path), metadata
            
        finally:
            # Cleanup temporary video file
            try:
                os.unlink(temp_video.name)
            except:
                pass
    
    def is_video_file(self, filename: str) -> bool:
        """Check if file is a video based on extension."""
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}
        return Path(filename).suffix.lower() in video_extensions
    
    def get_video_info(self, video_bytes: bytes, video_filename: str) -> dict:
        """Get basic video information without extracting frame."""
        temp_video = tempfile.NamedTemporaryFile(
            suffix=Path(video_filename).suffix or ".mp4",
            delete=False
        )
        temp_video.write(video_bytes)
        temp_video.close()
        
        try:
            cap = cv2.VideoCapture(temp_video.name)
            if not cap.isOpened():
                raise RuntimeError("Could not open video file")
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 30
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = total_frames / fps if fps > 0 else 0
            
            cap.release()
            
            return {
                "filename": video_filename,
                "size_bytes": len(video_bytes),
                "total_frames": total_frames,
                "fps": fps,
                "width": width,
                "height": height,
                "duration_seconds": duration
            }
        finally:
            try:
                os.unlink(temp_video.name)
            except:
                pass


# Global instance
video_processing_service = VideoProcessingService()
