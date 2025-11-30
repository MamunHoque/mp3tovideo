"""
Visual effects module for MP3 Spectrum Visualizer.
Handles background effects, animations, and strobe effects.
"""

import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from typing import Tuple, Optional


def apply_blur(image: Image.Image, intensity: float) -> Image.Image:
    """
    Apply Gaussian blur to an image.
    
    Args:
        image: PIL Image to blur
        intensity: Blur intensity (0.0 to 100.0)
        
    Returns:
        Blurred PIL Image
    """
    if intensity <= 0:
        return image
    
    # Convert intensity (0-100) to radius (0-20)
    radius = intensity / 5.0
    return image.filter(ImageFilter.GaussianBlur(radius=radius))


def apply_vignette(image: Image.Image, intensity: float) -> Image.Image:
    """
    Apply vignette effect (darken edges) to an image.
    
    Args:
        image: PIL Image to apply vignette to
        intensity: Vignette intensity (0.0 to 100.0)
        
    Returns:
        Image with vignette effect
    """
    if intensity <= 0:
        return image
    
    width, height = image.size
    center_x, center_y = width / 2, height / 2
    max_distance = np.sqrt(center_x**2 + center_y**2)
    
    # Convert image to numpy array
    img_array = np.array(image, dtype=np.float32)
    
    # Create vignette mask
    y, x = np.ogrid[:height, :width]
    distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
    mask = 1.0 - (distance / max_distance) * (intensity / 100.0)
    mask = np.clip(mask, 0.0, 1.0)
    
    # Apply vignette (darken edges)
    for c in range(img_array.shape[2]):
        img_array[:, :, c] *= mask
    
    return Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))


def apply_bw(image: Image.Image) -> Image.Image:
    """
    Convert image to black and white.
    
    Args:
        image: PIL Image to convert
        
    Returns:
        Grayscale PIL Image
    """
    return image.convert('L').convert('RGB')


def fit_background(image: Image.Image, canvas_size: Tuple[int, int], mode: str) -> Image.Image:
    """
    Fit background image to canvas size according to mode.
    
    Args:
        image: PIL Image to fit
        canvas_size: Target size (width, height)
        mode: Fit mode ('stretch', 'tile', 'center')
        
    Returns:
        Fitted PIL Image
    """
    canvas_width, canvas_height = canvas_size
    img_width, img_height = image.size
    
    if mode == 'stretch':
        # Stretch to fit canvas
        return image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
    
    elif mode == 'tile':
        # Tile the image
        tiled = Image.new('RGB', (canvas_width, canvas_height))
        for x in range(0, canvas_width, img_width):
            for y in range(0, canvas_height, img_height):
                tiled.paste(image, (x, y))
        return tiled
    
    elif mode == 'center':
        # Center the image, maintaining aspect ratio
        # Calculate scaling to fit within canvas
        scale = min(canvas_width / img_width, canvas_height / img_height)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create canvas and center image
        canvas = Image.new('RGB', (canvas_width, canvas_height), color=(0, 0, 0))
        x_offset = (canvas_width - new_width) // 2
        y_offset = (canvas_height - new_height) // 2
        canvas.paste(resized, (x_offset, y_offset))
        return canvas
    
    else:
        # Default to stretch
        return image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)


def apply_strobe(frame: Image.Image, spectrum_data: np.ndarray, color: Tuple[int, int, int], 
                 threshold: float = 0.5, intensity: float = 0.8) -> Image.Image:
    """
    Apply strobe effect based on audio intensity.
    
    Args:
        frame: PIL Image to apply strobe to
        spectrum_data: Spectrum data for the frame
        color: RGB color tuple for strobe
        threshold: Intensity threshold to trigger strobe (0.0 to 1.0)
        intensity: Strobe intensity (0.0 to 1.0)
        
    Returns:
        Image with strobe effect applied
    """
    # Calculate average intensity from spectrum
    audio_intensity = np.mean(spectrum_data) if len(spectrum_data) > 0 else 0.0
    # Normalize (simple normalization, may need tuning)
    normalized_intensity = min(1.0, audio_intensity / 0.1)
    
    if normalized_intensity < threshold:
        return frame
    
    # Create strobe overlay
    overlay = Image.new('RGB', frame.size, color=color)
    
    # Blend with original frame
    strobe_frame = Image.blend(frame, overlay, intensity)
    return strobe_frame


def fade_in(frame_number: int, total_frames: int) -> float:
    """
    Calculate fade-in alpha value for a frame.
    
    Args:
        frame_number: Current frame number (0-indexed)
        total_frames: Total number of frames for fade-in
        
    Returns:
        Alpha value (0.0 to 1.0)
    """
    if total_frames <= 0:
        return 1.0
    
    progress = min(1.0, frame_number / total_frames)
    return progress


def apply_fade_in(base_image: Image.Image, frame_number: int, total_frames: int) -> Image.Image:
    """
    Apply fade-in effect to an image.
    
    Args:
        base_image: Base image to fade in
        frame_number: Current frame number
        total_frames: Total frames for fade-in
        
    Returns:
        Image with fade-in applied
    """
    alpha = fade_in(frame_number, total_frames)
    
    if alpha >= 1.0:
        return base_image
    
    # Create black background
    black = Image.new('RGB', base_image.size, color=(0, 0, 0))
    
    # Blend with black background
    faded = Image.blend(black, base_image, alpha)
    return faded


def apply_background_animation(base_image: Image.Image, frame_number: int, 
                               animation_type: str, total_frames: Optional[int] = None) -> Image.Image:
    """
    Apply background animation effect.
    
    Args:
        base_image: Base background image
        frame_number: Current frame number
        animation_type: Type of animation ('none', 'fade_in', etc.)
        total_frames: Total frames for animation (used for fade_in)
        
    Returns:
        Image with animation applied
    """
    if animation_type == 'none' or animation_type is None:
        return base_image
    elif animation_type == 'fade_in':
        if total_frames is None:
            total_frames = 90  # Default 3 seconds at 30fps
        return apply_fade_in(base_image, frame_number, total_frames)
    else:
        return base_image

