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


def apply_beat_pulse(frame: Image.Image, beat_strength: float, 
                     scale_factor: float = 1.1) -> Image.Image:
    """
    Apply pulse effect on beats by scaling the image.
    
    Args:
        frame: PIL Image to pulse
        beat_strength: Beat strength (0.0 to 1.0)
        scale_factor: Maximum scale factor at full beat strength
        
    Returns:
        Image with pulse effect
    """
    if beat_strength < 0.01:
        return frame
    
    # Calculate scale based on beat strength
    scale = 1.0 + (scale_factor - 1.0) * beat_strength
    
    # Scale image
    width, height = frame.size
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    scaled = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Crop back to original size (centered)
    left = (new_width - width) // 2
    top = (new_height - height) // 2
    cropped = scaled.crop((left, top, left + width, top + height))
    
    return cropped


def apply_beat_flash(frame: Image.Image, beat_strength: float, 
                     color: Tuple[int, int, int] = (255, 255, 255),
                     max_intensity: float = 0.3) -> Image.Image:
    """
    Apply flash effect on beats.
    
    Args:
        frame: PIL Image to flash
        beat_strength: Beat strength (0.0 to 1.0)
        color: RGB color for flash
        max_intensity: Maximum flash intensity
        
    Returns:
        Image with flash effect
    """
    if beat_strength < 0.01:
        return frame
    
    # Calculate flash intensity
    intensity = beat_strength * max_intensity
    
    # Create flash overlay
    overlay = Image.new('RGB', frame.size, color=color)
    
    # Blend with original frame
    flashed = Image.blend(frame, overlay, intensity)
    return flashed


def apply_beat_strobe(frame: Image.Image, beat_strength: float, 
                      color: Tuple[int, int, int] = (255, 255, 255),
                      threshold: float = 0.5) -> Image.Image:
    """
    Apply strobe effect synchronized to beats.
    
    Args:
        frame: PIL Image to strobe
        beat_strength: Beat strength (0.0 to 1.0)
        color: RGB color for strobe
        threshold: Minimum beat strength to trigger strobe
        
    Returns:
        Image with beat-synchronized strobe
    """
    if beat_strength < threshold:
        return frame
    
    # Full intensity strobe on beat
    overlay = Image.new('RGB', frame.size, color=color)
    
    # Calculate intensity based on beat strength
    intensity = min(0.8, beat_strength)
    
    # Blend with original frame
    strobed = Image.blend(frame, overlay, intensity)
    return strobed


def apply_beat_zoom(frame: Image.Image, beat_strength: float,
                    zoom_amount: float = 0.05) -> Image.Image:
    """
    Apply zoom effect on beats.
    
    Args:
        frame: PIL Image to zoom
        beat_strength: Beat strength (0.0 to 1.0)
        zoom_amount: Amount to zoom (0.0 to 1.0)
        
    Returns:
        Image with zoom effect
    """
    if beat_strength < 0.01:
        return frame
    
    # Calculate zoom based on beat strength
    zoom = 1.0 + (zoom_amount * beat_strength)
    
    width, height = frame.size
    new_width = int(width / zoom)
    new_height = int(height / zoom)
    
    # Calculate crop box (centered)
    left = (width - new_width) // 2
    top = (height - new_height) // 2
    
    # Crop and resize back
    cropped = frame.crop((left, top, left + new_width, top + new_height))
    zoomed = cropped.resize((width, height), Image.Resampling.LANCZOS)
    
    return zoomed


def apply_fade_transition(image1: Image.Image, image2: Image.Image, progress: float) -> Image.Image:
    """
    Apply fade transition between two images.
    
    Args:
        image1: First image (fading out)
        image2: Second image (fading in)
        progress: Transition progress (0.0 to 1.0)
        
    Returns:
        Blended image
    """
    if progress <= 0:
        return image1
    if progress >= 1:
        return image2
    
    # Ensure both images are same mode
    if image1.mode != 'RGB':
        image1 = image1.convert('RGB')
    if image2.mode != 'RGB':
        image2 = image2.convert('RGB')
    
    # Blend images
    return Image.blend(image1, image2, progress)


