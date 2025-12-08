"""
Visualizer module for different audio visualization styles.
Implements various visualizer types with customizable colors and effects.
"""

import numpy as np
from PIL import Image, ImageDraw
from typing import Tuple, Optional, Dict, Any
import math


class BaseVisualizer:
    """Base class for all visualizers."""
    
    def __init__(self, width: int, height: int, settings: Dict[str, Any]):
        """
        Initialize visualizer.
        
        Args:
            width: Image width
            height: Image height
            settings: Settings dictionary
        """
        self.width = width
        self.height = height
        self.settings = settings
    
    def render(self, bands: np.ndarray, spectrum_data: np.ndarray, 
               frame_number: int) -> Image.Image:
        """
        Render visualization.
        
        Args:
            bands: Frequency band magnitudes
            spectrum_data: Full spectrum data
            frame_number: Current frame number
            
        Returns:
            PIL Image with visualization
        """
        raise NotImplementedError("Subclasses must implement render()")
    
    def get_color(self, index: int, total: int, magnitude: float) -> Tuple[int, int, int, int]:
        """
        Get color for visualization based on gradient settings.
        
        Args:
            index: Current index
            total: Total number of elements
            magnitude: Magnitude value (0.0 to 1.0)
            
        Returns:
            RGBA color tuple
        """
        gradient_type = self.settings.get('color_gradient', 'frequency-based')
        
        if gradient_type == 'pitch_rainbow':
            return self._pitch_rainbow_color(index, total, magnitude)
        elif gradient_type == 'frequency-based':
            return self._frequency_based_color(index, total, magnitude)
        elif gradient_type == 'energy-based':
            return self._energy_based_color(magnitude)
        elif gradient_type == 'custom':
            return self._custom_color(index, total, magnitude)
        elif gradient_type == 'monochrome':
            return self._monochrome_color(magnitude)
        elif gradient_type == 'neon':
            return self._neon_color(index, total, magnitude)
        elif gradient_type == 'sunset':
            return self._sunset_color(index, total, magnitude)
        elif gradient_type == 'ocean':
            return self._ocean_color(index, total, magnitude)
        elif gradient_type == 'fire':
            return self._fire_color(magnitude)
        else:
            return self._frequency_based_color(index, total, magnitude)
    
    def _pitch_rainbow_color(self, index: int, total: int, magnitude: float) -> Tuple[int, int, int, int]:
        """Rainbow spectrum based on pitch/frequency."""
        # Map index to hue (0-360)
        hue = (index / total) * 360
        # Convert HSV to RGB
        h = hue / 60
        x = 1 - abs((h % 2) - 1)
        
        if h < 1:
            r, g, b = 1, x, 0
        elif h < 2:
            r, g, b = x, 1, 0
        elif h < 3:
            r, g, b = 0, 1, x
        elif h < 4:
            r, g, b = 0, x, 1
        elif h < 5:
            r, g, b = x, 0, 1
        else:
            r, g, b = 1, 0, x
        
        # Apply magnitude as brightness
        brightness = 0.5 + (magnitude * 0.5)
        r = int(r * 255 * brightness)
        g = int(g * 255 * brightness)
        b = int(b * 255 * brightness)
        
        return (r, g, b, 255)
    
    def _frequency_based_color(self, index: int, total: int, magnitude: float) -> Tuple[int, int, int, int]:
        """Color based on frequency range: low=red, mid=green, high=blue."""
        if index < total / 3:
            # Low frequency - red to yellow
            r = 255
            g = int(255 * (index / (total / 3)))
            b = 0
        elif index < total * 2 / 3:
            # Mid frequency - yellow to cyan
            r = int(255 * (1 - (index - total / 3) / (total / 3)))
            g = 255
            b = int(255 * ((index - total / 3) / (total / 3)))
        else:
            # High frequency - cyan to blue
            r = 0
            g = int(255 * (1 - (index - total * 2 / 3) / (total / 3)))
            b = 255
        
        return (r, g, b, 255)
    
    def _energy_based_color(self, magnitude: float) -> Tuple[int, int, int, int]:
        """Color intensity based on energy/amplitude."""
        # Blue to red gradient based on energy
        if magnitude < 0.33:
            r = 0
            g = int(magnitude * 3 * 255)
            b = 255
        elif magnitude < 0.66:
            r = int((magnitude - 0.33) * 3 * 255)
            g = 255
            b = int((1 - (magnitude - 0.33) * 3) * 255)
        else:
            r = 255
            g = int((1 - (magnitude - 0.66) * 3) * 255)
            b = 0
        
        return (r, g, b, 255)
    
    def _custom_color(self, index: int, total: int, magnitude: float) -> Tuple[int, int, int, int]:
        """Custom gradient between two user-defined colors."""
        start_color = self.settings.get('custom_color_start', [255, 0, 255])
        end_color = self.settings.get('custom_color_end', [0, 255, 255])
        
        # Interpolate between start and end colors
        t = index / total if total > 0 else 0
        r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * t)
        
        # Apply magnitude as brightness
        brightness = 0.5 + (magnitude * 0.5)
        r = int(r * brightness)
        g = int(g * brightness)
        b = int(b * brightness)
        
        return (r, g, b, 255)
    
    def _monochrome_color(self, magnitude: float) -> Tuple[int, int, int, int]:
        """Single color with varying intensity."""
        base_color = self.settings.get('monochrome_color', [255, 255, 255])
        
        r = int(base_color[0] * magnitude)
        g = int(base_color[1] * magnitude)
        b = int(base_color[2] * magnitude)
        
        return (r, g, b, 255)
    
    def _neon_color(self, index: int, total: int, magnitude: float) -> Tuple[int, int, int, int]:
        """Neon colors: vibrant cyan, magenta, yellow."""
        t = index / total if total > 0 else 0
        brightness = 0.5 + (magnitude * 0.5)
        
        if t < 0.33:
            # Cyan to magenta
            r = int(255 * (t / 0.33) * brightness)
            g = int(255 * (1 - t / 0.33) * brightness)
            b = int(255 * brightness)
        elif t < 0.66:
            # Magenta to yellow
            t_local = (t - 0.33) / 0.33
            r = int(255 * brightness)
            g = int(255 * t_local * brightness)
            b = int(255 * (1 - t_local) * brightness)
        else:
            # Yellow to cyan
            t_local = (t - 0.66) / 0.34
            r = int(255 * (1 - t_local) * brightness)
            g = int(255 * brightness)
            b = int(255 * t_local * brightness)
        
        return (r, g, b, 255)
    
    def _sunset_color(self, index: int, total: int, magnitude: float) -> Tuple[int, int, int, int]:
        """Sunset gradient: purple, orange, pink, yellow."""
        t = index / total if total > 0 else 0
        brightness = 0.5 + (magnitude * 0.5)
        
        if t < 0.25:
            # Purple to orange
            t_local = t / 0.25
            r = int((128 + 127 * t_local) * brightness)
            g = int((0 + 165 * t_local) * brightness)
            b = int((128 - 128 * t_local) * brightness)
        elif t < 0.5:
            # Orange to pink
            t_local = (t - 0.25) / 0.25
            r = int((255 - 0 * t_local) * brightness)
            g = int((165 - 73 * t_local) * brightness)
            b = int((0 + 203 * t_local) * brightness)
        elif t < 0.75:
            # Pink to yellow
            t_local = (t - 0.5) / 0.25
            r = int(255 * brightness)
            g = int((92 + 163 * t_local) * brightness)
            b = int((203 - 203 * t_local) * brightness)
        else:
            # Yellow
            r = int(255 * brightness)
            g = int(255 * brightness)
            b = int(0 * brightness)
        
        return (r, g, b, 255)
    
    def _ocean_color(self, index: int, total: int, magnitude: float) -> Tuple[int, int, int, int]:
        """Ocean gradient: deep blue, cyan, turquoise."""
        t = index / total if total > 0 else 0
        brightness = 0.5 + (magnitude * 0.5)
        
        if t < 0.5:
            # Deep blue to cyan
            t_local = t / 0.5
            r = int((0 + 0 * t_local) * brightness)
            g = int((105 + 150 * t_local) * brightness)
            b = int((148 + 107 * t_local) * brightness)
        else:
            # Cyan to turquoise
            t_local = (t - 0.5) / 0.5
            r = int((0 + 64 * t_local) * brightness)
            g = int((255 - 31 * t_local) * brightness)
            b = int((255 - 47 * t_local) * brightness)
        
        return (r, g, b, 255)
    
    def _fire_color(self, magnitude: float) -> Tuple[int, int, int, int]:
        """Fire gradient based on intensity: black, red, orange, yellow, white."""
        if magnitude < 0.25:
            # Black to red
            t = magnitude / 0.25
            r = int(139 * t)
            g = 0
            b = 0
        elif magnitude < 0.5:
            # Red to orange
            t = (magnitude - 0.25) / 0.25
            r = int(139 + (255 - 139) * t)
            g = int(69 * t)
            b = 0
        elif magnitude < 0.75:
            # Orange to yellow
            t = (magnitude - 0.5) / 0.25
            r = 255
            g = int(69 + (255 - 69) * t)
            b = 0
        else:
            # Yellow to white
            t = (magnitude - 0.75) / 0.25
            r = 255
            g = 255
            b = int(255 * t)
        
        return (r, g, b, 255)


