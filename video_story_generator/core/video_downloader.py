"""
Video downloader module using yt-dlp.
Handles downloading videos from various social media platforms.
"""

import yt_dlp
import os
from typing import Optional, Dict, Callable
from pathlib import Path


class VideoDownloader:
    """Handles video downloading from social media platforms."""
    
    def __init__(self, output_dir: str = "downloads"):
        """
        Initialize video downloader.
        
        Args:
            output_dir: Directory to save downloaded videos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.last_download_path = None
        
    def download_video(
        self,
        url: str,
        filename: Optional[str] = None,
        progress_callback: Optional[Callable[[Dict], None]] = None
    ) -> Optional[str]:
        """
        Download video from URL.
        
        Args:
            url: Video URL (YouTube, TikTok, Instagram, etc.)
            filename: Optional custom filename (without extension)
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to downloaded video file or None if failed
        """
        try:
            # Prepare output template
            if filename:
                output_template = str(self.output_dir / f"{filename}.%(ext)s")
            else:
                output_template = str(self.output_dir / "%(title)s.%(ext)s")
            
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': output_template,
                'noplaylist': True,
                'quiet': False,
                'no_warnings': False,
                'merge_output_format': 'mp4',
            }
            
            # Add progress hook if callback provided
            if progress_callback:
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        progress_callback({
                            'status': 'downloading',
                            'downloaded_bytes': d.get('downloaded_bytes', 0),
                            'total_bytes': d.get('total_bytes', 0),
                            'speed': d.get('speed', 0),
                            'eta': d.get('eta', 0),
                            'percent': d.get('_percent_str', '0%'),
                        })
                    elif d['status'] == 'finished':
                        progress_callback({
                            'status': 'finished',
                            'filename': d.get('filename', ''),
                        })
                
                ydl_opts['progress_hooks'] = [progress_hook]
            
            # Download video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Get the downloaded file path
                if filename:
                    downloaded_file = self.output_dir / f"{filename}.mp4"
                else:
                    downloaded_file = self.output_dir / f"{info['title']}.mp4"
                
                self.last_download_path = str(downloaded_file)
                return self.last_download_path
                
        except Exception as e:
            print(f"Error downloading video: {e}")
            return None
    
    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        Get video information without downloading.
        
        Args:
            url: Video URL
            
        Returns:
            Dictionary with video info or None if failed
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'thumbnail': info.get('thumbnail', ''),
                    'description': info.get('description', ''),
                    'width': info.get('width', 0),
                    'height': info.get('height', 0),
                    'fps': info.get('fps', 0),
                    'format': info.get('format', 'Unknown'),
                }
                
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None
    
    def get_last_download_path(self) -> Optional[str]:
        """Get path to last downloaded video."""
        return self.last_download_path
    
    def clear_downloads(self):
        """Clear all downloaded videos."""
        try:
            for file in self.output_dir.glob("*"):
                if file.is_file():
                    file.unlink()
            return True
        except Exception as e:
            print(f"Error clearing downloads: {e}")
            return False