def apply_crossfade_transition(image1: Image.Image, image2: Image.Image, progress: float) -> Image.Image:
    """
    Apply crossfade transition (same as fade).
    
    Args:
        image1: First image
        image2: Second image
        progress: Transition progress (0.0 to 1.0)
        
    Returns:
        Blended image
    """
    return apply_fade_transition(image1, image2, progress)


def apply_slide_transition(image1: Image.Image, image2: Image.Image, progress: float,
                           direction: str = 'left') -> Image.Image:
    """
    Apply slide transition between two images.
    
    Args:
        image1: First image
        image2: Second image
        progress: Transition progress (0.0 to 1.0)
        direction: Slide direction ('left', 'right', 'up', 'down')
        
    Returns:
        Composite image with slide effect
    """
    if progress <= 0:
        return image1
    if progress >= 1:
        return image2
    
    width, height = image1.size
    
    # Ensure both images are RGBA for compositing
    if image1.mode != 'RGBA':
        image1 = image1.convert('RGBA')
    if image2.mode != 'RGBA':
        image2 = image2.convert('RGBA')
    
    # Create result image
    result = Image.new('RGBA', (width, height))
    
    # Calculate positions based on direction
    if direction == 'left':
        pos1 = (int(-width * progress), 0)
        pos2 = (int(width * (1 - progress)), 0)
    elif direction == 'right':
        pos1 = (int(width * progress), 0)
        pos2 = (int(-width * (1 - progress)), 0)
    elif direction == 'up':
        pos1 = (0, int(-height * progress))
        pos2 = (0, int(height * (1 - progress)))
    else:  # down
        pos1 = (0, int(height * progress))
        pos2 = (0, int(-height * (1 - progress)))
    
    # Paste images at calculated positions
    result.paste(image1, pos1)
    result.paste(image2, pos2)
    
    return result.convert('RGB')


def apply_zoom_transition(image1: Image.Image, image2: Image.Image, progress: float) -> Image.Image:
    """
    Apply zoom transition (image1 zooms out while image2 fades in).
    
    Args:
        image1: First image (zooming out)
        image2: Second image (fading in)
        progress: Transition progress (0.0 to 1.0)
        
    Returns:
        Composite image with zoom effect
    """
    if progress <= 0:
        return image1
    if progress >= 1:
        return image2
    
    width, height = image1.size
    
    # Zoom out image1
    zoom_factor = 1.0 + progress
    new_width = int(width * zoom_factor)
    new_height = int(height * zoom_factor)
    
    # Resize image1 (zoom out)
    zoomed1 = image1.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Crop to original size (centered)
    left = (new_width - width) // 2
    top = (new_height - height) // 2
    zoomed1 = zoomed1.crop((left, top, left + width, top + height))
    
    # Fade in image2
    return apply_fade_transition(zoomed1, image2, progress)


def apply_beat_shake(frame: Image.Image, beat_strength: float, intensity: int = 50) -> Image.Image:
    """
    Apply shake effect based on beat strength.
    
    Args:
        frame: PIL Image to shake
        beat_strength: Beat strength (0.0 to 1.0)
        intensity: Shake intensity (0-100)
        
    Returns:
        Image with shake effect
    """
    if beat_strength < 0.01 or intensity == 0:
        return frame
    
    import random
    
    width, height = frame.size
    
    # Calculate shake amount based on beat strength and intensity
    max_shake = int((intensity / 100) * 20)  # Max 20 pixels shake
    shake_amount = int(max_shake * beat_strength)
    
    # Random offset
    offset_x = random.randint(-shake_amount, shake_amount)
    offset_y = random.randint(-shake_amount, shake_amount)
    
    # Create new image with black background
    result = Image.new('RGB', (width, height), (0, 0, 0))
    
    # Paste original image with offset
    result.paste(frame, (offset_x, offset_y))
    
    return result



