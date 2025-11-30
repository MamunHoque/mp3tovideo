"""
Video generation module for MP3 Spectrum Visualizer.
Handles frame generation, spectrum visualization, and video assembly.
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import ffmpeg
from typing import Tuple, Optional, Dict, Any
import tempfile
import shutil

from core.audio_processor import AudioProcessor
from core.effects import (
    apply_blur, apply_vignette, apply_bw, fit_background,
    apply_strobe, apply_background_animation
)


class VideoGenerator:
    """Generates video files with spectrum visualization."""
    
    def __init__(self, audio_processor: AudioProcessor, settings: Dict[str, Any]):
        """
        Initialize video generator.
        
        Args:
            audio_processor: AudioProcessor instance
            settings: Settings dictionary
        """
        self.audio_processor = audio_processor
        self.settings = settings
        self.width = settings.get('video_width', 1920)
        self.height = settings.get('video_height', 1080)
        self.frame_rate = settings.get('frame_rate', 30)
        self.temp_dir = None
    
    def _create_temp_dir(self) -> str:
        """Create temporary directory for frames."""
        if self.temp_dir is None:
            self.temp_dir = tempfile.mkdtemp(prefix='spectrum_viz_')
        return self.temp_dir
    
    def _cleanup_temp_dir(self) -> None:
        """Clean up temporary directory."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
    
    def _draw_spectrum_bars(self, bands: np.ndarray, width: int, height: int) -> Image.Image:
        """
        Draw spectrum bars visualization.
        
        Args:
            bands: Frequency band magnitudes
            width: Image width
            height: Image height
            
        Returns:
            PIL Image with spectrum bars
        """
        num_bands = len(bands)
        bar_width = width // num_bands
        bar_spacing = 2
        
        # Create image
        spectrum_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(spectrum_img)
        
        # Normalize bands
        if np.max(bands) > 0:
            normalized_bands = bands / np.max(bands)
        else:
            normalized_bands = bands
        
        # Draw bars
        for i, magnitude in enumerate(normalized_bands):
            bar_height = int(magnitude * height * 0.8)  # Use 80% of height
            x = i * bar_width + bar_spacing
            
            # Color gradient: low freq = red, mid = green, high = blue
            if i < num_bands / 3:
                # Low frequency - red to yellow
                r = 255
                g = int(255 * (i / (num_bands / 3)))
                b = 0
            elif i < num_bands * 2 / 3:
                # Mid frequency - yellow to cyan
                r = int(255 * (1 - (i - num_bands / 3) / (num_bands / 3)))
                g = 255
                b = int(255 * ((i - num_bands / 3) / (num_bands / 3)))
            else:
                # High frequency - cyan to blue
                r = 0
                g = int(255 * (1 - (i - num_bands * 2 / 3) / (num_bands / 3)))
                b = 255
            
            color = (r, g, b, 255)
            
            # Draw bar from bottom
            y1 = height - bar_height
            y2 = height
            draw.rectangle([x, y1, x + bar_width - bar_spacing, y2], fill=color)
        
        return spectrum_img
    
    def _load_background(self) -> Optional[Image.Image]:
        """Load and prepare background image."""
        bg_path = self.settings.get('background_path', '')
        if not bg_path or not os.path.exists(bg_path):
            # Create default black background
            return Image.new('RGB', (self.width, self.height), (0, 0, 0))
        
        try:
            bg = Image.open(bg_path).convert('RGB')
            fit_mode = self.settings.get('background_fit', 'stretch')
            bg = fit_background(bg, (self.width, self.height), fit_mode)
            
            # Apply effects
            if self.settings.get('background_bw', False):
                bg = apply_bw(bg)
            
            blur_intensity = self.settings.get('background_blur', 0)
            if blur_intensity > 0:
                bg = apply_blur(bg, blur_intensity)
            
            vignette_intensity = self.settings.get('vignette_intensity', 0)
            if vignette_intensity > 0:
                bg = apply_vignette(bg, vignette_intensity)
            
            return bg
        except Exception as e:
            print(f"Error loading background: {e}")
            return Image.new('RGB', (self.width, self.height), (0, 0, 0))
    
    def _add_text_overlay(self, image: Image.Image, text: str, position: str = 'center',
                         color: Tuple[int, int, int] = (255, 255, 255)) -> Image.Image:
        """
        Add text overlay to image.
        
        Args:
            image: Base image
            text: Text to add
            position: Position ('center', 'top', 'bottom', etc.)
            color: Text color (RGB)
            
        Returns:
            Image with text overlay
        """
        if not text:
            return image
        
        draw = ImageDraw.Draw(image)
        
        # Try to use a nice font, fallback to default
        try:
            font_size = min(self.height // 20, 72)
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", min(self.height // 20, 72))
            except:
                font = ImageFont.load_default()
        
        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate position
        if position == 'center':
            x = (self.width - text_width) // 2
            y = (self.height - text_height) // 2
        elif position == 'top':
            x = (self.width - text_width) // 2
            y = 50
        elif position == 'bottom':
            x = (self.width - text_width) // 2
            y = self.height - text_height - 50
        else:
            x = (self.width - text_width) // 2
            y = (self.height - text_height) // 2
        
        # Draw text with outline for visibility
        outline_color = (0, 0, 0)
        for adj in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            draw.text((x + adj[0], y + adj[1]), text, font=font, fill=outline_color)
        draw.text((x, y), text, font=font, fill=color)
        
        return image
    
    def _add_logo(self, image: Image.Image, logo_path: str) -> Image.Image:
        """
        Add logo overlay to image.
        
        Args:
            image: Base image
            logo_path: Path to logo image
            
        Returns:
            Image with logo overlay
        """
        if not logo_path or not os.path.exists(logo_path):
            return image
        
        try:
            logo = Image.open(logo_path).convert('RGBA')
            # Resize logo to reasonable size (10% of height)
            logo_size = int(self.height * 0.1)
            logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # Position in top-right corner
            x = self.width - logo.width - 20
            y = 20
            
            # Paste with alpha
            image.paste(logo, (x, y), logo)
            return image
        except Exception as e:
            print(f"Error adding logo: {e}")
            return image
    
    def generate_frame(self, frame_number: int) -> Image.Image:
        """
        Generate a single video frame.
        
        Args:
            frame_number: Frame number (0-indexed)
            
        Returns:
            PIL Image for the frame
        """
        # Load background
        frame = self._load_background()
        
        # Apply background animation
        animation_type = self.settings.get('background_animation', 'none')
        total_frames = int(self.audio_processor.get_duration() * self.frame_rate)
        frame = apply_background_animation(frame, frame_number, animation_type, total_frames)
        
        # Get spectrum data
        num_bands = 64
        bands = self.audio_processor.get_frame_bands(frame_number, num_bands, self.frame_rate)
        spectrum_data = self.audio_processor.get_frame_spectrum(frame_number, self.frame_rate)
        
        # Draw spectrum bars
        spectrum_img = self._draw_spectrum_bars(bands, self.width, self.height)
        
        # Composite spectrum over background
        frame = Image.alpha_composite(frame.convert('RGBA'), spectrum_img)
        frame = frame.convert('RGB')
        
        # Apply strobe effect
        if self.settings.get('strobe_enabled', False):
            strobe_color = tuple(self.settings.get('strobe_color', [255, 255, 255]))
            frame = apply_strobe(frame, spectrum_data, strobe_color)
        
        # Add text overlay
        text_overlay = self.settings.get('text_overlay', '')
        if text_overlay:
            text_color = tuple(self.settings.get('text_color', [255, 255, 255]))
            text_position = self.settings.get('text_position', 'center')
            frame = self._add_text_overlay(frame, text_overlay, text_position, text_color)
        
        # Add logo
        logo_path = self.settings.get('logo_path', '')
        if logo_path:
            frame = self._add_logo(frame, logo_path)
        
        return frame
    
    def generate_frames(self, output_dir: str, start_frame: int = 0, 
                       end_frame: Optional[int] = None, progress_callback=None) -> int:
        """
        Generate all video frames.
        
        Args:
            output_dir: Directory to save frames
            start_frame: Starting frame number
            end_frame: Ending frame number (None for all frames)
            progress_callback: Callback function(frame_number, total_frames)
            
        Returns:
            Number of frames generated
        """
        duration = self.audio_processor.get_duration()
        total_frames = int(duration * self.frame_rate)
        
        if end_frame is None:
            end_frame = total_frames
        
        end_frame = min(end_frame, total_frames)
        
        for frame_num in range(start_frame, end_frame):
            frame = self.generate_frame(frame_num)
            frame_path = os.path.join(output_dir, f'frame_{frame_num:06d}.png')
            frame.save(frame_path)
            
            if progress_callback:
                progress_callback(frame_num - start_frame, end_frame - start_frame)
        
        return end_frame - start_frame
    
    def assemble_video(self, frames_dir: str, output_path: str, audio_path: str) -> bool:
        """
        Assemble frames into video using ffmpeg.
        
        Args:
            frames_dir: Directory containing frame images
            output_path: Output video path
            audio_path: Path to audio file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get frame pattern
            frame_pattern = os.path.join(frames_dir, 'frame_%06d.png')
            
            # Create ffmpeg input for frames
            frame_input = ffmpeg.input(frame_pattern, framerate=self.frame_rate)
            
            # Create ffmpeg input for audio
            audio_input = ffmpeg.input(audio_path)
            
            # Combine video and audio
            output = ffmpeg.output(
                frame_input.video,
                audio_input.audio,
                output_path,
                vcodec='libx264',
                acodec='aac',
                pix_fmt='yuv420p',
                **{'b:v': '5000k', 'b:a': '192k'}
            )
            
            # Overwrite output file if exists
            output = ffmpeg.overwrite_output(output)
            
            # Run ffmpeg
            ffmpeg.run(output, quiet=True, overwrite_output=True)
            
            return True
        except Exception as e:
            print(f"Error assembling video: {e}")
            return False
    
    def generate_video(self, output_path: str, progress_callback=None, 
                      preview_seconds: Optional[int] = None) -> bool:
        """
        Generate complete video file.
        
        Args:
            output_path: Output video file path
            progress_callback: Callback function(current, total) for progress
            preview_seconds: If specified, only generate this many seconds (for preview)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create temp directory for frames
            temp_dir = self._create_temp_dir()
            
            # Calculate frame range
            duration = self.audio_processor.get_duration()
            if preview_seconds:
                duration = min(duration, preview_seconds)
            
            total_frames = int(duration * self.frame_rate)
            
            # Generate frames
            if progress_callback:
                progress_callback(0, total_frames + 1)
            
            self.generate_frames(temp_dir, 0, total_frames, 
                               lambda f, t: progress_callback(f + 1, total_frames + 1) if progress_callback else None)
            
            # Assemble video
            if progress_callback:
                progress_callback(total_frames, total_frames + 1)
            
            success = self.assemble_video(temp_dir, output_path, self.audio_processor.audio_path)
            
            # Cleanup
            self._cleanup_temp_dir()
            
            if progress_callback:
                progress_callback(total_frames + 1, total_frames + 1)
            
            return success
        except Exception as e:
            print(f"Error generating video: {e}")
            self._cleanup_temp_dir()
            return False

