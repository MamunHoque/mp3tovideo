"""
Video background processing module.
Handles loading, caching, and processing of video backgrounds.
"""

import cv2
import numpy as np
from PIL import Image
from typing import Optional, List
import os


class VideoBackground:
    """Handles video background loading and frame extraction."""
    
    def __init__(self, video_path: str, target_fps: int = 30):
        """
        Initialize video background processor.
        
        Args:
            video_path: Path to video file
            target_fps: Target frame rate for output video
        """
        self.video_path = video_path
        self.target_fps = target_fps
        self.video_capture = None
        self.video_fps = None
        self.total_frames = None
        self.duration = None
        self.frame_cache = []
        self.cache_loaded = False
        
    def load_video(self) -> bool:
        """
        Load video file and extract metadata.
        
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(self.video_path):
            return False
            
        try:
            self.video_capture = cv2.VideoCapture(self.video_path)
            if not self.video_capture.isOpened():
                return False
                
            self.video_fps = self.video_capture.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            self.duration = self.total_frames / self.video_fps if self.video_fps > 0 else 0
            
            return True
        except Exception as e:
            print(f"Error loading video: {e}")
            return False
    
    def get_duration(self) -> float:
        """Get video duration in seconds."""
        return self.duration if self.duration else 0.0
    
    def cache_frames(self, max_frames: Optional[int] = None) -> bool:
        """
        Cache video frames in memory for faster access.
        
        Args:
            max_frames: Maximum number of frames to cache (None for all)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.video_capture or not self.video_capture.isOpened():
            if not self.load_video():
                return False
        
        try:
            self.frame_cache = []
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            frame_count = 0
            max_to_cache = max_frames if max_frames else self.total_frames
            
            while frame_count < max_to_cache:
                ret, frame = self.video_capture.read()
                if not ret:
                    break
                    
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert to PIL Image
                pil_image = Image.fromarray(frame_rgb)
                self.frame_cache.append(pil_image)
                frame_count += 1
            
            self.cache_loaded = True
            return True
            
        except Exception as e:
            print(f"Error caching frames: {e}")
            return False
    
    def get_frame_at_time(self, time_seconds: float, target_size: tuple) -> Optional[Image.Image]:
        """
        Get video frame at specific time with looping support.
        
        Args:
            time_seconds: Time in seconds
            target_size: Target size (width, height) for the frame
            
        Returns:
            PIL Image or None if error
        """
        if self.duration == 0:
            return None
        
        # Loop video if time exceeds duration
        looped_time = time_seconds % self.duration
        
        # Calculate frame number
        frame_number = int(looped_time * self.video_fps)
        
        if self.cache_loaded and frame_number < len(self.frame_cache):
            # Get from cache
            frame = self.frame_cache[frame_number]
        else:
            # Read from video file
            frame = self._read_frame_from_video(frame_number)
            
        if frame:
            # Resize to target size
            return frame.resize(target_size, Image.Resampling.LANCZOS)
        
        return None
    
    def get_frame_at_frame_number(self, frame_number: int, audio_duration: float, 
                                   target_size: tuple) -> Optional[Image.Image]:
        """
        Get video frame for a specific output frame number with looping.
        
        Args:
            frame_number: Output video frame number
            audio_duration: Total audio duration in seconds
            target_size: Target size (width, height) for the frame
            
        Returns:
            PIL Image or None if error
        """
        # Calculate time for this frame
        time_seconds = frame_number / self.target_fps
        return self.get_frame_at_time(time_seconds, target_size)
    
    def _read_frame_from_video(self, frame_number: int) -> Optional[Image.Image]:
        """
        Read a specific frame from video file.
        
        Args:
            frame_number: Frame number to read
            
        Returns:
            PIL Image or None if error
        """
        if not self.video_capture or not self.video_capture.isOpened():
            if not self.load_video():
                return None
        
        try:
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = self.video_capture.read()
            
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return Image.fromarray(frame_rgb)
            
            return None
            
        except Exception as e:
            print(f"Error reading frame {frame_number}: {e}")
            return None
    
    def close(self):
        """Release video resources."""
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
        self.frame_cache = []
        self.cache_loaded = False
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()




