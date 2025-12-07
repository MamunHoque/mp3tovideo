"""
Frame extraction module using OpenCV.
Handles extracting frames from videos with scene detection.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Optional, Callable, Dict
from PIL import Image
import os


class FrameExtractor:
    """Handles frame extraction from videos."""
    
    def __init__(self, output_dir: str = "frames"):
        """
        Initialize frame extractor.
        
        Args:
            output_dir: Directory to save extracted frames
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_frames = []
        
    def extract_frames(
        self,
        video_path: str,
        fps: Optional[int] = 1,
        max_frames: Optional[int] = None,
        progress_callback: Optional[Callable[[Dict], None]] = None
    ) -> List[str]:
        """
        Extract frames from video at specified FPS.
        
        Args:
            video_path: Path to video file
            fps: Frames per second to extract (None for all frames)
            max_frames: Maximum number of frames to extract
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of paths to extracted frame images
        """
        if not os.path.exists(video_path):
            print(f"Video file not found: {video_path}")
            return []
        
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"Failed to open video: {video_path}")
                return []
            
            # Get video properties
            video_fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / video_fps if video_fps > 0 else 0
            
            # Calculate frame interval
            if fps:
                frame_interval = int(video_fps / fps)
            else:
                frame_interval = 1
            
            frame_count = 0
            extracted_count = 0
            self.extracted_frames = []
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Extract frame at specified interval
                if frame_count % frame_interval == 0:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Save frame
                    frame_path = self.output_dir / f"frame_{extracted_count:06d}.jpg"
                    pil_image = Image.fromarray(frame_rgb)
                    pil_image.save(frame_path, quality=95)
                    
                    self.extracted_frames.append(str(frame_path))
                    extracted_count += 1
                    
                    # Progress callback
                    if progress_callback:
                        progress_callback({
                            'status': 'extracting',
                            'current_frame': frame_count,
                            'total_frames': total_frames,
                            'extracted_count': extracted_count,
                            'percent': (frame_count / total_frames) * 100 if total_frames > 0 else 0,
                        })
                    
                    # Check max frames limit
                    if max_frames and extracted_count >= max_frames:
                        break
                
                frame_count += 1
            
            cap.release()
            
            if progress_callback:
                progress_callback({
                    'status': 'finished',
                    'extracted_count': extracted_count,
                })
            
            return self.extracted_frames
            
        except Exception as e:
            print(f"Error extracting frames: {e}")
            return []
    
    def extract_key_frames(
        self,
        video_path: str,
        threshold: float = 30.0,
        max_frames: Optional[int] = None,
        progress_callback: Optional[Callable[[Dict], None]] = None
    ) -> List[str]:
        """
        Extract key frames based on scene changes.
        
        Args:
            video_path: Path to video file
            threshold: Scene change detection threshold (higher = fewer scenes)
            max_frames: Maximum number of frames to extract
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of paths to extracted key frame images
        """
        if not os.path.exists(video_path):
            print(f"Video file not found: {video_path}")
            return []
        
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"Failed to open video: {video_path}")
                return []
            
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            frame_count = 0
            extracted_count = 0
            self.extracted_frames = []
            prev_frame = None
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert to grayscale for comparison
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Check if this is a key frame (scene change)
                is_key_frame = False
                if prev_frame is None:
                    is_key_frame = True  # First frame
                else:
                    # Calculate difference from previous frame
                    diff = cv2.absdiff(prev_frame, gray)
                    mean_diff = np.mean(diff)
                    
                    if mean_diff > threshold:
                        is_key_frame = True
                
                if is_key_frame:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Save frame
                    frame_path = self.output_dir / f"keyframe_{extracted_count:06d}.jpg"
                    pil_image = Image.fromarray(frame_rgb)
                    pil_image.save(frame_path, quality=95)
                    
                    self.extracted_frames.append(str(frame_path))
                    extracted_count += 1
                    
                    # Check max frames limit
                    if max_frames and extracted_count >= max_frames:
                        break
                
                prev_frame = gray
                frame_count += 1
                
                # Progress callback
                if progress_callback and frame_count % 30 == 0:
                    progress_callback({
                        'status': 'extracting',
                        'current_frame': frame_count,
                        'total_frames': total_frames,
                        'extracted_count': extracted_count,
                        'percent': (frame_count / total_frames) * 100 if total_frames > 0 else 0,
                    })
            
            cap.release()
            
            if progress_callback:
                progress_callback({
                    'status': 'finished',
                    'extracted_count': extracted_count,
                })
            
            return self.extracted_frames
            
        except Exception as e:
            print(f"Error extracting key frames: {e}")
            return []
    
    def get_extracted_frames(self) -> List[str]:
        """Get list of extracted frame paths."""
        return self.extracted_frames
    
    def clear_frames(self):
        """Clear all extracted frames."""
        try:
            for file in self.output_dir.glob("*.jpg"):
                file.unlink()
            self.extracted_frames = []
            return True
        except Exception as e:
            print(f"Error clearing frames: {e}")
            return False
    
    def get_frame_count(self) -> int:
        """Get number of extracted frames."""
        return len(self.extracted_frames)