class BarsVisualizer(BaseVisualizer):
    """Classic spectrum bars visualization."""
    
    def render(self, bands: np.ndarray, spectrum_data: np.ndarray, 
               frame_number: int) -> Image.Image:
        """Render spectrum bars."""
        num_bands = len(bands)
        bar_width = self.width // num_bands
        bar_spacing = 2
        
        # Create transparent image
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Normalize bands
        if np.max(bands) > 0:
            normalized_bands = bands / np.max(bands)
        else:
            normalized_bands = bands
        
        # Draw bars
        for i, magnitude in enumerate(normalized_bands):
            bar_height = int(magnitude * self.height * 0.8)
            x = i * bar_width + bar_spacing
            
            color = self.get_color(i, num_bands, magnitude)
            
            # Draw bar from bottom
            # Ensure bar_height doesn't exceed height and coordinates are valid
            bar_height = min(bar_height, self.height)
            y1 = max(0, self.height - bar_height)
            y2 = self.height
            # Ensure valid rectangle coordinates
            if y1 < y2 and x < x + bar_width - bar_spacing:
                draw.rectangle([x, y1, x + bar_width - bar_spacing, y2], fill=color)
        
        return img


class FilledWaveformVisualizer(BaseVisualizer):
    """Filled waveform visualization."""
    
    def render(self, bands: np.ndarray, spectrum_data: np.ndarray, 
               frame_number: int) -> Image.Image:
        """Render filled waveform."""
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        num_points = len(bands)
        if num_points < 2:
            return img
        
        # Normalize bands
        if np.max(bands) > 0:
            normalized_bands = bands / np.max(bands)
        else:
            normalized_bands = bands
        
        # Create waveform points
        points_top = []
        points_bottom = []
        center_y = self.height // 2
        
        for i, magnitude in enumerate(normalized_bands):
            x = int((i / num_points) * self.width)
            wave_height = int(magnitude * self.height * 0.4)
            
            points_top.append((x, center_y - wave_height))
            points_bottom.append((x, center_y + wave_height))
        
        # Draw filled polygon
        all_points = points_top + points_bottom[::-1]
        
        # Get average color
        avg_magnitude = np.mean(normalized_bands)
        color = self.get_color(num_points // 2, num_points, avg_magnitude)
        
        if len(all_points) >= 3:
            draw.polygon(all_points, fill=color)
        
        return img


class CircleVisualizer(BaseVisualizer):
    """Circular spectrum analyzer."""
    
    def render(self, bands: np.ndarray, spectrum_data: np.ndarray, 
               frame_number: int) -> Image.Image:
        """Render circular spectrum."""
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        num_bands = len(bands)
        center_x = self.width // 2
        center_y = self.height // 2
        base_radius = min(self.width, self.height) // 4
        max_bar_length = min(self.width, self.height) // 3
        
        # Normalize bands
        if np.max(bands) > 0:
            normalized_bands = bands / np.max(bands)
        else:
            normalized_bands = bands
        
        # Draw bars radiating from center
        for i, magnitude in enumerate(normalized_bands):
            angle = (i / num_bands) * 2 * math.pi
            bar_length = magnitude * max_bar_length
            
            # Start point
            x1 = center_x + int(base_radius * math.cos(angle))
            y1 = center_y + int(base_radius * math.sin(angle))
            
            # End point
            x2 = center_x + int((base_radius + bar_length) * math.cos(angle))
            y2 = center_y + int((base_radius + bar_length) * math.sin(angle))
            
            color = self.get_color(i, num_bands, magnitude)
            
            # Draw line with width
            draw.line([(x1, y1), (x2, y2)], fill=color, width=3)
        
        return img


class LineWaveformVisualizer(BaseVisualizer):
    """Traditional oscilloscope-style line waveform."""
    
    def render(self, bands: np.ndarray, spectrum_data: np.ndarray, 
               frame_number: int) -> Image.Image:
        """Render line waveform."""
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        num_points = len(bands)
        if num_points < 2:
            return img
        
        # Normalize bands
        if np.max(bands) > 0:
            normalized_bands = bands / np.max(bands)
        else:
            normalized_bands = bands
        
        # Create waveform points
        points = []
        center_y = self.height // 2
        
        for i, magnitude in enumerate(normalized_bands):
            x = int((i / num_points) * self.width)
            # Alternate above and below center for waveform effect
            wave_height = int(magnitude * self.height * 0.4)
            if i % 2 == 0:
                y = center_y - wave_height
            else:
                y = center_y + wave_height
            points.append((x, y))
        
        # Draw line
        if len(points) >= 2:
            # Get average color
            avg_magnitude = np.mean(normalized_bands)
            color = self.get_color(num_points // 2, num_points, avg_magnitude)
            
            draw.line(points, fill=color, width=3)
        
        return img


class ParticleVisualizer(BaseVisualizer):
    """Particle system that reacts to audio."""
    
    def __init__(self, width: int, height: int, settings: Dict[str, Any]):
        """Initialize particle visualizer."""
        super().__init__(width, height, settings)
        self.particles = []
        self.max_particles = 200
    
    def render(self, bands: np.ndarray, spectrum_data: np.ndarray, 
               frame_number: int) -> Image.Image:
        """Render particle system."""
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        num_bands = len(bands)
        
        # Normalize bands
        if np.max(bands) > 0:
            normalized_bands = bands / np.max(bands)
        else:
            normalized_bands = bands
        
        # Generate new particles based on audio intensity
        for i, magnitude in enumerate(normalized_bands):
            if magnitude > 0.3 and len(self.particles) < self.max_particles:
                # Create particle
                x = int((i / num_bands) * self.width)
                y = self.height // 2
                
                # Random velocity based on magnitude
                vx = (np.random.random() - 0.5) * magnitude * 20
                vy = (np.random.random() - 0.5) * magnitude * 20
                
                color = self.get_color(i, num_bands, magnitude)
                
                self.particles.append({
                    'x': x,
                    'y': y,
                    'vx': vx,
                    'vy': vy,
                    'life': 1.0,
                    'color': color,
                    'size': int(magnitude * 10) + 2
                })
        
        # Update and draw particles
        new_particles = []
        for particle in self.particles:
            # Update position
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Apply gravity
            particle['vy'] += 0.5
            
            # Reduce life
            particle['life'] -= 0.02
            
            # Keep particle if still alive and in bounds
            if particle['life'] > 0:
                # Draw particle
                x = int(particle['x'])
                y = int(particle['y'])
                size = particle['size']
                
                # Fade color based on life
                r, g, b, a = particle['color']
                a = int(255 * particle['life'])
                color = (r, g, b, a)
                
                if 0 <= x < self.width and 0 <= y < self.height:
                    draw.ellipse([x - size, y - size, x + size, y + size], fill=color)
                    new_particles.append(particle)
        
        self.particles = new_particles
        
        return img


class NCSBarsVisualizer(BaseVisualizer):
    """NCS (NoCopyrightSounds) style centered bars with glow effect."""
    
    def render(self, bands: np.ndarray, spectrum_data: np.ndarray, 
               frame_number: int) -> Image.Image:
        """Render NCS-style centered bars with glow."""
        num_bands = len(bands)
        bar_width = self.width // num_bands
        bar_spacing = 2
        
        # Create transparent image
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Normalize bands
        if np.max(bands) > 0:
            normalized_bands = bands / np.max(bands)
        else:
            normalized_bands = bands
        
        # Draw bars centered vertically
        center_y = self.height // 2
        
        for i, magnitude in enumerate(normalized_bands):
            bar_height = int(magnitude * self.height * 0.4)
            x = i * bar_width + bar_spacing
            
            color = self.get_color(i, num_bands, magnitude)
            
            # Draw bar symmetrically from center
            # Ensure bar_height doesn't exceed half height and coordinates are valid
            max_bar_height = min(bar_height, center_y, self.height - center_y)
            y1 = max(0, center_y - max_bar_height)
            y2 = min(self.height, center_y + max_bar_height)
            # Ensure valid rectangle coordinates
            if y1 < y2 and x < x + bar_width - bar_spacing:
                draw.rectangle([x, y1, x + bar_width - bar_spacing, y2], fill=color)
        
        # Apply glow effect
        img = self._apply_glow(img, radius=15, iterations=2)
        
        return img
    
    def _apply_glow(self, image: Image.Image, radius: int = 10, iterations: int = 2) -> Image.Image:
        """Apply glow/bloom effect to image."""
        from PIL import ImageFilter
        
        # Create a copy for glowing
        glow = image.copy()
        
        # Apply multiple blur passes for stronger glow
        for _ in range(iterations):
            glow = glow.filter(ImageFilter.GaussianBlur(radius=radius))
        
        # Blend glow with original
        result = Image.new('RGBA', image.size, (0, 0, 0, 0))
        result = Image.alpha_composite(result, glow)
        result = Image.alpha_composite(result, image)
        
        return result


class DualSpectrumVisualizer(BaseVisualizer):
    """Dual spectrum with mirrored top/bottom display."""
    
    def render(self, bands: np.ndarray, spectrum_data: np.ndarray, 
               frame_number: int) -> Image.Image:
        """Render mirrored dual spectrum."""
        num_bands = len(bands)
        bar_width = self.width // num_bands
        bar_spacing = 2
        
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Normalize bands
        if np.max(bands) > 0:
            normalized_bands = bands / np.max(bands)
        else:
            normalized_bands = bands
        
        center_y = self.height // 2
        
        for i, magnitude in enumerate(normalized_bands):
            bar_height = int(magnitude * self.height * 0.45)
            x = i * bar_width + bar_spacing
            
            color = self.get_color(i, num_bands, magnitude)
            
            # Top bars (mirrored down from center)
            draw.rectangle([x, center_y - bar_height, x + bar_width - bar_spacing, center_y], fill=color)
            
            # Bottom bars (mirrored up from center)
            draw.rectangle([x, center_y, x + bar_width - bar_spacing, center_y + bar_height], fill=color)
        
        return img


class WaveformParticleVisualizer(BaseVisualizer):
    """Hybrid waveform with particle effects."""
    
    def __init__(self, width: int, height: int, settings: Dict[str, Any]):
        """Initialize hybrid visualizer."""
        super().__init__(width, height, settings)
        self.particles = []
        self.max_particles = 150
    
    def render(self, bands: np.ndarray, spectrum_data: np.ndarray, 
               frame_number: int) -> Image.Image:
        """Render waveform with particles."""
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        num_points = len(bands)
        if num_points < 2:
            return img
        
        # Normalize bands
        if np.max(bands) > 0:
            normalized_bands = bands / np.max(bands)
        else:
            normalized_bands = bands
        
        # Draw waveform
        points = []
        center_y = self.height // 2
        
        for i, magnitude in enumerate(normalized_bands):
            x = int((i / num_points) * self.width)
            wave_height = int(magnitude * self.height * 0.3)
            y = center_y - wave_height
            points.append((x, y))
        
        if len(points) >= 2:
            avg_magnitude = np.mean(normalized_bands)
            color = self.get_color(num_points // 2, num_points, avg_magnitude)
            draw.line(points, fill=color, width=3)
        
        # Generate particles at peaks
        for i, magnitude in enumerate(normalized_bands):
            if magnitude > 0.5 and len(self.particles) < self.max_particles:
                x = int((i / num_points) * self.width)
                y = center_y - int(magnitude * self.height * 0.3)
                
                vx = (np.random.random() - 0.5) * 5
                vy = -np.random.random() * 5
                
                color = self.get_color(i, num_points, magnitude)
                
                self.particles.append({
                    'x': x, 'y': y, 'vx': vx, 'vy': vy,
                    'life': 1.0, 'color': color, 'size': 3
                })
        
        # Update and draw particles
        new_particles = []
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.3  # gravity
            particle['life'] -= 0.03
            
            if particle['life'] > 0:
                x, y = int(particle['x']), int(particle['y'])
                size = particle['size']
                r, g, b, a = particle['color']
                a = int(255 * particle['life'])
                color = (r, g, b, a)
                
                if 0 <= x < self.width and 0 <= y < self.height:
                    draw.ellipse([x - size, y - size, x + size, y + size], fill=color)
                    new_particles.append(particle)
        
        self.particles = new_particles
        
        return img


class ModernGradientBarsVisualizer(BaseVisualizer):
    """Modern style bars with smooth gradients and rounded corners."""
    
    def render(self, bands: np.ndarray, spectrum_data: np.ndarray, 
               frame_number: int) -> Image.Image:
        """Render modern gradient bars."""
        from PIL import ImageDraw
        
        num_bands = len(bands)
        bar_width = max(10, self.width // num_bands)
        bar_spacing = 4
        
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Normalize bands
        if np.max(bands) > 0:
            normalized_bands = bands / np.max(bands)
        else:
            normalized_bands = bands
        
        for i, magnitude in enumerate(normalized_bands):
            bar_height = int(magnitude * self.height * 0.8)
            x = i * bar_width + bar_spacing
            
            # Get color
            color = self.get_color(i, num_bands, magnitude)
            
            # Draw rounded rectangle
            # Ensure bar_height doesn't exceed height and coordinates are valid
            bar_height = min(bar_height, self.height)
            y1 = max(0, self.height - bar_height)
            y2 = self.height
            
            # Ensure valid rectangle coordinates before drawing
            if y1 < y2 and x < x + bar_width - bar_spacing:
                # Draw bar with rounded top
                corner_radius = min(bar_width // 2, 10)
                self._draw_rounded_rectangle(draw, [x, y1, x + bar_width - bar_spacing, y2], 
                                            corner_radius, color)
        
        return img
    
    def _draw_rounded_rectangle(self, draw, coords, radius, fill):
        """Draw a rounded rectangle."""
        x1, y1, x2, y2 = coords
        
        # Validate coordinates
        if x1 >= x2 or y1 >= y2:
            return  # Invalid coordinates, skip drawing
        
        # Ensure radius doesn't exceed rectangle dimensions
        radius = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)
        if radius <= 0:
            # If radius is invalid, just draw a regular rectangle
            draw.rectangle([x1, y1, x2, y2], fill=fill)
            return
        
        # Draw main rectangle
        if y1 + radius < y2:
            draw.rectangle([x1, y1 + radius, x2, y2], fill=fill)
        if x1 + radius < x2 - radius and y1 < y1 + radius:
            draw.rectangle([x1 + radius, y1, x2 - radius, y1 + radius], fill=fill)
        
        # Draw corners (only if they fit)
        if y1 + radius * 2 <= y2:
            if x1 + radius * 2 <= x2:
                draw.ellipse([x1, y1, x1 + radius * 2, y1 + radius * 2], fill=fill)
            if x2 - radius * 2 >= x1:
                draw.ellipse([x2 - radius * 2, y1, x2, y1 + radius * 2], fill=fill)


class PulseRingVisualizer(BaseVisualizer):
    """Expanding rings that pulse with bass frequencies."""
    
    def __init__(self, width: int, height: int, settings: Dict[str, Any]):
        """Initialize pulse ring visualizer."""
        super().__init__(width, height, settings)
        self.rings = []
    
    def render(self, bands: np.ndarray, spectrum_data: np.ndarray, 
               frame_number: int) -> Image.Image:
        """Render expanding pulse rings."""
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Normalize bands
        if np.max(bands) > 0:
            normalized_bands = bands / np.max(bands)
        else:
            normalized_bands = bands
        
        # Get bass energy (low frequencies)
        bass_energy = np.mean(normalized_bands[:len(normalized_bands)//4])
        
        # Create new ring on strong bass
        if bass_energy > 0.5 and (not self.rings or self.rings[-1]['radius'] > 30):
            center_x = self.width // 2
            center_y = self.height // 2
            
            color = self.get_color(0, 10, bass_energy)
            
            self.rings.append({
                'x': center_x,
                'y': center_y,
                'radius': 5,
                'life': 1.0,
                'color': color,
                'thickness': int(10 * bass_energy)
            })
        
        # Update and draw rings
        new_rings = []
        for ring in self.rings:
            ring['radius'] += 5
            ring['life'] -= 0.02
            
            if ring['life'] > 0 and ring['radius'] < max(self.width, self.height):
                r, g, b, a = ring['color']
                a = int(255 * ring['life'])
                color = (r, g, b, a)
                
                thickness = ring['thickness']
                x, y = ring['x'], ring['y']
                radius = ring['radius']
                
                # Draw ring
                draw.ellipse([x - radius, y - radius, x + radius, y + radius], 
                           outline=color, width=thickness)
                
                new_rings.append(ring)
        
        self.rings = new_rings
        
        return img


class FrequencyDotsVisualizer(BaseVisualizer):
    """Grid of dots that scale with frequency bands."""
    
    def render(self, bands: np.ndarray, spectrum_data: np.ndarray, 
               frame_number: int) -> Image.Image:
        """Render frequency dots grid."""
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Normalize bands
        if np.max(bands) > 0:
            normalized_bands = bands / np.max(bands)
        else:
            normalized_bands = bands
        
        # Grid configuration
        num_bands = len(bands)
        cols = min(num_bands, 40)
        rows = 10
        
        cell_width = self.width // cols
        cell_height = self.height // rows
        
        for col in range(cols):
            if col >= len(normalized_bands):
                break
                
            magnitude = normalized_bands[col]
            
            # Number of active dots in column based on magnitude
            active_rows = int(magnitude * rows)
            
            for row in range(active_rows):
                x = col * cell_width + cell_width // 2
                y = self.height - (row * cell_height) - cell_height // 2
                
                # Dot size based on magnitude
                dot_size = int(5 + magnitude * 10)
                
                # Color based on frequency
                color = self.get_color(col, cols, magnitude)
                
                draw.ellipse([x - dot_size, y - dot_size, x + dot_size, y + dot_size], 
                           fill=color)
        
        return img


class VisualizerFactory:
    """Factory for creating visualizers."""
    
    @staticmethod
    def create(style: str, width: int, height: int, settings: Dict[str, Any]) -> BaseVisualizer:
        """
        Create visualizer instance.
        
        Args:
            style: Visualizer style name
            width: Image width
            height: Image height
            settings: Settings dictionary
            
        Returns:
            Visualizer instance
        """
        style = style.lower().replace(' ', '_')
        
        if style == 'bars':
            return BarsVisualizer(width, height, settings)
        elif style == 'filled_waveform':
            return FilledWaveformVisualizer(width, height, settings)
        elif style == 'circle':
            return CircleVisualizer(width, height, settings)
        elif style == 'line_waveform':
            return LineWaveformVisualizer(width, height, settings)
        elif style == 'particle':
            return ParticleVisualizer(width, height, settings)
        elif style == 'ncs_bars':
            return NCSBarsVisualizer(width, height, settings)
        elif style == 'dual_spectrum':
            return DualSpectrumVisualizer(width, height, settings)
        elif style == 'waveform_particle':
            return WaveformParticleVisualizer(width, height, settings)
        elif style == 'modern_gradient_bars':
            return ModernGradientBarsVisualizer(width, height, settings)
        elif style == 'pulse_ring':
            return PulseRingVisualizer(width, height, settings)
        elif style == 'frequency_dots':
            return FrequencyDotsVisualizer(width, height, settings)
        else:
            # Default to bars
            return BarsVisualizer(width, height, settings)


